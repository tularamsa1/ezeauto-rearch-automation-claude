import random
import sys
from datetime import datetime

import pytest

from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, receipt_validator, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_172():

    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI Refund By API_AXIS_DIRECT_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay refund using api for AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    103: RemotePay
    172: TC172
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'AXIS_DIRECT' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password
                                                                              }
                                                  )
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(200, 300)

            order_id = datetime.now().strftime('%m%d%H%M%S')

            # acquisition and payment_gateway is AXIS
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="AXIS",
                                                                           payment_gateway="AXIS")
            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("Remotepay Initiate Tid Dependent response is:", response)

            ui_driver = TestSuiteSetup.initialize_firefox_driver()
            payment_link_url = response['paymentLink']
            ui_driver.get(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = remotePayTxnPage(ui_driver)
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
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"results from the txn table : txn_id_original : {txn_id_original}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"results from the txn table : customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"results from the txn table : payer_name : {payer_name}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"results from the txn table : auth_code : {auth_code}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"results from the txn table : org_code_txn : {org_code_txn}")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"results from the txn table : rrn_original : {rrn_original}")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"results from the txn table : txn_type_original : {txn_type_original}")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"results from the txn table : created_time_original : {created_time_original}")
            device_serial_original = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"results from the upi_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"results from the upi_merchant_config table : tid : {tid}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id_original)
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id_refunded : {txn_id_refunded}")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, refund_auth_code : {refund_auth_code}")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_type_refunded : {txn_type_refunded}")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, rrn_refunded : {rrn_refunded}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, created_time : {created_time}")


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
                                        "pmt_status": "STATUS:AUTHORIZED_REFUNDED",
                                        "pmt_status_2": "STATUS:REFUNDED",
                                        "pmt_mode": "UPI",
                                        "pmt_mode_2": "UPI",
                                        "settle_status": "SETTLED",
                                        "settle_status_2": "SETTLED",
                                        "txn_id": txn_id_original,
                                        "txn_id_2": txn_id_refunded,
                                        "txn_amt": str(amount) + ".00",
                                        "txn_amt_2": str(amount) + ".00",
                                        "customer_name": customer_name,
                                        "customer_name_2": customer_name,
                                        "payer_name": payer_name,
                                        "payer_name_2": payer_name,
                                        "order_id": order_id,
                                        "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                                        "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                                        "rrn": str(rrn_original),
                                        "date_2": date_and_time,
                                        "date": original_date_and_time
                                    }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)

                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

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
                                        "acquirer_code": "AXIS",
                                        "issuer_code": "AXIS",
                                        "txn_type": txn_type_original,
                                        "mid": mid,
                                        "tid": tid,
                                        "org_code": org_code_txn,
                                        "acquirer_code_2": "AXIS",
                                        "txn_type_2": txn_type_refunded,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "org_code_2": org_code_txn,
                                        "date": original_date_time
                                    }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_original
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                date_api_original = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_refunded
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["postingDate"]

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
                                    "date": date_time_converter.from_api_to_datetime_format(date_api_original)
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
                                        "acquirer_code": "AXIS",
                                        "acquirer_code_2": "AXIS",
                                        "bank_code": "AXIS",
                                        "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                        "upi_txn_type_2": "REFUND",
                                        "upi_bank_code": "AXIS_DIRECT",
                                        "upi_bank_code_2": "AXIS_DIRECT",
                                        "mid": mid,
                                        "tid": tid,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "device_serial": device_serial_original
                                    }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'AXIS_DIRECT';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db_original = result['mid'].iloc[0]
                tid_db_original = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db_orginial= result['device_serial'].iloc[0]


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
                                              'RRN': "",
                                              'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              'AUTH CODE': ""
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
def test_common_100_103_173():

    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_Refund_Failed_AXIS_DIRECT_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay upi refund failed via AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    103: RemotePay
    173: TC173
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'AXIS_DIRECT' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password
                                                                              }
                                                  )

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 201.06
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # acquisition and payment_gateway is AXIS
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="AXIS",
                                                                           payment_gateway="AXIS")
            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("Remotepay Initiate Tid Dependent response is:", response)

            ui_driver = TestSuiteSetup.initialize_firefox_driver()
            payment_link_url = response['paymentLink']
            ui_driver.get(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = remotePayTxnPage(ui_driver)
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
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id  from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name  from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name  from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code  from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn  from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original  from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original  from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original  from db query : {created_time_original} ")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Fetching txn_device_serial  from db query : {txn_device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid  from db query : {mid} ")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid  from db query : {tid} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id_original)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            logger.debug(f"response : response")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {rrn_refunded} ")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original  from db query : {created_time_original} ")

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
                                        "txn_amt":"{:.2f}".format(amount),
                                        "txn_amt_2": "{:.2f}".format(amount),
                                        "customer_name": customer_name,
                                        "customer_name_2": customer_name,
                                        "payer_name": payer_name,
                                        "payer_name_2": payer_name,
                                        "order_id": order_id,
                                        "pmt_msg": "PAYMENT SUCCESSFUL",
                                        "pmt_msg_2": "PAYMENT FAILED",
                                        "rrn": str(rrn_original),
                                        "date_2": date_and_time,
                                        "date": original_date_and_time
                                     }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

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
                                        "acquirer_code": "AXIS",
                                        "issuer_code": "AXIS",
                                        "txn_type": txn_type_original,
                                        "mid": mid,
                                        "tid": tid,
                                        "org_code": org_code_txn,
                                        "acquirer_code_2": "AXIS",
                                        "txn_type_2": txn_type_refunded,
                                        "org_code_2": org_code_txn,
                                        "date_2": refunded_date_time,
                                        "date": original_date_time
                                      }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_original
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = str(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                date_api_original = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_refunded
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = str(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["postingDate"]

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
                                    "acquirer_code": acquirer_code_api_original,
                                    "issuer_code": issuer_code_api_original,
                                    "txn_type": txn_type_api_original,
                                    "mid": mid_api_original,
                                    "tid": tid_api_original,
                                    "org_code": org_code_api_original,
                                    "acquirer_code_2": acquirer_code_api_refunded,
                                    "txn_type_2": txn_type_api_refunded,
                                    "org_code_2": org_code_api_refunded,
                                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                                    "date": date_time_converter.from_api_to_datetime_format(date_api_original)
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
                                    "acquirer_code": "AXIS",
                                    "acquirer_code_2": "AXIS",
                                    "bank_code": "AXIS",
                                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                    "upi_txn_type_2": "REFUND",
                                    "upi_bank_code": "AXIS_DIRECT",
                                    "upi_bank_code_2": "AXIS_DIRECT",
                                    "mid": mid,
                                    "tid": tid,
                                    "device_serial": txn_device_serial
                                  }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = float(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = float(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'AXIS_DIRECT';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db_original = result['mid'].iloc[0]
                tid_db_original = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db_original = result['device_serial'].iloc[0]

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
                                    "device_serial" : device_serial_db_original
                                }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_original)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_original),
                                              'BASE AMOUNT:': "Rs." + str(amount) ,
                                              'date': txn_date,
                                              'time': txn_time
                                              }

                logger.debug(f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")
                receipt_validator.perform_charge_slip_validations(txn_id_original,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

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
def test_common_100_103_174():

    """
    Sub Feature Code:UI_Common_PM_RP_RP_UPI_partial_Refund_AXIS_DIRECT_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay upi partial refund via AXIS_DIRECT
    TC naming code description:
    100: Payment Method
    103: RemotePay
    174: TC174
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -------------------------------Reset Settings to default(started)--------------------------------------------
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'AXIS_DIRECT' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password
                                                                              }
                                                  )

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(200, 300)
            refunded_amount = 100
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # acquisition and payment_gateway is AXIS
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="AXIS",payment_gateway="AXIS")
            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("Remotepay Initiate Tid Dependent response is:", response)

            ui_driver = TestSuiteSetup.initialize_firefox_driver()
            payment_link_url = response['paymentLink']
            ui_driver.get(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = remotePayTxnPage(ui_driver)
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
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching txn_id  from db query : {txn_id_original} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name  from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name  from db query : {payer_name} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code  from db query : {auth_code} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn  from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original  from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_original  from db query : {txn_type_original} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original  from db query : {created_time_original} ")
            device_serial_original = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial from db query : {device_serial} ")
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid  from db query : {mid} ")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid  from db query : {tid} ")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refunded_amount,
                                                                    "originalTransactionId": str(txn_id_original)
                                                                    }
                                                      )
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching refund_auth_code  from db query : {refund_auth_code} ")
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type_refunded  from db query : {txn_type_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_refunded  from db query : {rrn_refunded} ")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Fetching posting_date  from db query : {posting_date} ")
            created_date_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_date_time  from db query : {created_date_time} ")

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
                date_and_time = date_time_converter.to_app_format(created_date_time)
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
                                        "txn_amt": str(amount) + ".00",
                                        "txn_amt_2": str(refunded_amount) + ".00",
                                        "customer_name": customer_name,
                                        "customer_name_2": customer_name,
                                        "payer_name": payer_name,
                                        "payer_name_2": payer_name,
                                        "order_id": order_id,
                                        "pmt_msg": "PAYMENT SUCCESSFUL",
                                        "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                                        "rrn": str(rrn_original),
                                        "date_2": date_and_time,
                                        "date": original_date_and_time  # add date for refund cases also
                                    }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

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
                refunded_date_time = date_time_converter.db_datetime(created_date_time)
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
                                        "acquirer_code": "AXIS",
                                        "issuer_code": "AXIS",
                                        "txn_type": txn_type_original,
                                        "mid": mid,
                                        "tid": tid,
                                        "org_code": org_code_txn,
                                        "acquirer_code_2": "AXIS",
                                        "txn_type_2": txn_type_refunded,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "org_code_2": org_code_txn,
                                        "date_2": refunded_date_time,
                                        "date": original_date_time
                                    }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_original
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                date_api_original = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_refunded
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["postingDate"]

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
                                        "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
                                        "date": date_time_converter.from_api_to_datetime_format(date_api_original)
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
                                        "acquirer_code": "AXIS",
                                        "acquirer_code_2": "AXIS",
                                        "bank_code": "AXIS",
                                        "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                        "upi_txn_type_2": "REFUND",
                                        "upi_bank_code": "AXIS_DIRECT",
                                        "upi_bank_code_2": "AXIS_DIRECT",
                                        "mid": mid,
                                        "tid": tid,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "device_serial": device_serial_original
                                    }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int( result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'AXIS_DIRECT';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db_original = result['mid'].iloc[0]
                tid_db_original = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db_orginial = result['device_serial'].iloc[0]

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
                                    "mid_2": mid_db_refunded,
                                    "tid_2": tid_db_refunded,
                                    "device_serial": device_serial_db_orginial,
                                    }

                logger.debug(f"actual_db_values : {actual_db_values} for the testcase_id {testcase_id}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_date_time)

                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'BASE AMOUNT:': "Rs." + str(refunded_amount) + ".00",
                                              'date': txn_date,
                                              'time': txn_time
                                              }

                logger.debug(f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

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
def test_common_100_103_175():

    """
    Sub Feature Code: UI_Common_PM_RP_Upi_two_times_second_partial_refund_amount_greater_than_original_amount_Tid_dep
    Sub Feature Description: Tid Dep - Tid Dep - Verification of a two remote pay partial refund when second partial refund amount is greater than original amount
    TC naming code description:
    100: Payment Method
    103: RemotePay
    175: TC175
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'AXIS_DIRECT' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password
                                                                              }
                                                  )

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 300
            refunded_amount = 150
            greater_refund_amount = 151
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # acquisition and payment_gateway is AXIS
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="AXIS",payment_gateway="AXIS")
            print("device serial is :", device_serial)

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password,
                                                                    "deviceSerial": device_serial
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response of remotepay initiate {response}")
            print("Remotepay Initiate Tid Dependent response is:", response)

            ui_driver = TestSuiteSetup.initialize_firefox_driver()
            payment_link_url = response['paymentLink']
            ui_driver.get(payment_link_url)
            logger.info("Opening the link in the browser")
            rp_upi_txn = remotePayTxnPage(ui_driver)
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
            txn_id_original = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_original} ")
            status = result['status'].values[0]
            logger.debug(f"Fetching status from db query : {status} ")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching Customer Name from db query : {customer_name} ")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching Payer Name from db query : {payer_name} ")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from db query : {org_code_txn} ")
            rrn_original = result['rr_number'].iloc[0]
            logger.debug(f"Fetching rrn_original from db query : {rrn_original} ")
            txn_type_original = result['txn_type'].values[0]
            settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from db query : {settlement_status} ")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from db query : {acquirer_code} ")
            issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from db query : {issuer_code} ")
            created_time_original = result['created_time'].values[0]
            logger.debug(f"Fetching created_time_original from db query : {created_time_original} ")
            device_serial_original = result['device_serial'].values[0]
            logger.debug(f"Fetching device_serial_original from db query : {device_serial_original} ")
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refunded_amount,
                                                                    "originalTransactionId": str(txn_id_original)
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api is : {response}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": greater_refund_amount,
                                                                    "originalTransactionId": str(txn_id_original)
                                                                    }
                                                      )

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from refund api when refund amount is greater than original amount : {response}")
            api_error_message = response["errorMessage"]

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' and orig_txn_id ='" + str(txn_id_original) + "'"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            refund_auth_code = result['auth_code'].values[0]
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            rrn_refunded = result['rr_number'].iloc[0]
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching Transaction id, rrn from db query, txn_id : {txn_id_refunded}, rrn : {rrn_refunded} ")

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
                                        "txn_amt": str(amount) + ".00",
                                        "txn_amt_2": str(refunded_amount) + ".00",
                                        "customer_name": customer_name,
                                        "customer_name_2": customer_name,
                                        "payer_name": payer_name,
                                        "payer_name_2": payer_name,
                                        "order_id": order_id,
                                        "pmt_msg": "PAYMENT SUCCESSFUL",
                                        "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                                        "rrn": str(rrn_original),
                                        "date_2": date_and_time,
                                        "date": original_date_and_time
                                      }

                logger.debug(f"expected_app_values : {expected_app_values} for the testcase_id {testcase_id}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {payment_msg_refunded}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_original)

                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_original}, {app_rrn_original}")
                app_payment_status_original = txn_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_original_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_original}, {app_original_date_and_time}")

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
                                        "acquirer_code": "AXIS",
                                        "issuer_code": "AXIS",
                                        "txn_type": txn_type_original,
                                        "mid": mid,
                                        "tid": tid,
                                        "org_code": org_code_txn,
                                        "acquirer_code_2": "AXIS",
                                        "txn_type_2": txn_type_refunded,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "org_code_2": org_code_txn,
                                        "date_2": refunded_date_time,
                                        "date": original_date_time,
                                        "err_msg": "Amount to refund is greater than refundable amount."
                                    }

                logger.debug(f"expected_api_values : {expected_api_values} for the testcase_id {testcase_id}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_original
                                                                        }
                                                          )

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")

                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                date_api_original = response["postingDate"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id_refunded
                                                                        }
                                                          )
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                logger.debug(f"response : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                date_api_refunded = response["postingDate"]

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
                                        "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),
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
                                        "acquirer_code": "AXIS",
                                        "acquirer_code_2": "AXIS",
                                        "bank_code": "AXIS",
                                        "bank_code_2": "AXIS_DIRECT",
                                        "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                        "upi_txn_type_2": "REFUND",
                                        "upi_bank_code": "AXIS_DIRECT",
                                        "upi_bank_code_2": "AXIS_DIRECT",
                                        "mid": mid,
                                        "tid": tid,
                                        "mid_2": mid,
                                        "tid_2": tid,
                                        "device_serial": device_serial_original
                                    }

                logger.debug(f"expected_db_values : {expected_db_values} for the testcase_id {testcase_id}")

                query = "select * from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_refunded = result["status"].iloc[0]
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                amount_db_refunded = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_refunded = result["state"].iloc[0]
                acquirer_code_db_refunded = result["acquirer_code"].iloc[0]
                settlement_status_db_refunded = result["settlement_status"].iloc[0]
                tid_db_refunded = result['tid'].values[0]
                mid_db_refunded = result['mid'].values[0]


                query = "select * from upi_txn where txn_id='" + txn_id_refunded + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_refunded = result["status"].iloc[0]
                upi_txn_type_db_refunded = result["txn_type"].iloc[0]
                upi_bank_code_db_refunded = result["bank_code"].iloc[0]
                upi_mc_id_db_refunded = result["upi_mc_id"].iloc[0]
                bank_code_db_refunded = result["bank_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_original = result["state"].iloc[0]
                acquirer_code_db_original = result["acquirer_code"].iloc[0]
                bank_code_db_original = result["bank_code"].iloc[0]
                settlement_status_db_original = result["settlement_status"].iloc[0]


                query = "select * from upi_txn where txn_id='" + txn_id_original + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_original = result["status"].iloc[0]
                upi_txn_type_db_original = result["txn_type"].iloc[0]
                upi_bank_code_db_original = result["bank_code"].iloc[0]
                upi_mc_id_db_original = result["upi_mc_id"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'AXIS_DIRECT';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db_original = result['mid'].iloc[0]
                tid_db_original = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db_original) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db_orginial = result['device_serial'].iloc[0]

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
                                    "upi_txn_type": upi_txn_type_db_original,
                                    "upi_txn_type_2": upi_txn_type_db_refunded,
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

        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_chargeslip_values = {'PAID BY:': 'UPI',
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'BASE AMOUNT:': "Rs." + str(refunded_amount) + ".00",
                                              'date': txn_date,
                                              'time': txn_time,
                                              }

                logger.debug(f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_refunded,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


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

