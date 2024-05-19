import random
import sys
import pytest
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_048():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Full_Refund_Via_API_Razorpay
    Sub Feature Description: Performing a upi full refund using api for Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 048: TC048
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db()
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(1700, 1800)
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = payment_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount_api
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn
            api_details_hmac['RequestBody']['payload']['qr_code']['entity']['id'] = publish_id
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED REFUNDED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": refund_txn_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": refund_date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_customer_name_refunded = txn_history_page.fetch_customer_name_text()
                logger.debug(
                    f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refunded}")
                app_payer_name_refunded = txn_history_page.fetch_payer_name_text()
                logger.debug(
                    f"Fetching payer_name from txn history for the txn : {refund_txn_id}, {app_payer_name_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement "
                    f"status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "customer_name_2": app_customer_name_refunded,
                    "payer_name_2": app_payer_name_refunded,
                    "pmt_msg_2": payment_msg_refunded,
                    "date_2": app_date_and_time_refunded,
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
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "REFUNDED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": str(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "order_id_2": order_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "date_2": refund_date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        order_id_api = elements["externalRefNumber"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = int(elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        mid_api_refunded = elements["mid"]
                        tid_api_refunded = elements["tid"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        order_id_api_refunded = elements["orderNumber"]
                        customer_name_api_refunded = elements["customerName"]
                        payer_name_api_refunded = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(amount),
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].values[0]
                payment_mode_db_refunded = result["payment_mode"].values[0]
                amount_db_refunded = int(result["amount"].values[0])
                state_db_refunded = result["state"].values[0]
                payment_gateway_db_refunded = result["payment_gateway"].values[0]
                acquirer_code_db_refunded = result["acquirer_code"].values[0]
                bank_code_db_refunded = result["bank_code"].values[0]
                settlement_status_db_refunded = result["settlement_status"].values[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]
                order_id_db_refunded = result['external_ref'].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].values[0]
                upi_txn_type_db_refunded = result["txn_type"].values[0]
                upi_bank_code_db_refunded = result["bank_code"].values[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": str(amount_db_refunded),
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": "-" if refund_rrn is None else refund_rrn,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,

                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "auth_code_2": auth_code_portal_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(refund_created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date, 'time': txn_time,
                    'AUTH CODE': "" if refund_auth_code is None else refund_auth_code
                }
                receipt_validator.perform_charge_slip_validations(refund_txn_id,
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_049():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Partial_Refund_Via_Razorpay
    Sub Feature Description: Performing a upi partial refund using api for Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 049: TC049
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db()
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(2700, 2800)
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = payment_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount_api
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn
            api_details_hmac['RequestBody']['payload']['qr_code']['entity']['id'] = publish_id
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            refund_amt = amount - 1000
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": refund_amt, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:,.2f}".format(refund_amt),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": refund_txn_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": refund_date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_customer_name_refunded = txn_history_page.fetch_customer_name_text()
                logger.debug(
                    f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refunded}")
                app_payer_name_refunded = txn_history_page.fetch_payer_name_text()
                logger.debug(
                    f"Fetching payer_name from txn history for the txn : {refund_txn_id}, {app_payer_name_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement "
                    f"status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "customer_name_2": app_customer_name_refunded,
                    "payer_name_2": app_payer_name_refunded,
                    "pmt_msg_2": payment_msg_refunded,
                    "date_2": app_date_and_time_refunded,
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
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": str(refund_amt), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "date_2": refund_date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = int(elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        mid_api_refunded = elements["mid"]
                        tid_api_refunded = elements["tid"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        customer_name_api_refunded = elements["customerName"]
                        payer_name_api_refunded = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name_2": payer_name_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(refund_amt),
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].values[0]
                payment_mode_db_refunded = result["payment_mode"].values[0]
                amount_db_refunded = int(result["amount"].values[0])
                state_db_refunded = result["state"].values[0]
                payment_gateway_db_refunded = result["payment_gateway"].values[0]
                acquirer_code_db_refunded = result["acquirer_code"].values[0]
                settlement_status_db_refunded = result["settlement_status"].values[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].values[0]
                upi_txn_type_db_refunded = result["txn_type"].values[0]
                upi_bank_code_db_refunded = result["bank_code"].values[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": str(amount_db_refunded),
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refund_amt),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": "-" if refund_rrn is None else refund_rrn,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "auth_code_2": auth_code_portal_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(refund_created_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI',
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(refund_amt),
                    'date': txn_date, 'time': txn_time,
                    'AUTH CODE': "" if refund_auth_code is None else refund_auth_code
                }
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time)

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date_2, 'time': txn_time_2,
                    'AUTH CODE': "" if auth_code is None else auth_code
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password},
                    expected_charge_slip_values_2)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    refund_txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_050():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_Posted_Via_API_Razorpay
    Sub Feature Description: Performing a upi refund posted using api for Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 050: TC050
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db()
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(1200, 1300)
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = payment_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount_api
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn
            api_details_hmac['RequestBody']['payload']['qr_code']['entity']['id'] = publish_id
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "REVPENDING",
                    "txn_id_2": refund_txn_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "pmt_msg_2": "REFUND PENDING",
                    "date_2": refund_date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_customer_name_refunded = txn_history_page.fetch_customer_name_text()
                logger.debug(
                    f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refunded}")
                app_payer_name_refunded = txn_history_page.fetch_payer_name_text()
                logger.debug(
                    f"Fetching payer_name from txn history for the txn : {refund_txn_id}, {app_payer_name_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement "
                    f"status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "customer_name_2": app_customer_name_refunded,
                    "payer_name_2": app_payer_name_refunded,
                    "pmt_msg_2": payment_msg_refunded,
                    "date_2": app_date_and_time_refunded,
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
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "pmt_status_2": "REFUND_POSTED",
                    "txn_amt_2": str(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_INITIATED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code_txn,
                    "order_id_2": order_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "date_2": refund_date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        order_id_api = elements["externalRefNumber"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = int(elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        order_id_api_refunded = elements["orderNumber"]
                        customer_name_api_refunded = elements["customerName"]
                        payer_name_api_refunded = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "REFUND_POSTED",
                    "pmt_state_2": "REFUND_INITIATED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(amount),
                    "upi_txn_status_2": "REFUND_POSTED",
                    "settle_status_2": "REVPENDING",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].values[0]
                payment_mode_db_refunded = result["payment_mode"].values[0]
                amount_db_refunded = int(result["amount"].values[0])
                state_db_refunded = result["state"].values[0]
                payment_gateway_db_refunded = result["payment_gateway"].values[0]
                acquirer_code_db_refunded = result["acquirer_code"].values[0]
                settlement_status_db_refunded = result["settlement_status"].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].values[0]
                upi_txn_type_db_refunded = result["txn_type"].values[0]
                upi_bank_code_db_refunded = result["bank_code"].values[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": str(amount_db_refunded),
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUND_POSTED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": "-" if refund_rrn is None else refund_rrn,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "auth_code_2": auth_code_portal_2
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
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date, 'time': txn_time,
                    'AUTH CODE': "" if auth_code is None else auth_code
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_051():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_Failed_Via_API_Razorpay
    Sub Feature Description: Performing a upi refund failed using api for Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 051: TC051
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db()
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(1400, 1500)
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = payment_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount_api
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn
            api_details_hmac['RequestBody']['payload']['qr_code']['entity']['id'] = publish_id
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "FAILED",
                    "txn_id_2": refund_txn_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "pmt_msg_2": "PAYMENT FAILED",
                    "date_2": refund_date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_customer_name_refunded = txn_history_page.fetch_customer_name_text()
                logger.debug(
                    f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refunded}")
                app_payer_name_refunded = txn_history_page.fetch_payer_name_text()
                logger.debug(
                    f"Fetching payer_name from txn history for the txn : {refund_txn_id}, {app_payer_name_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement "
                    f"status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "customer_name_2": app_customer_name_refunded,
                    "payer_name_2": app_payer_name_refunded,
                    "pmt_msg_2": payment_msg_refunded,
                    "date_2": app_date_and_time_refunded,
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
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "pmt_status_2": "FAILED",
                    "txn_amt_2": str(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "org_code_2": org_code_txn,
                    "order_id_2": order_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "date_2": refund_date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        order_id_api = elements["externalRefNumber"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = int(elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        order_id_api_refunded = elements["orderNumber"]
                        customer_name_api_refunded = elements["customerName"]
                        payer_name_api_refunded = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(amount),
                    "upi_txn_status_2": "FAILED",
                    "settle_status_2": "FAILED",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].values[0]
                payment_mode_db_refunded = result["payment_mode"].values[0]
                amount_db_refunded = int(result["amount"].values[0])
                state_db_refunded = result["state"].values[0]
                payment_gateway_db_refunded = result["payment_gateway"].values[0]
                acquirer_code_db_refunded = result["acquirer_code"].values[0]
                settlement_status_db_refunded = result["settlement_status"].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].values[0]
                upi_txn_type_db_refunded = result["txn_type"].values[0]
                upi_bank_code_db_refunded = result["bank_code"].values[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": str(amount_db_refunded),
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "FAILED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": "-" if refund_rrn is None else refund_rrn,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "auth_code_2": auth_code_portal_2
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
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date, 'time': txn_time,
                    'AUTH CODE': "" if auth_code is None else auth_code
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_052():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Refund_With_Decimal_Via_Razorpay
    Sub Feature Description: Verification of a upi refund with decimal value using api for Razorpay
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 052: TC052
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db()
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(1800, 1900)
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC_success')
            api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = payment_id
            api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = amount_api
            api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn
            api_details_hmac['RequestBody']['payload']['qr_code']['entity']['id'] = publish_id
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            refund_amt = amount - 100.55
            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": refund_amt, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' and orig_txn_id ='{txn_id}'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            refund_rrn = result['rr_number'].values[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched refund_customer_name from txn table is : {refund_customer_name}")
            refund_txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id_refunded from txn table is : {refund_txn_id}")
            refund_payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched refund_payer_name from txn table is : {refund_payer_name}")
            refund_org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched refund_org_code_txn from txn table is : {refund_org_code_txn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched refund_auth_code from txn table is : {refund_auth_code}")

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
                refund_date_and_time = date_time_converter.to_app_format(refund_created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": "{:,.2f}".format(refund_amt),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": refund_txn_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": refund_date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(refund_txn_id)
                app_customer_name_refunded = txn_history_page.fetch_customer_name_text()
                logger.debug(
                    f"Fetching customer_name from txn history for the txn : {refund_txn_id}, {app_customer_name_refunded}")
                app_payer_name_refunded = txn_history_page.fetch_payer_name_text()
                logger.debug(
                    f"Fetching payer_name from txn history for the txn : {refund_txn_id}, {app_payer_name_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {refund_txn_id}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement "
                    f"status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "customer_name_2": app_customer_name_refunded,
                    "payer_name_2": app_payer_name_refunded,
                    "pmt_msg_2": payment_msg_refunded,
                    "date_2": app_date_and_time_refunded,
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
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "pmt_status_2": "REFUNDED",
                    "txn_amt_2": str(refund_amt), "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "txn_type_2": refund_txn_type,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "order_id_2": order_id,
                    "customer_name_2": refund_customer_name,
                    "payer_name_2": refund_payer_name,
                    "date_2": refund_date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        order_id_api = elements["externalRefNumber"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                for elements in responseInList:
                    if elements["txnId"] == refund_txn_id:
                        status_api_refunded = elements["status"]
                        amount_api_refunded = (elements["amount"])
                        payment_mode_api_refunded = elements["paymentMode"]
                        state_api_refunded = elements["states"][0]
                        settlement_status_api_refunded = elements["settlementStatus"]
                        acquirer_code_api_refunded = elements["acquirerCode"]
                        org_code_api_refunded = elements["orgCode"]
                        mid_api_refunded = elements["mid"]
                        tid_api_refunded = elements["tid"]
                        txn_type_api_refunded = elements["txnType"]
                        date_api_refunded = elements["createdTime"]
                        order_id_api_refunded = elements["orderNumber"]
                        customer_name_api_refunded = elements["customerName"]
                        payer_name_api_refunded = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),

                    "pmt_status_2": status_api_refunded,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_2": customer_name_api_refunded,
                    "payer_name_2": payer_name_api_refunded,
                    "order_id_2": order_id_api_refunded,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(refund_amt),
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].values[0]
                payment_mode_db_refunded = result["payment_mode"].values[0]
                amount_db_refunded = (result["amount"].values[0])
                state_db_refunded = result["state"].values[0]
                payment_gateway_db_refunded = result["payment_gateway"].values[0]
                acquirer_code_db_refunded = result["acquirer_code"].values[0]
                settlement_status_db_refunded = result["settlement_status"].values[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{refund_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].values[0]
                upi_txn_type_db_refunded = result["txn_type"].values[0]
                upi_bank_code_db_refunded = result["bank_code"].values[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt_2": str(amount_db_refunded),
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "pmt_gateway_2": payment_gateway_db_refunded,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(refund_created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(refund_amt),
                    "username_2": app_username,
                    "txn_id_2": refund_txn_id,
                    "rrn_2": "-" if refund_rrn is None else refund_rrn,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {

                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "rrn_2": rr_number_2,
                    "auth_code_2": auth_code_portal_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(refund_created_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI',
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(refund_amt),
                    'date': txn_date, 'time': txn_time,
                    'AUTH CODE': "" if refund_auth_code is None else refund_auth_code
                }
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date_2, 'time': txn_time_2,
                    'AUTH CODE': "" if auth_code is None else auth_code
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password},
                    expected_charge_slip_values_2)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    refund_txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'
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