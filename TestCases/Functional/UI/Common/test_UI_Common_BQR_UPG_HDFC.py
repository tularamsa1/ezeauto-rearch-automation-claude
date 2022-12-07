import shutil
import sys
import pytest
import random
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
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
def test_common_100_102_019():
    """
    :Description: Verification of a BQRV4 BQR UPG txn when Auto refund is enabled via HDFC
    :Sub Feature code: UI_Common_BQRV4_BQR_UPG_AUTOREFUND_ENABLED_HDFC
    :TC naming code description: 100->Payment Method, 102->BQR, 019-> TC019
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        merchant_id = result["visa_merchant_id_primary"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='HDFC' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            print("Merchant id for this merchant is :", merchant_id)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": upg_txn_id, "TXN_AMOUNT": str(amount), "MERCHANT_PAN": merchant_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            created_time = result['created_time'].values[0]

            logger.debug(f"Fetching auth_code, created_time from database for "
                         f"current merchant:{auth_code}, {created_time}")
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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "UPG_REFUND_PENDING",
                                       "txn_amt": str(amount)+".00",
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       #"customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": external_ref,"pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code,
                                       "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
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
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     #"customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "auth_code": app_auth_code,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time}
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
                expected_api_values = {"pmt_status": "UPG_REFUND_PENDING","txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "UPG_REFUND_PENDING",
                                       "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "date": date}
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
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                #auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     #"auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                expected_db_values = {"txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                      "pmt_status": "UPG_REFUND_PENDING",
                                      "pmt_state": "UPG_REFUND_PENDING",
                                      "acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid,
                                      "pmt_gateway": "HDFC",
                                      "rrn" : str(rrn), "settle_status": "SETTLED",
                                      "bqr_pmt_status": "success", "bqr_pmt_state": "UPG_REFUND_PENDING",
                                      "bqr_txn_amt": float(amount),
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": merchant_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code,
                                      "ipr_pmt_mode": "BHARATQR",
                                      "ipr_bank_code": "HDFC",
                                      "ipr_org_code": org_code,
                                      "ipr_rrn": str(rrn),
                                      "ipr_txn_amt": amount,
                                      "ipr_mid": mid,
                                      "ipr_tid": tid,
                                      "ipr_config_id": bqr_mc_id,
                                      "ipr_pg_merchant_id": bqr_m_pan
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                # bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

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
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
                                    "ipr_rrn": str(ipr_rrn),
                                    "ipr_txn_amt": ipr_amount,
                                    "ipr_mid": ipr_mid,
                                    "ipr_tid": ipr_tid,
                                    "ipr_config_id": ipr_config_id,
                                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_020():
    """
    :Description: Verification of a BQRV4 BQR UPG txn when Auto refund is disabled via HDFC
    :Sub Feature code: UI_Common_BQRV4_BQR_UPG_AUTOREFUND_DISABLED_HDFC
    :TC naming code description: 100->Payment Method, 102->BQR, 020-> TC020
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        merchant_id = result["visa_merchant_id_primary"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        GlobalVariables.setupCompletedSuccessfully = True
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
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='HDFC' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            print("Merchant id for this merchant is :", merchant_id)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": upg_txn_id, "TXN_AMOUNT": str(amount), "MERCHANT_PAN": merchant_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            created_time = result['created_time'].values[0]

            logger.debug(f"Fetching auth_code, created_time from database for "
                         f"current merchant:{auth_code}, {created_time}")
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
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "UPG_AUTHORIZED",
                                       "txn_amt": str(amount)+".00",
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       #"customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": external_ref,"pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code,
                                       "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
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
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     #"customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "auth_code": app_auth_code,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time}
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
                expected_api_values = {"pmt_status": "UPG_AUTHORIZED","txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "UPG_AUTHORIZED",
                                       "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "date": date}
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
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                #auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     #"auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api)}
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
                expected_db_values = {"txn_amt": float(amount),"pmt_mode": "BHARATQR",
                                      "pmt_status": "UPG_AUTHORIZED",
                                      "pmt_state": "UPG_AUTHORIZED",
                                      "acquirer_code" : "HDFC", "bank_name" : "HDFC Bank",
                                      "mid" :mid, "tid" : tid,
                                      "pmt_gateway": "HDFC",
                                      "rrn" : str(rrn), "settle_status": "SETTLED",
                                      "bqr_pmt_status": "success", "bqr_pmt_state": "UPG_AUTHORIZED",
                                      "bqr_txn_amt": float(amount),
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": merchant_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code,
                                      "ipr_pmt_mode": "BHARATQR",
                                      "ipr_bank_code": "HDFC",
                                      "ipr_org_code": org_code,
                                      "ipr_rrn": str(rrn),
                                      "ipr_txn_amt": amount,
                                      "ipr_mid": mid,
                                      "ipr_tid": tid,
                                      "ipr_config_id": bqr_mc_id,
                                      "ipr_pg_merchant_id": bqr_m_pan
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                # bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

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
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
                                    "ipr_rrn": str(ipr_rrn),
                                    "ipr_txn_amt": ipr_amount,
                                    "ipr_mid": ipr_mid,
                                    "ipr_tid": ipr_tid,
                                    "ipr_config_id": ipr_config_id,
                                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_021():
    """
    :Description: Verification of  a BQR UPG Failed txn when Auto refund is enabled via HDFC
    :Sub Feature code: UI_Common_PM_BQR_UPG_Failed_AUTOREFUND_ENABLED_HDFC_21
    :TC naming code description: 100->Payment Method
                                102->BQR
                                021-> TC21
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')
        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('UPGRefund',request_body={"username": portal_username, "password": portal_password, "settingForOrgCode":org_code})
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info("Finished performing preconditions before starting test case execution")
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

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='HDFC' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            print("Merhant id for this merchant is :", merchant_id)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": upg_txn_id, "TXN_AMOUNT": str(amount), "MERCHANT_PAN": merchant_id,
                                                                    "STATUS_CODE": "02", "STATUS_DESC": "failed",
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select id from txn where org_code='"+org_code+"' order by created_time desc limit 1"#fetch txn id besed on order id from txn table
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            upg_txn_id = result["id"].iloc[0]
            logger.debug(f"Transaction id of upg txn is : {upg_txn_id}")

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
                expectedAppValues = {"Payment mode": "BHARAT QR", "Payment Txn ID": upg_txn_id, "Payment Amt": "{:.2f}".format(amount),
                                     "Payment Status": "STATUS:UPG_FAILED"}
                loginPage = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_txn_id(upg_txn_id)
                app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status}")
                app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
                app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id}")
                app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt}")

                actualAppValues = {"Payment mode": app_payment_mode, "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),
                                     "Payment Status": app_payment_status}

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
                expectedAPIValues = {"Payment Status":"UPG_FAILED","Amount": amount, "Payment Mode": "BHARATQR","Acquirer Code":"HDFC"}
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username, "password": app_password,
                                                                        "txnId": upg_txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                accuirer_code_api = response["acquirerCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")


                actualAPIValues = {"Payment Status":status_api,"Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api}
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
                expectedDBValues = {"Payment Status": "UPG_FAILED", "Payment mode":"BHARATQR" , "Payment amount":"{:.2f}".format(amount),"Acquirer Code":"HDFC", "State":"UPG_FAILED", "State Bharatqr": "UPG_FAILED", "Amount Bharatqr": amount, "Status Bharatqr": "failed"}
                #
                query = "select status,amount,payment_mode,acquirer_code,state from txn where id='" + upg_txn_id + "'"
                logger.debug(f"DB query to fetch status,acquirer_code, amount, payment mode and state from DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = "{:.2f}".format(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                accuirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db} ")
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
                logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
                logger.debug(f"Fetching Transaction state from DB : {state_db} ")

                query = "select state,txn_amount,status_desc from bharatqr_txn where id='" + upg_txn_id + "'"
                logger.debug(f"DB query to fetch state, txn amount and status_desc from bahratqr_txn DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
                state_bharatqr_db = result["state"].iloc[0]
                amount_bharatqr_db = result["txn_amount"].iloc[0]
                status_bharatqr_db = result["status_desc"].iloc[0]
                logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
                logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
                logger.debug(f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
                #
                actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "State":state_db,"Acquirer Code":accuirer_code_db, "State Bharatqr": state_bharatqr_db, "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}
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
                expectedPortalValues = {"Payment Status": "Upg Failed", "Payment mode": "BHARATQR",
                                        "Payment amount": str(amount)}
                #
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                loginPagePortal = PortalLoginPage(ui_driver)
                # username_portal = read_config("credentials", 'username_portal')
                # password_portal = read_config('credentials', 'password_portal')
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
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_022():
    """
    :Description: Verification of  a BQRV4 BQR UPG Refund txn when Auto refund is disabled through Portal via HDFC
    :Sub Feature code: UI_Common_BQRV4_BQR_UPG_Refund_Via_Portal_HDFC
    :TC naming code description: 100->Payment Method, 102->BQR, 022-> TC022
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        merchant_id = result["visa_merchant_id_primary"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

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
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='HDFC' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": upg_txn_id, "TXN_AMOUNT": str(amount), "MERCHANT_PAN": merchant_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            created_time = result['created_time'].values[0]

            logger.debug(f"Fetching auth_code, created_time from database for "
                         f"current merchant:{auth_code}, {created_time}")

            ui_driver = TestSuiteSetup.initialize_portal_driver()
            login_page_portal = PortalLoginPage(ui_driver)
            logger.info(f"Logging in Portal using username : {portal_username}")
            login_page_portal.perform_login_to_portal(portal_username, portal_password)
            home_page_portal = PortalHomePage(ui_driver)
            home_page_portal.wait_for_home_page_load()
            home_page_portal.search_merchant_name(org_code)
            logger.info(f"Switching to merchant : {org_code}")
            home_page_portal.click_switch_button(org_code)
            home_page_portal.click_transaction_search_menu()
            logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
            home_page_portal.click_on_transaction_details_based_on_transaction_id(txn_id)
            logger.debug("Clicking on refund button")
            home_page_portal.click_on_refund_button()
            home_page_portal.perform_refund_of_txn(amount)
            logger.info("Performing Page refresh after refund is performed")

            query = "select * from txn where org_code='" + org_code + "' and orig_txn_id ='" + str(txn_id) + "' "
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            rrn_refunded = result['rr_number'].iloc[0]
            created_time_refunded = result['created_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_refunded)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "UPG_AUTH_REFUNDED",
                                       "txn_amt": str(amount)+".00","settle_status": "SETTLED",
                                       "txn_id": txn_id, "rrn": str(rrn),
                                       # "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": external_ref, "pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code,
                                       "date": date_and_time,
                                       "pmt_mode_2": "BHARAT QR", "pmt_status_2": "UPG_REFUNDED",
                                       "txn_amt_2": str(amount)+".00", "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_refunded, #"rrn_2": str(rrn_refunded),
                                       # "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id_2": external_ref, "pmt_msg_2": "PAYMENT SUCCESSFUL",
                                       # "auth_code": auth_code,
                                       "date_2": date_and_time_2
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
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
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_refunded}, {payment_status_refunded}")
                # app_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_refunded}, {payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_txn_id_refunded}")
                app_amount_refunded = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_refunded}, {app_amount_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time_refunded}")
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_refunded}, {app_settlement_status_refunded}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg_refunded = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_refunded}, {app_payment_msg_refunded}")
                app_order_id_refunded = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_refunded}, {app_order_id_refunded}")
                # app_rrn_refunded = txn_history_page.fetch_RRN_text()
                # logger.info(
                #     f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     # "customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "auth_code": app_auth_code,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_refunded,
                                     "pmt_status_2": payment_status_refunded.split(':')[1],
                                     "txn_amt_2": app_amount_refunded.split(' ')[1],
                                     "txn_id_2": app_txn_id_refunded, #"rrn_2": str(app_rrn_refunded),
                                     # "customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status_2": app_settlement_status_refunded,
                                     "order_id_2": app_order_id_refunded,
                                     # "auth_code": app_auth_code,
                                     "pmt_msg_2": app_payment_msg_refunded,
                                     "date_2": app_date_and_time_refunded
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
                date_2 = date_time_converter.db_datetime(created_time_refunded)
                expected_api_values = {"pmt_status": "UPG_AUTH_REFUNDED", "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "UPG_REFUNDED",
                                       "rrn": str(rrn), "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "UPG_REFUNDED", "txn_amt_2": float(amount),
                                       "pmt_mode_2": "BHARATQR",
                                       "pmt_state_2": "UPG_REFUNDED",
                                       #"rrn_2": str(rrn_refunded),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC", #"issuer_code_2": "HDFC",
                                       "txn_type_2": "REFUND",
                                       "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "date_2": date_2
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                #rrn_api_refunded = response["rrNumber"]
                settlement_status_api_refunded = response["settlementStatus"]
                #issuer_code_api_refunded = response["issuerCode"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api_refunded = response["createdTime"]


                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     # "auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_refunded, "txn_amt_2": amount_api_refunded,
                                     "pmt_mode_2": payment_mode_api_refunded,
                                     "pmt_state_2": state_api_refunded, #"rrn_2": str(rrn_api_refunded),
                                     "settle_status_2": settlement_status_api_refunded,
                                     "acquirer_code_2": acquirer_code_api_refunded,
                                     #"issuer_code_2": issuer_code_api_refunded,
                                     "mid_2": mid_api_refunded,"tid_2": tid_api_refunded,
                                     "txn_type_2": txn_type_api_refunded,
                                     "org_code_2": org_code_api_refunded,
                                     # "auth_code": auth_code_api,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                expected_db_values = {"txn_amt": float(amount), "pmt_mode": "BHARATQR",
                                      "pmt_status": "UPG_AUTH_REFUNDED",
                                      "pmt_state": "UPG_REFUNDED",
                                      "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid,
                                      "pmt_gateway": "HDFC",
                                      "rrn": str(rrn), "settle_status": "SETTLED",
                                      "bqr_pmt_status": "success", "bqr_pmt_state": "UPG_REFUNDED",
                                      "bqr_txn_amt": float(amount),
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": merchant_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code,
                                      "ipr_pmt_mode": "BHARATQR",
                                      "ipr_bank_code": "HDFC",
                                      "ipr_org_code": org_code,
                                      "ipr_rrn": str(rrn),
                                      "ipr_txn_amt": amount,
                                      "ipr_mid": mid,
                                      "ipr_tid": tid,
                                      "ipr_config_id": bqr_mc_id,
                                      "ipr_pg_merchant_id": bqr_m_pan
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                # bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

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
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn": rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
                                    "ipr_rrn": str(ipr_rrn),
                                    "ipr_txn_amt": ipr_amount,
                                    "ipr_mid": ipr_mid,
                                    "ipr_tid": ipr_tid,
                                    "ipr_config_id": ipr_config_id,
                                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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
def test_common_100_102_023():
    """
    :Description: Verification of  a BQRV4 BQR UPG Refund txn when Auto refund is disabled through API via HDFC
    :Sub Feature code: UI_Common_BQRV4_BQR_UPG_Refund_Via_API_HDFC
    :TC naming code description: 100->Payment Method, 102->BQR, 023-> TC023
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'HDFC', portal_username, portal_password, 'BQRV4')

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

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                "status = 'ACTIVE' and bank_code='HDFC'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        terminal_info_id = result["terminal_info_id"].iloc[0]
        bqr_mc_id = result["id"].iloc[0]
        bqr_m_pan = result["merchant_pan"].iloc[0]
        merchant_id = result["visa_merchant_id_primary"].iloc[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

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
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 1000)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            auth_code = "AE" + upg_txn_id.split('E')[1]
            rrn = "RE" + upg_txn_id.split('E')[1]

            query = "select visa_merchant_id_primary from bharatqr_merchant_config where org_code='" + org_code + "' and bank_code='HDFC' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].iloc[0]
            print("Merchant id for this merchant is :", merchant_id)
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, merchant pan : Txn_id: {upg_txn_id}, Auth code : {auth_code}, RRN : {rrn}, {merchant_id}, merchant pan")

            api_details = DBProcessor.get_api_details('callbackHDFC',
                                                      request_body={"PRIMARY_ID": upg_txn_id, "TXN_AMOUNT": str(amount), "MERCHANT_PAN": merchant_id,
                                                                    "AUTH_CODE": auth_code, "RRN": rrn})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + upg_txn_id + "';")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].iloc[0]
            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            created_time = result['created_time'].values[0]

            logger.debug(f"Fetching auth_code, created_time from database for "
                         f"current merchant:{auth_code}, {created_time}")

            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            print(response)
            query = "select * from txn where org_code='" + org_code + "' and orig_txn_id ='" + str(txn_id) + "' "
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_refunded = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id_refunded} ")
            refund_auth_code = result['auth_code'].values[0]
            rrn_refunded = result['rr_number'].iloc[0]
            created_time_refunded = result['created_time'].values[0]

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_2 = date_time_converter.to_app_format(created_time_refunded)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "UPG_AUTH_REFUNDED",
                                       "txn_amt": str(amount)+".00","settle_status": "SETTLED",
                                       "txn_id": txn_id, "rrn": str(rrn),
                                       # "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": external_ref, "pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code,
                                       "date": date_and_time,
                                       "pmt_mode_2": "BHARAT QR", "pmt_status_2": "UPG_REFUNDED",
                                       "txn_amt_2": str(amount)+".00", "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_refunded, #"rrn_2": str(rrn_refunded),
                                       # "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id_2": external_ref, "pmt_msg_2": "PAYMENT SUCCESSFUL",
                                       # "auth_code": auth_code,
                                       "date_2": date_and_time_2
                                       }
                logger.debug(f"expectedAppValues: {expected_app_values}")
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
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_refunded)

                payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_refunded}, {payment_status_refunded}")
                # app_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_refunded}, {payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_txn_id_refunded}")
                app_amount_refunded = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_refunded}, {app_amount_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_refunded}, {app_date_and_time_refunded}")
                # app_customer_name = txn_history_page.fetch_customer_name_text()
                # logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_refunded}, {app_settlement_status_refunded}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg_refunded = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_refunded}, {app_payment_msg_refunded}")
                app_order_id_refunded = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_refunded}, {app_order_id_refunded}")
                # app_rrn_refunded = txn_history_page.fetch_RRN_text()
                # logger.info(
                #     f"Fetching txn_id from txn history for the txn : {txn_id_refunded}, {app_rrn_refunded}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     # "customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "auth_code": app_auth_code,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_refunded,
                                     "pmt_status_2": payment_status_refunded.split(':')[1],
                                     "txn_amt_2": app_amount_refunded.split(' ')[1],
                                     "txn_id_2": app_txn_id_refunded, #"rrn_2": str(app_rrn_refunded),
                                     # "customer_name": app_customer_name,"payer_name": app_payer_name,
                                     "settle_status_2": app_settlement_status_refunded,
                                     "order_id_2": app_order_id_refunded,
                                     # "auth_code": app_auth_code,
                                     "pmt_msg_2": app_payment_msg_refunded,
                                     "date_2": app_date_and_time_refunded
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
                date_2 = date_time_converter.db_datetime(created_time_refunded)
                expected_api_values = {"pmt_status": "UPG_AUTH_REFUNDED", "txn_amt": float(amount),
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "UPG_REFUNDED",
                                       "rrn": str(rrn), "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "pmt_status_2": "UPG_REFUNDED", "txn_amt_2": float(amount),
                                       "pmt_mode_2": "BHARATQR",
                                       "pmt_state_2": "UPG_REFUNDED",
                                       #"rrn_2": str(rrn_refunded),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC", #"issuer_code_2": "HDFC",
                                       "txn_type_2": "REFUND",
                                       "mid_2": mid, "tid_2": tid,
                                       "org_code_2": org_code,
                                       "date_2": date_2
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = float(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = float(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                state_api_refunded = response["states"][0]
                #rrn_api_refunded = response["rrNumber"]
                settlement_status_api_refunded = response["settlementStatus"]
                #issuer_code_api_refunded = response["issuerCode"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                mid_api_refunded = response["mid"]
                tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                # auth_code_api = response["authCode"]
                date_api_refunded = response["createdTime"]


                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     # "auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "pmt_status_2": status_api_refunded, "txn_amt_2": amount_api_refunded,
                                     "pmt_mode_2": payment_mode_api_refunded,
                                     "pmt_state_2": state_api_refunded, #"rrn_2": str(rrn_api_refunded),
                                     "settle_status_2": settlement_status_api_refunded,
                                     "acquirer_code_2": acquirer_code_api_refunded,
                                     #"issuer_code_2": issuer_code_api_refunded,
                                     "mid_2": mid_api_refunded,"tid_2": tid_api_refunded,
                                     "txn_type_2": txn_type_api_refunded,  "org_code_2": org_code_api_refunded,
                                     # "auth_code": auth_code_api,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded)
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
                expected_db_values = {"txn_amt": float(amount), "pmt_mode": "BHARATQR",
                                      "pmt_status": "UPG_AUTH_REFUNDED",
                                      "pmt_state": "UPG_REFUNDED",
                                      "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid,
                                      "pmt_gateway": "HDFC",
                                      "rrn": str(rrn), "settle_status": "SETTLED",
                                      "bqr_pmt_status": "success", "bqr_pmt_state": "UPG_REFUNDED",
                                      "bqr_txn_amt": float(amount),
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_merchant_pan": merchant_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code,
                                      "ipr_pmt_mode": "BHARATQR",
                                      "ipr_bank_code": "HDFC",
                                      "ipr_org_code": org_code,
                                      "ipr_rrn": str(rrn),
                                      "ipr_txn_amt": amount,
                                      "ipr_mid": mid,
                                      "ipr_tid": tid,
                                      "ipr_config_id": bqr_mc_id,
                                      "ipr_pg_merchant_id": bqr_m_pan
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                # bqr_txn_type_db = result["txn_type"].iloc[0]
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

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
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn": rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_merchant_pan": bqr_merchant_pan_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
                                    "ipr_rrn": str(ipr_rrn),
                                    "ipr_txn_amt": ipr_amount,
                                    "ipr_mid": ipr_mid,
                                    "ipr_tid": ipr_tid,
                                    "ipr_config_id": ipr_config_id,
                                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
