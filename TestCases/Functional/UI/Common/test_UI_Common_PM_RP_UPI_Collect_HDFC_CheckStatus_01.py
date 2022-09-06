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
def test_common_100_103_004():
    """
    Sub Feature Code: UI_Common_PM_RP_upi collect_Success_Via_upi_Collect_Checkstatus_HDFC
    Sub Feature Description: Verification of a Remote Pay successful upi collect txn via HDFC using check status
    TC naming code description:
    100: Payment Method
    103: RemotePay
    004: TC_004
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        logger.info("Execution Started for the test case : test_common_100_103_004")
        app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_004')
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_004')
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

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
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

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
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
            remotePayUpiCollectTxn.clickOnRemotePayCancelUPI()
            remotePayUpiCollectTxn.clickOnRemotePayProceed()
            logger.info("UPI Collect txn is completed.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            txn_id = result['id'].values[0]
            status = result['status'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            settlement_status = result['settlement_status'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]
            posting_date = result['posting_date'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]

            logger.debug(
                f"Fetching txn_id, rrn and status from the txn table : txn_id : {txn_id}, status : {status}")

            query = "select id from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            auth_code = result['auth_code'].values[0]

            # ------------------------------------------------------------------------------------------------
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
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "auth_code": auth_code,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")

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
                    "auth_code": app_auth_code,
                    "date": app_date_and_time
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
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date
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
                auth_code_api = response["authCode"]
                date_api = response["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                expected_db_values = {
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
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
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
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
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid,
                    "tid": tid
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
                # --------------------------------------------------------------------------------------------
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username,
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
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
                    "txn_amt": portal_amount, "username": portal_username}
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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------

            # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                                   'time': txn_time,
                                   'AUTH CODE': auth_code}
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
def test_common_100_103_005():
    """
    Sub Feature Code: UI_Common_PM_RP_upi_collect_failed_Via_Pure_upicollect_Checkstatus_HDFC
    Sub Feature Description: Verification of a Remote Pay failed upi collect txn via HDFC using check status
    TC naming code description:
    100: Payment Method
    103: RemotePay
    005: TC_005
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_005')
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

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            amount = 111
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')
            ui_driver.get(paymentLinkUrl)
            remotePayUpiCollectTxn = remotePayTxnPage(ui_driver)
            remotePayUpiCollectTxn.clickOnRemotePayUPI()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="),
                'cyan'))
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

            ReportProcessor.capture_ss_when_app_val_exe_failed()  # If In the execution or try block app driver is not initialized then we can remove this line
            ReportProcessor.capture_ss_when_portal_val_exe_failed()  # If In the execution or try block portal driver is not initialized then we can remove this line
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
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started APP validation for the test case : {testcase_id}")
                expectedAppValues = {"Payment mode": "UPI", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
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
                logger.info("Api Validation Started for the test case : test_common_100_103_005")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": Txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
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
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                logger.info("DB Validation Started for the test case : test_common_100_103_005")
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI",
                                    "Payment amount": amount, "Transaction Type": "COLLECT"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select txn_type from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result1 = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result1}")
                txnType_db1 = result1["txn_type"].iloc[0]
                # payment_mode_db = result["payment_mode"].iloc[0]
                # amount_db1 = int(result["amount"].iloc[0])
                # state_db = result["state"].iloc[0]

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount_db,
                                  "Transaction Type": txnType_db1}
                # "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
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

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                logger.info("Portal Validation Started for the test case : test_common_100_103_005")
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")

                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
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
def test_common_100_103_032():
    """
    Sub Feature Code: UI_Common_PM_RP_upi_Collect_Pending_HDFC
    Sub Feature Description: Verification of a check status for upi collect pending txn via HDFC
    TC naming code description:
    100: Payment Method
    101: RemotePay
    032: TC032
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

        query = "update remotepay_setting set setting_value= '6' where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")
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

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")
            
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
                                       "pmt_status_original": "PENDING",
                                       "txn_amount_original": str(amount),
                                       "settle_status_original": "PENDING",
                                       "txn_id_original": original_txn_id,
                                       "customer_name_original": original_customer_name,
                                       "payer_name_original": original_payer_name,
                                       "order_id_original": order_id,
                                       "payment_msg_original": "PAYMENT PENDING",
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
                # app_rrn = transactions_history_page.fetch_RRN_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
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
                expected_api_values = {"pmt_status": "PENDING",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "PENDING",
                                       "settlement_status": "PENDING",
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
                                     "date_original": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "settlement_status": "PENDING",
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
                    "pmt_mode": original_payment_mode,
                    "txn_amt": amount,
                    "settlement_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "intent_status": intent_status
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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_089():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_Collect_Amount_Mismatch_HDFC
    Sub Feature Description: Verification of a Remote Pay upi collect for amount mismatch.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    048: TC048
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_gateway='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update remotepay_setting set setting_value= '1' where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # ---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
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
            logger.debug(f"Query to fetch txn timeout from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"Waiting for txn to timeout for {org_code} is {org_setting_value} min")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"Waiting for txn to timeout for Ezetap org is : {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"timeout time is : {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"timeout for Ezetap org is: {defaultValue} min.")
                time.sleep(3 + (defaultValue * 60))

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]
            logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")
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

            query = "select * from payment_intent where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

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
                                       "customer_name_original": original_customer_name,
                                       # "payer_name_original": original_payer_name,
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
                # app_rrn = transactions_history_page.fetch_RRN_text()
                # logger.info(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {original_txn_id}, {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {original_txn_id}, {app_customer_name}")
                # app_payer_name = transactions_history_page.fetch_payer_name_text()
                # logger.info(
                #     f"Fetching txn payer name from txn history for the txn : {original_txn_id}, {app_payer_name}")
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
                                     "customer_name_original": app_customer_name,
                                     # "payer_name_original": app_payer_name,
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

                api_details = DBProcessor.get_api_details('paymentStatus',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": original_txn_id})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug("Response from API DETAILS is :", api_details)
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
                                     "date_original": date_time_converter.from_api_to_datetime_format(date_api)
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
                    # "acquirer_code": "HDFC",
                    # "bank_code": "HDFC",
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
                    "pmt_mode": original_payment_mode,
                    "txn_amt": amount,
                    "settlement_status": original_settlement_status,
                    # "acquirer_code": original_acquirer_code,
                    # "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type_db": upi_txn_type_db,
                    "upi_bank_code_db": upi_bank_code_db,
                    "upi_mc_id_db": upi_mc_id_db,
                    "intent_status": intent_status
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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)