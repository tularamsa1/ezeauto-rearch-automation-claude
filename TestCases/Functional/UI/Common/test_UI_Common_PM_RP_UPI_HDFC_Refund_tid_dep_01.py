import random
import sys
from datetime import datetime
import pytest

from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter, \
    receipt_validator, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_103_161():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI Refund By API_HDFC_Tid_dep
    Sub Feature Description: Tid Dep - Tid Dep - Verification of a Remote Pay refund using api for HDFC
    TC naming code description:100: Payment Method,103: RemotePay,161: TC161
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize(browser_type="firefox")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(200, 300)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is: {order_id}")

            # acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")
            logger.debug(f"device_serial is: {device_serial}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            # ui_driver = TestSuiteSetup.initialize_firefox_driver()
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {tid}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of upi_merchant_config table is : {result}")
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Fetching upi_mc_id from db query : {upi_mc_id} ")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(txn_id_original)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                txn_id_original) + "'"
            logger.debug(f"Query to fetch txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching refund_auth_code from db query : {refund_auth_code} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_refunded from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_refunded from db query : {rrn_refunded} ")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from db query : {created_time} ")
            refund_amt = result['amount'].values[0]
            logger.debug(f"Fetching refund_amt from db query : {refund_amt} ")

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
                original_date_and_time = date_time_converter.to_app_format(created_time_original)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED REFUNDED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id_original,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "auth_code": auth_code,
                    "auth_code_2": refund_auth_code,
                    "date_2": date_and_time,
                    "date": original_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_refunded}, {app_auth_code_refunded}")
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
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_auth_code_original = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_original}, {app_auth_code_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "auth_code_2": app_auth_code_refunded,
                    "date_2": app_date_and_time,
                    "date": app_original_date_and_time
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_original,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_refunded,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "auth_code_2": refund_auth_code,
                    "auth_code": auth_code,
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_original
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original is : {payment_mode_api_original}")
                rrn_api_original = response["rrNumber"]
                logger.debug(f"rrn_api_original is : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original is : {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original is : {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original is : {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original is : {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original is : {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid_api_original is : {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid_api_original is : {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original is : {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original is : {auth_code_api_original}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_refunded
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded is : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn_api_refunded is : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded is : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded is : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded is : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded is : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid_api_refunded is : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid_api_refunded is : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded is : {txn_type_api_refunded}")
                auth_code_api_refunded = response["authCode"]
                logger.debug(f"auth_code_api_refunded is : {auth_code_api_refunded}")

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
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code_2": auth_code_api_refunded,
                    "auth_code": auth_code_api_original
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "AUTHORIZED_REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "upi_txn_status": "AUTHORIZED_REFUNDED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "device_serial": device_serial,
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in DB validation is : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"status_db_refunded is : {status_db_refunded}")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_refunded is : {payment_mode_db_refunded}")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_refunded is : {amount_db_refunded}")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"state_db_refunded is : {state_db_refunded}")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_refunded is : {acquirer_code_db_refunded}")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_refunded is : {settlement_status_db_refunded}")
                tid_db_refunded = result['tid'].values[0]
                logger.debug(f"tid_db_refunded is : {tid_db_refunded}")
                mid_db_refunded = result['mid'].values[0]
                logger.debug(f"mid_db_refunded is : {mid_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB validation is : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"upi_status_db_refunded is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_refunded is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_refunded is : {upi_bank_code_db_refunded}")
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db_refunded is : {upi_mc_id_db_refunded}")

                query = "select * from txn where id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in DB validation is : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"status_db_original is : {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_original is : {payment_mode_db_original}")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_original is : {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"state_db_original is : {state_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_original is : {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_original is : {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_original is : {settlement_status_db_original}")

                query = "select * from upi_txn where txn_id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB validation is : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"upi_status_db_original is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_original is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_original is : {upi_bank_code_db_original}")
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db_original is : {upi_mc_id_db_original}")

                query = "select * from upi_merchant_config where org_code ='" + str(
                    org_code) + "' and bank_code = 'HDFC';"
                logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_merchant_config table in DB validation is : {result}")
                mid_db_original = result['mid'].iloc[0]
                logger.debug(f"mid_db_original is : {mid_db_original}")
                tid_db_original = result['tid'].iloc[0]
                logger.debug(f"mid_db_original is : {mid_db_original}")

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {result}")
                device_serial_db_orginial = result['device_serial'].iloc[0]
                logger.debug(f"device_serial_db_orginial is : {device_serial_db_orginial}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "upi_mc_id": upi_mc_id_db_original,
                    "upi_mc_id_2": upi_mc_id_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "device_serial": device_serial_db_orginial,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_refunded),
                                              'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': refund_auth_code
                                              }

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_original)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn_original is None else rrn_original,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": (str(refund_amt).split('.')[0]) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if refund_auth_code is None else refund_auth_code,
                    "rrn_2": "-" if rrn_refunded is None else rrn_refunded,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
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
def test_common_100_103_162():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_Refund_Failed_HDFC_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay upi refund failed via HDFC
    TC naming code description:100: Payment Method,103: RemotePay,162: TC162
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password
                                                                              }
                                                  )

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize(browser_type="firefox")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 333
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is: {order_id}")

            # acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")

            logger.debug(f"device_serial is: {device_serial}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            # ui_driver = TestSuiteSetup.initialize_firefox_driver()
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from db query : {mid} ")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from db query : {tid} ")
            txn_ext_ref = result['external_ref'].values[0]
            logger.debug(f"Fetching txn_ext_ref from db query : {txn_ext_ref} ")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": amount,
                "originalTransactionId": str(txn_id_original)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                txn_id_original) + "';"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result  for refunded txn details from txn table is : {result}")
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from db query : {txn_id_refunded} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_refunded from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_refunded from db query : {rrn_refunded} ")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from db query : {created_time} ")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code_2 from db query : {auth_code_2} ")
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
                original_date_and_time = date_time_converter.to_app_format(created_time_original)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:FAILED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "txn_id": txn_id_original,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT FAILED",
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "date_2": date_and_time,
                    "date": original_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_rrn_refunded = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
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
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time,
                    "date": app_original_date_and_time
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                refunded_date_time = date_time_converter.db_datetime(created_time)
                original_date_time = date_time_converter.db_datetime(created_time_original)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "FAILED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "FAILED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_original,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_refunded,
                    "org_code_2": org_code_txn,
                    "auth_code": auth_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_original
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original is : {payment_mode_api_original}")
                rrn_api_original = response["rrNumber"]
                logger.debug(f"rrn_api_original is : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original is : {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original is : {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original is : {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original is : {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original is : {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid_api_original is : {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid_api_original is : {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original is : {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original is : {auth_code_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"date_api_original is : {date_api_original}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_refunded
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn_api_refunded : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded : {org_code_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded : {txn_type_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date_api_refunded : {date_api_refunded}")

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
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

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
                    "pmt_status_2": "FAILED",
                    "pmt_state_2": "FAILED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "FAILED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "FAILED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "device_serial": device_serial
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in DB Validation is : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"status_db_refunded is : {status_db_refunded}")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_refunded is : {payment_mode_db_refunded}")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_refunded is : {amount_db_refunded}")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"state_db_refunded is : {state_db_refunded}")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_refunded is : {acquirer_code_db_refunded}")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_refunded is : {settlement_status_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB Validation is : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"upi_status_db_refunded is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_refunded is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_refunded is : {upi_bank_code_db_refunded}")

                query = "select * from txn where id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn original details from txn table in DB Validation is : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"status_db_original is : {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_original is : {payment_mode_db_original}")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_original is : {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"state_db_original is : {state_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_original is : {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_original is : {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_original is : {settlement_status_db_original}")

                query = "select * from upi_txn where txn_id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB Validation is : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"upi_status_db_original is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_original is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_original is : {upi_bank_code_db_original}")

                query = "select * from upi_merchant_config where org_code ='" + str(
                    org_code) + "' and bank_code = 'HDFC';"
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_merchant_config table in DB Validation is : {result}")
                mid_db_original = result['mid'].iloc[0]
                logger.debug(f"mid_db_original is : {mid_db_original}")
                tid_db_original = result['tid'].iloc[0]
                logger.debug(f"tid_db_original is : {tid_db_original}")

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of terminal_info table in DB Validation is : {result}")
                device_serial_db_orginial = result['device_serial'].iloc[0]
                logger.debug(f"device_serial_db_orginial is : {device_serial_db_orginial}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "device_serial": device_serial_db_orginial,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_original)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn_original,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "FAILED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": (str(amount_db_refunded).split('.')[0]) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": "-" if rrn_refunded is None else rrn_refunded,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, txn_ext_ref)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
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
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_103_163():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_partial_Refund_HDFC_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay upi partial refund via HDFC
    TC naming code description:100: Payment Method,103: RemotePay,163: TC163
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize(browser_type="firefox")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(200, 300)
            logger.info(f"amount is: {amount}")
            refunded_amount = 100
            logger.info(f"refunded_amount is: {refunded_amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is: {order_id}")

            # acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")
            logger.info(f"device_serial is: {device_serial}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            # ui_driver = TestSuiteSetup.initialize_firefox_driver()
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn from the DB : {result}")
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from db query : {mid} ")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from db query : {tid} ")
            txn_ext_ref = result['external_ref'].values[0]
            logger.debug(f"Fetching txn_ext_ref from db query : {txn_ext_ref} ")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": refunded_amount,
                "originalTransactionId": str(txn_id_original)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of refunded details for txn from the DB : {result}")
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching refund_auth_code from db query : {refund_auth_code} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_refunded from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_refunded from db query : {rrn_refunded} ")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code_2 from db : {auth_code_2}")
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
                original_date_and_time = date_time_converter.to_app_format(created_time_original)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id_original,
                    "txn_amt": "{:.2f}".format(amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "auth_code": auth_code,
                    "auth_code_2": refund_auth_code,
                    "date_2": date_and_time,
                    "date": original_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_refunded}, {app_auth_code_refunded}")
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
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_auth_code_original = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_original}, {app_auth_code_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "auth_code_2": app_auth_code_refunded,
                    "date_2": app_date_and_time,
                    "date": app_original_date_and_time
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                refunded_date_time = date_time_converter.db_datetime(created_time)
                original_date_time = date_time_converter.db_datetime(created_time_original)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_original,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_refunded,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "auth_code_2": refund_auth_code,
                    "auth_code": auth_code,
                    "date_2": refunded_date_time,
                    "date": original_date_time
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_original
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original : {payment_mode_api_original}")
                rrn_api_original = response["rrNumber"]
                logger.debug(f"rrn_api_original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original : {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original : {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original : {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original : {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original : {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid_api_original : {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid_api_original : {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original : {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original : {auth_code_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"date_api_original : {date_api_original}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_refunded
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn_api_refunded : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid_api_refunded : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid_api_refunded : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded : {txn_type_api_refunded}")
                auth_code_api_refunded = response["authCode"]
                logger.debug(f"auth_code_api_refunded : {auth_code_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"date_api_refunded : {date_api_refunded}")

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
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code_2": auth_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original)
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")

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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refunded_amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "device_serial": device_serial
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of refunded details from txn table in DB Validation is: {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"status_db_refunded is: {status_db_refunded}")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_refunded is: {payment_mode_db_refunded}")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_refunded is: {amount_db_refunded}")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"state_db_refunded is: {state_db_refunded}")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_refunded is: {acquirer_code_db_refunded}")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_refunded is: {settlement_status_db_refunded}")
                tid_db_refunded = result['tid'].values[0]
                logger.debug(f"tid_db_refunded is: {tid_db_refunded}")
                mid_db_refunded = result['mid'].values[0]
                logger.debug(f"mid_db_refunded is: {mid_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB Validation is: {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"upi_status_db_refunded is : {upi_status_db_refunded}")
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_refunded is : {upi_txn_type_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_refunded is : {upi_bank_code_db_refunded}")

                query = "select * from txn where id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of orginal details from txn table in DB Validation is: {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"status_db_original is : {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_original is : {payment_mode_db_original}")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_original is : {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"state_db_original is : {state_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_original is : {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_original is : {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_original is : {settlement_status_db_original}")

                query = "select * from upi_txn where txn_id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in DB Validation is: {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"upi_status_db_original is : {upi_status_db_original}")
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db_original is : {upi_txn_type_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_original is : {upi_bank_code_db_original}")

                query = "select * from upi_merchant_config where org_code ='" + str(
                    org_code) + "' and bank_code = 'HDFC';"
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_merchant_config table in DB Validation is: {result}")
                mid_db = result['mid'].iloc[0]
                logger.debug(f"mid_db is : {mid_db}")
                tid_db = result['tid'].iloc[0]
                logger.debug(f"tid_db is : {tid_db}")

                query = "select * from terminal_info where tid ='" + str(tid_db) + "';"
                logger.debug(f"Query to fetch data from terminal_info : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db = result['device_serial'].iloc[0]
                logger.debug(f"device_serial_db is : {device_serial_db}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "upi_txn_type": upi_txn_type_db_original,
                    "upi_txn_type_2": upi_txn_type_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "device_serial": device_serial_db,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_refunded),
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': refund_auth_code
                                              }

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_original)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn_original,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": (str(amount_db_refunded).split('.')[0]) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": "-" if rrn_refunded is None else rrn_refunded,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, txn_ext_ref)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
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
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_103_164():
    """
    Sub Feature Code: UI_Common_PM_RP_Upi_two_times_second_partial_refund_amount_greater_than_original_amount_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a two remote pay partial refund when second partial refund amount is greater than original amount
    TC naming code description:100: Payment Method,103: RemotePay,164: TC164
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize(browser_type="firefox")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 300
            logger.info(f"amount is: {amount}")
            refunded_amount = 150
            logger.info(f"refunded_amount is: {refunded_amount}")
            greater_refund_amount = 151
            logger.info(f"greater_refund_amount is: {greater_refund_amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is: {order_id}")

            # acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            # ui_driver = TestSuiteSetup.initialize_firefox_driver()
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            ui_browser.goto(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = RemotePayTxnPage(ui_browser)
            logger.info("Clicking on UPI to start the txn.")
            rp_upi_txn.clickOnRemotePayUPI()
            logger.info("Launching UPI")
            rp_upi_txn.clickOnRemotePayLaunchUPI()
            rp_upi_txn.clickOnRemotePayCancelUPI()
            rp_upi_txn.clickOnRemotePayProceed()
            logger.info("UPI txn is completed.")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "'"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table is : {result}")
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")
            device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from db query : {mid} ")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from db query : {tid} ")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": refunded_amount,
                "originalTransactionId": str(txn_id_original)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username,
                "password": app_password,
                "amount": greater_refund_amount,
                "originalTransactionId": str(txn_id_original)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(
                f"Response received from refund api when refund amount is greater than original amount : {response}")
            api_error_message = response["errorMessage"]
            logger.debug(f"api_error_message is  : {api_error_message}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(
                txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of refunded details for txn table is : {result}")
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id_refunded from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching refund_auth_code from db query : {refund_auth_code} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_refunded from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_refunded from db query : {rrn_refunded} ")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from db query : {created_time} ")
            created_time_second_txn = result['created_time'].values[0]
            logger.debug(f"Fetching posting_date from db query : {created_time} ")

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
                original_date_and_time = date_time_converter.to_app_format(created_time_original)

                expected_app_values = {
                    "pmt_status": "STATUS:AUTHORIZED",
                    "pmt_status_2": "STATUS:REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_id": txn_id_original,
                    "txn_id_2": txn_id_refunded,
                    "txn_amt": "{:.2f}".format(amount),
                    "txn_amt_2": "{:.2f}".format(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "auth_code": auth_code,
                    "auth_code_2": refund_auth_code,
                    "date_2": date_and_time,
                    "date": original_date_and_time
                }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_auth_code_refunded = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_refunded}, {app_auth_code_refunded}")
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
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")
                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_auth_code_original = txn_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {txn_id_original}, {app_auth_code_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original,
                    "pmt_status_2": app_payment_status_refunded,
                    "pmt_mode": app_payment_mode_original,
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status": app_settlement_status_original,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id": app_txn_id_original,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt": str(app_payment_amt_original),
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "pmt_msg": payment_msg_original,
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn": str(app_rrn_original),
                    "rrn_2": str(app_rrn_refunded),
                    "auth_code": app_auth_code_original,
                    "auth_code_2": app_auth_code_refunded,
                    "date_2": app_date_and_time,
                    "date": app_original_date_and_time
                }

                logger.debug(f"actual_app_values : {actual_app_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                original_date_time = date_time_converter.db_datetime(created_time_original)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "txn_amt": str(amount),
                    "txn_amt_2": str(refunded_amount),
                    "customer_name": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name": payer_name,
                    "payer_name_2": payer_name,
                    "order_id": order_id,
                    "rrn": str(rrn_original),
                    "rrn_2": str(rrn_refunded),
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type_original,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "acquirer_code_2": "HDFC",
                    "txn_type_2": txn_type_refunded,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn,
                    "auth_code_2": refund_auth_code,
                    "auth_code": auth_code,
                    "date": original_date_time,
                    "err_msg": f"Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: 150.00"
                }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_original
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status_api_original : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"amount_api_original : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"payment_mode_api_original : {payment_mode_api_original}")
                rrn_api_original = response["rrNumber"]
                logger.debug(f"rrn_api_original : {rrn_api_original}")
                state_api_original = response["states"][0]
                logger.debug(f"state_api_original : {state_api_original}")
                settlement_status_api_original = response["settlementStatus"]
                logger.debug(f"settlement_status_api_original : {settlement_status_api_original}")
                issuer_code_api_original = response["issuerCode"]
                logger.debug(f"issuer_code_api_original : {issuer_code_api_original}")
                acquirer_code_api_original = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_original : {acquirer_code_api_original}")
                org_code_api_original = response["orgCode"]
                logger.debug(f"org_code_api_original : {org_code_api_original}")
                mid_api_original = response["mid"]
                logger.debug(f"mid_api_original : {mid_api_original}")
                tid_api_original = response["tid"]
                logger.debug(f"tid_api_original : {tid_api_original}")
                txn_type_api_original = response["txnType"]
                logger.debug(f"txn_type_api_original : {txn_type_api_original}")
                auth_code_api_original = response["authCode"]
                logger.debug(f"auth_code_api_original : {auth_code_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"date_api_original : {date_api_original}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id_refunded
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"status_api_refunded : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"amount_api_refunded : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"payment_mode_api_refunded : {payment_mode_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"rrn_api_refunded : {rrn_api_refunded}")
                state_api_refunded = response["states"][0]
                logger.debug(f"state_api_refunded : {state_api_refunded}")
                settlement_status_api_refunded = response["settlementStatus"]
                logger.debug(f"settlement_status_api_refunded : {settlement_status_api_refunded}")
                acquirer_code_api_refunded = response["acquirerCode"]
                logger.debug(f"acquirer_code_api_refunded : {acquirer_code_api_refunded}")
                org_code_api_refunded = response["orgCode"]
                logger.debug(f"org_code_api_refunded : {org_code_api_refunded}")
                mid_api_refunded = response["mid"]
                logger.debug(f"mid_api_refunded : {mid_api_refunded}")
                tid_api_refunded = response["tid"]
                logger.debug(f"tid_api_refunded : {tid_api_refunded}")
                txn_type_api_refunded = response["txnType"]
                logger.debug(f"txn_type_api_refunded : {txn_type_api_refunded}")
                auth_code_api_refunded = response["authCode"]
                logger.debug(f"auth_code_api_refunded : {auth_code_api_refunded}")

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
                    "order_id": order_id,
                    "rrn": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code": acquirer_code_api_original,
                    "issuer_code": issuer_code_api_original,
                    "txn_type": txn_type_api_original,
                    "mid": mid_api_original,
                    "tid": tid_api_original,
                    "org_code": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "mid_2": mid_api_refunded,
                    "tid_2": tid_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code_2": auth_code_api_refunded,
                    "auth_code": auth_code_api_original,
                    "date": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "err_msg": api_error_message
                }

                logger.debug(f"expected_api_values : {actual_api_values} for the testcase_id {testcase_id}")
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
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "pmt_mode_2": "UPI",
                    "txn_amt": amount,
                    "txn_amt_2": refunded_amount,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_status_2": "REFUNDED",
                    "settle_status": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "bank_code": "HDFC",
                    "bank_code_2": "HDFC",
                    "upi_bank_code": "HDFC",
                    "upi_bank_code_2": "HDFC",
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "device_serial": device_serial
                }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from txn table : {result}")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"status_db_refunded : {status_db_refunded}")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_refunded : {payment_mode_db_refunded}")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_refunded : {amount_db_refunded}")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"state_db_refunded : {state_db_refunded}")
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_refunded : {acquirer_code_db_refunded}")
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_refunded : {settlement_status_db_refunded}")
                tid_db_refunded = result['tid'].values[0]
                logger.debug(f"tid_db_refunded : {tid_db_refunded}")
                mid_db_refunded = result['mid'].values[0]
                logger.debug(f"mid_db_refunded : {mid_db_refunded}")

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from upi_txn table : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                logger.debug(f"upi_status_db_refunded is : {upi_status_db_refunded}")
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_refunded is : {upi_bank_code_db_refunded}")
                bank_code_db_refunded = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_refunded is : {bank_code_db_refunded}")

                query = "select * from txn where id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from txn table : {result}")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"status_db_original is : {status_db_original}")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db_original is : {payment_mode_db_original}")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"amount_db_original is : {amount_db_original}")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"state_db_original is : {state_db_original}")
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db_original is : {acquirer_code_db_original}")
                bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db_original is : {bank_code_db_original}")
                settlement_status_db_original = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db_original is : {settlement_status_db_original}")

                query = "select * from upi_txn where txn_id='" + txn_id_original + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from upi_txn table : {result}")
                upi_status_db_original = result["status"].iloc[0]
                logger.debug(f"upi_status_db_original is : {upi_status_db_original}")
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db_original is : {upi_bank_code_db_original}")

                query = "select * from upi_merchant_config where org_code ='" + str(
                    org_code) + "' and bank_code = 'HDFC';"
                logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from upi_merchant_config : {result}")
                mid_db_original = result['mid'].iloc[0]
                logger.debug(f"mid_db_original is : {mid_db_original}")
                tid_db_original = result['tid'].iloc[0]
                logger.debug(f"tid_db_original is : {tid_db_original}")

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result data from terminal_info : {result}")
                device_serial_db_orginial = result['device_serial'].iloc[0]
                logger.debug(f"device_serial_db_orginial is : {device_serial_db_orginial}")

                actual_db_values = {
                    "pmt_status": status_db_original,
                    "pmt_status_2": status_db_refunded,
                    "pmt_state": state_db_original,
                    "pmt_state_2": state_db_refunded,
                    "pmt_mode": payment_mode_db_original,
                    "pmt_mode_2": payment_mode_db_refunded,
                    "txn_amt": amount_db_original,
                    "txn_amt_2": amount_db_refunded,
                    "upi_txn_status": upi_status_db_original,
                    "upi_txn_status_2": upi_status_db_refunded,
                    "settle_status": settlement_status_db_original,
                    "settle_status_2": settlement_status_db_refunded,
                    "acquirer_code": acquirer_code_db_original,
                    "acquirer_code_2": acquirer_code_db_refunded,
                    "bank_code": bank_code_db_original,
                    "bank_code_2": bank_code_db_refunded,
                    "upi_bank_code": upi_bank_code_db_original,
                    "upi_bank_code_2": upi_bank_code_db_refunded,
                    "mid": mid_db_original,
                    "tid": tid_db_original,
                    "mid_2": mid_db_refunded,
                    "tid_2": tid_db_refunded,
                    "device_serial": device_serial_db_orginial,
                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")

            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_refunded),
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': refund_auth_code
                                              }

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time_original)
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time_second_txn)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": txn_id_original,
                    "auth_code": auth_code,
                    "rrn": rrn_original,
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": str(refunded_amount) + ".00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_refunded,
                    "auth_code_2": refund_auth_code,
                    "rrn_2": rrn_refunded,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
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
