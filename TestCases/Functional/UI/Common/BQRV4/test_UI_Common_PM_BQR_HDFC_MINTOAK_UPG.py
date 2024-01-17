import sys
import pytest
import random
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_376():
    """
    Sub Feature Code: UI_Common_PM_BQR_UPG_AUTOREFUND_Disabled_HDFC_MINTOAK
    Sub Feature Description: Verification of a BQRV4 BQR UPG txn when Auto refund is disabled via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 376: TC376
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code,bank_code= 'HDFC_MINTOAK',portal_un= portal_username,portal_pw= portal_password,payment_mode= 'BQRV4')

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

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        logger.debug(f"Fetching from bharatqr_merchant_config mid:{mid}")
        tid = result["tid"].values[0]
        logger.debug(f"Fetching from bharatqr_merchant_config tid:{tid}")
        terminal_info_id = result["terminal_info_id"].values[0]
        logger.debug(f"Fetching from bharatqr_merchant_config terminal_info_id:{terminal_info_id}")
        bqr_mc_id = result["id"].values[0]
        logger.debug(f"Fetching from bharatqr_merchant_config bqr_mc_id:{bqr_mc_id}")
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching from bharatqr_merchant_config bqr_m_pan:{bqr_m_pan}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(371, 400)
            upg_txn_id = '220518115526031E' + str(random.randint(10000000, 999999999))

            query = f"select visa_merchant_id_primary from bharatqr_merchant_config where org_code='{org_code}' and bank_code='HDFC_MINTOAK' "
            result = DBProcessor.getValueFromDB(query)
            merchant_id = result["visa_merchant_id_primary"].values[0]
            logger.debug(f"Fetching Txn_id merchant pan : Txn_id: {upg_txn_id},  merchant pan, {merchant_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            logger.debug(f"mtxnID generated:{mtxn_id}")
            issuer_ref_number = str(random.randint(10000000, 99999999))
            logger.debug(f"issuer_ref_number generated:{issuer_ref_number}")
            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = upg_txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{upg_txn_id}';"
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query Result: {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"Fetching txn_id from invalid_pg_request table:{txn_id}")
            ipr_payment_mode = result["payment_mode"].values[0]
            logger.debug(f"Fetching ipr_payment_mode from invalid_pg_request table:{ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching ipr_bank_code from invalid_pg_request table:{ipr_bank_code}")
            ipr_org_code = result["org_code"].values[0]
            logger.debug(f"Fetching ipr_org_code from invalid_pg_request table:{ipr_org_code}")
            ipr_amount = result["amount"].values[0]
            logger.debug(f"Fetching ipr_amount from invalid_pg_request table:{ipr_amount}")
            ipr_mid = result["mid"].values[0]
            logger.debug(f"Fetching ipr_mid from invalid_pg_request table:{ipr_mid}")
            ipr_tid = result["tid"].values[0]
            logger.debug(f"Fetching ipr_tid from invalid_pg_request table:{ipr_tid}")
            ipr_config_id = result["config_id"].values[0]
            logger.debug(f"Fetching ipr_config_id from invalid_pg_request table:{ipr_config_id}")
            ipr_pg_merchant_id = result["pg_merchant_id"].values[0]
            logger.debug(f"Fetching ipr_pg_merchant_id from invalid_pg_request table:{ipr_pg_merchant_id}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query Result:{result}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from txn table:{external_ref}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from database for "
                         f"current merchant: {created_time}")
            amount_db = float(result["amount"].values[0])
            logger.debug(f"Fetching amount_db from txn table:{amount_db}")
            username = result['username'].values[0]
            logger.debug(f"Fetching username from txn table:{username}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetching payment_mode_db from txn table:{payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetching payment_status_db from txn table:{payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetching payment_state_db from txn table:{payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetching acquirer_code_db from txn table:{acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetching bank_name_db from txn table:{bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetching mid_db from txn table:{mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetching tid_db from txn table:{tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetching payment_gateway_db from txn table:{payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetching rr_number_db from txn table:{rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetching settlement_status_db from txn table:{settlement_status_db}")
            auth_code = result["auth_code"].values[0]
            logger.debug(f"Fetching auth_code from txn table:{auth_code}")

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
                                        "pmt_mode": "BHARAT QR",
                                        "pmt_status": "UPG_AUTHORIZED",
                                        "txn_amt": "{:.2f}".format(amount),
                                        "settle_status": "SETTLED",
                                        "txn_id": txn_id,
                                        "rrn": str(rr_number_db),
                                        "pmt_msg": "PAYMENT SUCCESSFUL",
                                        "date": date_and_time
                                     }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching app_rrn from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                                        "pmt_mode": payment_mode,
                                        "pmt_status": payment_status.split(':')[1],
                                        "txn_amt": app_amount.split(' ')[1],
                                        "txn_id": app_txn_id,
                                        "rrn": str(app_rrn),
                                        "settle_status": app_settlement_status,
                                        "pmt_msg": app_payment_msg,
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
                                        "pmt_status": "UPG_AUTHORIZED",
                                        "txn_amt": float(amount),
                                        "pmt_mode": "BHARATQR",
                                        "pmt_state": "UPG_AUTHORIZED",
                                        "rrn": str(rr_number_db),
                                        "settle_status": "SETTLED",
                                        "acquirer_code": "HDFC",
                                        "issuer_code": "HDFC",
                                        "txn_type": "CHARGE",
                                        "mid": mid,
                                        "tid": tid,
                                        "org_code": org_code,
                                        "date": date
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
                rrn_api = response["rrNumber"]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]
                logger.debug(f"API Details for original txn : rrn: {rrn_api},status:{status_api}, amount:{amount_api}, payment mode:{payment_mode_api}, state:{state_api}, settlement status:{settlement_status_api}, issuer code:{issuer_code_api}, acquirer code:{acquirer_code_api}, org code:{org_code_api}, mid:{mid_api}, tid:{tid_api}, txn type:{txn_type_api}, date:{date_api}")

                actual_api_values = {
                                        "pmt_status": status_api,
                                        "txn_amt": amount_api,
                                        "pmt_mode": payment_mode_api,
                                        "pmt_state": state_api,
                                        "rrn": str(rrn_api),
                                        "settle_status": settlement_status_api,
                                        "acquirer_code": acquirer_code_api,
                                        "issuer_code": issuer_code_api,
                                        "mid": mid_api,
                                        "txn_type": txn_type_api,
                                        "tid": tid_api,
                                        "org_code": org_code_api,
                                        "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                                        "txn_amt": float(amount),
                                        "pmt_mode": "BHARATQR",
                                        "pmt_status": "UPG_AUTHORIZED",
                                        "pmt_state": "UPG_AUTHORIZED",
                                        "acquirer_code" : "HDFC",
                                        "bank_name" : "HDFC Bank",
                                        "mid" :mid,
                                        "tid" : tid,
                                        "pmt_gateway": "MINTOAK",
                                        "rrn" : str(rr_number_db),
                                        "settle_status": "SETTLED",
                                        "bqr_pmt_status": "Success",
                                        "bqr_pmt_state": "UPG_AUTHORIZED",
                                        "bqr_txn_amt": float(amount),
                                        "brq_terminal_info_id": terminal_info_id,
                                        "bqr_bank_code": "HDFC",
                                        "bqr_merchant_config_id": bqr_mc_id,
                                        "bqr_txn_primary_id": txn_id,
                                        "bqr_org_code": org_code,
                                        "ipr_pmt_mode": "BHARATQR",
                                        "ipr_bank_code": "HDFC",
                                        "ipr_org_code": org_code,
                                        "ipr_txn_amt": amount,
                                        "ipr_mid": mid,
                                        "ipr_tid": tid,
                                        "ipr_config_id": bqr_mc_id,
                                        "ipr_pg_merchant_id": bqr_m_pan
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                logger.debug(f"Fetching bqr_status_db from txn table:{bqr_status_db}")
                bqr_state_db = result["state"].values[0]
                logger.debug(f"Fetching bqr_state_db from txn table:{bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].values[0])
                logger.debug(f"Fetching bqr_amount_db from txn table:{bqr_amount_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                logger.debug(f"Fetching brq_terminal_info_id_db from txn table:{brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].values[0]
                logger.debug(f"Fetching bqr_bank_code_db from txn table:{bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                logger.debug(f"Fetching bqr_merchant_config_id_db from txn table:{bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                logger.debug(f"Fetching bqr_txn_primary_id_db from txn table:{bqr_txn_primary_id_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Fetching bqr_rrn_db from txn table:{bqr_rrn_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Fetching bqr_org_code_db from txn table:{bqr_org_code_db}")

                actual_db_values = {
                                    "txn_amt": amount_db,
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db,
                                    "bank_name" : bank_name_db,
                                    "mid" :mid_db,
                                    "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "rrn" : bqr_rrn_db,
                                    "settle_status": settlement_status_db,
                                    "bqr_pmt_status": bqr_status_db,
                                    "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                                            "date_time": date_and_time_portal,
                                            "pmt_state": "UPG_AUTHORIZED",
                                            "pmt_type": "BHARATQR",
                                            "txn_amt": f"{str(amount)}.00",
                                            "username": username,
                                            "txn_id": txn_id,
                                            "auth_code": "-" if auth_code is None else auth_code,
                                            "rrn": rr_number_db
                                        }
                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.info(f"fetched date time from portal {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.info(f"fetched txn_id from portal {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"fetched total amount from portal {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"fetched auth_code from portal {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"fetched rr_number from portal {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.info(f"fetched txn_type from portal {transaction_type}")
                status = transaction_details[0]['Status']
                logger.info(f"fetched status {status}")
                username = transaction_details[0]['Username']
                logger.info(f"fetched username from portal {username}")

                actual_portal_values = {
                                            "date_time": date_time,
                                            "pmt_state": status,
                                            "pmt_type": transaction_type,
                                            "txn_amt": total_amount[1],
                                            "username": username,
                                            "txn_id": transaction_id,
                                            "auth_code": auth_code_portal,
                                            "rrn": rr_number
                                        }

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