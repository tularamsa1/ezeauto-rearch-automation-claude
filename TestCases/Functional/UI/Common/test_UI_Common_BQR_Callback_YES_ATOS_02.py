import sys
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
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
def test_common_100_102_136():
    """
    :Description: Verification of a BQRV4 BQR amount mismatch txn when Auto refund is disabled via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_BQR_amt_missmatch_callback_YES_ATOS
    :TC naming code description: 100->Payment Method, 102->BQR, 136-> TC136
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

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and " \
                                                        "status = 'ACTIVE' and bank_code='YES'"
        result = DBProcessor.getValueFromDB(query)
        terminal_info_id = result["terminal_info_id"].iloc[0]
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
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
            amount = 413
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
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + txn_id.split('E')[1]
            rrn = "RE" + txn_id.split('E')[1]

            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {pid}, Secondary id : {sid}")
            logger.debug("Performing 1st Callback")
            api_details = DBProcessor.get_api_details('callbackYES',
                                                      request_body={"primary_id": pid,"secondary_id":sid,
                                                                    "txn_amount": str(amount), "mpan": bqr_m_pan,
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
                    "pmt_mode_2": "BHARAT QR",
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
                    "txn_amt_2": float(amount), "pmt_mode_2": "BHARATQR",
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
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_code_2": "YES",
                    "payment_gateway_2": "ATOS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "ipr_pmt_mode": "BHARATQR",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn_upg),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": bqr_mc_id,
                    "ipr_pg_merchant_id": bqr_m_pan,
                    "bqr_pmt_status_2": "SUCCESS", "bqr_pmt_state_2": "UPG_AUTHORIZED",
                    "bqr_txn_amt_2": float(amount),
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "YES",
                    "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_upg,
                    "bqr_merchant_pan_2": bqr_m_pan,
                    "bqr_rrn_2": str(rrn_upg), "bqr_org_code_2": org_code

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
                bqr_amount_db = float(result["txn_amount"].iloc[0])
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

                query = "select * from bharatqr_txn where id='" + txn_id_upg + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_code"].iloc[0]
                bqr_state_db_new = result["state"].iloc[0]
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                # bqr_txn_type_db_new = result["txn_type"].iloc[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_new = result["merchant_pan"].iloc[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

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
                    "settle_status_2": settlement_status_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_code_2": bank_code_db_new,
                    "payment_gateway_2": payment_gateway_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "bqr_pmt_status_2": bqr_status_db_new, "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_merchant_pan_2": bqr_merchant_pan_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new, "bqr_org_code_2": bqr_org_code_db_new,
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