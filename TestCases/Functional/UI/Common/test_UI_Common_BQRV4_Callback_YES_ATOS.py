import shutil
import sys
from time import sleep
import pytest
import random
from datetime import datetime
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
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner,  date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_058():
    """
    :Description: Verification of a BQRV4 Callback Success  via YES_ATOS
    :Sub Feature code: UI_Common_PM_BQRV4_Callback_Success_YES_ATOS_058
    :TC naming code description: 100->Payment Method, 102->BQR, 058-> TC58
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

        query = "select mid, tid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

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
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            login_page.perform_login(app_username, app_password)
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.check_home_page_logo()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            pid = result["provider_ref_id"].iloc[0]
            sid = result["transaction_secondary_id"].iloc[0]
            pid += sid
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn})
            response = APIProcessor.send_request(api_details)
            print("Response received:", response)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            posting_date = result['posting_date'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")
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
                expected_app_values = {"pmt_mode": "UPI", "pmt_status": "AUTHORIZED","txn_amt": str(amount),
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "customer_name": customer_name,"payer_name": payer_name,"settle_status": "SETTLED",
                                       "order_id": order_id,"msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,"settle_status": app_settlement_status,
                                     "payer_name": app_payer_name,"order_id": app_order_id,"auth_code": app_auth_code,
                                     "msg": app_payment_msg, "date": app_date_and_time}
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
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
                expected_api_values = {"pmt_status": "AUTHORIZED","txn_amt": amount,"pmt_mode": "UPI",
                                       "pmt_state": "SETTLED", "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "YES", "issuer_code": "YES","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code, "auth_code": auth_code,
                                       "date": date}
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
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

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "auth_code": auth_code_api, "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "UPI","pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED","acquirer_code" : "YES", "bank_name" : "Yes Bank",
                                      "payer_name": payer_name, "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "rrn" : str(rrn), "settle_status": "SETTLED","upi_pmt_status": "AUTHORIZED",
                                      "upi_txn_type": "PAY_BQR", "upi_mc_id": upi_mc_id, "upi_bank_code": "YES"}
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                payer_name_db = result["payer_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "payer_name": payer_name_db, "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,"upi_pmt_status": upi_status_db,
                                    "upi_txn_type": upi_txn_type_db, "upi_mc_id": upi_mc_id_db, "upi_bank_code": upi_bank_code_db}
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
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"UPI" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
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
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
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
def test_common_100_102_069():
    """
    :Description: Verification of a BQRV4 generation using API and performing two Callback Success transaction when auto refund disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_two_Callback_Success_YES_ATOS_069
    :TC naming code description: 100->Payment Method, 102->BQR, 069-> TC69
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select mid, tid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")

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
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug("Generating QR using BQR QR generate APi")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            pid = result["provider_ref_id"].iloc[0]
            sid = result["transaction_secondary_id"].iloc[0]
            pid += sid
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            logger.debug("Performing 1st Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 1st call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            posting_date = result['created_time'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]

            rrn_new = "RE"+str(order_id)
            logger.debug("Performing 2nd Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn_new})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 2nd call back : {response}")
            query = "select * from txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            auth_code_new = result['auth_code'].values[0]
            posting_date_new = result['created_time'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")

            #
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
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                expected_app_values = {"pmt_mode": "UPI", "pmt_status": "AUTHORIZED","txn_amt": str(amount),
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": order_id,"msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time,
                                       "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED", "txn_amt_new": str(amount),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new, "rrn_new": str(rrn_new),
                                       "customer_name_new": customer_name_new, "payer_name_new": payer_name_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)
                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,"settle_status": app_settlement_status,
                                     "payer_name": app_payer_name,"order_id": app_order_id,"auth_code": app_auth_code,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new, "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1], "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "customer_name_new": app_customer_name_new, "settle_status_new": app_settlement_status_new,
                                     "payer_name_new": app_payer_name_new, "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
                                     "msg_new": app_payment_msg_new, "date_new": app_date_and_time_new
                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
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
                date_new = date_time_converter.db_datetime(posting_date_new)
                expected_api_values = {"pmt_status": "AUTHORIZED","txn_amt": amount,"pmt_mode": "UPI",
                                       "pmt_state": "SETTLED", "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "YES", "issuer_code": "YES","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code, "auth_code": auth_code,
                                       "date": date,
                                       "pmt_status_new": "AUTHORIZED", "txn_amt_new": amount, "pmt_mode_new": "UPI",
                                       "pmt_state_new": "SETTLED", "rrn_new": str(rrn_new), "settle_status_new": "SETTLED",
                                       "acquirer_code_new": "YES", "issuer_code_new": "YES", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code, "auth_code_new": auth_code_new,
                                       "date_new": date_new
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
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
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id_new})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api_new = response["status"]
                amount_api_new = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "auth_code": auth_code_api, "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new, "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new, "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new, "org_code_new": orgCode_api_new,
                                     "auth_code_new": auth_code_api_new,
                                     "date_new": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "UPI","pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED","acquirer_code" : "YES", "bank_name" : "Yes Bank",
                                      "payer_name": payer_name, "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "rrn" : str(rrn), "settle_status": "SETTLED","upi_pmt_status": "AUTHORIZED",
                                      "upi_txn_type": "PAY_BQR", "upi_mc_id": upi_mc_id, "upi_bank_code": "YES",
                                      "txn_amt_new": amount, "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED",
                                      "pmt_state_new": "SETTLED", "acquirer_code_new": "YES", "bank_name_new": "Yes Bank",
                                      "payer_name_new": payer_name_new, "mid_new": mid, "tid_new": tid, "pmt_gateway_new": "ATOS",
                                      "rrn_new": str(rrn_new), "settle_status_new": "SETTLED", "upi_pmt_status_new": "AUTHORIZED",
                                      "upi_txn_type_new": "PAY_BQR", "upi_mc_id_new": upi_mc_id, "upi_bank_code_new": "YES"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                payer_name_db = result["payer_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = int(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                payer_name_db_new = result["payer_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "payer_name": payer_name_db, "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,"upi_pmt_status": upi_status_db,
                                    "upi_txn_type": upi_txn_type_db, "upi_mc_id": upi_mc_id_db, "upi_bank_code": upi_bank_code_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "payer_name_new": payer_name_db_new, "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new, "upi_pmt_status_new": upi_status_db_new,
                                    "upi_txn_type_new": upi_txn_type_db_new, "upi_mc_id_new": upi_mc_id_db_new,
                                    "upi_bank_code_new": upi_bank_code_db_new
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
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"UPI" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
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
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
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
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_071():
    """
    :Description: Verification of a BQRV4 Callback After QR Expiry Success transaction when auto refund disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_Callback_After_expired_Success_YES_ATOS_069
    :TC naming code description: 100->Payment Method, 102->BQR, 071-> TC71
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select mid, tid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")

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
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug("Generating QR using BQR QR generate APi")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            pid = result["provider_ref_id"].iloc[0]
            sid = result["transaction_secondary_id"].iloc[0]
            pid += sid
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            sleep(60)
            logger.debug("Performing 1st Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 1st call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            #auth_code = result['auth_code'].values[0]
            posting_date = result['created_time'].values[0]
            #customer_name = result['customer_name'].values[0]
            #payer_name = result['payer_name'].values[0]

            query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]

            query = "select * from txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            rrn_new = result['rr_number'].values[0]
            auth_code_new = result['auth_code'].values[0]
            posting_date_new = result['created_time'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")
            #
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
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED", "txn_amt_new": str(amount),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new, "rrn_new": str(rrn_new),
                                       "customer_name_new": customer_name_new, "payer_name_new": payer_name_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new,
                                     "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1],
                                     "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "customer_name_new": app_customer_name_new,
                                     "settle_status_new": app_settlement_status_new,
                                     "payer_name_new": app_payer_name_new,
                                     "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
                                     "msg_new": app_payment_msg_new, "date_new": app_date_and_time_new
                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
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
                date_new = date_time_converter.db_datetime(posting_date_new)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": amount,"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "YES", "issuer_code": "YES","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_new": "AUTHORIZED", "txn_amt_new": amount, "pmt_mode_new": "UPI",
                                       "pmt_state_new": "SETTLED", "rrn_new": str(rrn_new), "settle_status_new": "SETTLED",
                                       "acquirer_code_new": "YES", "issuer_code_new": "YES", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code, "auth_code_new": auth_code_new,
                                       "date_new": date_new
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
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

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id_new})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api_new = response["status"]
                amount_api_new = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new, "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new, "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new, "org_code_new": orgCode_api_new,
                                     "auth_code_new": auth_code_api_new,
                                     "date_new": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "YES",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "settle_status": "FAILED",
                                      "txn_amt_new": amount, "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED",
                                      "pmt_state_new": "SETTLED", "acquirer_code_new": "YES", "bank_name_new": "Yes Bank",
                                      "payer_name_new": payer_name_new, "mid_new": mid, "tid_new": tid, "pmt_gateway_new": "ATOS",
                                      "rrn_new": str(rrn_new), "settle_status_new": "SETTLED", "upi_pmt_status_new": "AUTHORIZED",
                                      "upi_txn_type_new": "PAY_BQR", "upi_mc_id_new": upi_mc_id, "upi_bank_code_new": "YES"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = int(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                payer_name_db_new = result["payer_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "payer_name_new": payer_name_db_new, "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new, "upi_pmt_status_new": upi_status_db_new,
                                    "upi_txn_type_new": upi_txn_type_db_new, "upi_mc_id_new": upi_mc_id_db_new,
                                    "upi_bank_code_new": upi_bank_code_db_new
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
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"UPI" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_new)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id_new,
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
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_072():
    """
    :Description: Verification of a BQRV4 generation using API and performing two Callback transaction when auto refund disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_two_Callback_After_expired_YES_ATOS
    :TC naming code description: 100->Payment Method, 102->BQR, 072-> TC72
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select mid, tid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")

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
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug("Generating QR using BQR QR generate APi")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            pid = result["provider_ref_id"].iloc[0]
            sid = result["transaction_secondary_id"].iloc[0]
            pid += sid
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            sleep(60)
            logger.debug("Performing 1st Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no":rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 1st call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            #auth_code = result['auth_code'].values[0]
            posting_date = result['created_time'].values[0]
            #customer_name = result['customer_name'].values[0]
            #payer_name = result['payer_name'].values[0]

            query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "'; "
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa = result['vpa'].values[0]
            upi_mc_id = result['id'].values[0]

            query = "select * from txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].iloc[0]
            rrn_new = result['rr_number'].values[0]
            auth_code_new = result['auth_code'].values[0]
            posting_date_new = result['created_time'].values[0]
            customer_name_new = result['customer_name'].values[0]
            payer_name_new = result['payer_name'].values[0]

            rrn_new_3 = "RE" + str(order_id)
            logger.debug("Performing 2nd Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid, "secondary_id": sid,
                                                                    "txn_amount": str(amount),
                                                                    "auth_code": auth_code, "ref_no": rrn_new_3})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 2nd call back : {response}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new_3 = result["id"].iloc[0]
            auth_code_new_3 = result['auth_code'].values[0]
            posting_date_new_3 = result['created_time'].values[0]
            customer_name_new_3 = result['customer_name'].values[0]
            payer_name_new_3 = result['payer_name'].values[0]

            logger.info(f"Execution is completed for the test case : {testcase_id}")
            #
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
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                date_and_time_new_3 = date_time_converter.to_app_format(posting_date_new_3)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED","txn_amt": str(amount),
                                       "settle_status": "FAILED","txn_id": txn_id,
                                       "order_id": order_id,"msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED", "txn_amt_new": str(amount),
                                       "settle_status_new": "SETTLED", "txn_id_new": txn_id_new, "rrn_new": str(rrn_new),
                                       "customer_name_new": customer_name_new, "payer_name_new": payer_name_new,
                                       "order_id_new": order_id, "msg_new": "PAYMENT SUCCESSFUL",
                                       "auth_code_new": auth_code_new, "date_new": date_and_time_new,
                                       "pmt_mode_new_3": "UPI", "pmt_status_new_3": "AUTHORIZED",
                                       "txn_amt_new_3": str(amount),
                                       "settle_status_new_3": "SETTLED", "txn_id_new_3": txn_id_new_3,
                                       "rrn_new_3": str(rrn_new_3),
                                       "customer_name_new_3": customer_name_new_3, "payer_name_new_3": payer_name_new_3,
                                       "order_id_new_3": order_id, "msg_new_3": "PAYMENT SUCCESSFUL",
                                       "auth_code_new_3": auth_code_new_3, "date_new_3": date_and_time_new_3
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                app_auth_code_new = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new}, {app_auth_code_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_customer_name_new = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new}, {app_customer_name_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payer_name_new = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_new}, {app_payer_name_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_3)

                payment_status_new_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_3}, {payment_status_new_3}")
                app_auth_code_new_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_3}, {app_auth_code_new_3}")
                payment_mode_new_3 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_3}, {payment_mode_new_3}")
                app_txn_id_new_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_txn_id_new_3}")
                app_amount_new_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_3}, {app_amount_new_3}")
                app_date_and_time_new_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_3}, {app_date_and_time_new_3}")
                app_customer_name_new_3 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_new_3}, {app_customer_name_new_3}")
                app_settlement_status_new_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_3}, {app_settlement_status_new_3}")
                app_payer_name_new_3 = txn_history_page.fetch_payer_name_text()
                logger.info(
                    f"Fetching txn payer name from txn history for the txn : {txn_id_new_3}, {app_payer_name_new_3}")
                app_payment_msg_new_3 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_3}, {app_payment_msg_new_3}")
                app_order_id_new_3 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_3}, {app_order_id_new_3}")
                app_rrn_new_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_rrn_new_3}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_new": payment_mode_new,
                                     "pmt_status_new": payment_status_new.split(':')[1],
                                     "txn_amt_new": app_amount_new.split(' ')[1],
                                     "txn_id_new": app_txn_id_new, "rrn_new": str(app_rrn_new),
                                     "customer_name_new": app_customer_name_new,
                                     "settle_status_new": app_settlement_status_new,
                                     "payer_name_new": app_payer_name_new,
                                     "order_id_new": app_order_id_new, "auth_code_new": app_auth_code_new,
                                     "msg_new": app_payment_msg_new, "date_new": app_date_and_time_new,
                                     "pmt_mode_new_3": payment_mode_new_3,
                                     "pmt_status_new_3": payment_status_new_3.split(':')[1],
                                     "txn_amt_new_3": app_amount_new_3.split(' ')[1],
                                     "txn_id_new_3": app_txn_id_new_3, "rrn_new_3": str(app_rrn_new_3),
                                     "customer_name_new_3": app_customer_name_new_3,
                                     "settle_status_new_3": app_settlement_status_new_3,
                                     "payer_name_new_3": app_payer_name_new_3,
                                     "order_id_new_3": app_order_id_new_3, "auth_code_new_3": app_auth_code_new_3,
                                     "msg_new_3": app_payment_msg_new_3, "date_new_3": app_date_and_time_new_3
                                     }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
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
                date_new = date_time_converter.db_datetime(posting_date_new)
                date_new_3 = date_time_converter.db_datetime(posting_date_new_3)
                expected_api_values = {"pmt_status": "EXPIRED","txn_amt": amount,"pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED","settle_status": "FAILED",
                                       "acquirer_code": "YES", "issuer_code": "YES","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date,
                                       "pmt_status_new": "AUTHORIZED", "txn_amt_new": amount, "pmt_mode_new": "UPI",
                                       "pmt_state_new": "SETTLED", "rrn_new": str(rrn_new), "settle_status_new": "SETTLED",
                                       "acquirer_code_new": "YES", "issuer_code_new": "YES", "txn_type_new": "CHARGE",
                                       "mid_new": mid, "tid_new": tid, "org_code_new": org_code, "auth_code_new": auth_code_new,
                                       "date_new": date_new,
                                       "pmt_status_new_3": "AUTHORIZED", "txn_amt_new_3": amount,
                                       "pmt_mode_new_3": "UPI",
                                       "pmt_state_new_3": "SETTLED", "rrn_new_3": str(rrn_new_3),
                                       "settle_status_new_3": "SETTLED",
                                       "acquirer_code_new_3": "YES", "issuer_code_new_3": "YES",
                                       "txn_type_new_3": "CHARGE",
                                       "mid_new_3": mid, "tid_new_3": tid, "org_code_new_3": org_code,
                                       "auth_code_new_3": auth_code_new_3,
                                       "date_new_3": date_new_3
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
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

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id_new})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api_new = response["status"]
                amount_api_new = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                orgCode_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                auth_code_api_new = response["authCode"]
                date_api_new = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "app_password": app_password,
                                                                        "txnId": txn_id_new_3})
                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api_new_3 = response["status"]
                amount_api_new_3 = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api_new_3 = response["paymentMode"]
                state_api_new_3 = response["states"][0]
                rrn_api_new_3 = response["rrNumber"]
                settlement_status_api_new_3 = response["settlementStatus"]
                issuer_code_api_new_3 = response["issuerCode"]
                acquirer_code_api_new_3 = response["acquirerCode"]
                orgCode_api_new_3 = response["orgCode"]
                mid_api_new_3 = response["mid"]
                tid_api_new_3 = response["tid"]
                txn_type_api_new_3 = response["txnType"]
                auth_code_api_new_3 = response["authCode"]
                date_api_new_3 = response["createdTime"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_new": status_api_new, "txn_amt_new": amount_api_new, "pmt_mode_new": payment_mode_api_new,
                                     "pmt_state_new": state_api_new, "rrn_new": str(rrn_api_new),
                                     "settle_status_new": settlement_status_api_new,
                                     "acquirer_code_new": acquirer_code_api_new, "issuer_code_new": issuer_code_api_new, "mid_new": mid_api_new,
                                     "txn_type_new": txn_type_api_new, "tid_new": tid_api_new, "org_code_new": orgCode_api_new,
                                     "auth_code_new": auth_code_api_new,
                                     "date_new": date_time_converter.from_api_to_datetime_format(date_api_new),
                                     "pmt_status_new_3": status_api_new_3, "txn_amt_new_3": amount_api_new_3,
                                     "pmt_mode_new_3": payment_mode_api_new_3,
                                     "pmt_state_new_3": state_api_new_3, "rrn_new_3": str(rrn_api_new_3),
                                     "settle_status_new_3": settlement_status_api_new_3,
                                     "acquirer_code_new_3": acquirer_code_api_new_3,
                                     "issuer_code_new_3": issuer_code_api_new_3, "mid_new_3": mid_api_new_3,
                                     "txn_type_new_3": txn_type_api_new_3, "tid_new_3": tid_api_new_3,
                                     "org_code_new_3": orgCode_api_new_3,
                                     "auth_code_new_3": auth_code_api_new_3,
                                     "date_new_3": date_time_converter.from_api_to_datetime_format(date_api_new_3)
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
                expected_db_values = {"txn_amt": amount,"pmt_mode": "BHARATQR","pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED","acquirer_code" : "YES",
                                      "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "settle_status": "FAILED",
                                      "txn_amt_new": amount, "pmt_mode_new": "UPI", "pmt_status_new": "AUTHORIZED",
                                      "pmt_state_new": "SETTLED", "acquirer_code_new": "YES", "bank_name_new": "Yes Bank",
                                      "payer_name_new": payer_name_new, "mid_new": mid, "tid_new": tid, "pmt_gateway_new": "ATOS",
                                      "rrn_new": str(rrn_new), "settle_status_new": "SETTLED", "upi_pmt_status_new": "AUTHORIZED",
                                      "upi_txn_type_new": "PAY_BQR", "upi_mc_id_new": upi_mc_id, "upi_bank_code_new": "YES",
                                      "txn_amt_new_3": amount, "pmt_mode_new_3": "UPI",
                                      "pmt_status_new_3": "AUTHORIZED",
                                      "pmt_state_new_3": "SETTLED", "acquirer_code_new_3": "YES",
                                      "bank_name_new_3": "Yes Bank",
                                      "payer_name_new_3": payer_name_new_3, "mid_new_3": mid, "tid_new_3": tid,
                                      "pmt_gateway_new_3": "ATOS",
                                      "rrn_new_3": str(rrn_new_3), "settle_status_new_3": "SETTLED",
                                      "upi_pmt_status_new_3": "AUTHORIZED",
                                      "upi_txn_type_new_3": "PAY_BQR", "upi_mc_id_new_3": upi_mc_id,
                                      "upi_bank_code_new_3": "YES"
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = int(result["amount"].iloc[0])
                payment_mode_db_new = result["payment_mode"].iloc[0]
                payment_status_db_new = result["status"].iloc[0]
                payment_state_db_new = result["state"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_name_db_new = result["bank_name"].iloc[0]
                payer_name_db_new = result["payer_name"].iloc[0]
                mid_db_new = result["mid"].iloc[0]
                tid_db_new = result["tid"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                rr_number_db_new = result["rr_number"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new_3 = int(result["amount"].iloc[0])
                payment_mode_db_new_3 = result["payment_mode"].iloc[0]
                payment_status_db_new_3 = result["status"].iloc[0]
                payment_state_db_new_3 = result["state"].iloc[0]
                acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
                bank_name_db_new_3 = result["bank_name"].iloc[0]
                payer_name_db_new_3 = result["payer_name"].iloc[0]
                mid_db_new_3 = result["mid"].iloc[0]
                tid_db_new_3 = result["tid"].iloc[0]
                payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
                rr_number_db_new_3 = result["rr_number"].iloc[0]
                settlement_status_db_new_3 = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new_3 = result["status"].iloc[0]
                upi_txn_type_db_new_3 = result["txn_type"].iloc[0]
                upi_mc_id_db_new_3 = result["upi_mc_id"].iloc[0]
                upi_bank_code_db_new_3 = result["bank_code"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "txn_amt_new": amount_db_new, "pmt_mode_new": payment_mode_db_new,
                                    "pmt_status_new": payment_status_db_new, "pmt_state_new": payment_state_db_new,
                                    "acquirer_code_new": acquirer_code_db_new, "bank_name_new": bank_name_db_new,
                                    "payer_name_new": payer_name_db_new, "mid_new": mid_db_new, "tid_new": tid_db_new,
                                    "pmt_gateway_new": payment_gateway_db_new, "rrn_new": rr_number_db_new,
                                    "settle_status_new": settlement_status_db_new, "upi_pmt_status_new": upi_status_db_new,
                                    "upi_txn_type_new": upi_txn_type_db_new, "upi_mc_id_new": upi_mc_id_db_new,
                                    "upi_bank_code_new": upi_bank_code_db_new,
                                    "txn_amt_new_3": amount_db_new_3, "pmt_mode_new_3": payment_mode_db_new_3,
                                    "pmt_status_new_3": payment_status_db_new_3,
                                    "pmt_state_new_3": payment_state_db_new_3,
                                    "acquirer_code_new_3": acquirer_code_db_new_3,
                                    "bank_name_new_3": bank_name_db_new_3,
                                    "payer_name_new_3": payer_name_db_new_3, "mid_new_3": mid_db_new_3,
                                    "tid_new_3": tid_db_new_3,
                                    "pmt_gateway_new_3": payment_gateway_db_new_3, "rrn_new_3": rr_number_db_new_3,
                                    "settle_status_new_3": settlement_status_db_new_3,
                                    "upi_pmt_status_new_3": upi_status_db_new_3,
                                    "upi_txn_type_new_3": upi_txn_type_db_new_3, "upi_mc_id_new_3": upi_mc_id_db_new_3,
                                    "upi_bank_code_new_3": upi_bank_code_db_new_3
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
            try:
                logger.info("Starting Portal Validation for the test case")
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"UPI" , "Payment amount":str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                logger.info(f"Logging in Portal using username : {portal_username}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(ui_driver)
                homePagePortal.wait_for_home_page_load()
                homePagePortal.search_merchant_name(org_code)
                logger.info(f"Switching to merchant : {org_code}")
                homePagePortal.click_switch_button(org_code)
                homePagePortal.click_transaction_search_menu()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1])}

                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
                logger.info("Portal Validation Completed successfully for test case")
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_new)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id_new,
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
        # ----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.uiVal
def test_common_100_102_064():
    """
    :Description: Verification of a BQRV4 UPI amount mismatch txn when Auto refund is disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_UPI_amt_missmatch_callback_YES_ATOS
    :TC naming code description: 100->Payment Method, 102->BQR, 064-> TC64
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from upi_merchant_config where bank_code = 'YES' AND status = 'ACTIVE' AND org_code = " \
                "'" + str(org_code) + "'; "
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
        upi_mc_id = result['id'].values[0]
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Fetching upi mc id and pg merch id from database for "
                     f"current merchant:{upi_mc_id}, {pg_merchant_id}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = 46
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug("Generating QR using BQR QR generate APi")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '" \
                    ""+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            pid = result["provider_ref_id"].iloc[0]
            sid = result["transaction_secondary_id"].iloc[0]
            pid += sid
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]
            customer_vpa = str(order_id)+"@upi"
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            logger.debug("Performing 1st Callback")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount),
                                                                    "customer_vpa": customer_vpa,
                                                                    "auth_code": auth_code, "ref_no":rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for 1st call back : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            posting_date = result['created_time'].values[0]
            external_ref = result['external_ref'].values[0]

            query = ("select * from invalid_pg_request where request_id ='" + pid + "';")
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_upg = result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + txn_id_upg + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            posting_date_upg = result['created_time'].values[0]
            rrn_upg = result['rr_number'].iloc[0]
            external_ref_upg = result['external_ref'].values[0]
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
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_2 = date_time_converter.to_app_format(posting_date_upg)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "STATUS:PENDING",
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "txn_amt": str(amount),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT PENDING",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "STATUS:UPG_AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_upg,
                    "txn_amt_2": str(amount),
                    "rrn_2": str(rrn_upg),
                    "order_id_2": external_ref_upg,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
                }
                logger.debug(f"actualAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()
                homePage.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_upg)

                app_payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_upg}, {app_payment_status_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_upg}, {app_date_and_time_new}")
                app_payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_upg}, {app_payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_upg}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_upg}, {app_amount_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_upg}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_upg}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_upg}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_upg}, {app_rrn_new}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_status": app_payment_status,
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_status_2": app_payment_status_new,
                    "pmt_mode_2": app_payment_mode_new,
                    "txn_id_2": app_txn_id_new,
                    "txn_amt_2": str(app_amount_new).split(' ')[1],
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "payment_msg_2": app_payment_msg_new,
                    "rrn_2": app_rrn_new,
                    "date_2": app_date_and_time_new
                }
                logger.debug(f"actualAppValues: {actual_app_values}")

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
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(posting_date)
                date_2 = date_time_converter.db_datetime(posting_date_upg)
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": float(amount),"pmt_mode": "BHARATQR",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "YES", "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "txn_amt_2": float(amount), "pmt_mode_2": "UPI",
                    "pmt_state_2": "UPG_AUTHORIZED", "rrn_2": str(rrn_upg),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "issuer_code_2": "YES",
                    "txn_type_2": 'CHARGE', "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_upg][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")

                status_api_new = response["status"]
                amount_api_new = float(response["amount"])
                payment_mode_api_new = response["paymentMode"]
                state_api_new = response["states"][0]
                rrn_api_new = response["rrNumber"]
                settlement_status_api_new = response["settlementStatus"]
                issuer_code_api_new = response["issuerCode"]
                acquirer_code_api_new = response["acquirerCode"]
                org_code_api_new = response["orgCode"]
                mid_api_new = response["mid"]
                tid_api_new = response["tid"]
                txn_type_api_new = response["txnType"]
                date_api_new = response["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "txn_type_2": txn_type_api_new, "mid_2": mid_api_new, "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "rrn_2": rrn_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new)
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "PENDING",
                    "pmt_state": "PENDING", "acquirer_code": "YES",
                    "mid": mid, "tid": tid, "pmt_gateway": "ATOS",
                    "settle_status": "PENDING",
                    "bqr_pmt_state": "PENDING",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "UPG_AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_code_2": "YES",
                    "payment_gateway_2": "ATOS",
                    "upi_txn_type_2": "UNKNOWN",
                    "upi_bank_code_2": "YES",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn_upg),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = int(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = int(
                    result["txn_amount"].iloc[0])
                bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_org_code_db = result['org_code'].values[0]


                query = "select * from txn where id='" + txn_id_upg + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_new = result["status"].iloc[0]
                payment_mode_db_new = result["payment_mode"].iloc[0]
                amount_db_new = float(result["amount"].iloc[0])
                state_db_new = result["state"].iloc[0]
                payment_gateway_db_new = result["payment_gateway"].iloc[0]
                acquirer_code_db_new = result["acquirer_code"].iloc[0]
                bank_code_db_new = result["bank_code"].iloc[0]
                settlement_status_db_new = result["settlement_status"].iloc[0]
                tid_db_new = result['tid'].values[0]
                mid_db_new = result['mid'].values[0]

                query = "select * from upi_txn where txn_id='" + txn_id_upg + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_new = result["status"].iloc[0]
                upi_txn_type_db_new = result["txn_type"].iloc[0]
                upi_bank_code_db_new = result["bank_code"].iloc[0]
                upi_mc_id_db_new = result["upi_mc_id"].iloc[0]

                query = ("select * from invalid_pg_request where txn_id ='" + txn_id_upg + "';")
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_mid = result["mid"].iloc[0]
                ipr_tid = result["tid"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_vpa = result["vpa"].iloc[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {
                    "txn_amt": amount_db, "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "pmt_status_2": status_db_new,
                    "pmt_state_2": state_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "txn_amt_2": amount_db_new,
                    "upi_txn_status_2": upi_status_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_code_2": bank_code_db_new,
                    "payment_gateway_2": payment_gateway_db_new,
                    "upi_txn_type_2": upi_txn_type_db_new,
                    "upi_bank_code_2": upi_bank_code_db_new,
                    "upi_mc_id_2": upi_mc_id_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
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
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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