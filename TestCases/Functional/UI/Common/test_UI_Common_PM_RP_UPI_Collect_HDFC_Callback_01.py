import random
import shutil
import sys
import time
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
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
def test_common_100_103_014():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Success_Via_Pure_UPI_Callback_HDFC
    Sub Feature Description: Verification of a Remote Pay successful pure upi txn via HDFC using callback
    Sub Feature Code: UI_Common_PM_UPI_Collect_success_callback_before_expiry_AutoRefund_Enabled_HDFC
    Sub Feature Description: Performing a  UPI Collect success callback via HDFC before expiry when auto refund is enabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    014: TC_014
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                paymentLinkUrl = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")
            upi_mc_id = result['id'].values[0]

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")

            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select * from upi_txn where txn_id = '" + txn_id + "';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            logger.debug(
                f"replacing the Intent ID with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn})
            print(api_details['CurlData'])
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
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            # status = result['status'].values[0]
            posting_date = result['posting_date'].values[0]
            # settlement_status = result['settlement_status'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]
            # acquirer_code = result['acquirer_code'].values[0]
            # issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amount": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    "auth_code": auth_code,
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
                txnHistoryPage = TransHistoryPage(app_driver)
                # txnHistoryPage.click_on_transaction_by_order_id(order_id)
                txnHistoryPage.click_on_transaction_by_txn_id(txn_id)

                app_payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_rrn = txnHistoryPage.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txnHistoryPage.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_auth_code = txnHistoryPage.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amount": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "rrn": str(app_rrn),
                    "date": app_date_and_time,
                    "auth_code": app_auth_code,
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of App Validation---------------------------------------

            # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "auth_code": auth_code,
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
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]
                auth_code_api = response["authCode"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api, "mid": mid_api,
                                     "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "auth_code": auth_code_api
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
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
                    "upi_txn_Status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid
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

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "tid": tid_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------

            # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(str(org_code))
                home_page_portal.wait_for_home_page_load()

                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")

            # -----------------------------------------End of Portal Validation---------------------------------------

            # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code}
                logger.debug(f"expected_values : {expected_values}")
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)

            except Exception as e:
                ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = "Fail"
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
def test_common_100_103_015():
    """
    Sub Feature Code: UI_Common_PM_RP_upi collect_Failed_Via_Pure_upi collect_Callback_HDFC
    Sub Feature Description: Verification of a Remote Pay failed pure upi collect txn via HDFC using callback
    TC naming code description:
    100: Payment Method
    103: RemotePay
    014: TC_015
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                paymentLinkUrl = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upiMerchantid : {upi_mc_id}")

            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            status = result['status'].values[0]
            posting_date = result['posting_date'].values[0]
            settlement_status = result['settlement_status'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")

            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]

            query = "select * from upi_txn where txn_id = '" + txn_id + "';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            logger.debug(
                f"replacing the Intent ID with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_failed_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn})
            print(api_details['CurlData'])
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
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amount": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "rrn": str(rrn),
                    "date": date_and_time,
                    # "auth_code": auth_code,
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
                txnHistoryPage = TransHistoryPage(app_driver)
                # txnHistoryPage.click_on_transaction_by_order_id(order_id)
                txnHistoryPage.click_on_transaction_by_txn_id(txn_id)

                app_payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_rrn = txnHistoryPage.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payer_name = txnHistoryPage.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                # app_auth_code = txnHistoryPage.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

                actual_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": app_payment_status,
                    "txn_amount": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "rrn": str(app_rrn),
                    "date": app_date_and_time,
                    # "auth_code": app_auth_code,
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of App Validation---------------------------------------

            # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    # "auth_code": auth_code,
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
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]
                # auth_code_api = response["authCode"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api, "mid": mid_api,
                                     "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     # "auth_code": auth_code_api
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
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
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid
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

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

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
                    "tid": tid_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------

            # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(str(org_code))
                home_page_portal.wait_for_home_page_load()

                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")

            # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
def test_common_100_103_016():
    """
    Sub Feature Code: UI_Common_PM_Success_RP_upi collect_Callback_After Expiry_HDFC
    Sub Feature Description:Verification of a Success Remote Pay pure upi collect txn after expiry for HDFC using callback
    Sub Feature Code: UI_Common_PM_UPI_Collect_success_callback_after_expiry_AutoRefund_Disabled_HDFC
    Sub Feature Description: Performing a  UPI Collect success callback via HDFC after  expiry when autorefund is disabled.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    016: TC_016
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

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
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            amount = random.randint(1, 10)
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
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

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

            # org_setting_value = result['setting_value'].values[0]
            # logger.info(f"max upi attempt for {org_code} is {org_setting_value}" )

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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upiMerchantid : {upi_mc_id}")

            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            # ref_id = '211115084892E01' + str(rrn)
            # status = result['status'].values[0]
            posting_date = result['posting_date'].values[0]
            # settlement_status = result['settlement_status'].values[0]
            # mid = result['mid'].values[0]
            # tid = result['tid'].values[0]
            # acquirer_code = result['acquirer_code'].values[0]
            # issuer_code = result['issuer_code'].values[0]
            # org_code_txn = result['org_code'].values[0]
            # txn_type = result['txn_type'].values[0]

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            logger.debug(
                f"replacing the Intent ID with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn})
            print(api_details['CurlData'])
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
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {"Payment Status Original": "FAILED", "Payment mode": "UPI",
                                       "Payment Txn ID": new_txn_id, "Payment Amt": str(amount),
                                       "Payment Status": "AUTHORIZED",
                                       "Payment mode Original": "UPI", "Payment Txn ID Original": original_txn_id,
                                       "Payment Amt Original": str(amount), "rrn": str(rrn),
                                       "rrn original": str(original_rrn), "date": date_and_time}

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                # txnHistoryPage.click_on_transaction_by_order_id(order_id)
                transactions_history_page.click_on_transaction_by_txn_id(new_txn_id)
                app_rrn = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {new_txn_id}, {app_rrn}")
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_second_transaction_by_order_id(order_id)
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {original_txn_id}, {app_rrn_original}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_txn_id_original}, {app_date_and_time}")

                actual_app_values = {"Payment Status": app_payment_status.split(':')[1],
                                     "Payment mode": app_payment_mode,
                                     "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                     "Payment Status Original": app_payment_status_original.split(':')[1],
                                     "Payment mode Original": app_payment_mode_original,
                                     "Payment Txn ID Original": app_txn_id_original,
                                     "Payment Amt Original": str(app_payment_amt_original), "rrn": str(app_rrn),
                                     "rrn original": str(app_rrn_original), "date": app_date_and_time}

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {"Payment Status Original": "FAILED", "Amount": amount, "Payment Mode": "UPI",
                                       "Payment Status": "AUTHORIZED", "Amount Original": amount,
                                       "Payment State Original": "FAILED", "Payment Mode Original": "UPI",
                                       "Payment State": "SETTLED", "date": date,
                                       # "rrn": str(rrn),
                                       # "rrn original": str(rrn)
                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": new_txn_id})
                print("API DETAILS for new_Txn_id after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                # rrn_api = response["rrNumber"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                state_api_original = response["states"][0]
                date_api = response["postingDate"]
                # rrn_api_original = response["rrNumber"]

                #
                actual_api_values = {"Payment Status": status_api, "Amount": amount_api,
                                     "Payment Mode": payment_mode_api,
                                     "Payment Status Original": status_api_original,
                                     "Amount Original": amount_api_original,
                                     "Payment State": state_api, "Payment State Original": state_api_original,
                                     "Payment Mode Original": payment_mode_api_original,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)
                                     # "rrn": str(rrn_api), "rrn original": str(rrn_api_original)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"Payment Status Original": "FAILED", "Payment State Original": "FAILED",
                                    "Payment mode": "UPI",
                                    "Payment amount": amount, "UPI_Txn_Status Original": "FAILED",
                                    "Payment Status": "AUTHORIZED", "Payment State": "SETTLED",
                                    "Payment mode Original": "UPI",
                                    "Payment amount Original": amount, "UPI_Txn_Status": "AUTHORIZED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount_db,
                                  "UPI_Txn_Status": upi_status_db, "Payment Status Original": status_db_original,
                                  "Payment State Original": state_db_original,
                                  "Payment mode Original": payment_mode_db_original,
                                  "Payment amount Original": amount_db_original,
                                  "UPI_Txn_Status Original": upi_status_db_original}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expectedPortalValues = {"Payment State Original": "Expired", "Payment Type": "UPI",
                                        "Payment State": "Settled", "Payment Type Original": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00",
                                        "Amount Original": "Rs." + str(amount) + ".00",
                                        "Username": app_username, "Username Original": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)

                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")

                home_page_portal.click_switch_button(org_code)
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(new_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_state = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_state_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actualPortalValues = {"Payment State Original": portal_state_original,
                                      "Payment Type": portal_txn_type_original,
                                      "Payment State": portal_state, "Payment Type Original": portal_txn_type,
                                      "Amount": portal_amt, "Amount Original": portal_amt_original,
                                      "Username": portal_username, "Username Original": portal_username_original}

                logger.debug(f"actualPortalValues : {actualPortalValues}")
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
def test_common_100_103_017():
    """
    Sub Feature Code: UI_Common_PM_UPI_Collect_Expired_Callback_AutoRefundEnabled_HDFC
    Sub Feature Description: Verification of a one upi collect expired via HDFC when auto refund is enalbed.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    017: TC_017
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

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
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            amount = random.randint(1, 10)
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
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = "select * from remotepay_setting where setting_name='maxUpiAttemptInCNP' and org_code = '" + str(
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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upiMerchantid : {upi_mc_id}")

            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            original_txn_id = result['id'].values[0]
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            ref_id = '211115084892E01' + str(rrn)
            status = result['status'].values[0]
            posting_date = result['posting_date'].values[0]
            settlement_status = result['settlement_status'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            logger.debug(
                f"replacing the Intent ID with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_expired_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn})
            print(api_details['CurlData'])
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
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch transaction details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            auth_code = result['auth_code'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amount": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "rrn": str(rrn),
                    "date": date_and_time,

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
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                actual_app_values = {"pmt_mode": app_payment_mode,
                                     "pmt_status": app_payment_status,
                                     "txn_amount": app_amount.split(' ')[1],
                                     "settle_status": app_settlement_status,
                                     "txn_id": app_txn_id,
                                     "customer_name": app_customer_name,
                                     "payer_name": app_payer_name,
                                     "order_id": app_order_id,
                                     "payment_msg": app_payment_msg,
                                     "rrn": str(app_rrn),
                                     "date": app_date_and_time}

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "rrn": str(rrn),
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": txn_type,
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code_txn,
                                       "date": date,
                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

                #
                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"Payment Status Original": "EXPIRED", "Payment State Original": "EXPIRED",
                                    "Payment mode": "UPI",
                                    "Payment amount": amount, "UPI_Txn_Status Original": "EXPIRED",
                                    "Payment Status": "EXPIRED", "Payment State": "EXPIRED",
                                    "Payment mode Original": "UPI",
                                    "Payment amount Original": amount, "UPI_Txn_Status": "EXPIRED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])
                state_db_original = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]

                actualDBValues = {"Payment Status": "EXPIRED",
                                  "Payment State": "EXPIRED",
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db,
                                  "UPI_Txn_Status": "EXPIRED",
                                  "Payment Status Original": "EXPIRED",
                                  "Payment State Original": state_db_original,
                                  "Payment mode Original": payment_mode_db_original,
                                  "Payment amount Original": amount_db_original,
                                  "UPI_Txn_Status Original": "EXPIRED"}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expectedPortalValues = {"Payment State Original": "Expired", "Payment Type": "UPI",
                                        "Payment State": "Settled", "Payment Type Original": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00",
                                        "Amount Original": "Rs." + str(amount) + ".00",
                                        "Username": app_username, "Username Original": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)

                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")

                home_page_portal.click_switch_button(org_code)
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_state = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_state_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actualPortalValues = {"Payment State Original": portal_state_original,
                                      "Payment Type": portal_txn_type_original,
                                      "Payment State": portal_state, "Payment Type Original": portal_txn_type,
                                      "Amount": portal_amt, "Amount Original": portal_amt_original,
                                      "Username": portal_username, "Username Original": portal_username_original}

                logger.debug(f"actualPortalValues : {actualPortalValues}")
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
def test_common_100_103_018():
    """
    Sub Feature Code: UI_Common_PM_RP_upi_collect_Expired_One_success_Callback_AutoRefundEnabled_HDFC
    Sub Feature Description: Verification of a Remote Pay upi collect txn after expiry via HDFC using success callback when auto refund is enabled.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    014: TC_018
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" + org_code + "';"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

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
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            amount = random.randint(1, 10)
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
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_driver.get(paymentLinkUrl)
                remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            # upi_mc_id = result['id'].values[0]
            # logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upiMerchantid : {upi_mc_id}")

            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {original_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id_expired and rrn_expired : {original_txn_id} and {original_rrn}")

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
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

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"Payment intent for UPI is: {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            logger.debug(f"upi_mc_id from the upi_merchant_config is:{upi_mc_id}")

            query = "select * from upi_txn where txn_id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch txn_ref from upi_txn for {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_ref = result['txn_ref'].values[0]

            logger.debug(
                f"replacing the Intent ID with {payment_intent_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': txn_ref, 'Txn_id': payment_intent_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn})

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
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pg_merchant_id),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            # After successful txn
            query = "select * from txn where orig_txn_id = '" + original_txn_id + "';"
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
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                new_date_and_time = date_time_converter.to_app_format(new_txn_date_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amount": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": original_txn_id,
                    "customer_name": original_customer_name,
                    "payer_name": original_payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "rrn": str(original_rrn),
                    "date": date_and_time,

                    "new_pmt_mode": "UPI",
                    "new_pmt_status": "REFUND_PENDING",
                    "new_txn_amt": str(amount),
                    "new_settle_status": "SETTLED",
                    "new_txn_id": new_txn_id,
                    "new_rrn": str(new_rrNumber),
                    "new_customer_name": new_txn_customer_name,
                    "new_payer_name": new_txn_payer_name,
                    "new_order_id": order_id,
                    "new_payment_msg": "PAYMENT SUCCESSFUL",
                    "new_date": new_date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

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
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status,
                    "txn_amount": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "rrn": str(app_rrn),
                    "date": app_date_and_time,

                    "new_pmt_mode": new_app_payment_mode,
                    "new_pmt_status": new_app_payment_status,
                    "new_txn_amt": new_app_amount.split(' ')[1],
                    "new_settle_status": new_app_settlement_status,
                    "new_txn_id": new_app_txn_id,
                    "new_customer_name": new_app_customer_name,
                    "new_payer_name": new_app_payer_name,
                    "new_order_id": new_app_order_id,
                    "new_payment_msg": new_app_payment_msg,
                    "new_rrn": str(new_app_rrn),
                    "new_date": new_app_date_and_time,

                }

                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(original_posting_date)
                new_date = date_time_converter.db_datetime(new_txn_date_time)
                expected_api_values = {"pmt_status": "FAILED",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "FAILED",
                                       "rrn": str(original_rrn),
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": original_txn_type,
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": original_org_code,
                                       "date": date,

                                       "new_pmt_status": "REFUND_PENDING",
                                       "new_txn_amt": amount,
                                       "new_pmt_mode": "UPI",
                                       "new_pmt_state": "REFUND_PENDING",
                                       "new_rrn": new_rrNumber,
                                       "new_settle_status": "SETTLED",
                                       "new_acquirer_code": "HDFC",
                                       "new_issuer_code": "HDFC",
                                       "new_txn_type": new_txn_type,
                                       "new_mid": new_txn_mid,
                                       "new_tid": new_txn_tid,
                                       "new_org_code": new_txn_org_code,
                                       "new_date": new_date,

                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                print("API DETAILS for new_Txn_id after callback:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
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
                                                                        "txnId": new_txn_id})
                logger.debug(f"Response received for transaction details api is : {response}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"API Details response is : {response}")
                new_status_api = response["status"]
                new_amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                new_payment_mode_api = response["paymentMode"]
                new_state_api = response["states"][0]
                new_rrn_api = response["rrNumber"]
                new_settlement_status_api = response["settlementStatus"]
                new_issuer_code_api = response["issuerCode"]
                new_acquirer_code_api = response["acquirerCode"]
                new_orgCode_api = response["orgCode"]
                new_mid_api = response["mid"]
                new_tid_api = response["tid"]
                new_txn_type_api = response["txnType"]
                new_date_api = response["createdTime"]

                #
                actual_api_values = {"pmt_status": status_api,
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
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),

                                     "new_pmt_status": new_status_api,
                                     "new_txn_amt": new_amount_api,
                                     "new_pmt_mode": new_payment_mode_api,
                                     "new_pmt_state": new_state_api,
                                     "new_rrn": new_rrn_api,
                                     "new_settle_status": new_settlement_status_api,
                                     "new_acquirer_code": new_acquirer_code_api,
                                     "new_issuer_code": new_issuer_code_api,
                                     "new_txn_type": new_txn_type_api,
                                     "new_mid": new_mid_api,
                                     "new_tid": new_tid_api,
                                     "new_org_code": new_orgCode_api,
                                     "new_date": date_time_converter.from_api_to_datetime_format(new_date_api)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "UPI",
                                    "txn_amt": amount,
                                    "upi_txn_status": "FAILED",
                                    "settle_status": "FAILED",
                                    "acquirer_code": "HDFC",
                                    "upi_txn_type": "REMOTE_PAY",
                                    "pmt_intent_status": "EXPIRED",
                                    "mid": original_mid,
                                    "tid": original_tid,

                                    "new_pmt_status": "REFUND_PENDING",
                                    "new_pmt_state": "REFUND_PENDING",
                                    "new_txn_amt": amount,
                                    "new_upi_txn_status": "REFUND_PENDING",
                                    "new_settle_status": "SETTLED",
                                    "new_acquirer_code": "HDFC",
                                    "upi_bank_code": "HDFC",
                                    "new_upi_txn_type": "COLLECT",
                                    "new_mid": new_txn_mid,
                                    "new_tid": new_txn_tid,

                                    }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + original_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                # upi_bank_code_db = result["bank_code"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_status_db = result["status"].iloc[0]
                new_payment_mode_db = result["payment_mode"].iloc[0]
                new_amount_db = int(result["amount"].iloc[0])
                new_state_db = result["state"].iloc[0]
                # new_bank_code_db = result["bank_code"].iloc[0]

                query = "select * from upi_txn where txn_id='" + new_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                new_upi_status_db = result["status"].iloc[0]
                # new_upi_amount_db = int(result["amount"].iloc[0])
                new_upi_txn_type_db = result["txn_type"].iloc[0]
                new_bank_code_db = result["bank_code"].iloc[0]

                actualDBValues = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "upi_txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "pmt_intent_status": intent_status,

                    "new_pmt_status": new_status_db,
                    "new_pmt_state": new_state_db,
                    "new_txn_amt": new_amount_db,
                    "new_upi_txn_status": new_upi_status_db,
                    "new_upi_txn_type": new_upi_txn_type_db,
                    "new_settle_status": new_txn_settlement_status,
                    "new_acquirer_code": new_txn_acquirer_code,
                    "upi_bank_code": new_bank_code_db,
                    "new_mid": new_mid_api,
                    "new_tid": new_tid_api

                }
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expectedPortalValues = {"Payment State Original": "Expired", "Payment Type": "UPI",
                                        "Payment State": "Settled", "Payment Type Original": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00",
                                        "Amount Original": "Rs." + str(amount) + ".00",
                                        "Username": app_username, "Username Original": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)

                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")

                home_page_portal.click_switch_button(org_code)
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_state = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(original_txn_id)
                portal_txn_type_original = portal_values_dict['Type']
                portal_state_original = portal_values_dict['Status']
                portal_amt_original = portal_values_dict['Total Amount']
                portal_username_original = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                logger.debug(f"Fetching Username from portal : {portal_username_original} ")

                actualPortalValues = {"Payment State Original": portal_state_original,
                                      "Payment Type": portal_txn_type_original,
                                      "Payment State": portal_state, "Payment Type Original": portal_txn_type,
                                      "Amount": portal_amt, "Amount Original": portal_amt_original,
                                      "Username": portal_username, "Username Original": portal_username_original}

                logger.debug(f"actualPortalValues : {actualPortalValues}")
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_two_callback():
    """
    Sub Feature Code: UI_Common_PM_2_Pure_UPI_success_callback_after_qr_expiry_AXIS_DIRECT_AutoRefund_Enabled
    Sub Feature Description: Performing two pure upi success callback via AXIS_DIRECT after expiry the qr when autorefund is enabled
    100: Payment Method
    101: Remote Pay
    056: TC056
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        TestSuiteSetup.revert_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                               portal_pw=portal_password)

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

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
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)

            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 49)

            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)

            payment_page.click_on_Upi_paymentMode()
            logger.info("selected payment mode is UPI")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            logger.info("resetting the com.ezetap.basicapp")
            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(63)

            query = "select * from upi_merchant_config where bank_code = 'AXIS_DIRECT' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")

            callback_1_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_1_rrn}")
            callback_1_ref_id = '211115084892E01' + str(callback_1_rrn)
            logger.debug(f"generated random ref_id is : {callback_1_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {callback_1_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': original_txn_id,
                                                                 'transactionAmount': amount,
                                                                 'merchantId': str(pg_merchant_id),
                                                                 'creditVpa': vpa,
                                                                 'rrn': callback_1_rrn,
                                                                 'gatewayTransactionId': callback_1_ref_id})

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
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_1 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_1 : {new_txn_id_1}")

            callback_2_rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {callback_2_rrn}")
            callback_2_ref_id = '211115084892E01' + str(callback_2_rrn)
            logger.debug(f"generated random ref_id is : {callback_2_ref_id}")

            logger.debug(
                f"replacing the Txn_id with {original_txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {original_rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl',
                                                      curl_data={'merchantTransactionId': original_txn_id,
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
            logger.debug(f"Query to fetch new_txn_id_1 from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id_2 = result['id'].values[0]
            logger.debug(f"Query result new_txn_id_2 : {new_txn_id_2}")

            query = "select * from txn where id = '" + original_txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            orig_txn_status = result['status'].values[0]
            orig_txn_customer_name = result['customer_name'].values[0]
            orig_txn_payer_name = result['payer_name'].values[0]
            orig_txn_settle_status = result['settlement_status'].values[0]
            orig_txn_acquirer_code = result['acquirer_code'].values[0]
            orig_txn_issuer_code = result['issuer_code'].values[0]
            orig_txn_org_code_txn = result['org_code'].values[0]
            orig_txn_type = result['txn_type'].values[0]
            orig_posting_date = result['posting_date'].values[0]

            query = "select * from txn where id = '" + new_txn_id_1 + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_status_1 = result['status'].values[0]
            new_txn_customer_name_1 = result['customer_name'].values[0]
            new_txn_payer_name_1 = result['payer_name'].values[0]
            new_txn_settle_status_1 = result['settlement_status'].values[0]
            new_txn_acquirer_code_1 = result['acquirer_code'].values[0]
            new_txn_issuer_code_1 = result['issuer_code'].values[0]
            new_txn_org_code_txn_1 = result['org_code'].values[0]
            new_txn_type_1 = result['txn_type'].values[0]
            new_txn_posting_date_1 = result['posting_date'].values[0]

            query = "select * from txn where id = '" + new_txn_id_2 + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_status_2 = result['status'].values[0]
            new_txn_customer_name_2 = result['customer_name'].values[0]
            new_txn_payer_name_2 = result['payer_name'].values[0]
            new_txn_settle_status_2 = result['settlement_status'].values[0]
            new_txn_acquirer_code_2 = result['acquirer_code'].values[0]
            new_txn_issuer_code_2 = result['issuer_code'].values[0]
            new_txn_org_code_txn_2 = result['org_code'].values[0]
            new_txn_type_2 = result['txn_type'].values[0]
            new_txn_posting_date_2 = result['posting_date'].values[0]

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            logger.error(f"Test case execution failed due to the exception : {e}")
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------

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
                    "payment_mode": "UPI",
                    "payment_status": "EXPIRED",
                    "txn_amount": str(amount),
                    "settlement_status": "FAILED",
                    "txn_id": original_txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "new_txn_payment_mode_1": "UPI",
                    "new_txn_payment_status_1": "REFUND_PENDING",
                    "new_txn_amount_1": str(amount),
                    "new_txn_settlement_status_1": "SETTLED",
                    "new_txn_id_1": new_txn_id_1,
                    "new_txn_customer_name_1": new_txn_customer_name_1,
                    "new_txn_payer_name_1": new_txn_payer_name_1,
                    "new_txn_order_id_1": order_id,
                    "new_txn_payment_msg_1": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_1": str(callback_1_rrn),
                    "new_txn_payment_mode_2": "UPI",
                    "new_txn_payment_status_2": "REFUND_PENDING",
                    "new_txn_amount_2": str(amount),
                    "new_txn_settlement_status_2": "SETTLED",
                    "new_txn_id_2": new_txn_id_2,
                    "new_txn_customer_name_2": new_txn_customer_name_2,
                    "new_txn_payer_name_2": new_txn_payer_name_2,
                    "new_txn_order_id_2": order_id,
                    "new_txn_payment_msg_2": "PAYMENT SUCCESSFUL",
                    "new_txn_rrn_2": str(callback_2_rrn),
                    "date": date_and_time,
                    "new_txn_date_1": new_txn_date_and_time_1,
                    "new_txn_date_2": new_txn_date_and_time_2
                }

                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver.reset()
                login_page.perform_login(app_username, app_password)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()

                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(original_txn_id)

                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {original_txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {original_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {original_txn_id}, {app_payment_msg}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_1)

                new_app_payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_1}, {new_app_payment_status_1}")
                new_app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_1}, {new_app_date_and_time_1}")
                new_app_payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_1}, {new_app_payment_mode_1}")
                new_app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_txn_id_1}")
                new_app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_1}, {new_app_amount_1}")
                new_app_rrn_1 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_1}, {new_app_rrn_1}")
                new_app_customer_name_1 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_1}, {new_app_customer_name_1}")
                new_app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_1}, {new_app_settlement_status_1}")
                new_app_payer_name_1 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_1}, {new_app_payer_name_1}")
                new_app_payment_status_1 = new_app_payment_status_1.split(':')[1]
                new_app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_1}, {new_app_order_id_1}")
                new_app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_1}, {new_app_payment_msg_1}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(new_txn_id_2)

                new_app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(
                    f"Fetching status from txn history for the txn : {new_txn_id_2}, {new_app_payment_status_2}")
                new_app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {new_txn_id_2}, {new_app_date_and_time_2}")
                new_app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {new_txn_id_2}, {new_app_payment_mode_2}")
                new_app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_txn_id_2}")
                new_app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {new_txn_id_2}, {new_app_amount_2}")
                new_app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {new_txn_id_2}, {new_app_rrn_2}")
                new_app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {new_txn_id_2}, {new_app_customer_name_2}")
                new_app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {new_txn_id_2}, {new_app_settlement_status_2}")
                new_app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {new_txn_id_2}, {new_app_payer_name_2}")
                new_app_payment_status_2 = new_app_payment_status_2.split(':')[1]
                new_app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {new_txn_id_2}, {new_app_order_id_2}")
                new_app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {new_txn_id_2}, {new_app_payment_msg_2}")

                actual_app_values = {
                    "payment_mode": "UPI",
                    "payment_status": app_payment_status,
                    "txn_amount": app_amount.split(' ')[1],
                    "settlement_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "new_txn_payment_mode_1": new_app_payment_mode_1,
                    "new_txn_payment_status_1": new_app_payment_status_1,
                    "new_txn_amount_1": str(new_app_amount_1).split(' ')[1],
                    "new_txn_settlement_status_1": new_app_settlement_status_1,
                    "new_txn_id_1": new_app_txn_id_1,
                    "new_txn_customer_name_1": new_app_customer_name_1,
                    "new_txn_payer_name_1": new_app_payer_name_1,
                    "new_txn_order_id_1": new_app_order_id_1,
                    "new_txn_payment_msg_1": new_app_payment_msg_1,
                    "new_txn_rrn_1": str(new_app_rrn_1),
                    "new_txn_payment_mode_2": new_app_payment_mode_2,
                    "new_txn_payment_status_2": new_app_payment_status_2,
                    "new_txn_amount_2": str(new_app_amount_2).split(' ')[1],
                    "new_txn_settlement_status_2": new_app_settlement_status_2,
                    "new_txn_id_2": new_app_txn_id_2,
                    "new_txn_customer_name_2": new_app_customer_name_2,
                    "new_txn_payer_name_2": new_app_payer_name_2,
                    "new_txn_order_id_2": new_app_order_id_2,
                    "new_txn_payment_msg_2": new_app_payment_msg_2,
                    "new_txn_rrn_2": str(new_app_rrn_2),
                    "date": app_date_and_time,
                    "new_txn_date_1": new_app_date_and_time_1,
                    "new_txn_date_2": new_app_date_and_time_2
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
                # time.sleep(5)
            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(orig_posting_date)
                new_txn_date_1 = date_time_converter.db_datetime(new_txn_posting_date_1)
                new_txn_date_2 = date_time_converter.db_datetime(new_txn_posting_date_2)
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount, "pmt_mode": "UPI",
                                       "pmt_state": "EXPIRED",
                                       "settlement_status": "FAILED",
                                       "acquirer_code": "AXIS",
                                       "issuer_code": "AXIS",
                                       "txn_type": orig_txn_type, "mid": mid, "tid": tid, "org_code": org_code,
                                       "new_pmt_status_1": "REFUND_PENDING",
                                       "new_txn_amt_1": amount, "new_pmt_mode_1": "UPI",
                                       "new_pmt_state_1": "REFUND_PENDING",
                                       # "new_rrn_1": str(callback_1_rrn),
                                       "new_settlement_status_1": "SETTLED",
                                       "new_acquirer_code_1": "AXIS",
                                       "new_issuer_code_1": "AXIS",
                                       "new_txn_type_1": new_txn_type_1, "new_mid_1": mid,
                                       "new_tid_1": tid, "new_org_code_1": org_code,
                                       "new_pmt_status_2": "REFUND_PENDING",
                                       "new_txn_amt_2": amount, "new_pmt_mode_2": "UPI",
                                       "new_pmt_state_2": "REFUND_PENDING",
                                       # "new_rrn_2": str(callback_2_rrn),
                                       "new_settlement_status_2": "SETTLED",
                                       "new_acquirer_code_2": "AXIS",
                                       "new_issuer_code_2": "AXIS",
                                       "new_txn_type_2": new_txn_type_2, "new_mid_2": mid,
                                       "new_tid_2": tid, "new_org_code_2": org_code,
                                       "date": date,
                                       "new_txn_date_1": new_txn_date_1,
                                       "new_txn_date_2": new_txn_date_2
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
                new_txn_date_api_1 = response["postingDate"]

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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settlement_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api, "org_code": orgCode_api,
                                     "new_pmt_status_1": new_txn_status_api_1,
                                     "new_txn_amt_1": new_txn_amount_api_1, "new_pmt_mode_1": new_payment_mode_api_1,
                                     "new_pmt_state_1": new_txn_state_api_1,
                                     # "new_rrn_1": str(new_txn_rrn_api_1),
                                     "new_settlement_status_1": new_txn_settlement_status_api_1,
                                     "new_acquirer_code_1": new_txn_acquirer_code_api_1,
                                     "new_issuer_code_1": new_txn_issuer_code_api_1,
                                     "new_txn_type_1": new_txn_txn_type_api_1, "new_mid_1": new_txn_mid_api_1,
                                     "new_tid_1": new_txn_tid_api_1, "new_org_code_1": new_txn_orgCode_api_1,
                                     "new_pmt_status_2": new_txn_status_api_2,
                                     "new_txn_amt_2": new_txn_amount_api_2, "new_pmt_mode_2": new_payment_mode_api_2,
                                     "new_pmt_state_2": new_txn_state_api_2,
                                     # "new_rrn_2": str(new_txn_rrn_api_2),
                                     "new_settlement_status_2": new_txn_settlement_status_api_2,
                                     "new_acquirer_code_2": new_txn_acquirer_code_api_2,
                                     "new_issuer_code_2": new_txn_issuer_code_api_2,
                                     "new_txn_type_2": new_txn_type_api_2, "new_mid_2": new_txn_mid_api_2,
                                     "new_tid_2": new_txn_tid_api_2, "new_org_code_2": new_txn_orgCode_api_2,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "new_txn_date_1": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_1),
                                     "new_txn_date_2": date_time_converter.from_api_to_datetime_format(
                                         new_txn_date_api_2)
                                     }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "EXPIRED",
                    "settlement_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "payment_gateway": "AXIS",
                    "upi_txn_type_db": "PAY_QR",
                    "upi_bank_code_db": "AXIS_DIRECT",
                    "upi_mc_id_db": upi_mc_id,
                    "new_pmt_status_1": "REFUND_PENDING",
                    "new_pmt_state_1": "REFUND_PENDING",
                    "new_pmt_mode_1": "UPI",
                    "new_txn_amt_1": amount,
                    "new_upi_txn_status_1": "REFUND_PENDING",
                    "new_settlement_status_1": "SETTLED",
                    "new_acquirer_code_1": "AXIS",
                    "new_bank_code_1": "AXIS",
                    "new_payment_gateway_1": "AXIS",
                    "new_upi_txn_type_db_1": "PAY_QR",
                    "new_upi_bank_code_db_1": "AXIS_DIRECT",
                    "new_upi_mc_id_db_1": upi_mc_id,
                    "new_pmt_status_2": "REFUND_PENDING",
                    "new_pmt_state_2": "REFUND_PENDING",
                    "new_pmt_mode_2": "UPI",
                    "new_txn_amt_2": amount,
                    "new_upi_txn_status_2": "REFUND_PENDING",
                    "new_settlement_status_2": "SETTLED",
                    "new_acquirer_code_2": "AXIS",
                    "new_bank_code_2": "AXIS",
                    "new_payment_gateway_2": "AXIS",
                    "new_upi_txn_type_db_2": "PAY_QR",
                    "new_upi_bank_code_db_2": "AXIS_DIRECT",
                    "new_upi_mc_id_db_2": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "new_txn_mid_1": mid,
                    "new_txn_tid_1": tid,
                    "new_txn_mid_2": mid,
                    "new_txn_tid_2": tid
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
                    "settlement_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "new_pmt_status_1": new_txn_status_db_1,
                    "new_pmt_state_1": new_txn_state_db_1,
                    "new_pmt_mode_1": new_txn_payment_mode_db_1,
                    "new_txn_amt_1": new_txn_amount_db_1,
                    "new_upi_txn_status_1": new_txn_upi_status_db_1,
                    "new_settlement_status_1": new_txn_settlement_status_db_1,
                    "new_acquirer_code_1": new_txn_acquirer_code_db_1,
                    "new_bank_code_1": new_txn_bank_code_db_1,
                    "new_payment_gateway_1": new_txn_payment_gateway_db_1,
                    "new_upi_txn_type_db_1": new_txn_upi_txn_type_db_1,
                    "new_upi_bank_code_db_1": new_txn_upi_bank_code_db_1,
                    "new_upi_mc_id_db_1": new_txn_upi_mc_id_db_1,
                    "new_pmt_status_2": new_txn_status_db_2,
                    "new_pmt_state_2": new_txn_state_db_2,
                    "new_pmt_mode_2": new_txn_payment_mode_db_2,
                    "new_txn_amt_2": new_txn_amount_db_2,
                    "new_upi_txn_status_2": new_txn_upi_status_db_2,
                    "new_settlement_status_2": new_txn_settlement_status_db_2,
                    "new_acquirer_code_2": new_txn_acquirer_code_db_2,
                    "new_bank_code_2": new_txn_bank_code_db_2,
                    "new_payment_gateway_2": new_txn_payment_gateway_db_2,
                    "new_upi_txn_type_db_2": new_txn_upi_txn_type_db_2,
                    "new_upi_bank_code_db_2": new_txn_upi_bank_code_db_2,
                    "new_upi_mc_id_db_2": new_txn_upi_mc_id_db_2,
                    "mid": mid_db,
                    "tid": tid_db,
                    "new_txn_mid_1": new_txn_mid_db_1,
                    "new_txn_tid_1": new_txn_tid_db_1,
                    "new_txn_mid_2": new_txn_mid_db_2,
                    "new_txn_tid_2": new_txn_tid_db_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                actual_portal_values = {}
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")

        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
