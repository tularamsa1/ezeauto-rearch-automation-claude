import random
import shutil
import string
import sys
import pytest
from termcolor import colored
from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_val
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_066():
    """
    :Description: Verification of  a BQRV4 UPG txn when Auto refund is enabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_UPG_AUTOREFUND_ENABLED_YES_ATOS_75
    :TC naming code description: 100->Payment Method
                                102->BQR
                                075-> TC75
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

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
        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = "select mid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        logger.debug(f"Query to set values as inactive to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where mid = '"+ mid+"' and org_code='" + org_code + "' and bank_code='YES' "
        logger.debug(f"Query to set values as active to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='YES' "
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
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]
            query = "select vpa, pgMerchantId from upi_merchant_config where org_code='" + org_code + "' and bank_code='YES' "
            result = DBProcessor.getValueFromDB(query)
            vpa = result["vpa"].iloc[0]
            pgMerchantId = result["pgMerchantId"].iloc[0]
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))+"@upi"
            print("Merchant vpa and Customer vpa for this merchant is :", vpa, customer_vpa)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {vpa}, merchant pan")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": upg_txn_id, "txn_amount": str(amount),
                                                                    "merchant_vpa": vpa, "customer_vpa": customer_vpa,
                                                                    "auth_code": auth_code, "ref_no": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            q_result = DBProcessor.getValueFromDB(query)
            print(q_result)
            txn_id = q_result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]
            posting_date = result['posting_date'].values[0]
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'YES'"
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
                date_and_time = date_time_val.date_and_time_val_against_app(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": str(amount),
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
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
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                date = date_time_val.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "UPG_REFUND_PENDING",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUND_PENDING", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

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

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_val.date_and_time_val_against_api(date_api)
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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "YES",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pgMerchantId
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

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

                query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
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
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
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
                expectedPortalValues = {"Payment Status": "Upg Refund Pending", "Payment mode": "BHARATQR",
                                        "Payment amount": str(amount)}
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
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(upg_txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1])}

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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")

        api_details = DBProcessor.get_api_details('UPGRefund', request_body={"username": portal_username,
                                                                                 "password": portal_password,
                                                                                 "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for reverting preconditions AutoRefund is : {response}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where mid = '" + mid + "' and org_code='" + org_code + "' and bank_code='YES'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_067():
    """
    :Description: Verification of  a BQRV4 UPG txn when Auto refund is disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_UPG_AUTOREFUND_DISABLED_YES_ATOS_76
    :TC naming code description: 100->Payment Method
                                102->BQR
                                076-> TC76
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

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
        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = "select mid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        logger.debug(f"Query to set values as inactive to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where mid = '"+ mid+"' and org_code='" + org_code + "' and bank_code='YES' "
        logger.debug(f"Query to set values as active to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='YES' "
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
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]
            query = "select vpa, pgMerchantId from upi_merchant_config where org_code='" + org_code + "' and bank_code='YES' "
            result = DBProcessor.getValueFromDB(query)
            vpa = result["vpa"].iloc[0]
            pgMerchantId = result["pgMerchantId"].iloc[0]
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9)) + "@upi"
            print("Merchant vpa and Customer vpa for this merchant is :", vpa, customer_vpa)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {vpa}, merchant pan")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": upg_txn_id, "txn_amount": str(amount),
                                                                    "merchant_vpa": vpa, "customer_vpa": customer_vpa,
                                                                    "auth_code": auth_code, "ref_no": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            q_result = DBProcessor.getValueFromDB(query)
            print(q_result)
            txn_id = q_result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]
            posting_date = result['posting_date'].values[0]
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'YES'"
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
                date_and_time = date_time_val.date_and_time_val_against_app(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": str(amount),
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
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
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                date = date_time_val.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

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

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_val.date_and_time_val_against_api(date_api)
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "YES",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pgMerchantId
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

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

                query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
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
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
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
                expectedPortalValues = {"Payment Status": "Upg Refund Pending", "Payment mode": "BHARATQR",
                                        "Payment amount": str(amount)}
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
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(upg_txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1])}

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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")

        api_details = DBProcessor.get_api_details('UPGRefund', request_body={"username": portal_username,
                                                                                 "password": portal_password,
                                                                                 "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for reverting preconditions AutoRefund is : {response}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where mid = '" + mid + "' and org_code='" + org_code + "' and bank_code='YES'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_068():
    """
    :Description: Verification of  a BQRV4 UPG Refund txn when Auto refund is disabled via YES_ATOS
    :Sub Feature code: UI_Common_PM_BQRV4_UPG_Refund_YES_ATOS_43
    :TC naming code description: 100->Payment Method
                                102->BQR
                                043-> TC43
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
       # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

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

        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select mid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        logger.debug(f"Query to set values as inactive to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where mid = '"+ mid+"' and org_code='" + org_code + "' and bank_code='YES' "
        logger.debug(f"Query to set values as active to db is : {query}")
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

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='YES' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            print("Merhant id for this merchant is :", merchant_id)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackYES',
                                                      request_body={"primary_id": upg_txn_id, "txn_amount": str(amount), "mpan": merchant_id,
                                                                    "auth_code": auth_code, "ref_no": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select id from txn where org_code='"+org_code+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            upg_txn_id = result["id"].iloc[0]
            logger.debug(f"Transaction id of upg txn is : {upg_txn_id}")

            logger.info("Opening Portal to perform refund of the transaction")
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            loginPagePortal = PortalLoginPage(ui_driver)
            logger.info(f"Logging in Portal using username : {portal_username}")
            loginPagePortal.perform_login_to_portal(portal_username, portal_password)
            homePagePortal = PortalHomePage(ui_driver)
            homePagePortal.search_merchant_name(org_code)
            logger.info(f"Switching to merchant : {org_code}")
            homePagePortal.click_switch_button(org_code)
            homePagePortal.click_transaction_search_menu()
            ui_driver.implicitly_wait(10)
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            homePagePortal.click_on_transaction_details_based_on_transaction_id(upg_txn_id)
            logger.debug("Clicking on refund button")
            homePagePortal.click_on_refund_button()
            homePagePortal.perform_refund_of_txn(amount)
            logger.info("Performing Page refresh after refund is performed")
            query = "select id from txn where org_code='" + org_code + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")

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
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment Status": "STATUS:UPG_REFUNDED", "Payment mode": "BHARAT QR", "Payment Txn ID": txn_id_refunded, "Payment Amt": str(amount), "Payment Status Original": "STATUS:UPG_AUTH_REFUNDED", "Payment mode Original": "BHARAT QR", "Payment Txn ID Original": upg_txn_id, "Payment Amt Original": str(amount)}
                loginPage = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_txn_id(txn_id_refunded)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
                transactionsHistoryPage.click_back_Btn_transaction_details()
                transactionsHistoryPage.click_on_transaction_by_txn_id(upg_txn_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")

                actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt), "Payment Status Original": app_payment_status_original, "Payment mode Original": app_payment_mode_original, "Payment Txn ID Original": app_txn_id_original, "Payment Amt Original": str(app_payment_amt_original)}

                logger.debug(f"actualAppValues: {actualAppValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
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
                expectedAPIValues = {"Payment Status":"UPG_REFUNDED","Amount": amount, "Payment Mode": "BHARATQR","Txn Type":"REFUND", "Acquirer Code":"YES", "Payment Status Original":"UPG_AUTH_REFUNDED","Amount Original": amount, "Payment Mode Original": "BHARATQR"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username, "password": app_password,
                                                                        "txnId": txn_id_refunded})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                txn_type_api = response["txnType"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username, "password": app_password,
                                                                        "txnId": upg_txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api_orginal = response["status"]
                amount_api_original = response["amount"]
                payment_mode_api_orginal = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api_orginal} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api_original} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api_orginal} ")
                #
                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Txn Type":txn_type_api, "Acquirer Code":accuirer_code_api, "Payment Status Original":status_api_orginal,"Amount Original": amount_api_original, "Payment Mode Original": payment_mode_api_orginal}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
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
                expectedDBValues = {"Payment Status": "UPG_REFUNDED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Txn Type":"REFUND","Acquirer Code":"YES", "Payment Status Original":"UPG_AUTH_REFUNDED","Amount Original": "{:.2f}".format(amount), "Payment Mode Original": "BHARATQR"}
                #
                query = "select status,amount,payment_mode,external_ref,txn_type,acquirer_code from txn where id='" + txn_id_refunded + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode,txn_type,acquirer_code and external reference from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                print(result)
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                txn_type_db = result["txn_type"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                query = "select status,amount,payment_mode,external_ref from txn where id='" + upg_txn_id + "'"
                logger.debug(f"DB query to fetch status, amount, payment mode and external reference of orginal txn from DB : {query}")
                print("Query:", query)
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                print(result)
                status_db_original = result["status"].iloc[0]
                payment_mode_db_original = result["payment_mode"].iloc[0]
                amount_db_original = "{:.2f}".format(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "Txn Type":txn_type_db, "Acquirer Code":accuirer_code_db,"Payment Status Original":status_db_original,"Amount Original": amount_db_original, "Payment Mode Original": payment_mode_db_original}
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
                expectedPortalValues = {"Payment Status": "Upg Refunded", "Payment mode":"BHARATQR" , "Payment amount":str(amount), "Payment Status Original":"Upg Auth Refunded","Amount Original": str(amount), "Payment Mode Original": "BHARATQR"}
                #
                ui_driver.refresh()
                transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id_refunded)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(upg_txn_id)
                portal_status_original = portalValuesDict['Status']
                portal_txn_type_original = portalValuesDict['Type']
                portal_amt_original = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status_original} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type_original} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt_original} ")
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Payment Status Original":portal_status_original,"Amount Original": str(portal_amt_original.split('.')[1]), "Payment Mode Original": portal_txn_type_original}

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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        api_details = DBProcessor.get_api_details('UPGRefund', request_body={"username": portal_username,
                                                                             "password": portal_password,
                                                                             "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for reverting preconditions AutoRefund is : {response}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where mid = '" + mid + "' and org_code='" + org_code + "' and bank_code='YES'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_069():
    """
    :Description: Verification of  a BQRV4 UPG txn when Auto refund is disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_UPG_AUTOREFUND_DISABLED_YES_ATOS_76
    :TC naming code description: 100->Payment Method
                                102->BQR
                                076-> TC76
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

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
        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        query = "select mid from terminal_info where org_code='" + org_code + "' and acquirer_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        logger.debug(f"Fetching mid from database for current merchant:{mid}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        logger.debug(f"Query to set values as inactive to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where mid = '"+ mid+"' and org_code='" + org_code + "' and bank_code='YES' "
        logger.debug(f"Query to set values as active to db is : {query}")
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        query = "update upi_merchant_config set status = 'INACTIVE' where org_code='" +org_code+ "' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update upi_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='YES' "
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
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]
            query = "select vpa, pgMerchantId from upi_merchant_config where org_code='" + org_code + "' and bank_code='YES' "
            result = DBProcessor.getValueFromDB(query)
            vpa = result["vpa"].iloc[0]
            pgMerchantId = result["pgMerchantId"].iloc[0]
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9)) + "@upi"
            print("Merchant vpa and Customer vpa for this merchant is :", vpa, customer_vpa)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {vpa}, merchant pan")
            api_details = DBProcessor.get_api_details('callbackUpiYES',
                                                      request_body={"primary_id": upg_txn_id, "txn_amount": str(amount),
                                                                    "merchant_vpa": vpa, "customer_vpa": customer_vpa,
                                                                    "auth_code": auth_code, "ref_no": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            q_result = DBProcessor.getValueFromDB(query)
            print(q_result)
            txn_id = q_result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            org_code_txn = result['org_code'].values[0]
            txn_type = result['txn_type'].values[0]
            posting_date = result['posting_date'].values[0]
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'YES'"
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
                date_and_time = date_time_val.date_and_time_val_against_app(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": str(amount),
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
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
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                date = date_time_val.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

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

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_val.date_and_time_val_against_api(date_api)
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "payment_gateway": "ATOS",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "YES",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pgMerchantId
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

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

                query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
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
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
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
                expectedPortalValues = {"Payment Status": "Upg Refund Pending", "Payment mode": "BHARATQR",
                                        "Payment amount": str(amount)}
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
                portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(upg_txn_id)
                portal_status = portalValuesDict['Status']
                portal_txn_type = portalValuesDict['Type']
                portal_amt = portalValuesDict['Total Amount']
                logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                print("Status of txn:", portal_status)
                print("Portal txn type ", portal_txn_type)
                #
                actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type,
                                      "Payment amount": str(portal_amt.split('.')[1])}

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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))

        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")

        api_details = DBProcessor.get_api_details('UPGRefund', request_body={"username": portal_username,
                                                                                 "password": portal_password,
                                                                                 "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for reverting preconditions AutoRefund is : {response}")
        query = "update bharatqr_merchant_config set status = 'INACTIVE' where mid = '" + mid + "' and org_code='" + org_code + "' and bank_code='YES'"
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting inactive", result)
        query = "update bharatqr_merchant_config set status = 'ACTIVE' where org_code='" + org_code + "' and bank_code='HDFC' "
        result = DBProcessor.setValueToDB(query)
        print("RESULT of updating DB setting active", result)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


