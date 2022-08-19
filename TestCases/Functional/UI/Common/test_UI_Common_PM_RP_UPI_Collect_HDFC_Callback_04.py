import random
import shutil
import sys
import time
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_029():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_before_qr_expiry_HDFC_AutoRefund_Disabled
    Sub Feature Description: Performing two pure upi failed callback via HDFC before expiry the qr when autorefund is disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    029: TC029
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                paymentLinkUrl = response['paymentLink']
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remote_pay_upi_collect_txn = remotePayTxnPage(ui_driver)
                remote_pay_upi_collect_txn.clickOnRemotePayUPI()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectAppSelection()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectId("abc")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectDropDown("okicici")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectProceed()

            logger.info("starting first callback")
            logger.info("fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch txn_ref from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")

            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_bank_code = result['bank_code'].values[0]
            logger.debug(f"bank code from txn is : {original_bank_code}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Settlement status from txn is : {original_acquirer_code}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")

            logger.info("completed second callback")
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
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {"pmt_mode_original": "UPI",
                                       "pmt_status_original": "FAILED",
                                       "txn_amount_original": str(amount),
                                       "settle_status_original": "FAILED",
                                       "txn_id_original": original_txn_id,
                                       "rrn_original": str(original_rrn),
                                       "customer_name_original": original_customer_name,
                                       "payer_name_original": original_payer_name,
                                       "order_id_original": order_id,
                                       "payment_msg_original": "PAYMENT FAILED",
                                       "date_original": date_and_time,
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {"pmt_mode_original": app_payment_mode,
                                    "pmt_status_original": app_payment_status,
                                    "txn_amount_original": app_amount.split(' ')[1],
                                    "settle_status_original": app_settlement_status,
                                    "txn_id_original": app_txn_id,
                                    "rrn_original": str(app_rrn),
                                    "customer_name_original": app_customer_name,
                                    "payer_name_original": app_payer_name,
                                    "order_id_original": app_order_id,
                                    "payment_msg_original": app_payment_msg,
                                    "date_original": app_date_and_time,
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settlement_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date_original": date,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                actual_api_values = {"pmt_status": status_api,
                                       "txn_amt": amount_api,
                                       "pmt_mode": payment_mode_api,
                                       "pmt_state": state_api,
                                       "settlement_status": status_api,
                                       "acquirer_code": acquirer_code_api,
                                       "issuer_code": issuer_code_api,
                                       "txn_type": txn_type_api,
                                       "mid": mid_api,
                                       "tid": tid_api,
                                       "org_code": orgCode_api,
                                     "date_original":  date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settlement_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type_db": "COLLECT",
                    "upi_bank_code_db": "HDFC",
                    "upi_mc_id_db": upi_mc_id,
                    "intent_status": "ACTIVE"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")
                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode":original_payment_mode,
                    "txn_amt": amount,
                    "settlement_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "intent_status":intent_status
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_030():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_failed_callback_before_qr_expiry_HDFC_AutoRefund_Disabled
    Sub Feature Description: Performing two pure upi failed callback via HDFC before expiry the qr when autorefund is disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    030: TC030
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                paymentLinkUrl = response['paymentLink']
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remote_pay_upi_collect_txn = remotePayTxnPage(ui_driver)
                remote_pay_upi_collect_txn.clickOnRemotePayUPI()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectAppSelection()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectId("abc")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectDropDown("okicici")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectProceed()

            logger.info("starting first callback")
            logger.info("fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch txn_ref from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")

            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_bank_code = result['bank_code'].values[0]
            logger.debug(f"bank code from txn is : {original_bank_code}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Settlement status from txn is : {original_acquirer_code}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")

            logger.info("completed second callback")
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
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {"pmt_mode_original": "UPI",
                                       "pmt_status_original": "FAILED",
                                       "txn_amount_original": str(amount),
                                       "settle_status_original": "FAILED",
                                       "txn_id_original": original_txn_id,
                                       "rrn_original": str(original_rrn),
                                       "customer_name_original": original_customer_name,
                                       "payer_name_original": original_payer_name,
                                       "order_id_original": order_id,
                                       "payment_msg_original": "PAYMENT FAILED",
                                       "date_original": date_and_time,
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {"pmt_mode_original": app_payment_mode,
                                    "pmt_status_original": app_payment_status,
                                    "txn_amount_original": app_amount.split(' ')[1],
                                    "settle_status_original": app_settlement_status,
                                    "txn_id_original": app_txn_id,
                                    "rrn_original": str(app_rrn),
                                    "customer_name_original": app_customer_name,
                                    "payer_name_original": app_payer_name,
                                    "order_id_original": app_order_id,
                                    "payment_msg_original": app_payment_msg,
                                    "date_original": app_date_and_time,
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settlement_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date_original": date,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                actual_api_values = {"pmt_status": status_api,
                                       "txn_amt": amount_api,
                                       "pmt_mode": payment_mode_api,
                                       "pmt_state": state_api,
                                       "settlement_status": status_api,
                                       "acquirer_code": acquirer_code_api,
                                       "issuer_code": issuer_code_api,
                                       "txn_type": txn_type_api,
                                       "mid": mid_api,
                                       "tid": tid_api,
                                       "org_code": orgCode_api,
                                     "date_original":  date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settlement_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type_db": "COLLECT",
                    "upi_bank_code_db": "HDFC",
                    "upi_mc_id_db": upi_mc_id,
                    "intent_status": "ACTIVE"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")
                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode":original_payment_mode,
                    "txn_amt": amount,
                    "settlement_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "intent_status":intent_status
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_031():
    """
    Sub Feature Code: UI_Common_PM_2_UPI_Collectfailed_callback_after__expiry_HDFC_AutoRefund_Enabled
    Sub Feature Description: Performing two  UPI Collect failed callback via HDFC after expiry the  when autorefund is enabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    031: TC031
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

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

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                paymentLinkUrl = response['paymentLink']
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remote_pay_upi_collect_txn = remotePayTxnPage(ui_driver)
                remote_pay_upi_collect_txn.clickOnRemotePayUPI()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectAppSelection()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectId("abc")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectDropDown("okicici")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectProceed()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch max Attempts from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"max upi attempt for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"Wating for timeout attempt: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Wating for timeout attempt time: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Wating for timeout for Ezetap org time: {org_setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            logger.info("starting first callback")
            logger.info("fetching pg merchant id and vps from the upi_merchant_config table to perform the 1st upi callback")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

            logger.info(
                "fetching txn_id from the txn table to perform the 1st upi callback")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch txn_ref from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 1st upi callback is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id to perform the 1st upi callback is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_1_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            logger.debug("executing the curl_data on the server to encrypt the data")
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes, "
                f"payload is the combination of the pg_merchant_id and the encrypted data")

            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after sending the request is : {response}")
            logger.info("completed first callback")

            logger.info("starting second callback")
            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number to perform the 2nd upi callback is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id to perform the 2nd upi callback is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': callback_2_rrn
                                                                 })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")
            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_bank_code = result['bank_code'].values[0]
            logger.debug(f"bank code from txn is : {original_bank_code}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Settlement status from txn is : {original_acquirer_code}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")

            logger.info("completed second callback")
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
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {"pmt_mode_original": "UPI",
                                       "pmt_status_original": "FAILED",
                                       "txn_amount_original": str(amount),
                                       "settle_status_original": "FAILED",
                                       "txn_id_original": original_txn_id,
                                       "rrn_original": str(original_rrn),
                                       "customer_name_original": original_customer_name,
                                       "payer_name_original": original_payer_name,
                                       "order_id_original": order_id,
                                       "payment_msg_original": "PAYMENT FAILED",
                                       "date_original": date_and_time,
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = transactions_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {"pmt_mode_original": app_payment_mode,
                                    "pmt_status_original": app_payment_status,
                                    "txn_amount_original": app_amount.split(' ')[1],
                                    "settle_status_original": app_settlement_status,
                                    "txn_id_original": app_txn_id,
                                    "rrn_original": str(app_rrn),
                                    "customer_name_original": app_customer_name,
                                    "payer_name_original": app_payer_name,
                                    "order_id_original": app_order_id,
                                    "payment_msg_original": app_payment_msg,
                                    "date_original": app_date_and_time,
                                     }

                logger.debug(f"actual_app_values: {actual_app_values}")
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settlement_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date_original": date,
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                actual_api_values = {"pmt_status": status_api,
                                       "txn_amt": amount_api,
                                       "pmt_mode": payment_mode_api,
                                       "pmt_state": state_api,
                                       "settlement_status": status_api,
                                       "acquirer_code": acquirer_code_api,
                                       "issuer_code": issuer_code_api,
                                       "txn_type": txn_type_api,
                                       "mid": mid_api,
                                       "tid": tid_api,
                                       "org_code": orgCode_api,
                                     "date_original":  date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settlement_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type_db": "COLLECT",
                    "upi_bank_code_db": "HDFC",
                    "upi_mc_id_db": upi_mc_id,
                    "intent_status": "EXPIRED"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")
                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode":original_payment_mode,
                    "txn_amt": amount,
                    "settlement_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "intent_status":intent_status
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
                expected_portal_values = {}

                actual_portal_values = {}

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)