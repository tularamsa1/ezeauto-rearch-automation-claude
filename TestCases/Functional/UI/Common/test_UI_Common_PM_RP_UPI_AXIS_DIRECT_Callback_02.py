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
def test_common_100_103_086():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Success_Callback_After_Expiry_AutoRefundEnabled_AXIS_DIRECT
    Sub Feature Description: Verification of a one upi  success callback after expiry via Axis Direct when auto refund is enalbed.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    086: TC_086
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='AXIS_DIRECT',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update remotepay_setting set setting_value=1 where setting_name='cnpTxnTimeoutDuration' and  " \
                "org_code='" + org_code + "'; "
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating remotepay_setting table: {result}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',  # Chane api name
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)  # Check
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                portal_driver = TestSuiteSetup.initialize_firefox_driver()
                paymentLinkUrl = response['paymentLink']
                portal_driver.get(paymentLinkUrl)
                logger.info("Opening the link in the browser")
                rp_upi_txn = remotePayTxnPage(portal_driver)
                logger.info("Clicking on UPI to start the txn.")
                rp_upi_txn.clickOnRemotePayUPI()
                logger.info("Launching UPI")
                rp_upi_txn.clickOnRemotePayLaunchUPI()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch txn timeout from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"txn timeout for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch timeout for Ezetap org is : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"txn timeout attempt is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            config_mid = result['mid'].values[0]
            config_tid = result['tid'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and mc_id: {upi_mc_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"  # Needs to modify these queries
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")

            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_created_time}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated random original_settlement_status is : {original_settlement_status}")
            original_mid = result['mid'].values[0]
            logger.debug(f"generated random original_mid is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"generated random original_tid is : {original_tid}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated random original_acquirer_code is : {original_acquirer_code}")
            original_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated random original_issuer_code is : {original_issuer_code}")
            original_org_code = result['org_code'].values[0]
            logger.debug(f"generated random original_org_code is : {original_org_code}")
            original_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated random original_txn_type is : {original_txn_type}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_ref_id = '211115084892E01' + str(original_rrn)


            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': original_rrn,
                                                                 'gatewayTransactionId': original_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the request.")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where orig_txn_id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated new customer_name is : {new_txn_customer_name}")
            new_txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated new payer_name is : {new_txn_payer_name}")
            new_txn_status = result['status'].values[0]
            logger.debug(f"generated new new txn status is : {new_txn_status}")
            new_txn_date_time = result['created_time'].values[0]
            logger.debug(f"generated new_posting_date is : {new_txn_date_time}")
            new_txn_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated new_settlement_status is : {new_txn_settlement_status}")
            new_txn_mid = result['mid'].values[0]
            logger.debug(f"generated new_mid is : {new_txn_mid}")
            new_txn_tid = result['tid'].values[0]
            logger.debug(f"generated new_tid is : {new_txn_tid}")
            new_original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"generated new_original_mid is : {new_original_txn_id}")
            new_txn_id = result['id'].values[0]
            logger.debug(f"generated new txn id is : {new_txn_id}")
            new_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated original_acquirer_code is : {new_txn_acquirer_code}")
            new_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated  original_issuer_code is : {new_txn_issuer_code}")
            new_txn_org_code = result['org_code'].values[0]
            logger.debug(f"generated  original_org_code is : {new_txn_org_code}")
            new_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated  original_txn_type is : {new_txn_type}")
            new_rrNumber = result['rr_number'].values[0]
            logger.debug(f"generated  rrNumber is : {new_rrNumber}")

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
                date_and_time = date_time_converter.to_app_format(original_created_time)
                new_date_and_time = date_time_converter.to_app_format(new_txn_date_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    # "customer_name": original_customer_name,
                    # "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    # "rrn": str(rrn),
                    "date": date_and_time,
                    # "auth_code": auth_code,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "rrn_2": str(new_rrNumber),
                    "customer_name_2": new_txn_customer_name,
                    "payer_name_2": new_txn_payer_name,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": new_date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)  # logger
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                # app_rrn = txnHistoryPage.fetch_RRN_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                # app_auth_code = txnHistoryPage.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)
                new_app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status}")
                new_app_payment_status = new_app_payment_status.split(':')[1]
                new_app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode}")
                new_app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id}")
                new_app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount}")
                new_app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {new_txn_id}, {new_app_rrn}")
                new_app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id}, {new_app_date_and_time}")
                new_app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status}")
                new_app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name}")
                new_app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name}")
                new_app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id}")
                new_app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg}")


                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    # "customer_name": app_customer_name,
                    # "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    # "rrn": str(app_rrn),
                    "date": app_date_and_time,
                    # "auth_code": app_auth_code,

                    "pmt_mode_2": new_app_payment_mode,
                    "pmt_status_2": new_app_payment_status,
                    "txn_amt_2": new_app_amount.split(' ')[1],
                    "settle_status_2": new_app_settlement_status,
                    "txn_id_2": new_app_txn_id,
                    "customer_name_2": new_app_customer_name,
                    "payer_name_2": new_app_payer_name,
                    "order_id_2": new_app_order_id,
                    "pmt_msg_2": new_app_payment_msg,
                    "rrn_2": str(new_app_rrn),
                    "date_2": new_app_date_and_time,
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
                date_time = date_time_converter.db_datetime(original_created_time)
                new_date = date_time_converter.db_datetime(new_txn_date_time) # Replace date with dateand time
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    # "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "REMOTE_PAY",
                    "mid": original_mid,
                    "tid": original_tid,
                    "org_code": original_org_code,
                    "date": date_time,
                    # "auth_code": auth_code,

                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "REFUND_PENDING",
                    # "new_rrn": new_rrNumber,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS",
                    "txn_type_2": new_txn_type,
                    "mid_2": new_txn_mid,
                    "tid_2": new_txn_tid,
                    "org_code_2": new_txn_org_code,
                    "date_2": new_date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                logger.debug("Respone from Api details is", api_details)  # Change API details, add loggers
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                # rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]
                # auth_code_api = response["authCode"] #No authcode in response

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                logger.debug(f"Response received for transaction details api is : {response}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"API Details response is : {response}")
                new_status_api = response["status"]
                new_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_state_api = response["states"][0]
                # new_rrn_api = response["rrNumber"]
                new_settlement_status_api = response["settlementStatus"]
                new_issuer_code_api = response["issuerCode"]
                new_acquirer_code_api = response["acquirerCode"]
                new_orgCode_api = response["orgCode"]
                new_mid_api = response["mid"]
                new_tid_api = response["tid"]
                new_txn_type_api = response["txnType"]
                new_date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     # "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     # "auth_code": auth_code_api

                                     "pmt_status_2": new_status_api,
                                     "txn_amt_2": new_amount_api,
                                     "pmt_mode_2": new_payment_mode_api,
                                     "pmt_state_2": new_state_api,
                                     # "new_rrn": new_rrn_api,
                                     "settle_status_2": new_settlement_status_api,
                                     "acquirer_code_2": new_acquirer_code_api,
                                     "issuer_code_2": new_issuer_code_api,
                                     "txn_type_2": new_txn_type_api,
                                     "mid_2": new_mid_api,
                                     "tid_2": new_tid_api,
                                     "org_code_2": new_orgCode_api,
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_date_api)

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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_Status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "EXPIRED",
                    "mid": config_mid,
                    "tid": config_tid,

                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_txn_type_2": "REMOTE_PAY_UPI_INTENT",
                    "mid_2": new_txn_mid,
                    "tid_2": new_txn_tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_upi_status_db = result["status"].iloc[0]
                new_upi_txn_type_db = result["txn_type"].iloc[0]
                new_bank_code_db = result["bank_code"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_status_db = result["status"].iloc[0]
                new_payment_mode_db = result["payment_mode"].iloc[0]
                new_amount_db = int(result["amount"].iloc[0])
                new_state_db = result["state"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_Status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid_db,
                    "tid": tid_db,

                    "pmt_status_2": new_status_db,
                    "pmt_state_2": new_state_db,
                    "txn_amt_2": new_amount_db,
                    "upi_txn_status_2": new_upi_status_db,
                    "upi_txn_type_2": new_upi_txn_type_db,
                    "settle_status_2": new_txn_settlement_status,
                    "acquirer_code_2": new_txn_acquirer_code,
                    "upi_bank_code_2": new_bank_code_db,
                    "mid_2": config_mid,
                    "tid_2": config_tid
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
                    expected_portal_values = {}
                    #
                    # Write the test case Portal validation code block here. Set this to pass if not required.
                    #
                    actual_portal_values = {}
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                    actualPortal=actual_portal_values)
                except Exception as e:
                    Configuration.perform_portal_val_exception(testcase_id, e)
                logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            # -----------------------------------------End of Portal Validation---------------------------------------
            # -----------------------------------------End of ChargeSlip Validation----------------------------------

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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_087():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Two_Success_Callback_After_Expiry_AutoRefundEnabled_AXIS_DIRECT
    Sub Feature Description: Verification of a two upi success callback after expiry via Axis Direct when auto refund is enalbed.
    100: Payment Method
    103: RemotePay
    087: TC087
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='AXIS_DIRECT',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update remotepay_setting set setting_value=1 where setting_name='cnpTxnTimeoutDuration' and  " \
                "org_code='" + org_code + "'; "
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating remotepay_setting table: {result}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                portal_driver = TestSuiteSetup.initialize_firefox_driver()
                paymentLinkUrl = response['paymentLink']
                portal_driver.get(paymentLinkUrl)
                logger.info("Opening the link in the browser")
                rp_upi_txn = remotePayTxnPage(portal_driver)
                logger.info("Clicking on UPI to start the txn.")
                rp_upi_txn.clickOnRemotePayUPI()
                logger.info("Launching UPI")
                rp_upi_txn.clickOnRemotePayLaunchUPI()
                logger.info("UPI txn is completed.")

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
                logger.info(f"max upi attempt is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
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
            original_settlement_status = result['settlement_status'].values[0]

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            original_ref_id = '211115084892E01' + str(callback_1_rrn)

            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': callback_1_rrn,
                                                                 'gatewayTransactionId': original_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upi/confirm/axisdirect")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_1 : {new_txn_id_1}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")

            callback_2_rrn = random.randint(1111110, 9999999)
            ref_id_2 = '211115084892E01' + str(callback_2_rrn)

            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': callback_2_rrn,
                                                                 'gatewayTransactionId': ref_id_2})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upi/confirm/axisdirect")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_2 : {new_txn_id_2}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            orig_txn_type = result['txn_type'].values[0]
            orig_posting_date = result['posting_date'].values[0]

            query = "select * from txn where id = '" + new_txn_id_1 + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_posting_date_1 = result['created_time'].values[0]

            query = "select * from txn where id = '" + new_txn_id_2 + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            new_txn_posting_date_2 = result['created_time'].values[0]
            new_txn_posting_date_api = result['posting_date'].values[0]

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        # -----------------------------------------End of Test Execution--------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(orig_posting_date)
                new_txn_date_and_time_1 = date_time_converter.to_app_format(new_txn_posting_date_1)
                new_txn_date_and_time_2 = date_time_converter.to_app_format(new_txn_posting_date_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    # "rrn_original": str(original_rrn),
                    # "customer_name_original": original_customer_name,
                    # "payer_name_original": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id_1,
                    "rrn_2": str(callback_1_rrn),
                    "customer_name_2": new_txn_customer_name_1,
                    "payer_name_2": new_txn_payer_name_1,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": new_txn_date_and_time_1,

                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "REFUND_PENDING",
                    "txn_amt_3": str(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": new_txn_id_2,
                    "rrn_3": str(callback_2_rrn),
                    "customer_name_3": new_txn_customer_name_2,
                    "payer_name_3": new_txn_payer_name_2,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "date_3": new_txn_date_and_time_2,

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
                logger.info(f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                # app_rrn = transactions_history_page.fetch_RRN_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                # app_customer_name = transactions_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                # app_payer_name = transactions_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_1)
                app_payment_status_1 = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id_1}, {app_payment_status_1}")
                app_payment_status_1 = app_payment_status_1.split(':')[1]
                app_payment_mode_1 = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {new_txn_id_1}, {app_payment_mode_1}")
                app_txn_id_1 = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {app_txn_id_1}")
                app_amount_1 = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_1}, {app_amount_1}")
                app_rrn_1 = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {app_rrn_1}")
                app_date_and_time_1 = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_1}, {app_date_and_time_1}")
                app_settlement_status_1 = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_1}, {app_settlement_status_1}")
                app_customer_name_1 = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {new_txn_id_1}, {app_customer_name_1}")
                app_payer_name_1 = transactions_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {new_txn_id_1}, {app_payer_name_1}")
                app_order_id_1 = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id_1}, {app_order_id_1}")
                app_payment_msg_1 = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {new_txn_id_1}, {app_payment_msg_1}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id_2)
                app_payment_status_2 = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id_2}, {app_payment_status_2}")
                app_payment_status_2 = app_payment_status_2.split(':')[1]
                app_payment_mode_2 = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {new_txn_id_2}, {app_payment_mode_1}")
                app_txn_id_2 = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {app_txn_id_2}")
                app_amount_2 = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_2}, {app_amount_2}")
                app_rrn_2 = transactions_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {app_rrn_2}")
                app_date_and_time_2 = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_2}, {app_date_and_time_2}")
                app_settlement_status_2 = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_2}, {app_settlement_status_2}")
                app_customer_name_2 = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {new_txn_id_2}, {app_customer_name_2}")
                app_payer_name_2 = transactions_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {new_txn_id_2}, {app_payer_name_2}")
                app_order_id_2 = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id_2}, {app_order_id_2}")
                app_payment_msg_2 = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {new_txn_id_2}, {app_payment_msg_2}")

                actual_app_values = {"pmt_mode": app_payment_mode,
                                    "pmt_status": app_payment_status,
                                    "txn_amt": app_amount.split(' ')[1],
                                    "settle_status": app_settlement_status,
                                    "txn_id": app_txn_id,
                                    # "rrn_original": str(app_rrn),
                                    # "customer_name_original": app_customer_name,
                                    # "payer_name_original": app_payer_name,
                                    "order_id": app_order_id,
                                    "pmt_msg": app_payment_msg,
                                    "date": app_date_and_time,

                                    "pmt_mode_2": app_payment_mode_1,
                                    "pmt_status_2": app_payment_status_1,
                                    "txn_amt_2": app_amount_1.split(' ')[1],
                                    "settle_status_2": app_settlement_status_1,
                                    "txn_id_2": app_txn_id_1,
                                    "rrn_2": str(app_rrn_1),
                                    "customer_name_2": app_customer_name_1,
                                    "payer_name_2": app_payer_name_1,
                                    "order_id_2": app_order_id_1,
                                    "pmt_msg_2": app_payment_msg_1,
                                    "date_2": app_date_and_time_1,

                                    "pmt_mode_3": app_payment_mode_2,
                                    "pmt_status_3": app_payment_status_2,
                                    "txn_amt_3": app_amount_2.split(' ')[1],
                                    "settle_status_3": app_settlement_status_2,
                                    "txn_id_3": app_txn_id_2,
                                    "rrn_3": str(app_rrn_2),
                                    "customer_name_3": app_customer_name_2,
                                    "payer_name_3": app_payer_name_2,
                                    "order_id_3": app_order_id_2,
                                    "pmt_msg_3": app_payment_msg_2,
                                    "date_3": app_date_and_time_2,
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
                date = date_time_converter.db_datetime(orig_posting_date)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_posting_date_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_posting_date_api)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": orig_txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,

                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING",
                                       # "new_rrn_1": str(callback_1_rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "AXIS",
                                       "issuer_code_2": "AXIS",
                                       "txn_type_2": new_txn_type_1,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,

                                       "pmt_status_3": "REFUND_PENDING",
                                       "txn_amt_3": amount,
                                       "pmt_mode_3": "UPI",
                                       "pmt_state_3": "REFUND_PENDING",
                                       # "new_rrn_2": str(callback_2_rrn),
                                       "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "AXIS",
                                       "issuer_code_3": "AXIS",
                                       "txn_type_3": new_txn_type_2, "mid_3": mid,
                                       "tid_3": tid, "org_code_3": org_code,
                                       "date": date,
                                       "date_2": new_txn_date_1,
                                       "date_3": new_txn_date_2
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

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id_1})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                new_txn_status_api_1 = response["status"]
                new_txn_amount_api_1 = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api_1 = response["paymentMode"]
                new_txn_state_api_1 = response["states"][0]
                # new_txn_rrn_api_1 = response["rrNumber"]
                new_txn_settlement_status_api_1 = response["settlementStatus"]
                new_txn_issuer_code_api_1 = response["issuerCode"]
                new_txn_acquirer_code_api_1 = response["acquirerCode"]
                new_txn_orgCode_api_1 = response["orgCode"]
                new_txn_mid_api_1 = response["mid"]
                new_txn_tid_api_1 = response["tid"]
                new_txn_txn_type_api_1 = response["txnType"]
                new_txn_date_api_1 = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id_2})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                new_txn_status_api_2 = response["status"]
                new_txn_amount_api_2 = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api_2 = response["paymentMode"]
                new_txn_state_api_2 = response["states"][0]
                # new_txn_rrn_api_2 = response["rrNumber"]
                new_txn_settlement_status_api_2 = response["settlementStatus"]
                new_txn_issuer_code_api_2 = response["issuerCode"]
                new_txn_acquirer_code_api_2 = response["acquirerCode"]
                new_txn_orgCode_api_2 = response["orgCode"]
                new_txn_mid_api_2 = response["mid"]
                new_txn_tid_api_2 = response["tid"]
                new_txn_type_api_2 = response["txnType"]
                new_txn_date_api_2 = response["postingDate"]
                #
                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,

                                     "pmt_status_2": new_txn_status_api_1,
                                     "txn_amt_2": new_txn_amount_api_1,
                                     "pmt_mode_2": new_payment_mode_api_1,
                                     "pmt_state_2": new_txn_state_api_1,
                                     # "new_rrn_1": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api_1,
                                     "acquirer_code_2": new_txn_acquirer_code_api_1,
                                     "issuer_code_2": new_txn_issuer_code_api_1,
                                     "txn_type_2": new_txn_txn_type_api_1,
                                     "mid_2": new_txn_mid_api_1,
                                     "tid_2": new_txn_tid_api_1,
                                     "org_code_2": new_txn_orgCode_api_1,


                                     "pmt_status_3": new_txn_status_api_2,
                                     "txn_amt_3": new_txn_amount_api_2,
                                     "pmt_mode_3": new_payment_mode_api_2,
                                     "pmt_state_3": new_txn_state_api_2,
                                     # "new_rrn_2": str(new_txn_rrn_api_2),
                                     "settle_status_3": new_txn_settlement_status_api_2,
                                     "acquirer_code_3": new_txn_acquirer_code_api_2,
                                     "issuer_code_3": new_txn_issuer_code_api_2,
                                     "txn_type_3": new_txn_type_api_2,
                                     "mid_3": new_txn_mid_api_2,
                                     "tid_3": new_txn_tid_api_2,
                                     "org_code_3": new_txn_orgCode_api_2,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api_1),
                                     "date_3": date_time_converter.from_api_to_datetime_format(new_txn_date_api_2)

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
                expected_db_values = {"pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,

                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type_2": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,

                    "pmt_status_3": "REFUND_PENDING",
                    "pmt_state_3": "REFUND_PENDING",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": amount,
                    "upi_txn_status_3": "REFUND_PENDING",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "AXIS",
                    "bank_code_3": "AXIS",
                    "pmt_gateway_3": "AXIS",
                    "upi_txn_type_3": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code_3": "AXIS_DIRECT",
                    "upi_mc_id_3": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                    "mid_3": mid,
                    "tid_3": tid
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_1 = result["status"].iloc[0]
                new_txn_payment_mode_db_1 = result["payment_mode"].iloc[0]
                new_txn_amount_db_1 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_1 = result["state"].iloc[0]
                new_txn_payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_1 = result["settlement_status"].iloc[0]
                new_txn_tid_db_1 = result['tid'].values[0]
                new_txn_mid_db_1 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_1 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_1 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_1 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_1 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db_2 = result["status"].iloc[0]
                new_txn_payment_mode_db_2 = result["payment_mode"].iloc[0]
                new_txn_amount_db_2 = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db_2 = result["state"].iloc[0]
                new_txn_payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_settlement_status_db_2 = result["settlement_status"].iloc[0]
                new_txn_tid_db_2 = result['tid'].values[0]
                new_txn_mid_db_2 = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id_2 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db_2 = result["status"].iloc[0]
                new_txn_upi_txn_type_db_2 = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db_2 = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,

                    "pmt_status_2": new_txn_status_db_1,
                    "pmt_state_2": new_txn_state_db_1,
                    "pmt_mode_2": new_txn_payment_mode_db_1,
                    "txn_amt_2": new_txn_amount_db_1,
                    "upi_txn_status_2": new_txn_upi_status_db_1,
                    "settle_status_2": new_txn_settlement_status_db_1,
                    "acquirer_code_2": new_txn_acquirer_code_db_1,
                    "bank_code_2": new_txn_bank_code_db_1,
                    "pmt_gateway_2": new_txn_payment_gateway_db_1,
                    "upi_txn_type_2": new_txn_upi_txn_type_db_1,
                    "upi_bank_code_2": new_txn_upi_bank_code_db_1,
                    "upi_mc_id_2": new_txn_upi_mc_id_db_1,

                    "pmt_status_3": new_txn_status_db_2,
                    "pmt_state_3": new_txn_state_db_2,
                    "pmt_mode_3": new_txn_payment_mode_db_2,
                    "txn_amt_3": new_txn_amount_db_2,
                    "upi_txn_status_3": new_txn_upi_status_db_2,
                    "settle_status_3": new_txn_settlement_status_db_2,
                    "acquirer_code_3": new_txn_acquirer_code_db_2,
                    "bank_code_3": new_txn_bank_code_db_2,
                    "pmt_gateway_3": new_txn_payment_gateway_db_2,
                    "upi_txn_type_3": new_txn_upi_txn_type_db_2,
                    "upi_bank_code_3": new_txn_upi_bank_code_db_2,
                    "upi_mc_id_3": new_txn_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db_1,
                    "tid_2": new_txn_tid_db_1,
                    "mid_3": new_txn_mid_db_2,
                    "tid_3": new_txn_tid_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_116():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_success_callback_after_expiry_AutoRefund_Disabled_AXIS_DIRECT
    Sub Feature Description: Performing a UPI  success callback via Axis Direct after expiry when autorefund is disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    116: TC_116
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='AXIS_DIRECT',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update remotepay_setting set setting_value=1 where setting_name='cnpTxnTimeoutDuration' and  " \
                "org_code='" + org_code + "'; "
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating remotepay_setting table: {result}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',  # Chane api name
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)  # Check
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                portal_driver = TestSuiteSetup.initialize_firefox_driver()
                paymentLinkUrl = response['paymentLink']
                portal_driver.get(paymentLinkUrl)
                logger.info("Opening the link in the browser")
                rp_upi_txn = remotePayTxnPage(portal_driver)
                logger.info("Clicking on UPI to start the txn.")
                rp_upi_txn.clickOnRemotePayUPI()
                logger.info("Launching UPI")
                rp_upi_txn.clickOnRemotePayLaunchUPI()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch txn timeout from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"txn timeout for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch timeout for Ezetap org is : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"txn timeout attempt is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Waiting for timeout: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Waiting for Ezetap org timeout : {setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            config_mid = result['mid'].values[0]
            config_tid = result['tid'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and mc_id: {upi_mc_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"  # Needs to modify these queries
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")

            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_created_time}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated random original_settlement_status is : {original_settlement_status}")
            original_mid = result['mid'].values[0]
            logger.debug(f"generated random original_mid is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"generated random original_tid is : {original_tid}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated random original_acquirer_code is : {original_acquirer_code}")
            original_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated random original_issuer_code is : {original_issuer_code}")
            original_org_code = result['org_code'].values[0]
            logger.debug(f"generated random original_org_code is : {original_org_code}")
            original_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated random original_txn_type is : {original_txn_type}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_ref_id = '211115084892E01' + str(original_rrn)


            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': original_rrn,
                                                                 'gatewayTransactionId': original_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the request.")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where orig_txn_id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated new customer_name is : {new_txn_customer_name}")
            new_txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated new payer_name is : {new_txn_payer_name}")
            new_txn_status = result['status'].values[0]
            logger.debug(f"generated new new txn status is : {new_txn_status}")
            new_txn_date_time = result['created_time'].values[0]
            logger.debug(f"generated new_posting_date is : {new_txn_date_time}")
            new_txn_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated new_settlement_status is : {new_txn_settlement_status}")
            new_txn_mid = result['mid'].values[0]
            logger.debug(f"generated new_mid is : {new_txn_mid}")
            new_txn_tid = result['tid'].values[0]
            logger.debug(f"generated new_tid is : {new_txn_tid}")
            new_original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"generated new_original_mid is : {new_original_txn_id}")
            new_txn_id = result['id'].values[0]
            logger.debug(f"generated new txn id is : {new_txn_id}")
            new_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated original_acquirer_code is : {new_txn_acquirer_code}")
            new_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated  original_issuer_code is : {new_txn_issuer_code}")
            new_txn_org_code = result['org_code'].values[0]
            logger.debug(f"generated  original_org_code is : {new_txn_org_code}")
            new_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated  original_txn_type is : {new_txn_type}")
            new_rrNumber = result['rr_number'].values[0]
            logger.debug(f"generated  rrNumber is : {new_rrNumber}")

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
                date_and_time = date_time_converter.to_app_format(original_created_time)
                new_date_and_time = date_time_converter.to_app_format(new_txn_date_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    # "customer_name": original_customer_name,
                    # "payer_name": original_payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    # "rrn": str(rrn),
                    "date": date_and_time,
                    # "auth_code": auth_code,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "rrn_2": str(new_rrNumber),
                    "customer_name_2": new_txn_customer_name,
                    "payer_name_2": new_txn_payer_name,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": new_date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)  # logger
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                # app_rrn = txnHistoryPage.fetch_RRN_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                # app_auth_code = txnHistoryPage.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)
                new_app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status}")
                new_app_payment_status = new_app_payment_status.split(':')[1]
                new_app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode}")
                new_app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id}")
                new_app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount}")
                new_app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {new_txn_id}, {new_app_rrn}")
                new_app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id}, {new_app_date_and_time}")
                new_app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status}")
                new_app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name}")
                new_app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name}")
                new_app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id}")
                new_app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg}")


                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    # "customer_name": app_customer_name,
                    # "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    # "rrn": str(app_rrn),
                    "date": app_date_and_time,
                    # "auth_code": app_auth_code,

                    "pmt_mode_2": new_app_payment_mode,
                    "pmt_status_2": new_app_payment_status,
                    "txn_amt_2": new_app_amount.split(' ')[1],
                    "settle_status_2": new_app_settlement_status,
                    "txn_id_2": new_app_txn_id,
                    "customer_name_2": new_app_customer_name,
                    "payer_name_2": new_app_payer_name,
                    "order_id_2": new_app_order_id,
                    "pmt_msg_2": new_app_payment_msg,
                    "rrn_2": str(new_app_rrn),
                    "date_2": new_app_date_and_time,
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
                date_time = date_time_converter.db_datetime(original_created_time)
                new_date = date_time_converter.db_datetime(new_txn_date_time) # Replace date with dateand time
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    # "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "REMOTE_PAY",
                    "mid": original_mid,
                    "tid": original_tid,
                    "org_code": original_org_code,
                    "date": date_time,
                    # "auth_code": auth_code,

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    # "new_rrn": new_rrNumber,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "issuer_code_2": "AXIS",
                    "txn_type_2": new_txn_type,
                    "mid_2": new_txn_mid,
                    "tid_2": new_txn_tid,
                    "org_code_2": new_txn_org_code,
                    "date_2": new_date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                logger.debug("Respone from Api details is", api_details)  # Change API details, add loggers
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                # rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]
                # auth_code_api = response["authCode"] #No authcode in response

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                logger.debug(f"Response received for transaction details api is : {response}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"API Details response is : {response}")
                new_status_api = response["status"]
                new_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_state_api = response["states"][0]
                # new_rrn_api = response["rrNumber"]
                new_settlement_status_api = response["settlementStatus"]
                new_issuer_code_api = response["issuerCode"]
                new_acquirer_code_api = response["acquirerCode"]
                new_orgCode_api = response["orgCode"]
                new_mid_api = response["mid"]
                new_tid_api = response["tid"]
                new_txn_type_api = response["txnType"]
                new_date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     # "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     # "auth_code": auth_code_api

                                     "pmt_status_2": new_status_api,
                                     "txn_amt_2": new_amount_api,
                                     "pmt_mode_2": new_payment_mode_api,
                                     "pmt_state_2": new_state_api,
                                     # "new_rrn": new_rrn_api,
                                     "settle_status_2": new_settlement_status_api,
                                     "acquirer_code_2": new_acquirer_code_api,
                                     "issuer_code_2": new_issuer_code_api,
                                     "txn_type_2": new_txn_type_api,
                                     "mid_2": new_mid_api,
                                     "tid_2": new_tid_api,
                                     "org_code_2": new_orgCode_api,
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_date_api)

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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_Status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "EXPIRED",
                    "mid": config_mid,
                    "tid": config_tid,

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_txn_type_2": "REMOTE_PAY_UPI_INTENT",
                    "mid_2": new_txn_mid,
                    "tid_2": new_txn_tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_upi_status_db = result["status"].iloc[0]
                new_upi_txn_type_db = result["txn_type"].iloc[0]
                new_bank_code_db = result["bank_code"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_status_db = result["status"].iloc[0]
                new_payment_mode_db = result["payment_mode"].iloc[0]
                new_amount_db = int(result["amount"].iloc[0])
                new_state_db = result["state"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_Status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid_db,
                    "tid": tid_db,

                    "pmt_status_2": new_status_db,
                    "pmt_state_2": new_state_db,
                    "txn_amt_2": new_amount_db,
                    "upi_txn_status_2": new_upi_status_db,
                    "upi_txn_type_2": new_upi_txn_type_db,
                    "settle_status_2": new_txn_settlement_status,
                    "acquirer_code_2": new_txn_acquirer_code,
                    "upi_bank_code_2": new_bank_code_db,
                    "mid_2": config_mid,
                    "tid_2": config_tid
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
                    expected_portal_values = {}
                    #
                    # Write the test case Portal validation code block here. Set this to pass if not required.
                    #
                    actual_portal_values = {}
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                    actualPortal=actual_portal_values)
                except Exception as e:
                    Configuration.perform_portal_val_exception(testcase_id, e)
                logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            # -----------------------------------------End of Portal Validation---------------------------------------
            if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
                logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
                try:
                    txn_date, txn_time = date_time_converter.to_chargeslip_format(new_txn_date_time)
                    expected_values = {'PAID BY:': 'UPI',
                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                       # 'RRN': str(callback_1_rrn),
                                       'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                       'date': txn_date,
                                       'time': txn_time,
                                       # 'AUTH CODE': ""
                                       }
                    logger.debug(f"expected_values : {expected_values}")
                    receipt_validator.perform_charge_slip_validations(new_txn_id,
                                                                      {"username": app_username,
                                                                       "password": app_password},
                                                                      expected_values)

                except Exception as e:
                    Configuration.perform_charge_slip_val_exception(testcase_id, e)
                    logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation----------------------------------

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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_117():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_success_callback_before_expiry_AXIS_DIRECT_AutoRefund_Disabled
    Sub Feature Description: Verification of a two UPI  success callback via Axis Direct before expiry the when autorefund is disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    117: TC_117
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='AXIS_DIRECT',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',  # Chane api name
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)  # Check
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                portal_driver = TestSuiteSetup.initialize_firefox_driver()
                paymentLinkUrl = response['paymentLink']
                portal_driver.get(paymentLinkUrl)
                logger.info("Opening the link in the browser")
                rp_upi_txn = remotePayTxnPage(portal_driver)
                logger.info("Clicking on UPI to start the txn.")
                rp_upi_txn.clickOnRemotePayUPI()
                logger.info("Launching UPI")
                rp_upi_txn.clickOnRemotePayLaunchUPI()

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            config_mid = result['mid'].values[0]
            config_tid = result['tid'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and mc_id: {upi_mc_id}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"  # Needs to modify these queries
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_created_time}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated random original_settlement_status is : {original_settlement_status}")
            original_mid = result['mid'].values[0]
            logger.debug(f"generated random original_mid is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"generated random original_tid is : {original_tid}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated random original_acquirer_code is : {original_acquirer_code}")
            original_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated random original_issuer_code is : {original_issuer_code}")
            original_org_code = result['org_code'].values[0]
            logger.debug(f"generated random original_org_code is : {original_org_code}")
            original_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated random original_txn_type is : {original_txn_type}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_ref_id = '211115084892E01' + str(original_rrn)


            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': original_rrn,
                                                                 'gatewayTransactionId': original_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the request.")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id= '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated new customer_name is : {new_txn_customer_name}")
            new_txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated new payer_name is : {new_txn_payer_name}")
            new_txn_status = result['status'].values[0]
            logger.debug(f"generated new new txn status is : {new_txn_status}")
            new_txn_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"generated new_settlement_status is : {new_txn_settlement_status}")
            new_txn_mid = result['mid'].values[0]
            logger.debug(f"generated new_mid is : {new_txn_mid}")
            new_txn_tid = result['tid'].values[0]
            logger.debug(f"generated new_tid is : {new_txn_tid}")
            new_original_txn_id = result['orig_txn_id'].values[0]
            logger.debug(f"generated new_original_mid is : {new_original_txn_id}")
            new_txn_id = result['id'].values[0]
            logger.debug(f"generated new txn id is : {new_txn_id}")
            new_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"generated original_acquirer_code is : {new_txn_acquirer_code}")
            new_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"generated  original_issuer_code is : {new_txn_issuer_code}")
            new_txn_org_code = result['org_code'].values[0]
            logger.debug(f"generated  original_org_code is : {new_txn_org_code}")
            new_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated  original_txn_type is : {new_txn_type}")
            new_rrNumber = result['rr_number'].values[0]
            logger.debug(f"generated  rrNumber is : {new_rrNumber}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': callback_2_rrn,
                                                                 'gatewayTransactionId': callback_2_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            orig_txn_customer_name = result['customer_name'].values[0]
            orig_txn_payer_name = result['payer_name'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            new_txn_payer_name = result['payer_name'].values[0]
            new_txn_type = result['txn_type'].values[0]
            new_txn_date_time = result['created_time'].values[0]
            logger.debug(f"generated new_posting_date is : {new_txn_date_time}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

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
                date_and_time = date_time_converter.to_app_format(original_created_time)
                new_date_and_time = date_time_converter.to_app_format(new_txn_date_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "customer_name": orig_txn_customer_name,
                    "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "customer_name_2": new_txn_customer_name,
                    "payer_name_2": new_txn_payer_name,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn_2": str(callback_2_rrn),
                    "date": date_and_time,
                    "date_2": new_date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)  # logger
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)

                new_app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status_1}")
                new_app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id}, {new_app_date_and_time_1}")
                new_app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode_1}")
                new_app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id_1}")
                new_app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount_1}")
                new_app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_rrn_1}")
                new_app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name_1}")
                new_app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status_1}")
                new_app_payer_name_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name_1}")
                new_app_payment_status_1 = new_app_payment_status_1.split(':')[1]
                new_app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id_1}")
                new_app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg_1}")


                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "rrn": str(app_rrn),

                    "pmt_mode_2": new_app_payment_mode_1,
                    "pmt_status_2": new_app_payment_status_1,
                    "txn_amt_2": str(new_app_amount_1).split(' ')[1],
                    "settle_status_2": new_app_settlement_status_1,
                    "txn_id_2": new_app_txn_id_1,
                    "customer_name_2": new_app_customer_name_1,
                    "payer_name_2": new_app_payer_name_1,
                    "order_id_2": new_app_order_id_1,
                    "pmt_msg_2": new_app_payment_msg_1,
                    "rrn_2": str(new_app_rrn_1),
                    "date": app_date_and_time,
                    "date_2": new_app_date_and_time_1,
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
                date_time = date_time_converter.db_datetime(original_created_time)
                new_date = date_time_converter.db_datetime(new_txn_date_time) # Replace date with dateand time
                expected_api_values = {
                                        "pmt_status": "AUTHORIZED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "SETTLED",
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": orig_txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "customer_name": orig_txn_customer_name,
                                       "payer_name": orig_txn_payer_name,
                                       "rrn": str(original_rrn),

                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "SETTLED",
                                       # "new_rrn_1": str(callback_1_rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "AXIS",
                                       "issuer_code_2": "AXIS",
                                       "txn_type_2": new_txn_type,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                        "org_code_2": org_code,
                                       "date": date_time,
                                        "customer_name_2": new_txn_customer_name,
                                       "payer_name_2": new_txn_payer_name,
                                       "rrn_2": str(callback_2_rrn),
                                       "date_2": new_date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
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
                date_api = response["createdTime"]
                customer_name_api = response["customerName"]
                payer_name_api = response["payerName"]
                rrn_api = response["rrNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                new_txn_status_api = response["status"]
                new_txn_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_txn_state_api = response["states"][0]
                # new_txn_rrn_api_1 = response["rrNumber"]
                new_txn_settlement_status_api = response["settlementStatus"]
                new_txn_issuer_code_api = response["issuerCode"]
                new_txn_acquirer_code_api = response["acquirerCode"]
                new_txn_orgCode_api = response["orgCode"]
                new_txn_mid_api = response["mid"]
                new_txn_tid_api = response["tid"]
                new_txn_txn_type_api = response["txnType"]
                new_txn_date_api = response["createdTime"]
                new_customer_name_api = response["customerName"]
                new_payer_name_api = response["payerName"]
                new_rrn_api = response["rrNumber"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "customer_name": customer_name_api,
                                     "payer_name": payer_name_api,
                                     "rrn": str(rrn_api),

                                     "pmt_status_2": new_txn_status_api,
                                     "txn_amt_2": new_txn_amount_api,
                                     "pmt_mode_2": new_payment_mode_api,
                                     "pmt_state_2": new_txn_state_api,
                                     # "new_rrn_1": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api,
                                     "acquirer_code_2": new_txn_acquirer_code_api,
                                     "issuer_code_2": new_txn_issuer_code_api,
                                     "txn_type_2": new_txn_txn_type_api,
                                     "mid_2": new_txn_mid_api,
                                     "tid_2": new_txn_tid_api,
                                     "org_code_2": new_txn_orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api),
                                     "customer_name_2": new_customer_name_api,
                                     "payer_name_2": new_payer_name_api,
                                     "rrn_2": str(new_rrn_api),
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
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type_2": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db = result["status"].iloc[0]
                new_txn_payment_mode_db = result["payment_mode"].iloc[0]
                new_txn_amount_db = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db = result["state"].iloc[0]
                new_txn_payment_gateway_db = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db = result["bank_code"].iloc[0]
                new_txn_settlement_status_db = result["settlement_status"].iloc[0]
                new_txn_tid_db = result['tid'].values[0]
                new_txn_mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db = result["status"].iloc[0]
                new_txn_upi_txn_type_db = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,

                    "pmt_status_2": new_txn_status_db,
                    "pmt_state_2": new_txn_state_db,
                    "pmt_mode_2": new_txn_payment_mode_db,
                    "txn_amt_2": new_txn_amount_db,
                    "upi_txn_status_2": new_txn_upi_status_db,
                    "settle_status_2": new_txn_settlement_status_db,
                    "acquirer_code_2": new_txn_acquirer_code_db,
                    "bank_code_2": new_txn_bank_code_db,
                    "pmt_gateway_2": new_txn_payment_gateway_db,
                    "upi_txn_type_2": new_txn_upi_txn_type_db,
                    "upi_bank_code_2": new_txn_upi_bank_code_db,
                    "upi_mc_id_2": new_txn_upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db,
                    "tid_2": new_txn_tid_db,

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
                    expected_portal_values = {}
                    #
                    # Write the test case Portal validation code block here. Set this to pass if not required.
                    #
                    actual_portal_values = {}
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                    actualPortal=actual_portal_values)
                except Exception as e:
                    Configuration.perform_portal_val_exception(testcase_id, e)
                logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
                logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
                try:
                    txn_date, txn_time = date_time_converter.to_chargeslip_format(new_txn_date_time)
                    expected_values = {'PAID BY:': 'UPI',
                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                       # 'RRN': str(callback_1_rrn),
                                       'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                       'date': txn_date,
                                       'time': txn_time,
                                       # 'AUTH CODE': ""
                                       }
                    logger.debug(f"expected_values : {expected_values}")
                    receipt_validator.perform_charge_slip_validations(new_txn_id,
                                                                      {"username": app_username,
                                                                       "password": app_password},
                                                                      expected_values)

                except Exception as e:
                    Configuration.perform_charge_slip_val_exception(testcase_id, e)
                logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation----------------------------------

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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_118():
    """
    Sub Feature Code: UI_Common_PM_RP_2_UPI_success_callback_before_expiry_AXIS_DIRECT_AutoRefund_Enabled
    Sub Feature Description: Verification of two UPI success callback via Axis Direct before expiry the when autorefund is enabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    118: TC_118
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='AXIS_DIRECT',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 40)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"Entered order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',  # Chane api name
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)  # Check
            if response['success'] == False:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                portal_driver = TestSuiteSetup.initialize_firefox_driver()
                paymentLinkUrl = response['paymentLink']
                portal_driver.get(paymentLinkUrl)
                logger.info("Opening the link in the browser")
                rp_upi_txn = remotePayTxnPage(portal_driver)
                logger.info("Clicking on UPI to start the txn.")
                rp_upi_txn.clickOnRemotePayUPI()
                logger.info("Launching UPI")
                rp_upi_txn.clickOnRemotePayLaunchUPI()

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and mc_id: {upi_mc_id}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"  # Needs to modify these queries
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_created_time = result['created_time'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_created_time}")
            original_mid = result['mid'].values[0]
            logger.debug(f"generated random original_mid is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"generated random original_tid is : {original_tid}")
            original_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {original_rrn}")
            original_ref_id = '211115084892E01' + str(original_rrn)


            logger.debug(
                f"replacing the payment intent with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': payment_intent_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': original_rrn,
                                                                 'gatewayTransactionId': original_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")
            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"Executed curl data on the remote server is: {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the request.")
            print(type(data_buffer))
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where id= '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated new customer_name is : {new_txn_customer_name}")
            new_txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated new payer_name is : {new_txn_payer_name}")
            new_txn_id = result['id'].values[0]
            logger.debug(f"generated new txn id is : {new_txn_id}")
            new_txn_type = result['txn_type'].values[0]
            logger.debug(f"generated  original_txn_type is : {new_txn_type}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_2_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': callback_2_rrn,
                                                                 'gatewayTransactionId': callback_2_ref_id})

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('confirm_axisdirect',
                                                      request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response : {response}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch new_txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            orig_txn_customer_name = result['customer_name'].values[0]
            orig_txn_payer_name = result['payer_name'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            new_txn_customer_name = result['customer_name'].values[0]
            new_txn_payer_name = result['payer_name'].values[0]
            new_txn_type = result['txn_type'].values[0]
            new_txn_date_time = result['created_time'].values[0]
            logger.debug(f"generated new_posting_date is : {new_txn_date_time}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

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
                date_and_time = date_time_converter.to_app_format(original_created_time)
                new_date_and_time = date_time_converter.to_app_format(new_txn_date_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "customer_name": orig_txn_customer_name,
                    "payer_name": orig_txn_payer_name,
                    "rrn": str(original_rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "REFUND_PENDING",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": new_txn_id,
                    "customer_name_2": new_txn_customer_name,
                    "payer_name_2": new_txn_payer_name,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "rrn_2": str(callback_2_rrn),
                    "date": date_and_time,
                    "date_2": new_date_and_time,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)  # logger
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id)

                new_app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id}, {new_app_payment_status_1}")
                new_app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id}, {new_app_date_and_time_1}")
                new_app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id}, {new_app_payment_mode_1}")
                new_app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_txn_id_1}")
                new_app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id}, {new_app_amount_1}")
                new_app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id}, {new_app_rrn_1}")
                new_app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id}, {new_app_customer_name_1}")
                new_app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id}, {new_app_settlement_status_1}")
                new_app_payer_name_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id}, {new_app_payer_name_1}")
                new_app_payment_status_1 = new_app_payment_status_1.split(':')[1]
                new_app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id}, {new_app_order_id_1}")
                new_app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id}, {new_app_payment_msg_1}")


                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "rrn": str(app_rrn),

                    "pmt_mode_2": new_app_payment_mode_1,
                    "pmt_status_2": new_app_payment_status_1,
                    "txn_amt_2": str(new_app_amount_1).split(' ')[1],
                    "settle_status_2": new_app_settlement_status_1,
                    "txn_id_2": new_app_txn_id_1,
                    "customer_name_2": new_app_customer_name_1,
                    "payer_name_2": new_app_payer_name_1,
                    "order_id_2": new_app_order_id_1,
                    "pmt_msg_2": new_app_payment_msg_1,
                    "rrn_2": str(new_app_rrn_1),
                    "date": app_date_and_time,
                    "date_2": new_app_date_and_time_1,
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
                date_time = date_time_converter.db_datetime(original_created_time)
                new_date = date_time_converter.db_datetime(new_txn_date_time) # Replace date with dateand time
                expected_api_values = {
                                        "pmt_status": "AUTHORIZED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "SETTLED",
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": orig_txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "customer_name": orig_txn_customer_name,
                                       "payer_name": orig_txn_payer_name,
                                       "rrn": str(original_rrn),

                                       "pmt_status_2": "REFUND_PENDING",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "UPI",
                                       "pmt_state_2": "REFUND_PENDING",
                                       # "new_rrn_1": str(callback_1_rrn),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "AXIS",
                                       "issuer_code_2": "AXIS",
                                       "txn_type_2": new_txn_type,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "date": date_time,
                                        # "new_txn_customer_name": new_txn_customer_name,
                                       # "new_txn_payer_name": new_txn_payer_name,
                                       # "new_rrn": str(callback_2_rrn),
                                       "date_2": new_date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
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
                date_api = response["createdTime"]
                customer_name_api = response["customerName"]
                payer_name_api = response["payerName"]
                rrn_api = response["rrNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                new_txn_status_api = response["status"]
                new_txn_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_txn_state_api = response["states"][0]
                # new_txn_rrn_api_1 = response["rrNumber"]
                new_txn_settlement_status_api = response["settlementStatus"]
                new_txn_issuer_code_api = response["issuerCode"]
                new_txn_acquirer_code_api = response["acquirerCode"]
                new_txn_orgCode_api = response["orgCode"]
                new_txn_mid_api = response["mid"]
                new_txn_tid_api = response["tid"]
                new_txn_txn_type_api = response["txnType"]
                new_txn_date_api = response["createdTime"]
                # new_customer_name_api = response["customerName"]
                # new_payer_name_api = response["payerName"]
                # new_rrn_api = response["rrNumber"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "customer_name": customer_name_api,
                                     "payer_name": payer_name_api,
                                     "rrn": str(rrn_api),
                                     "pmt_status_2": new_txn_status_api,
                                     "txn_amt_2": new_txn_amount_api,
                                     "pmt_mode_2": new_payment_mode_api,
                                     "pmt_state_2": new_txn_state_api,
                                     # "new_rrn_1": str(new_txn_rrn_api_1),
                                     "settle_status_2": new_txn_settlement_status_api,
                                     "acquirer_code_2": new_txn_acquirer_code_api,
                                     "issuer_code_2": new_txn_issuer_code_api,
                                     "txn_type_2": new_txn_txn_type_api,
                                     "mid_2": new_txn_mid_api,
                                     "tid_2": new_txn_tid_api,
                                     "org_code_2": new_txn_orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "date_2": date_time_converter.from_api_to_datetime_format(new_txn_date_api),
                                     # "new_txn_customer_name": new_customer_name_api,
                                     # "new_txn_payer_name": new_payer_name_api,
                                     # "new_rrn": str(new_rrn_api),
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
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,

                    "pmt_status_2": "REFUND_PENDING",
                    "pmt_state_2": "REFUND_PENDING",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "REFUND_PENDING",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "AXIS",
                    "bank_code_2": "AXIS",
                    "pmt_gateway_2": "AXIS",
                    "upi_txn_type_2": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code_2": "AXIS_DIRECT",
                    "upi_mc_id_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "mid_2": mid,
                    "tid_2": tid,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_status_db = result["status"].iloc[0]
                new_txn_payment_mode_db = result["payment_mode"].iloc[0]
                new_txn_amount_db = int(
                    result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                new_txn_state_db = result["state"].iloc[0]
                new_txn_payment_gateway_db = result["payment_gateway"].iloc[0]
                new_txn_acquirer_code_db = result["acquirer_code"].iloc[0]
                new_txn_bank_code_db = result["bank_code"].iloc[0]
                new_txn_settlement_status_db = result["settlement_status"].iloc[0]
                new_txn_tid_db = result['tid'].values[0]
                new_txn_mid_db = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_txn_upi_status_db = result["status"].iloc[0]
                new_txn_upi_txn_type_db = result["txn_type"].iloc[0]
                new_txn_upi_bank_code_db = result["bank_code"].iloc[0]
                new_txn_upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,

                    "pmt_status_2": new_txn_status_db,
                    "pmt_state_2": new_txn_state_db,
                    "pmt_mode_2": new_txn_payment_mode_db,
                    "txn_amt_2": new_txn_amount_db,
                    "upi_txn_status_2": new_txn_upi_status_db,
                    "settle_status_2": new_txn_settlement_status_db,
                    "acquirer_code_2": new_txn_acquirer_code_db,
                    "bank_code_2": new_txn_bank_code_db,
                    "pmt_gateway_2": new_txn_payment_gateway_db,
                    "upi_txn_type_2": new_txn_upi_txn_type_db,
                    "upi_bank_code_2": new_txn_upi_bank_code_db,
                    "upi_mc_id_2": new_txn_upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "mid_2": new_txn_mid_db,
                    "tid_2": new_txn_tid_db,

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
                    expected_portal_values = {}
                    #
                    # Write the test case Portal validation code block here. Set this to pass if not required.
                    #
                    actual_portal_values = {}
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                    actualPortal=actual_portal_values)
                except Exception as e:
                    Configuration.perform_portal_val_exception(testcase_id, e)
                logger.info(f"Completed Portal validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
            # -----------------------------------------End of Portal Validation---------------------------------------
            if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
                logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
                try:
                    txn_date, txn_time = date_time_converter.to_chargeslip_format(original_created_time)
                    expected_values = {'PAID BY:': 'UPI',
                                       'merchant_ref_no': 'Ref # ' + str(order_id),
                                       # 'RRN': str(callback_1_rrn),
                                       'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                       'date': txn_date,
                                       'time': txn_time,
                                       # 'AUTH CODE': ""
                                       }
                    logger.debug(f"expected_values : {expected_values}")
                    receipt_validator.perform_charge_slip_validations(txn_id,
                                                                      {"username": app_username,
                                                                       "password": app_password},
                                                                      expected_values)

                except Exception as e:
                    Configuration.perform_charge_slip_val_exception(testcase_id, e)
                logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation----------------------------------

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)