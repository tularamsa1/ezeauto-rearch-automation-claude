import random
import sys
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_101_206():
    """
    Sub Feature Code: TID_Dep_UI_Common_PM_UPI_amount_mismatch_Via_Pure_UPI_Success_Callback_AXISDIRECT
    Sub Feature Description: TID Dep-Performing a amount mismatch using upi success callback via AXIS_DIRECT
    TC naming code description: 100: Payment Method, 101: UPI, 206: TC206
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and payment_mode ='UPI' and acquirer_code='AXIS' and payment_gateway='AXIS';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # acquisition and payment_gateway is AXIS
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="AXIS",
                                                                           payment_gateway="AXIS")

            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating bqr qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)

            txn_id = response["txnId"]
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result for upi_merchant_config table is : {result}")
            upi_mc_id = result['id'].values[0]
            logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
            pg_merchant_id = result['pgMerchantId'].values[0]
            logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
            vpa = result['vpa'].values[0]
            logger.debug(f"fetched vpa : {vpa}")
            tid = result['tid'].values[0]
            logger.debug(f"fetched tid : {tid}")
            mid = result['mid'].values[0]
            logger.debug(f"fetched mid : {mid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(f"fetched terminal_info_id : {terminal_info_id}")

            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated ref_id is : {ref_id}")

            amount = amount + 1
            logger.debug(f"changing amount to perform the mismatch scenario")
            logger.debug(
                f"replacing the Txn_id with {txn_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data")
            api_details = DBProcessor.get_api_details('axis_direct_upi_success_curl', curl_data={
                'merchantTransactionId': txn_id,
                'transactionAmount': amount,
                'merchantId': str(pg_merchant_id),
                'creditVpa': vpa,
                'rrn': rrn,
                'gatewayTransactionId': ref_id
            })
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''
            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            logger.debug(f"executing the curl_data on the remote server")
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(f"preparing the request payload data to trigger the /api/2.0/upi/confirm/axisdirect")
            api_details = DBProcessor.get_api_details('confirm_axisdirect', request_body={"data": data_buffer})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for /api/2.0/upi/confirm/axisdirect : {response}")

            query = "select * from invalid_pg_request where request_id ='" + txn_id + "';"
            logger.debug(f"query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"txn_id from invalid_pg_request table is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            ipr_auth_code = result["auth_code"].iloc[0]
            ipr_bank_code = result["bank_code"].iloc[0]
            ipr_org_code = result["org_code"].iloc[0]
            ipr_amount = result["amount"].iloc[0]
            ipr_rrn = result["rrn"].iloc[0]
            ipr_mid = result["mid"].iloc[0]
            ipr_tid = result["tid"].iloc[0]
            ipr_config_id = result["config_id"].iloc[0]
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            ipr_error_message = result["error_message"].iloc[0]
            logger.debug(f"ipr_error_message from invalid_pg_request : {ipr_error_message}")

            query = "select * from txn where id = '" + ipr_txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time : {created_time}")
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

            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            created_time_2 = result['created_time'].values[0]

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "rrn": str(rrn),
                    # "order_id": external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,

                    "pmt_mode_1": "UPI",
                    "pmt_status_1": "PENDING",
                    "txn_amt_1": str(amount - 1) + ".00",
                    "settle_status_1": "PENDING",
                    "order_id_1": order_id,
                    "pmt_msg_1": "PAYMENT PENDING",
                    "date_1": date_and_time_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")
                logger.info("resetting the app")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)

                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {ipr_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status_1 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status_1}")
                app_date_and_time_1 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time_1}")
                payment_mode_1 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode_1}")
                app_txn_id_1 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id_1}")
                app_amount_1 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount_1}")
                app_settlement_status_1 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status_1}")
                app_payment_msg_1 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg_1}")
                app_order_id_1 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id_1}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settlement_status,
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    # "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,

                    "pmt_mode_1": payment_mode_1,
                    "pmt_status_1": payment_status_1.split(':')[1],
                    "txn_amt_1": app_amount_1.split(' ')[1],
                    "settle_status_1": app_settlement_status_1,
                    "order_id_1": app_order_id_1,
                    "pmt_msg_1": app_payment_msg_1,
                    "date_1": app_date_and_time_1
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
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,

                    "pmt_status_1": "PENDING",
                    "txn_amt_1": amount - 1, "pmt_mode_1": "UPI",
                    "pmt_state_1": "PENDING",
                    "settle_status_1": "PENDING",
                    "acquirer_code_1": "AXIS",
                    "issuer_code_1": "AXIS",
                    "txn_type_1": txn_type, "mid_1": mid, "tid_1": tid,
                    "org_code_1": org_code_txn,
                    "device_serial_1": str(device_serial)
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_ipr = [x for x in response["txns"] if x["txnId"] == ipr_txn_id][0]
                logger.debug(f"Response after filtering data of authorized txn is : {response_ipr}")

                status_api = response_ipr["status"]
                amount_api = float(response_ipr["amount"])
                payment_mode_api = response_ipr["paymentMode"]
                state_api = response_ipr["states"][0]
                rrn_api = response_ipr["rrNumber"]
                settlement_status_api = response_ipr["settlementStatus"]
                issuer_code_api = response_ipr["issuerCode"]
                acquirer_code_api = response_ipr["acquirerCode"]
                orgCode_api = response_ipr["orgCode"]
                mid_api = response_ipr["mid"]
                tid_api = response_ipr["tid"]
                txn_type_api = response_ipr["txnType"]
                date_api = response_ipr["createdTime"]

                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api_1 = response_1["status"]
                amount_api_1 = float(response_1["amount"])
                payment_mode_api_1 = response_1["paymentMode"]
                state_api_1 = response_1["states"][0]
                settlement_status_api_1 = response_1["settlementStatus"]
                issuer_code_api_1 = response_1["issuerCode"]
                acquirer_code_api_1 = response_1["acquirerCode"]
                orgCode_api_1 = response_1["orgCode"]
                mid_api_1 = response_1["mid"]
                tid_api_1 = response_1["tid"]
                txn_type_api_1 = response_1["txnType"]
                device_serial_api_1 = response_1["deviceSerial"]

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

                    "pmt_status_1": status_api_1,
                    "txn_amt_1": amount_api_1, "pmt_mode_1": payment_mode_api_1,
                    "pmt_state_1": state_api_1,
                    "settle_status_1": settlement_status_api_1,
                    "acquirer_code_1": acquirer_code_api_1,
                    "issuer_code_1": issuer_code_api_1,
                    "txn_type_1": txn_type_api_1, "mid_1": mid_api_1, "tid_1": tid_api_1,
                    "org_code_1": orgCode_api_1,
                    "device_serial_1": str(device_serial_api_1)
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
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "bank_code": "AXIS",
                    "pmt_gateway": "AXIS",
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "AXIS",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "ipr_error_msg": "The given amount - " + str(txn_id) + " doesnt match with the transaction amount.",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "UPG_AUTHORIZED",

                    "pmt_status_1": "PENDING",
                    "pmt_state_1": "PENDING",
                    "pmt_mode_1": "UPI",
                    "txn_amt_1": amount - 1,
                    "settle_status_1": "PENDING",
                    "acquirer_code_1": "AXIS",
                    "bank_code_1": "AXIS",
                    "pmt_gateway_1": "AXIS",
                    "mid_1": mid,
                    "tid_1": tid,
                    "upi_txn_type_1": "PAY_QR",
                    "upi_bank_code_1": "AXIS_DIRECT",
                    "upi_mc_id_1": upi_mc_id,
                    "upi_txn_status_1": "PENDING",
                    "device_serial_1": str(device_serial)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + ipr_txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data pending txn from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_1 = result["status"].iloc[0]
                upi_txn_type_db_1 = result["txn_type"].iloc[0]
                upi_bank_code_db_1 = result["bank_code"].iloc[0]
                upi_mc_id_db_1 = result["upi_mc_id"].iloc[0]

                query = "select * from txn where id = '" + txn_id + "';"
                logger.debug(f"Query to fetch pending txn details from database : {query}")
                result = DBProcessor.getValueFromDB(query)
                status_db_1 = result["status"].iloc[0]
                payment_mode_db_1 = result["payment_mode"].iloc[0]
                amount_db_1 = int(result["amount"].iloc[0])
                state_db_1 = result["state"].iloc[0]
                payment_gateway_db_1 = result["payment_gateway"].iloc[0]
                acquirer_code_db_1 = result["acquirer_code"].iloc[0]
                bank_code_db_1 = result["bank_code"].iloc[0]
                settlement_status_db_1 = result["settlement_status"].iloc[0]
                tid_db_1 = result['tid'].values[0]
                mid_db_1 = result['mid'].values[0]
                device_serial_db_1 = result['device_serial'].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_txn_status": upi_status_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "ipr_error_msg": ipr_error_message,

                    "pmt_status_1": status_db_1,
                    "pmt_state_1": state_db_1,
                    "pmt_mode_1": payment_mode_db_1,
                    "txn_amt_1": amount_db_1,
                    "settle_status_1": settlement_status_db_1,
                    "acquirer_code_1": acquirer_code_db_1,
                    "bank_code_1": bank_code_db_1,
                    "pmt_gateway_1": payment_gateway_db_1,
                    "mid_1": mid_db_1,
                    "tid_1": tid_db_1,
                    "upi_txn_type_1": upi_txn_type_db_1,
                    "upi_bank_code_1": upi_bank_code_db_1,
                    "upi_mc_id_1": upi_mc_id_db_1,
                    "upi_txn_status_1": upi_status_db_1,
                    "device_serial_1": device_serial_db_1,

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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": "EZETAP",
                    "txn_id": ipr_txn_id,
                    "rrn": str(rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
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
