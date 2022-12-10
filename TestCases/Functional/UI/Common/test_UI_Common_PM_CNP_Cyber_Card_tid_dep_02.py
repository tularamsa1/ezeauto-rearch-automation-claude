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
    ResourceAssigner, date_time_converter, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_151():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Cyber_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a successful debit card txn via CNP link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    151: TC_151
    """

    expected_success_message = "Your payment is successfully completed! You may close the browser now."

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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code +"' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:

            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            msg =""
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['id'].values[0]
            logger.info(f"id from setting is: {tid_settings}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial_db
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("response is:", response)

            payment_link_url = response['paymentLink']
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(payment_link_url)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.clickOnDebitCardToExpand()
            logger.info("Enter Debit card details")
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 0002")
            remote_pay_txn.enterDebitCardExpiryMonth("12")
            remote_pay_txn.enterDebitCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()
            remote_pay_txn.clickOnSubmitButton()
            remote_pay_txn.wait_for_success_message()
            success_message = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your success message is:  {success_message}")
            logger.info(f"Your expected success message is:  {expected_success_message}")

            if success_message == expected_success_message:
                pass
            else:
                raise Exception("Success messages are not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            txn_bank_name = result['bank_name'].values[0]
            logger.debug(f"Query result, txn_bank_name : {txn_bank_name}")
            txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, txn_acquirer_code : {txn_acquirer_code}")
            txn_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settlement_status : {txn_settlement_status}")
            txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, txn_payment_mode : {txn_payment_mode}")
            txn_amount = result['amount'].values[0]
            logger.debug(f"Query result, txn_amount : {txn_amount}")
            txn_created_time = result['created_time'].values[0]
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_gateway : {payment_gateway}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_mode : {payment_mode}")
            payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_flow : {payment_flow}")
            payment_option = result['payment_option'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_option : {payment_option}")
            payment_option_value1 = result['payment_option_value1'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_option_value1 : {payment_option_value1}")
            payment_status = result['payment_status'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_status : {payment_status}")
            state = result['state'].values[0]
            logger.debug(f"Query result from cnp_txn, state : {state}")
            payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_card_brand : {payment_card_brand}")
            payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result from cnp_txn, payment_card_type : {payment_card_type}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result from cnp_txn, acquirer_code : {acquirer_code}")
            issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result from cnp_txn, issuer_code : {issuer_code}")
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")


            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_card_type}")
            cnp_txn_external_ref = result['external_ref'].values[0]
            logger.debug(f"Query result, cnp_txn_external_ref : {cnp_txn_external_ref}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]


            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_rrn_number = result['rr_number'].values[0]
            logger.debug(f"Query result, cnpware_txn_rrn_number : {cnpware_txn_rrn_number}")
            cnpware_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_acquirer_code : {cnpware_txn_acquirer_code}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            cnpware_txn_external_ref = result['external_ref'].values[0]
            logger.debug(f"Query result, cnpware_txn_external_ref : {cnpware_txn_external_ref}")
            cnpware_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_auth_code : {cnpware_txn_auth_code}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()
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
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            ReportProcessor.get_TC_Exe_Time()
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
                date_and_time = date_time_converter.to_app_format(txn_created_time)
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "AUTHORIZED",
                                     "txn_amt": "{:.2f}".format(amount),
                                     "txn_id": txn_id,
                                     "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT SUCCESSFUL",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "auth_code": txn_auth_code,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
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
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "rrn": payment_rrn,
                                   "order_id": payment_order_id,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "auth_code": payment_auth_code,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(txn_created_time)
                logger.info(f"Started API validation for the test case : {testcase_id}")

                expectedAPIValues = {"pmt_status": "AUTHORIZED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": cnp_txn_state,
                                     "acquirer_code": cnp_txn_acquirer_code,
                                     "settle_status": txn_settle_status,
                                     "rrn": cnp_txn_rrn,
                                     "issuer_code": txn_issuer_code,
                                     "txn_type": cnpware_txn_txn_type,
                                     "org_code": org_code,
                                     "date": date,
                                     "tid": txn_tid,
                                     "mid": txn_mid,
                                     "device_serial": txn_device_serial,
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                # Use txn details
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_in_list = response["txns"]
                status_api = ''
                amount_api = ''

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlement_status_api = elements["settlementStatus"]
                        rr_number_api = elements["rrNumber"]
                        issuer_code_api = elements["issuerCode"]
                        txn_type_api = elements["txnType"]
                        org_code_api = elements["orgCode"]
                        tid_api = elements["tid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {device_serial_api} ")

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlement_status_api,
                                   "rrn": rr_number_api,
                                   "issuer_code": issuer_code_api,
                                   "txn_type": txn_type_api,
                                   "org_code": org_code_api,
                                   "date": date,
                                   "tid": tid_api,
                                   "mid": mid_api,
                                   "device_serial": device_serial_api
                                   }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")

                expectedDBValues = {
                                    "pmt_status": "AUTHORIZED",
                                    "pmt_state": "SETTLED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "SETTLED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": cnpware_payment_flow,
                                    "pmt_intent_status": "COMPLETED",
                                    "tid": txn_tid,
                                    "mid": txn_mid,
                                    "device_serial": txn_device_serial,
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])
                bank_name_db = result["bank_name"].iloc[0]
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {
                                  "pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": amount,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status,
                                  "tid": tid_db,
                                  "mid": mid_db,
                                  "device_serial": device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")

            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_created_time)
                expectedValues = {'CARD TYPE': 'VISA',
                                  'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': str(cnp_txn_rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                  'date': txn_date, "time": txn_time,
                                  "AUTH CODE": txn_auth_code}

                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_152():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Failed_Cyber_Tid_dep
    Sub Feature Description: Tid Dep - Verification debit card failed txn for cybersource pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    152: TC_152
    """

    expectedfailed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."

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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            msg =""
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            query = "select * from merchant_pg_config where org_code = '" + str(org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['id'].values[0]
            logger.info(f"id from setting is: {tid_settings}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial_db
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("response is:", response)

            ui_driver = TestSuiteSetup.initialize_portal_driver()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            externalRef = response.get('externalRefNumber')
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(payment_link_url)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.clickOnDebitCardToExpand()
            logger.info("Enter Debit card details")
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
            remote_pay_txn.enterDebitCardExpiryMonth("12")
            remote_pay_txn.enterDebitCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()

            actualFailedMessage = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"After txn message is:  : {actualFailedMessage}")

            if expectedfailed_message == actualFailedMessage:
                pass
            else:
                print("Failed Message is not matching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_flow}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")

            query = "select * from payment_intent where id='" + payment_intent_id + "'"
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            payment_intent_status = result["status"].iloc[0]


            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:

            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_exe_failed()
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                logger.info(f"Started APP validation for the test case : {testcase_id}")

                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": "{:.2f}".format(amount),
                                     "txn_id": txn_id,
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "date": date_and_time,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "date": app_date_and_time,
                                   "order_id": payment_order_id,
                                   "msg": payment_status_msg,
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                date = date_time_converter.db_datetime(posting_date)
                logger.info(f"Started API validation for the test case : {testcase_id}")

                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": "FAILED",
                                     "acquirer_code": "HDFC",
                                     "settle_status": "FAILED",
                                     "issuer_code": "HDFC",
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date,
                                     "tid": txn_tid,
                                     "mid": txn_mid,
                                     "device_serial": txn_device_serial,
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")


                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                amount_api = response["amount"]
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_in_list = response["txns"]

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        acquirer_code__api = elements["acquirerCode"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        txn_type_api = elements["txnType"]
                        org_code_api = elements["orgCode"]
                        date_api = elements["postingDate"]
                        tid_api = elements["tid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {device_serial_api} ")


                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": payment_mode_api,
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlement_status_api,
                                   "issuer_code": issuer_code_api,
                                   "txn_type": txn_type_api,
                                   "org_code": org_code_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api),
                                   "tid": tid_api,
                                   "mid": mid_api,
                                   "device_serial": device_serial_api
                                   }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"

        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")

                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "ACTIVE",
                                    "tid": txn_tid,
                                    "mid": txn_mid,
                                    "device_serial": txn_device_serial
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                settle_status_db = result["settlement_status"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

                actualDBValues = {"pmt_status": status_db,
                                  "pmt_state": state_db,
                                  "pmt_mode": payment_mode_db,
                                  "txn_amt": amount,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status,
                                  "tid": tid_db,
                                  "mid": mid_db,
                                  "device_serial": device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_100_103_153():
    """
     Sub Feature Code: UI_Common_PM_CNP_Refund_Card_txn_Tid_dep
     Sub Feature Description: Tid Dep - Veification of a refund for card txn using remote pay.
     TC naming code description:
     100: Payment Method
     103: RemotePay
     153: TC_153
     """

    expected_message = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."

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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'CYBERSOURCE' and payment_mode = 'CNP';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------

        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            query = "select * from merchant_pg_config where org_code = '" + str(
                org_code) + "' and payment_gateway = 'CYBERSOURCE'"
            logger.debug(f"Query to fetch tid from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            tid_settings = result['tid'].values[0]
            logger.info(f"tid from setting is: {tid_settings}")

            # get the deviceSerial from terminal_info
            query = "select * from terminal_info where tid='" + str(tid_settings) + "';"
            logger.debug(f"Query to fetch id from the termial info table : {query}")
            result = DBProcessor.getValueFromDB(query)
            terminal_info_id = result['id'].values[0]
            logger.info(f"id from setting is: {tid_settings}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {mid_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Query result, deviceSerial from db : {device_serial_db}")
            tid_db = result['tid'].iloc[0]
            logger.debug(f"Query result, tid from db : {tid_db}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial_db
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")

            payment_link_url = response.get('paymentLink')
            payment_intent_id = response.get('paymentIntentId')

            query = "select * from remotepay_setting where setting_name='maximumPayAttemptsAllowed' and org_code = '" + str(org_code) + "';"
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

            query1 = "select * from remotepay_setting where setting_name='maximumPayAttemptsAllowed' and org_code = 'EZETAP'"
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
                while org_setting_value >= 0:
                    if org_setting_value == 0:
                        ui_driver = TestSuiteSetup.initialize_portal_driver()
                        ui_driver.get(payment_link_url)
                        break
                    else:
                        logger.debug(f"Running with org code max attempts.")
                        ui_driver = TestSuiteSetup.initialize_portal_driver()
                        ui_driver.get(payment_link_url)
                        remotePayTxn = remotePayTxnPage(ui_driver)
                        remotePayTxn.clickOnCreditCardToExpand()
                        remotePayTxn.enterNameOnTheCard("Sandeep")
                        remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
                        remotePayTxn.enterCreditCardExpiryMonth("12")
                        remotePayTxn.enterCreditCardExpiryYear("2050")
                        remotePayTxn.enterCreditCardCvv("111")
                        remotePayTxn.clickOnProceedToPay()
                        # ui_driver.execute_script("window.open('');")
                        org_setting_value -= 1
                    print("setting value is :", org_setting_value)

            elif setting_value:
                while setting_value >= 0:
                    if setting_value == 0:
                        ui_driver = TestSuiteSetup.initialize_portal_driver()
                        ui_driver.get(payment_link_url)
                        break
                    else:
                        ui_driver = TestSuiteSetup.initialize_portal_driver()
                        ui_driver.get(payment_link_url)
                        remotePayTxn = remotePayTxnPage(ui_driver)
                        remotePayTxn.clickOnCreditCardToExpand()
                        remotePayTxn.enterNameOnTheCard("Sandeep")
                        remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
                        remotePayTxn.enterCreditCardExpiryMonth("12")
                        remotePayTxn.enterCreditCardExpiryYear("2050")
                        remotePayTxn.enterCreditCardCvv("111")
                        remotePayTxn.clickOnProceedToPay()
                        setting_value -= 1
                    print("setting value is :", setting_value)

            else:
                pass
            logger.info("Timeout execution completed.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
            txn_state = result['state'].values[0]
            logger.debug(f"Query result, db txn_state from db : {txn_state}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnpware_payment_flow : {cnpware_payment_flow}")

            cnpware_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, cnpware_payment_flow : {cnpware_pmt_mode}")

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

                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "PENDING",
                                     "txn_amt": "{:.2f}".format(amount),
                                     "txn_id": txn_id,
                                     "order_id": order_id,
                                     "msg": "PAYMENT PENDING",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")


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
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_order_id}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "order_id": payment_order_id,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            try:
                date = date_time_converter.db_datetime(created_time)
                expectedAPIValues = {"pmt_status": "PENDING",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": cnp_txn_state,
                                     "acquirer_code": "HDFC",
                                     "settle_status": "PENDING",
                                     "issuer_code": "HDFC",
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date,
                                     "tid": txn_tid,
                                     "mid": txn_mid,
                                     "device_serial": txn_device_serial
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                # Use txn details
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                response_in_list = response["txns"]
                status_api = ''
                amount_api = ''

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        txn_type_api = elements["txnType"]
                        org_code_api = elements["orgCode"]
                        date_api = elements["postingDate"]
                        tid_api = elements["tid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {tid_api} ")
                        mid_api = elements["mid"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {mid_api} ")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Fetching Transaction payment Card Type from transaction api : {device_serial_api} ")

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlement_status_api,
                                   "issuer_code": issuer_code_api,
                                   "txn_type": txn_type_api,
                                   "org_code": org_code_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api),
                                   "tid": tid_api,
                                   "mid": mid_api,
                                   "device_serial": device_serial_api
                                   }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"pmt_status": "PENDING",
                                    "pmt_state": "PENDING",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "PENDING",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_mode": "CNP",
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": cnpware_payment_flow,
                                    "pmt_intent_status": "ACTIVE",
                                    "tid": txn_tid,
                                    "mid": txn_mid,
                                    "device_serial": txn_device_serial
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])
                bank_name_db = result["bank_name"].iloc[0]
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {"pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": txn_amt_db,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "cnpware_pmt_mode": cnpware_pmt_mode,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status,
                                  "tid": tid_db,
                                  "mid": mid_db,
                                  "device_serial": device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

