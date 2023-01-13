import random
import sys
import pytest
from datetime import datetime
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import  Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_100_103_159():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_UPG_REFUND_PENDING_VIA_HDFC_when_UPGRefund_Enabled_&_UPGAutoRefund_Enabled_Tid_dep
    Sub Feature Description: Tid Dep - Verificayion of a upg txn using success callback via HDFC when upg refund and upg autorefund are enabled
    TC naming code description:100: Payment Method,103: Remote Pay,159: TC159
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
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"

        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 500)
            logger.info(f"amount is: {amount}")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.info(f"result of vpa from upi_merchant_config table is: {vpa}")
            upi_mc_id = result['id'].values[0]
            logger.info(f"result of upi_mc_id from upi_merchant_config table is: {upi_mc_id}")
            upi_mc_mid = result['mid'].iloc[0]
            logger.info(f"result of upi_mc_mid from upi_merchant_config table is: {upi_mc_mid}")
            upi_mc_tid = result['tid'].iloc[0]
            logger.info(f"result of upi_mc_tid from upi_merchant_config table is: {upi_mc_tid}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            request_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            logger.debug(f"generated random request_id is : {request_id}")
            vpa = 'abccccc@ybl'
            logger.debug(f"passing vpa is : {vpa}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id number is : {ref_id}")
            logger.debug(f"replacing the Txn_id with {request_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data "f"reference id with {ref_id}")

            api_details = DBProcessor.get_api_details('upi_success_curl',curl_data={
                'ref_id': ref_id,
                'Txn_id': request_id,
                'amount': str(amount) + ".00",
                'vpa': vpa,
                'rrn': rrn
            })

            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)

            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',request_body={
                'pgMerchantId': str(pg_merchant_id),
                'meRes': str(data_buffer)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from callBack Upi Merchant Res is : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + request_id + "';")
            logger.debug(f"Query to fetch invalid_pg_request from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of invalid_pg_request table is : {result}")
            txn_id = result['txn_id'].iloc[0]
            logger.debug(f"Query result of txn_id from cnpware_payment_flow : {txn_id}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            txn_mid = result['mid'].values[0]
            txn_tid = result['tid'].values[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------s

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
                    "txn_id": txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_status": "UPG_REFUND_PENDING",
                    "settle_status":"SETTLED",
                    "rrn": str(rrn),
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                app_payment_status_original = txn_history_page.fetch_txn_status_text()

                logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = txn_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
                app_txn_id_original = txn_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn_original}")
                app_settle_status_original = txn_history_page.fetch_settlement_status_text()
                logger.debug(f"Settlement Status from txn history for the txn : {txn_id}, {app_settle_status_original}")
                app_payment_msg_original = txn_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Payment Message from txn history for the txn : {txn_id}, {app_payment_msg_original}")

                actual_app_values = {
                    "pmt_status": app_payment_status_original.split(':')[1],
                    "pmt_mode": app_payment_mode_original,
                    "txn_id": app_txn_id_original,
                    "txn_amt": str(app_payment_amt_original),
                    "rrn": str(app_rrn_original),
                    "settle_status": app_settle_status_original,
                    "payment_msg": app_payment_msg_original,
                    "date": date_and_time
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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "txn_amt": amount,
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_mode": "UPI",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "CHARGE",
                    "mid": txn_mid,
                    "tid": txn_tid
                }

                logger.debug(f"expectedAPIValues: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnDetails',request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id
                })

                logger.debug(f"API DETAILS for original_txn_id : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api is : {state_api}")
                settle_status_api =response["settlementStatus"]
                logger.debug(f"settle_status_api is : {settle_status_api}")
                acq_code_api =response["acquirerCode"]
                logger.debug(f"acq_code_api is : {acq_code_api}")
                issuer_code_api =response["issuerCode"]
                logger.debug(f"issuer_code_api is : {issuer_code_api}")
                txn_type_api =response["txnType"]
                logger.debug(f"txn_type_api is : {txn_type_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_state": state_api,
                    "pmt_mode": payment_mode_api,
                    "settle_status": settle_status_api,
                    "acquirer_code":acq_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api
                }

                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "pmt_state": "UPG_REFUND_PENDING",
                    "upi_txn_status": "UPG_REFUND_PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "HDFC",
                    "mid": txn_mid,
                    "tid": txn_tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": txn_mid,
                    "ipr_tid": txn_tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table in db validation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db is : {settlement_status_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table in db validation : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db is : {upi_bank_code_db}")

                query = "select * from invalid_pg_request where request_id ='" + request_id + "';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of invalid_pg_request table in db validation : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                logger.debug(f"ipr_payment_mode is: {ipr_payment_mode}")
                ipr_bank_code = result["bank_code"].iloc[0]
                logger.debug(f"ipr_bank_code is: {ipr_bank_code}")
                ipr_org_code = result["org_code"].iloc[0]
                logger.debug(f"ipr_org_code is: {ipr_org_code}")
                ipr_amount = result["amount"].iloc[0]
                logger.debug(f"ipr_amount is: {ipr_amount}")
                ipr_rrn = result["rrn"].iloc[0]
                logger.debug(f"ipr_rrn is: {ipr_rrn}")
                ipr_mid = result["mid"].iloc[0]
                logger.debug(f"ipr_mid is: {ipr_mid}")
                ipr_tid = result["tid"].iloc[0]
                logger.debug(f"ipr_tid is: {ipr_tid}")
                ipr_config_id = result["config_id"].iloc[0]
                logger.debug(f"ipr_config_id is: {ipr_config_id}")
                ipr_vpa = result["vpa"].iloc[0]
                logger.debug(f"ipr_vpa is: {ipr_vpa}")
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
                logger.debug(f"ipr_pg_merchant_id is: {ipr_pg_merchant_id}")

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
                    "mid": upi_mc_mid,
                    "tid": upi_mc_tid,
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

                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
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
def test_common_100_103_160():
    """
    Sub Feature Code:UI_Common_PM_RP_RP_UPI_UPG_FAILED_VIA_HDFC_when_UPGRefund_&_UPGAutoRefund_Disabled_Tid_dep
    Sub Feature Description:Tid Dep - Performing a upg txn using failed callback when upg refund and upg autorefund are disabled
    TC naming code description:100: Payment Method,103: RemotePay,160: TC160
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
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "false"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'HDFC' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)

        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)---------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 500)
            logger.info(f"amount is: {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"order_id is: {order_id}")

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of upi_merchant_config table is : {result}")
            pg_merchant_id = result['pgMerchantId'].values[0]
            logger.debug(f"Query result of pg_merchant_id from upi_merchant_config table is : {pg_merchant_id}")
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result of vpa from upi_merchant_config table is : {vpa}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password,
                                                                              org_code)

            request_id = '220518115526031E' + str(random.randint(10000000, 999999999))
            logger.debug(f"generated random request_id is : {request_id}")
            vpa = 'abccccc@ybl'
            logger.debug(f"passing vpa is : {vpa}")
            amount = random.randint(300, 399)
            logger.debug(f"generated random amount is : {amount}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id number is : {ref_id}")

            logger.debug(f"replacing the Txn_id with {request_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data "f"reference id with {ref_id}")

            api_details = DBProcessor.get_api_details('upi_failed_curl',curl_data={
                'ref_id': ref_id,
                'Txn_id': request_id,
                'amount': str(amount) + ".00",
                'vpa': vpa, 'rrn': rrn
            })

            logger.info(f"Api details response is: ", {api_details['CurlData']})
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)

            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")

            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',request_body={
                'pgMerchantId': str(pg_merchant_id),
                'meRes': str(data_buffer)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response from callBack Upi Merchant Resposne is  : {response}")

            query = "select * from invalid_pg_request where request_id ='" + request_id + "';"
            logger.debug(f"Query to fetch data from invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of invalid_pg_request table is : {result}")
            txn_id = result['txn_id'].iloc[0]
            logger.debug(f"Query result of txn_id table is : {txn_id}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn table are : {result}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"External Ref from txn table are : {external_ref}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Org Code from txn table are : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from txn table are : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code from txn table are : {auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"posting_date from txn table are : {posting_date}")
            txn_mid = result['mid'].values[0]
            logger.debug(f"txn_mid from txn table are : {txn_mid}")
            txn_tid = result['tid'].values[0]
            logger.debug(f"txn_tid from txn table are : {txn_tid}")

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
                expectedAppValues = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "rrn": str(rrn),
                    "order_id": external_ref,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
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
                app_payment_status = txn_history_page.fetch_txn_status_text()

                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actualAppValues = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time
                }

                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {
                    "pmt_status": "UPG_FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_FAILED",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": txn_type,
                    "mid": txn_mid,
                    "tid": txn_tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date
                }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails',request_body={
                    "username": app_username,
                    "password": app_password,
                    "txnId": txn_id
                })

                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")

                logger.debug("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                logger.debug(f"status_api is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api is : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn_api is : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api is : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code_api is : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api is : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"auth_code_api is : {auth_code_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api is : {date_api}")

                actualAPIValues = {
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
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {
                    "pmt_status": "UPG_FAILED",
                    "pmt_state": "UPG_FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "bank_code": "HDFC",
                    "payment_gateway": "HDFC",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "HDFC",
                    "mid": txn_mid,
                    "tid": txn_tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "HDFC",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": txn_mid,
                    "ipr_tid": txn_tid,
                    "ipr_vpa": vpa,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table: {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db is : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db is : {settlement_status_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table: {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db is : {upi_bank_code_db}")

                query = "select * from invalid_pg_request where request_id ='" + request_id + "';"
                logger.debug(f"Query to fetch data from invalid_pg_request table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of invalid_pg_request table: {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                logger.debug(f"ipr_payment_mode is : {ipr_payment_mode}")
                ipr_bank_code = result["bank_code"].iloc[0]
                logger.debug(f"ipr_bank_code is : {ipr_bank_code}")
                ipr_org_code = result["org_code"].iloc[0]
                logger.debug(f"ipr_org_code is : {ipr_org_code}")
                ipr_amount = result["amount"].iloc[0]
                logger.debug(f"ipr_amount is : {ipr_amount}")
                ipr_rrn = result["rrn"].iloc[0]
                logger.debug(f"ipr_rrn is : {ipr_rrn}")
                ipr_auth_code = result["auth_code"].iloc[0]
                logger.debug(f"ipr_auth_code is : {ipr_auth_code}")
                ipr_mid = result["mid"].iloc[0]
                logger.debug(f"ipr_mid is : {ipr_mid}")
                ipr_tid = result["tid"].iloc[0]
                logger.debug(f"ipr_tid is : {ipr_tid}")
                ipr_vpa = result["vpa"].iloc[0]
                logger.debug(f"ipr_vpa is : {ipr_vpa}")
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
                logger.debug(f"ipr_pg_merchant_id is : {ipr_pg_merchant_id}")

                query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' and bank_code = 'HDFC';"
                logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from upi_merchant_config : {query}")
                mid_db = result['mid'].iloc[0]
                logger.debug(f"mid_db is : {mid_db}")
                tid_db = result['tid'].iloc[0]
                logger.debug(f"tid_db is : {tid_db}")

                actualDBValues = {
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
                    "mid": mid_db,
                    "tid": tid_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,

                }

                logger.debug(f"actualDBValues : {actualDBValues}")

                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)

