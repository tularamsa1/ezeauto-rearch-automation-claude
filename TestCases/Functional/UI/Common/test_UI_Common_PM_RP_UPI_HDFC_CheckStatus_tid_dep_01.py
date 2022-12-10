import random
import shutil
import sys
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
def test_common_100_103_157():

    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_Success_Via_CheckStatus_HDFC_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay successful upi txn via HDFC using check status
    TC naming code description:
    100: Payment Method
    103: RemotePay
    157: TC_157
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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            print("Random number is generated for amount in float :", amount)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            #acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")

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


            portal_driver = TestSuiteSetup.initialize_firefox_driver()
            payment_link_url = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')
            portal_driver.get(payment_link_url)
            remote_pay_upi_txn = remotePayTxnPage(portal_driver)
            remote_pay_upi_txn.clickOnRemotePayUPI()
            remote_pay_upi_txn.clickOnRemotePayLaunchUPI()
            remote_pay_upi_txn.clickOnRemotePayCancelUPI()
            remote_pay_upi_txn.clickOnRemotePayProceed()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn from db : {rrn}")
            txn_id = result['id'].values[0]
            print("txn_id is :", txn_id)
            logger.debug(f"Query result, txn_id from db : {txn_id}")
            status = result['status'].values[0]
            logger.debug(f"Query result, status from db : {status}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name from db : {payer_name}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn from db : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type from db : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")


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
                                        "txn_amt": "{:.2f}".format(amount),
                                        "settle_status": "SETTLED",
                                        "txn_id": txn_id,
                                        "rrn": str(rrn),
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
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                                        "pmt_status": "AUTHORIZED",
                                        "txn_amt": amount,
                                        "pmt_mode": "UPI",
                                        "pmt_state": "SETTLED",
                                        "rrn": str(rrn),
                                        "settle_status": "SETTLED",
                                        "acquirer_code": "HDFC",
                                        "issuer_code": "HDFC",
                                        "txn_type": txn_type,
                                        "mid": txn_mid,
                                        "tid": txn_tid,
                                        "org_code": org_code_txn,
                                        "date": date,
                                        "device_serial": txn_device_serial
                                    }

                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id
                                                                        }
                                                          )
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
                device_serial_api = response["deviceSerial"]

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
                                        "org_code": orgCode_api,
                                        "date": date_time_converter.from_api_to_datetime_format(date_api),
                                        "device_serial": device_serial_api
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
                                        "acquirer_code": "HDFC",
                                        "bank_code": "HDFC",
                                        "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                        "upi_bank_code": "HDFC",
                                        "pmt_intent_status": "COMPLETED",
                                        "tid": txn_tid,
                                        "mid": txn_mid,
                                        "device_serial": txn_device_serial,
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

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'HDFC';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db = result['mid'].iloc[0]
                tid_db = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db = result['device_serial'].iloc[0]

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
                                        "pmt_intent_status": payment_intent_status,
                                        "mid": mid_db,
                                        "tid": tid_db,
                                        "device_serial": device_serial_db
                                    }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)

            except Exception as e:

                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------------

            # -----------------------------------------Start of ChargeSlip Validation-----------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'PAID BY:': 'UPI',
                                   'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
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
        Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_100_103_158():

    """
    Sub Feature Code : UI_Common_PM_RP_RP_UPI_Failed_Via_CheckStatus_HDFC_Tid_dep
    Sub Feature Description :Tid Dep - Verification of a Remote Pay failed UPI txn via HDFC using check status
    TC naming code description:
    100: Payment Method
    103: RemotePay
    158: TC_158
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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True

        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            logger.info("Test Case Execution Started for the test case : test_com_100_103_006")

            amount = 111
            order_id = datetime.now().strftime('%m%d%H%M%S')

            # acquisition and payment_gateway is HDFC
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")
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
            payment_intent_id = response.get('paymentIntentId')
            ui_driver.get(payment_link_url)
            remote_pay_upi_txn = remotePayTxnPage(ui_driver)
            remote_pay_upi_txn.clickOnRemotePayUPI()
            remote_pay_upi_txn.clickOnRemotePayLaunchUPI()
            remote_pay_upi_txn.clickOnRemotePayCancelUPI()
            remote_pay_upi_txn.clickOnRemotePayProceed()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn from db : {rrn}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id from db : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
            status = result['status'].values[0]
            logger.debug(f"Query result, status from db : {status}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name from db : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name from db : {payer_name}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"Query result, mid from db : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"Query result, tid from db : {txn_tid}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn from db : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type from db : {txn_type}")
            txn_device_serial = result['device_serial'].values[0]
            logger.debug(f"Query result, device_serial from db : {txn_device_serial}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:

            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started APP validation for the test case : {testcase_id}")
                date_and_time = date_time_converter.to_app_format(created_time)

                expectedAppValues = {"pmt_mode": "UPI",
                                     "pmt_status": "FAILED",
                                     "txn_amt": "{:.2f}".format(amount),
                                     "settle_status": "FAILED",
                                     "txn_id": txn_id,
                                     "rrn": str(rrn),
                                     "customer_name": customer_name,
                                     "payer_name": payer_name,
                                     "order_id": order_id,
                                     "payment_msg": "PAYMENT FAILED",
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
                txn_history_page.click_on_transaction_by_order_id(order_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
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

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(created_time)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "UPI",
                                     "pmt_state": "FAILED",
                                     "rrn": str(rrn),
                                     "settle_status": "FAILED",
                                     "acquirer_code": "HDFC",
                                     "issuer_code": "HDFC",
                                     "txn_type": txn_type,
                                     "mid": txn_mid,
                                     "tid": txn_tid,
                                     "org_code": org_code_txn,
                                     "date": date,
                                     "device_serial": txn_device_serial
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                #
                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
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
                device_serial_api = response["deviceSerial"]


                actualAPIValues = {"pmt_status": status_api,
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
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "UPI",
                                    "txn_amt": amount,
                                    "upi_txn_status": "FAILED",
                                    "settle_status": "FAILED",
                                    "acquirer_code": "HDFC",
                                    "bank_code": "HDFC",
                                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                                    "upi_bank_code": "HDFC",
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
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'HDFC';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db = result['mid'].iloc[0]
                tid_db = result['tid'].iloc[0]

                query = "select * from terminal_info where tid ='" + str(tid_db) + "';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db = result['device_serial'].iloc[0]

                actualDBValues = {"pmt_status": status_db,
                                  "pmt_state": state_db,
                                  "pmt_mode": payment_mode_db,
                                  "txn_amt": amount_db,
                                  "upi_txn_status": upi_status_db,
                                  "settle_status": settlement_status_db,
                                  "acquirer_code": acquirer_code_db,
                                  "bank_code": bank_code_db,
                                  "upi_txn_type": upi_txn_type_db,
                                  "upi_bank_code": upi_bank_code_db,
                                  "pmt_intent_status": payment_intent_status,
                                  "tid": tid_db,
                                  "mid": mid_db,
                                  "device_serial": device_serial_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")

                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


