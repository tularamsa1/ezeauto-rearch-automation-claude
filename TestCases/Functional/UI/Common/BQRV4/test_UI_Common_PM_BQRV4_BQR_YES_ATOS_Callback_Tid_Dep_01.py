import sys
import random
import time
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_304():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Callback_Success_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Success Callback Via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 304: TC304
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")

            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            pid = result["provider_ref_id"].iloc[0]
            logger.debug(f"Value of provider_ref_id obtained from bharatqr_txn table : {pid}")
            sid = result["transaction_secondary_id"].iloc[0]
            logger.debug(f"Value of transaction_secondary_id obtained from bharatqr_txn table : {sid}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from bharatqr_txn table : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            logger.debug(f"Value of auth_code obtained from bharatqr_txn table : {auth_code}")
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn obtained from bharatqr_txn table : {rrn}")

            api_details = DBProcessor.get_api_details('callbackYES',request_body={
                "primary_id": pid,
                "secondary_id":sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no":rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained from callback : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {payment_state_db}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Value of txn_type obtained from txn table : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Value of org_code obtained from txn table : {org_code_txn}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table : {bank_name_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            rr_number_db = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rr_number_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {status_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {state_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table : {bank_code_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id}, {app_auth_code}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
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
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "date": date,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                auth_code_api = response["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                date_api = response["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                customer_name_api = response["customerName"]
                logger.debug(f"Value of customerName obtained from txnlist api is : {customer_name_api}")
                payer_name_api = response["payerName"]
                logger.debug(f"Value of payerName obtained from txnlist api is : {payer_name_api}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

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
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api)
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_code": "YES",
                    "pmt_gateway": "ATOS",
                    "mid": mid,
                    "tid": tid,
                    "bank_name": "Yes Bank",
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "device_serial": str(device_serial),
                    "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "YES",
                    "bqr_pmt_status": "SUCCESS"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for DB validation : {bqr_status_code_db}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_txn_amt_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_transaction_primary_id_db}")
                bqr_status_db = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for DB validation : {bqr_status_db}")
                bqr_rrn_db = result["rrn"].iloc[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for DB validation : {bqr_rrn_db}")
                bqr_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")

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
                    "bank_name": bank_name_db,
                    "payer_name": payer_name_db,
                    "rrn": rr_number_db,
                    "device_serial": str(device_serial_db),
                    "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_pmt_status": bqr_status_db
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
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
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
                    "auth_code": auth_code_portal,
                    "rrn": rr_number
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code}
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
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_305():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Callback_After_expired_Success_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Callback After QR Expiry Success transaction when auto refund disabled via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 305: TC305
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")
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

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            pid = result["provider_ref_id"].iloc[0]
            logger.debug(f"Value of provider_ref_id obtained from bharatqr_txn table : {pid}")
            sid = result["transaction_secondary_id"].iloc[0]
            logger.debug(f"Value of transaction_secondary_id obtained from bharatqr_txn table : {sid}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from bharatqr_txn table : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            logger.debug(f"Value of auth_code obtained from bharatqr_txn table : {auth_code}")
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn obtained from bharatqr_txn table : {rrn}")

            api_details = DBProcessor.get_api_details('callbackYES', request_body={
                "primary_id": pid,
                "secondary_id": sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no": rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained from callback : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Value of payment_status obtained from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            query = "select * from txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table based on org_code : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table based on org_code : {result}")
            txn_id_new = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table based on org_code : {txn_id_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table based on org_code : {rrn_new}")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table based on org_code : {auth_code_new}")
            created_time_new = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table based on org_code : {created_time_new}")
            customer_name_new = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table based on org_code : {customer_name_new}")
            payer_name_new = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table based on org_code : {payer_name_new}")
            amount_db_new = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table based on org_code  : {amount_db_new}")
            payment_mode_db_new = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table based on org_code : {payment_mode_db_new}")
            payment_status_db_new = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table based on org_code : {payment_status_db_new}")
            payment_state_db_new = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table based on org_code : {payment_state_db_new}")
            acquirer_code_db_new = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table based on org_code  : {acquirer_code_db_new}")
            bank_name_db_new = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table based on org_code : {bank_name_db_new}")
            payer_name_db_new = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table based on org_code : {payer_name_db_new}")
            mid_db_new = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table based on org_code : {mid_db_new}")
            tid_db_new = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table based on org_code : {tid_db_new}")
            payment_gateway_db_new = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table based on org_code : {payment_gateway_db_new}")
            rr_number_db_new = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table based on org_code : {rr_number_db_new}")
            settlement_status_db_new = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table based on org_code : {settlement_status_db_new}")
            device_serial_new = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table based on org_code : {device_serial_new}")

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
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new,
                    "rrn_2": str(rrn_new),
                    "customer_name_2": customer_name_new,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_new,
                    "date_2": date_and_time_new
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new,
                    "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new,
                    "rrn_2": str(app_rrn_new),
                    "customer_name_2": app_customer_name_new,
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "auth_code_2": app_auth_code_new,
                    "pmt_msg_2": app_payment_msg_new,
                    "date_2": app_date_and_time_new
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
                date_new = date_time_converter.db_datetime(created_time_new)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "device_serial": str(device_serial),
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "issuer_code_2": "YES",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new,
                    "date_2": date_new,
                    "device_serial_2": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of another txnlist api is : {response_2}")
                status_api_new = response_2["status"]
                logger.debug(f"Value of status obtained from another txnlist api is : {status_api_new}")
                amount_api_new = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from another txnlist api is : {amount_api_new}")
                payment_mode_api_new = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from another txnlist api is : {payment_mode_api_new}")
                state_api_new = response_2["states"][0]
                logger.debug(f"Value of states obtained from another txnlist api is : {state_api_new}")
                rrn_api_new = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from another txnlist api is : {rrn_api_new}")
                settlement_status_api_new = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from another txnlist api is : {settlement_status_api_new}")
                issuer_code_api_new = response_2["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from another txnlist api is : {issuer_code_api_new}")
                acquirer_code_api_new = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from another txnlist api is : {acquirer_code_api_new}")
                org_code_api_new = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from another txnlist api is : {org_code_api_new}")
                mid_api_new = response_2["mid"]
                logger.debug(f"Value of mid obtained from another txnlist api is : {mid_api_new}")
                tid_api_new = response_2["tid"]
                logger.debug(f"Value of tid obtained from another txnlist api is : {tid_api_new}")
                txn_type_api_new = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from another txnlist api is : {txn_type_api_new}")
                auth_code_api_new = response_2["authCode"]
                logger.debug(f"Value of authCode obtained from another txnlist api is : {auth_code_api_new}")
                date_api_new = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from another txnlist api is : {date_api_new}")
                device_serial_api_new = response_2["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from another txnlist api is : {device_serial_api_new}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "device_serial": str(device_serial_api),
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "mid_2": mid_api_new,
                    "txn_type_2": txn_type_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "auth_code_2": auth_code_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                    "device_serial_2": str(device_serial_api_new)
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
                    "txn_amt": amount,
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "acquirer_code": "YES",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "ATOS",
                    "settle_status": "FAILED",
                    "device_serial": str(device_serial),
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "txn_amt_2": amount,
                    "pmt_mode_2": "BHARATQR",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_name_2": "Yes Bank",
                    "payer_name_2": payer_name_new,
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "ATOS",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "bqr_pmt_status_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": float(amount),
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "YES",
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_new,
                    "bqr_rrn_2": str(rrn_new),
                    "bqr_org_code_2": org_code,
                    "bank_code_2": "YES",
                    "bqr_terminal_info_id_2": terminal_info_id,
                    "device_serial_2": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_txn_amt_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_transaction_primary_id_db}")
                bqr_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")

                query = "select * from bharatqr_txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for another txn : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for another txn : {result}")
                bqr_status_db_new = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for another txn : {bqr_status_db_new}")
                bqr_state_db_new = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for another txn : {bqr_state_db_new}")
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for another txn : {bqr_amount_db_new}")
                bqr_txn_type_db_new = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for another txn : {bqr_txn_type_db_new}")
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for another txn : {brq_terminal_info_id_db_new}")
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for another txn : {bqr_bank_code_db_new}")
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for another txn : {bqr_merchant_config_id_db_new}")
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for another txn : {bqr_txn_primary_id_db_new}")
                bqr_rrn_db_new = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for another txn : {bqr_rrn_db_new}")
                bqr_org_code_db_new = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for another txn : {bqr_org_code_db_new}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "txn_amt_2": amount_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "pmt_status_2": payment_status_db_new,
                    "pmt_state_2": payment_state_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_name_2": bank_name_db_new,
                    "payer_name_2": payer_name_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "pmt_gateway_2": payment_gateway_db_new,
                    "rrn_2": rr_number_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "bqr_pmt_status_2": bqr_status_db_new,
                    "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "bqr_txn_type_2": bqr_txn_type_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new,
                    "bqr_org_code_2": bqr_org_code_db_new,
                    "device_serial": str(device_serial_db),
                    "bank_code_2": bqr_bank_code_db,
                    "bqr_terminal_info_id_2": bqr_terminal_info_id_db,
                    "device_serial_2": str(device_serial_new)
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new,
                    "auth_code_2": auth_code_new,
                    "rrn_2": rrn_new
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_new)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id_new,
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
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_306():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Two_Callback_Success_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR generation using API and performing two Callback Success transaction
    TC naming code description: 100: Payment Method, 102: BQRV4, 306: TC306
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")
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

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Value of txn_id obtained from BQR generation response : {txn_id}")

            query = "select * from bharatqr_txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            pid = result["provider_ref_id"].iloc[0]
            logger.debug(f"Value of provider_ref_id obtained from bharatqr_txn table : {pid}")
            sid = result["transaction_secondary_id"].iloc[0]
            logger.debug(f"Value of transaction_secondary_id obtained from bharatqr_txn table : {sid}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from bharatqr_txn table : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            logger.debug(f"Value of auth_code obtained from bharatqr_txn table : {auth_code}")
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn obtained from bharatqr_txn table : {rrn}")

            api_details = DBProcessor.get_api_details('callbackYES',request_body={
                "primary_id": pid,
                "secondary_id":sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no":rrn
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for First callback : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table for first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for first callback : {result}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for first callback : {posting_date}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for first callback : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for first callback : {payer_name}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount_db obtained from txn table for first callback : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode_db obtained from txn table for first callback : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Value of payment_status_db obtained from txn table for first callback : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Value of payment_state_db obtained from txn table for first callback : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code_db obtained from txn table for first callback : {acquirer_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name_db obtained from txn table for first callback : {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table for first callback : {payer_name_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid_db obtained from txn table for first callback : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid_db obtained from txn table for first callback : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway_db obtained from txn table for first callback : {payment_gateway_db}")
            rr_number_db = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number_db obtained from txn table for first callback : {rr_number_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for first callback : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table for first callback : {device_serial_db}")

            rrn_new = "RE" + str(order_id)
            logger.debug("Generated rrn_new values is: ", rrn_new)

            api_details = DBProcessor.get_api_details('callbackYES',request_body={
                "primary_id": pid,
                "secondary_id": sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no": rrn_new
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for Second callback : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table for second callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for second callback : {result}")
            txn_id_new = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table for second callback : {txn_id_new}")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for second callback : {auth_code_new}")
            posting_date_new = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for second callback : {posting_date_new}")
            customer_name_new = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for second callback : {customer_name_new}")
            payer_name_new = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for second callback : {payer_name_new}")
            amount_db_new = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for second callback : {amount_db_new}")
            payment_mode_db_new = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for second callback : {payment_mode_db_new}")
            payment_status_db_new = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for second callback : {payment_status_db_new}")
            payment_state_db_new = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for second callback : {payment_state_db_new}")
            acquirer_code_db_new = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for second callback : {acquirer_code_db_new}")
            bank_name_db_new = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table for second callback : {bank_name_db_new}")
            payer_name_db_new = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table for second callback : {payer_name_db_new}")
            mid_db_new = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table for second callback : {mid_db_new}")
            tid_db_new = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table for second callback : {tid_db_new}")
            payment_gateway_db_new = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for second callback : {payment_gateway_db_new}")
            rr_number_db_new = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table for second callback : {rr_number_db_new}")
            settlement_status_db_new = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for second callback : {settlement_status_db_new}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                date_and_time_new = date_time_converter.to_app_format(posting_date_new)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new,
                    "rrn_2": str(rrn_new),
                    "customer_name_2": customer_name_new,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_new,
                    "date_2": date_and_time_new
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
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
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "auth_code": app_auth_code,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new,
                    "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new,
                    "rrn_2": str(app_rrn_new),
                    "customer_name_2": app_customer_name_new,
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "auth_code_2": app_auth_code_new,
                    "pmt_msg_2": app_payment_msg_new,
                    "date_2": app_date_and_time_new
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
                date = date_time_converter.db_datetime(posting_date)
                date_new = date_time_converter.db_datetime(posting_date_new)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "auth_code": auth_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "issuer_code_2": "YES",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new,
                    "date_2": date_new,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                rrn_api = response_1["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                auth_code_api = response_1["authCode"]
                logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of another txn_id is : {response_2}")
                status_api_new = response_2["status"]
                logger.debug(f"Value of status obtained from another txn_id is : {status_api_new}")
                amount_api_new = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from another txn_id is : {amount_api_new}")
                payment_mode_api_new = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from another txn_id is : {payment_mode_api_new}")
                state_api_new = response_2["states"][0]
                logger.debug(f"Value of states obtained from another txn_id is : {state_api_new}")
                rrn_api_new = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from another txn_id is : {rrn_api_new}")
                settlement_status_api_new = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from another txn_id is : {settlement_status_api_new}")
                issuer_code_api_new = response_2["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from another txn_id is : {issuer_code_api_new}")
                acquirer_code_api_new = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from another txn_id is : {acquirer_code_api_new}")
                org_code_api_new = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from another txn_id is : {org_code_api_new}")
                mid_api_new = response_2["mid"]
                logger.debug(f"Value of mid obtained from another txn_id is : {mid_api_new}")
                tid_api_new = response_2["tid"]
                logger.debug(f"Value of tid obtained from another txn_id is : {tid_api_new}")
                txn_type_api_new = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from another txn_id is : {txn_type_api_new}")
                auth_code_api_new = response_2["authCode"]
                logger.debug(f"Value of authCode obtained from another txn_id is : {auth_code_api_new}")
                date_api_new = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from another txn_id is : {date_api_new}")

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
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "mid_2": mid_api_new,
                    "txn_type_2": txn_type_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "auth_code_2": auth_code_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
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
                    "txn_amt": amount,
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_name": "Yes Bank",
                    "payer_name": payer_name,
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "ATOS",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "bqr_pmt_status": "SUCCESS",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_rrn": str(rrn),
                    "bqr_org_code": org_code,
                    "txn_amt_2": amount,
                    "pmt_mode_2": "BHARATQR",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_name_2": "Yes Bank",
                    "payer_name_2": payer_name_new,
                    "mid_2": mid, "tid_2": tid,
                    "pmt_gateway_2": "ATOS",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "bqr_pmt_status_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": float(amount),
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "YES",
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_new,
                    "bqr_rrn_2": str(rrn_new),
                    "bqr_org_code_2": org_code,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_status_db = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for DB validation : {bqr_status_db}")
                bqr_rrn_db = result["rrn"].iloc[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for DB validation : {bqr_rrn_db}")
                bqr_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_amount_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {brq_terminal_info_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_txn_primary_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for new txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for new txn_id : {result}")
                bqr_status_db_new = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for new txn_id : {bqr_status_db_new}")
                bqr_state_db_new = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for new txn_id : {bqr_state_db_new}")
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for new txn_id : {bqr_amount_db_new}")
                bqr_txn_type_db_new = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for new txn_id : {bqr_txn_type_db_new}")
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for new txn_id : {brq_terminal_info_id_db_new}")
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for new txn_id : {bqr_bank_code_db_new}")
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for new txn_id : {bqr_merchant_config_id_db_new}")
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for new txn_id : {bqr_txn_primary_id_db_new}")
                bqr_rrn_db_new = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for new txn_id : {bqr_rrn_db_new}")
                bqr_org_code_db_new = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for new txn_id : {bqr_org_code_db_new}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_name": bank_name_db,
                    "payer_name": payer_name_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "rrn": rr_number_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_status": bqr_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "txn_amt_2": amount_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "pmt_status_2": payment_status_db_new,
                    "pmt_state_2": payment_state_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_name_2": bank_name_db_new,
                    "payer_name_2": payer_name_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "pmt_gateway_2": payment_gateway_db_new,
                    "rrn_2": rr_number_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "bqr_pmt_status_2": bqr_status_db_new,
                    "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "bqr_txn_type_2": bqr_txn_type_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new,
                    "bqr_org_code_2": bqr_org_code_db_new,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                date_and_time_portal_2 = date_time_converter.to_portal_format(posting_date_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": auth_code,
                    "rrn": rrn,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new,
                    "auth_code_2": auth_code_new,
                    "rrn_2": rrn_new
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[0]['Auth Code']
                rr_number_2 = transaction_details[0]['RR Number']
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(posting_date_new)

                expected_charge_slip_values_1 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_new)
                }
                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_1)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_2)
                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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
@pytest.mark.portalVal
def test_common_100_102_307():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Amount_Mismatch_Callback_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR amount mismatch txn when Auto refund is disabled via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 307: TC307
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = 413
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")

            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            pid = result["provider_ref_id"].iloc[0]
            logger.debug(f"Value of provider_ref_id obtained from bharatqr_txn table : {pid}")
            sid = result["transaction_secondary_id"].iloc[0]
            logger.debug(f"Value of transaction_secondary_id obtained from bharatqr_txn table : {sid}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from bharatqr_txn table : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            logger.debug(f"Value of auth_code obtained from bharatqr_txn table : {auth_code}")
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn obtained from bharatqr_txn table : {rrn}")

            api_details = DBProcessor.get_api_details('callbackYES', request_body={
                "primary_id": pid,
                "secondary_id": sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no": rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for callback : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table : {external_ref}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db}")

            query = "select * from invalid_pg_request where request_id ='" + pid + "';"
            logger.debug(f"Query to fetch data from invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of invalid_pg_request table : {result}")
            txn_id_upg = result['txn_id'].iloc[0]
            logger.debug(f"Value of txn_id obtained from invalid_pg_request table : {txn_id_upg}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from invalid_pg_request table : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from invalid_pg_request table : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f"Value of org_code obtained from invalid_pg_request table : {ipr_org_code}")
            ipr_amount = result["amount"].iloc[0]
            logger.debug(f"Value of amount obtained from invalid_pg_request table : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f"Value of rrn obtained from invalid_pg_request table : {ipr_rrn}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from invalid_pg_request table : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from invalid_pg_request table : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f"Value of config_id obtained from invalid_pg_request table : {ipr_config_id}")
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            logger.debug(f"Value of pg_merchant_id obtained from invalid_pg_request table : {ipr_pg_merchant_id}")

            query = "select * from txn where id = '" + txn_id_upg + "';"
            logger.debug(f"Query to fetch data from txn table based on txn_id_upg : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table based on txn_id_upg : {result}")
            created_time_upg = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table based on txn_id_upg : {created_time_upg}")
            rrn_upg = result['rr_number'].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table based on txn_id_upg : {rrn_upg}")
            external_ref_upg = result['external_ref'].values[0]
            logger.debug(f"Value of external_ref obtained from txn table based on txn_id_upg : {external_ref_upg}")
            status_db_new = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table based on txn_id_upg : {status_db_new}")
            payment_mode_db_new = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table based on txn_id_upg : {payment_mode_db_new}")
            amount_db_new = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table based on txn_id_upg : {amount_db_new}")
            state_db_new = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table based on txn_id_upg : {state_db_new}")
            payment_gateway_db_new = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table based on txn_id_upg : {payment_gateway_db_new}")
            acquirer_code_db_new = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table based on txn_id_upg : {acquirer_code_db_new}")
            bank_code_db_new = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from txn table based on txn_id_upg : {bank_code_db_new}")
            settlement_status_db_new = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table based on txn_id_upg : {settlement_status_db_new}")
            tid_db_new = result['tid'].values[0]
            logger.debug(f"Value of tid obtained from txn table based on txn_id_upg : {tid_db_new}")
            mid_db_new = result['mid'].values[0]
            logger.debug(f"Value of mid obtained from txn table based on txn_id_upg : {mid_db_new}")

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_upg)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "STATUS:PENDING",
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "txn_amt": "{:.2f}".format(amount),
                    "order_id": external_ref,
                    "pmt_msg": "PAYMENT PENDING",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "STATUS:UPG_AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_upg,
                    "txn_amt_2": "{:.2f}".format(amount),
                    "rrn_2": str(rrn_upg),
                    # "order_id_2": external_ref_upg,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_upg}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_upg}, {app_payment_msg_new}")
                # app_order_id_new = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_upg}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_upg}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_status": app_payment_status,
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_status_2": app_payment_status_new,
                    "pmt_mode_2": app_payment_mode_new,
                    "txn_id_2": app_txn_id_new,
                    "txn_amt_2": str(app_amount_new).split(' ')[1],
                    "settle_status_2": app_settlement_status_new,
                    # "order_id_2": app_order_id_new,
                    "payment_msg_2": app_payment_msg_new,
                    "rrn_2": app_rrn_new,
                    "date_2": app_date_and_time_new
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
                date_2 = date_time_converter.db_datetime(created_time_upg)
                expected_api_values = {
                    "pmt_status": "PENDING",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid, "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "rrn_2": str(rrn_upg),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "issuer_code_2": "YES",
                    "txn_type_2": 'CHARGE',
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "date_2": date_2,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for first transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from first txnlist api is : {status_api}")
                amount_api = float(response_1["amount"])
                logger.debug(f"Value of amount obtained from first txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from first txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from first txnlist api is : {state_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from first txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from first txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from first txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from first txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from first txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from first txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from first txnlist api is : {txn_type_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from first txnlist api is : {date_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from first txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_upg][0]
                logger.debug(f"Response after filtering data of second txnlist api is : {response_2}")
                status_api_new = response_2["status"]
                logger.debug(f"Value of status obtained from second txnlist api is : {status_api_new}")
                amount_api_new = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from second txnlist api is : {amount_api_new}")
                payment_mode_api_new = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from second txnlist api is : {payment_mode_api_new}")
                state_api_new = response_2["states"][0]
                logger.debug(f"Value of states obtained from second txnlist api is : {state_api_new}")
                rrn_api_new = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from second txnlist api is : {rrn_api_new}")
                settlement_status_api_new = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from second txnlist api is : {settlement_status_api_new}")
                issuer_code_api_new = response_2["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from second txnlist api is : {issuer_code_api_new}")
                acquirer_code_api_new = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from second txnlist api is : {acquirer_code_api_new}")
                org_code_api_new = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from second txnlist api is : {org_code_api_new}")
                mid_api_new = response_2["mid"]
                logger.debug(f"Value of mid obtained from second txnlist api is : {mid_api_new}")
                tid_api_new = response_2["tid"]
                logger.debug(f"Value of tid obtained from second txnlist api is : {tid_api_new}")
                txn_type_api_new = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from second txnlist api is : {txn_type_api_new}")
                date_api_new = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from second txnlist api is : {date_api_new}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "txn_type_2": txn_type_api_new,
                    "mid_2": mid_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "rrn_2": rrn_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                    "device_serial": str(device_serial_api)
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
                    "txn_amt": amount,
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "acquirer_code": "YES",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "ATOS",
                    "settle_status": "PENDING",
                    "bqr_pmt_state": "PENDING",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "pmt_status_2": "UPG_AUTHORIZED",
                    "pmt_state_2": "UPG_AUTHORIZED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_code_2": "YES",
                    "pmt_gateway_2": "ATOS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "ipr_pmt_mode": "BHARATQR",
                    "ipr_bank_code": "YES",
                    "ipr_org_code": org_code,
                    "ipr_rrn": str(rrn_upg),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": merchant_config_id,
                    "ipr_pg_merchant_id": merchant_pan,
                    "bqr_pmt_status_2": "SUCCESS",
                    "bqr_pmt_state_2": "UPG_AUTHORIZED",
                    "bqr_txn_amt_2": float(amount),
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "YES",
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_upg,
                    "bqr_rrn_2": str(rrn_upg),
                    "bqr_org_code_2": org_code,
                    "bqr_merchant_pan_2": merchant_pan,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {brq_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_txn_primary_id_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")

                query = "select * from bharatqr_txn where id='" + txn_id_upg + "'"
                logger.debug(f"Query to fetch data from txn table based on txn_id_upg for DB Validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of txn table based on txn_id_upg for DB Validation : {result}")
                bqr_status_db_new = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from txn table based on txn_id_upg for DB Validation : {bqr_status_db_new}")
                bqr_state_db_new = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from txn table based on txn_id_upg for DB Validation : {bqr_state_db_new}")
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from txn table based on txn_id_upg for DB Validation : {bqr_amount_db_new}")
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from txn table based on txn_id_upg for DB Validation: {brq_terminal_info_id_db_new}")
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from txn table based on txn_id_upg for DB Validation : {bqr_bank_code_db_new}")
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from txn table based on txn_id_upg for DB Validation : {bqr_merchant_config_id_db_new}")
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from txn table based on txn_id_upg for DB Validation : {bqr_txn_primary_id_db_new}")
                bqr_merchant_pan_db_new = result["merchant_pan"].iloc[0]
                logger.debug(f"Value of merchant_pan obtained from txn table based on txn_id_upg for DB Validation: {bqr_merchant_pan_db_new}")
                bqr_rrn_db_new = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from txn table based on txn_id_upg for DB Validation : {bqr_rrn_db_new}")
                bqr_org_code_db_new = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from txn table based on txn_id_upg for DB Validation: {bqr_org_code_db_new}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
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
                    "pmt_gateway_2": payment_gateway_db_new,
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
                    "bqr_pmt_status_2": bqr_status_db_new,
                    "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_merchant_pan_2": bqr_merchant_pan_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new,
                    "bqr_org_code_2": bqr_org_code_db_new,
                    "device_serial": str(device_serial_db)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time_upg)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": "{:.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id_upg,
                    "auth_code": auth_code,
                    "rrn": rrn_upg
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref_upg)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code_portal = transaction_details[0]['Auth Code']
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
                    "auth_code": auth_code_portal,
                    "rrn": rr_number
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_102_308():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Two_Callback_After_Expired_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR generation using API and performing two Callback after QR Expiry transaction when auto refund disabled via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 308: TC308
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='YES', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "update terminal_dependency_config set terminal_dependent_enabled=1 where org_code ='" + org_code + "' and acquirer_code='YES' and payment_gateway='ATOS'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = "select * from bharatqr_merchant_config where org_code='" + org_code + "' and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch data from bharatqr_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of bharatqr_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        terminal_info_id = result['terminal_info_id'].values[0]
        logger.debug(f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
        merchant_config_id = result['id'].values[0]
        logger.debug(f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

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

            amount = random.randint(401, 1000)
            logger.debug(f"Entered amount is : {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR generation is : {response}")

            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            query = "select * from bharatqr_txn where org_code='"+org_code+"' and id LIKE '"+datetime.utcnow().strftime('%y%m%d')+"%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of bharatqr_txn table : {result}")
            pid = result["provider_ref_id"].iloc[0]
            logger.debug(f"Value of provider_ref_id obtained from bharatqr_txn table : {pid}")
            sid = result["transaction_secondary_id"].iloc[0]
            logger.debug(f"Value of transaction_secondary_id obtained from bharatqr_txn table : {sid}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from bharatqr_txn table : {txn_id}")
            auth_code = "AE" + txn_id.split('E')[1]
            logger.debug(f"Value of auth_code obtained from bharatqr_txn table : {auth_code}")
            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn obtained from bharatqr_txn table : {rrn}")

            api_details = DBProcessor.get_api_details('callbackYES',request_body={
                "primary_id": pid,
                "secondary_id":sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no":rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for First callback : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table for first callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for first callback : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for first callback : {created_time}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for first callback : {amount_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for first callback : {payment_mode_db}")
            payment_status_db = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for first callback : {payment_status_db}")
            payment_state_db = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for first callback : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for first callback : {acquirer_code_db}")
            mid_db = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table for first callback : {mid_db}")
            tid_db = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table for first callback : {tid_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for first callback : {payment_gateway_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for first callback : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table for first callback : {device_serial_db}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            txn_id_new = result["id"].iloc[0]
            logger.debug(f"Value of id obtained from txn table : {txn_id_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rrn_new}")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code_new}")
            created_time_new = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table : {created_time_new}")
            customer_name_new = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table : {customer_name_new}")
            payer_name_new = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name_new}")
            amount_db_new = int(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table : {amount_db_new}")
            payment_mode_db_new = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table : {payment_mode_db_new}")
            payment_status_db_new = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table : {payment_status_db_new}")
            payment_state_db_new = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table : {payment_state_db_new}")
            acquirer_code_db_new = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db_new}")
            bank_name_db_new = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table : {bank_name_db_new}")
            payer_name_db_new = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name_db_new}")
            mid_db_new = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table : {mid_db_new}")
            tid_db_new = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table : {tid_db_new}")
            payment_gateway_db_new = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table : {payment_gateway_db_new}")
            rr_number_db_new = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table : {rr_number_db_new}")
            settlement_status_db_new = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table : {settlement_status_db_new}")
            device_serial_db_new = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table : {device_serial_db_new}")

            rrn_new_3 = "RE" + str(order_id)
            logger.debug("Generated rrn_new_3 values is: ", rrn_new_3)

            api_details = DBProcessor.get_api_details('callbackYES',request_body={
                "primary_id": pid,
                "secondary_id": sid,
                "txn_amount": str(amount),
                "auth_code": auth_code,
                "ref_no": rrn_new_3,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for Second callback : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table for second callback : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table for second callback : {result}")
            txn_id_new_3 = result["id"].iloc[0]
            logger.debug(f"Value of txn_id obtained from txn table for second callback : {txn_id_new_3}")
            auth_code_new_3 = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table for second callback : {auth_code_new_3}")
            created_time_new_3 = result['created_time'].values[0]
            logger.debug(f"Value of created_time obtained from txn table for second callback : {created_time_new_3}")
            customer_name_new_3 = result['customer_name'].values[0]
            logger.debug(f"Value of customer_name obtained from txn table for second callback : {customer_name_new_3}")
            payer_name_new_3 = result['payer_name'].values[0]
            logger.debug(f"Value of payer_name obtained from txn table for second callback : {payer_name_new_3}")
            amount_db_new_3 = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from txn table for second callback : {amount_db_new_3}")
            payment_mode_db_new_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from txn table for second callback : {payment_mode_db_new_3}")
            payment_status_db_new_3 = result["status"].iloc[0]
            logger.debug(f"Value of status obtained from txn table for second callback : {payment_status_db_new_3}")
            payment_state_db_new_3 = result["state"].iloc[0]
            logger.debug(f"Value of state obtained from txn table for second callback : {payment_state_db_new_3}")
            acquirer_code_db_new_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table for second callback : {acquirer_code_db_new_3}")
            bank_name_db_new_3 = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table for second callback : {bank_name_db_new_3}")
            payer_name_db_new_3 = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table for second callback : {payer_name_db_new_3}")
            mid_db_new_3 = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from txn table for second callback : {mid_db_new_3}")
            tid_db_new_3 = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from txn table for second callback : {tid_db_new_3}")
            payment_gateway_db_new_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Value of payment_gateway obtained from txn table for second callback : {payment_gateway_db_new_3}")
            rr_number_db_new_3 = result["rr_number"].iloc[0]
            logger.debug(f"Value of rr_number obtained from txn table for second callback : {rr_number_db_new_3}")
            settlement_status_db_new_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Value of settlement_status obtained from txn table for second callback : {settlement_status_db_new_3}")
            device_serial_db_new_3 = result['device_serial'].values[0]
            logger.debug(f"Value of device_serial obtained from txn table for second callback : {device_serial_db_new_3}")

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
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                date_and_time_new_3 = date_time_converter.to_app_format(created_time_new_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": "{:.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount)+".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_new,
                    "rrn_2": str(rrn_new),
                    "customer_name_2": customer_name_new,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_new,
                    "date_2": date_and_time_new,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": "{:.2f}".format(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_new_3,
                    "rrn_3": str(rrn_new_3),
                    "customer_name_3": customer_name_new_3,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "auth_code_3": auth_code_new_3,
                    "date_3": date_and_time_new_3
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                # home_page.check_home_page_logo()
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_3)
                payment_status_new_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_3}, {payment_status_new_3}")
                app_auth_code_new_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_new_3}, {app_auth_code_new_3}")
                payment_mode_new_3 = txn_history_page.fetch_txn_type_text()
                logger.info( f"Fetching payment mode from txn history for the txn : {txn_id_new_3}, {payment_mode_new_3}")
                app_txn_id_new_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_txn_id_new_3}")
                app_amount_new_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_3}, {app_amount_new_3}")
                app_date_and_time_new_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_3}, {app_date_and_time_new_3}")
                app_customer_name_new_3 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_new_3}, {app_customer_name_new_3}")
                app_settlement_status_new_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_3}, {app_settlement_status_new_3}")
                app_payment_msg_new_3 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_new_3}, {app_payment_msg_new_3}")
                app_order_id_new_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new_3}, {app_order_id_new_3}")
                app_rrn_new_3 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_3}, {app_rrn_new_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new,
                    "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new,
                    "rrn_2": str(app_rrn_new),
                    "customer_name_2": app_customer_name_new,
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "auth_code_2": app_auth_code_new,
                    "pmt_msg_2": app_payment_msg_new,
                    "date_2": app_date_and_time_new,
                    "pmt_mode_3": payment_mode_new_3,
                    "pmt_status_3": payment_status_new_3.split(':')[1],
                    "txn_amt_3": app_amount_new_3.split(' ')[1],
                    "txn_id_3": app_txn_id_new_3,
                    "rrn_3": str(app_rrn_new_3),
                    "customer_name_3": app_customer_name_new_3,
                    "settle_status_3": app_settlement_status_new_3,
                    "order_id_3": app_order_id_new_3,
                    "auth_code_3": app_auth_code_new_3,
                    "pmt_msg_3": app_payment_msg_new_3,
                    "date_3": app_date_and_time_new_3
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
                date_new = date_time_converter.db_datetime(created_time_new)
                date_new_3 = date_time_converter.db_datetime(created_time_new_3)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "YES",
                    "issuer_code": "YES",
                    "txn_type": "CHARGE",
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "issuer_code_2": "YES",
                    "txn_type_2": "CHARGE",
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code,
                    "auth_code_2": auth_code_new,
                    "date_2": date_new,
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "SETTLED",
                    "rrn_3": str(rrn_new_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "YES",
                    "issuer_code_3": "YES",
                    "txn_type_3": "CHARGE",
                    "mid_3": mid, "tid_3": tid,
                    "org_code_3": org_code,
                    "auth_code_3": auth_code_new_3,
                    "date_3": date_new_3,
                    "device_serial": str(device_serial),
                    "device_serial_2": str(device_serial),
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for first transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of first txn is : {response_1}")
                status_api = response_1["status"]
                logger.debug(f"Value of status obtained from first txnlist api is : {status_api}")
                amount_api = int(response_1["amount"])
                logger.debug(f"Value of amount obtained from first txnlist api is : {amount_api}")
                payment_mode_api = response_1["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from first txnlist api is : {payment_mode_api}")
                state_api = response_1["states"][0]
                logger.debug(f"Value of states obtained from first txnlist api is : {state_api}")
                settlement_status_api = response_1["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from first txnlist api is : {settlement_status_api}")
                issuer_code_api = response_1["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from first txnlist api is : {issuer_code_api}")
                acquirer_code_api = response_1["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from first txnlist api is : {acquirer_code_api}")
                org_code_api = response_1["orgCode"]
                logger.debug(f"Value of orgCode obtained from first txnlist api is : {org_code_api}")
                mid_api = response_1["mid"]
                logger.debug(f"Value of mid obtained from first txnlist api is : {mid_api}")
                tid_api = response_1["tid"]
                logger.debug(f"Value of tid obtained from first txnlist api is : {tid_api}")
                txn_type_api = response_1["txnType"]
                logger.debug(f"Value of txnType obtained from first txnlist api is : {txn_type_api}")
                date_api = response_1["createdTime"]
                logger.debug(f"Value of createdTime obtained from first txnlist api is : {date_api}")
                device_serial_api = response_1["deviceSerial"]
                logger.debug(f"Value of device_serial obtained from first txnlist api is : {device_serial_api}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_new][0]
                logger.debug(f"Response after filtering data of second txn is : {response_2}")
                status_api_new = response_2["status"]
                logger.debug(f"Value of status obtained from second txnlist api is : {status_api_new}")
                amount_api_new = float(response_2["amount"])
                logger.debug(f"Value of amount obtained from second txnlist api is : {amount_api_new}")
                payment_mode_api_new = response_2["paymentMode"]
                logger.debug(f"Value of paymentMode obtained second txnlist api is : {payment_mode_api_new}")
                state_api_new = response_2["states"][0]
                logger.debug(f"Value of states obtained from second txnlist api is : {state_api_new}")
                rrn_api_new = response_2["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from second txnlist api is : {rrn_api_new}")
                settlement_status_api_new = response_2["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from second txnlist api is : {settlement_status_api_new}")
                issuer_code_api_new = response_2["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from second txnlist api is : {issuer_code_api_new}")
                acquirer_code_api_new = response_2["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from second txnlist api is : {acquirer_code_api_new}")
                org_code_api_new = response_2["orgCode"]
                logger.debug(f"Value of orgCode obtained from second txnlist api is : {org_code_api_new}")
                mid_api_new = response_2["mid"]
                logger.debug(f"Value of mid obtained from second txnlist api is : {mid_api_new}")
                tid_api_new = response_2["tid"]
                logger.debug(f"Value of tid obtained from second txnlist api is : {tid_api_new}")
                txn_type_api_new = response_2["txnType"]
                logger.debug(f"Value of txnType obtained from second txnlist api is : {txn_type_api_new}")
                auth_code_api_new = response_2["authCode"]
                logger.debug(f"Value of authCode obtained from second txnlist api is : {auth_code_api_new}")
                date_api_new = response_2["createdTime"]
                logger.debug(f"Value of createdTime obtained from second txnlist api is : {date_api_new}")
                device_serial_api_new = response_2["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from second txnlist api is : {device_serial_api_new}")

                response_3 = [x for x in response["txns"] if x["txnId"] == txn_id_new_3][0]
                logger.debug(f"Response after filtering data of third txn is : {response_3}")
                status_api_new_3 = response_3["status"]
                logger.debug(f"Value of status obtained from third txnlist api is : {status_api_new_3}")
                amount_api_new_3 = float(response_3["amount"])
                logger.debug(f"Value of amount obtained from third txnlist api is : {amount_api_new_3}")
                payment_mode_api_new_3 = response_3["paymentMode"]
                logger.debug(f"Value of paymentMode obtained from third txnlist api is : {payment_mode_api_new_3}")
                state_api_new_3 = response_3["states"][0]
                logger.debug(f"Value of states obtained from third txnlist api is : {state_api_new_3}")
                rrn_api_new_3 = response_3["rrNumber"]
                logger.debug(f"Value of rrNumber obtained from third txnlist api is : {rrn_api_new_3}")
                settlement_status_api_new_3 = response_3["settlementStatus"]
                logger.debug(f"Value of settlementStatus obtained from third txnlist api is : {settlement_status_api_new_3}")
                issuer_code_api_new_3 = response_3["issuerCode"]
                logger.debug(f"Value of issuerCode obtained from third txnlist api is : {issuer_code_api_new_3}")
                acquirer_code_api_new_3 = response_3["acquirerCode"]
                logger.debug(f"Value of acquirerCode obtained from third txnlist api is : {acquirer_code_api_new_3}")
                org_code_api_new_3 = response_3["orgCode"]
                logger.debug(f"Value of orgCode obtained from third txnlist api is: {org_code_api_new_3}")
                mid_api_new_3 = response_3["mid"]
                logger.debug(f"Value of mid obtained from third txnlist api is : {mid_api_new_3}")
                tid_api_new_3 = response_3["tid"]
                logger.debug(f"Value of tid obtained from third txnlist api is : {tid_api_new_3}")
                txn_type_api_new_3 = response_3["txnType"]
                logger.debug(f"Value of txnType obtained from third txnlist api is : {txn_type_api_new_3}")
                auth_code_api_new_3 = response_3["authCode"]
                logger.debug(f"Value of authCode obtained from third txnlist api is : {auth_code_api_new_3}")
                date_api_new_3 = response_3["createdTime"]
                logger.debug(f"Value of createdTime obtained from third txnlist api is : {date_api_new_3}")
                device_serial_api_new_3 = response_3["deviceSerial"]
                logger.debug(f"Value of deviceSerial obtained from third txnlist api is : {device_serial_api_new_3}")

                actual_api_values = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_new,
                    "txn_amt_2": amount_api_new,
                    "pmt_mode_2": payment_mode_api_new,
                    "pmt_state_2": state_api_new,
                    "rrn_2": str(rrn_api_new),
                    "settle_status_2": settlement_status_api_new,
                    "acquirer_code_2": acquirer_code_api_new,
                    "issuer_code_2": issuer_code_api_new,
                    "mid_2": mid_api_new,
                    "txn_type_2": txn_type_api_new,
                    "tid_2": tid_api_new,
                    "org_code_2": org_code_api_new,
                    "auth_code_2": auth_code_api_new,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                    "pmt_status_3": status_api_new_3,
                    "txn_amt_3": amount_api_new_3,
                    "pmt_mode_3": payment_mode_api_new_3,
                    "pmt_state_3": state_api_new_3,
                    "rrn_3": str(rrn_api_new_3),
                    "settle_status_3": settlement_status_api_new_3,
                    "acquirer_code_3": acquirer_code_api_new_3,
                    "issuer_code_3": issuer_code_api_new_3,
                    "mid_3": mid_api_new_3,
                    "txn_type_3": txn_type_api_new_3,
                    "tid_3": tid_api_new_3,
                    "org_code_3": org_code_api_new_3,
                    "auth_code_3": auth_code_api_new_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_3),
                    "device_serial": device_serial_api,
                    "device_serial_2": device_serial_api_new,
                    "device_serial_3": device_serial_api_new_3
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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "acquirer_code": "YES",
                    "mid": mid, "tid": tid,
                    "pmt_gateway": "ATOS",
                    "settle_status": "FAILED",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": float(amount),
                    "bqr_txn_type": "DYNAMIC_QR",
                    "brq_terminal_info_id": terminal_info_id,
                    "bqr_bank_code": "YES",
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    "bqr_org_code": org_code,
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "BHARATQR",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "acquirer_code_2": "YES",
                    "bank_name_2": "Yes Bank",
                    "payer_name_2": payer_name_new,
                    "mid_2": mid,
                    "tid_2": tid,
                    "pmt_gateway_2": "ATOS",
                    "rrn_2": str(rrn_new),
                    "settle_status_2": "SETTLED",
                    "bqr_pmt_status_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": float(amount),
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "brq_terminal_info_id_2": terminal_info_id,
                    "bqr_bank_code_2": "YES",
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_new,
                    "bqr_rrn_2": str(rrn_new),
                    "bqr_org_code_2": org_code,
                    "txn_amt_3": float(amount),
                    "pmt_mode_3": "BHARATQR",
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "acquirer_code_3": "YES",
                    "bank_name_3": "Yes Bank",
                    "payer_name_3": payer_name_new_3,
                    "mid_3": mid, "tid_3": tid,
                    "pmt_gateway_3": "ATOS",
                    "rrn_3": str(rrn_new_3),
                    "settle_status_3": "SETTLED",
                    "bqr_pmt_status_3": "SUCCESS",
                    "bqr_pmt_state_3": "SETTLED",
                    "bqr_txn_amt_3": float(amount),
                    "bqr_txn_type_3": "DYNAMIC_QR",
                    "brq_terminal_info_id_3": terminal_info_id,
                    "bqr_bank_code_3": "YES",
                    "bqr_merchant_config_id_3": merchant_config_id,
                    "bqr_txn_primary_id_3": txn_id_new_3,
                    "bqr_rrn_3": str(rrn_new_3),
                    "bqr_org_code_3": org_code,
                    "device_serial": str(device_serial),
                    "device_serial_2": str(device_serial),
                    "device_serial_3": str(device_serial),
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for DB validation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for DB validation : {result}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for DB validation : {bqr_state_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for DB validation : {bqr_txn_type_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for DB validation : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for DB validation : {bqr_merchant_config_id_db}")
                bqr_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for DB validation : {bqr_org_code_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for DB validation : {bqr_amount_db}")
                brq_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for DB validation : {brq_terminal_info_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for DB validation : {bqr_txn_primary_id_db}")

                query = "select * from bharatqr_txn where id='" + txn_id_new + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for second txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for second txn_id : {result}")
                bqr_status_db_new = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for second txn_id : {bqr_status_db_new}")
                bqr_state_db_new = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for second txn_id : {bqr_state_db_new}")
                bqr_amount_db_new = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for second txn_id : {bqr_amount_db_new}")
                bqr_txn_type_db_new = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for second txn_id : {bqr_txn_type_db_new}")
                brq_terminal_info_id_db_new = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for second txn_id : {brq_terminal_info_id_db_new}")
                bqr_bank_code_db_new = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for second txn_id : {bqr_bank_code_db_new}")
                bqr_merchant_config_id_db_new = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for second txn_id : {bqr_merchant_config_id_db_new}")
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for second txn_id : {bqr_txn_primary_id_db_new}")
                bqr_rrn_db_new = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for second txn_id : {bqr_rrn_db_new}")
                bqr_org_code_db_new = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for second txn_id : {bqr_org_code_db_new}")

                query = "select * from bharatqr_txn where id='" + txn_id_new_3 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table for third txn_id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table for third txn_id : {result}")
                bqr_status_db_new_3 = result["status_code"].iloc[0]
                logger.debug(f"Value of status_code obtained from bharatqr_txn table for third txn_id : {bqr_status_db_new}")
                bqr_state_db_new_3 = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table for third txn_id : {bqr_state_db_new_3}")
                bqr_amount_db_new_3 = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table for third txn_id : {bqr_amount_db_new_3}")
                bqr_txn_type_db_new_3 = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table for third txn_id : {bqr_txn_type_db_new_3}")
                brq_terminal_info_id_db_new_3 = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table for third txn_id : {brq_terminal_info_id_db_new_3}")
                bqr_bank_code_db_new_3 = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table for third txn_id : {bqr_bank_code_db_new_3}")
                bqr_merchant_config_id_db_new_3 = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table for third txn_id : {bqr_merchant_config_id_db_new_3}")
                bqr_txn_primary_id_db_new_3 = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table for third txn_id : {bqr_txn_primary_id_db_new_3}")
                bqr_rrn_db_new_3 = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table for third txn_id : {bqr_rrn_db_new_3}")
                bqr_org_code_db_new_3 = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table for third txn_id : {bqr_org_code_db_new_3}")

                actual_db_values = {
                    "txn_amt": amount_db,
                    "pmt_mode": payment_mode_db,
                    "pmt_status": payment_status_db,
                    "pmt_state": payment_state_db,
                    "acquirer_code": acquirer_code_db,
                    "mid": mid_db, "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "settle_status": settlement_status_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_amount_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "brq_terminal_info_id": brq_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_org_code": bqr_org_code_db,
                    "txn_amt_2": amount_db_new,
                    "pmt_mode_2": payment_mode_db_new,
                    "pmt_status_2": payment_status_db_new,
                    "pmt_state_2": payment_state_db_new,
                    "acquirer_code_2": acquirer_code_db_new,
                    "bank_name_2": bank_name_db_new,
                    "payer_name_2": payer_name_db_new,
                    "mid_2": mid_db_new,
                    "tid_2": tid_db_new,
                    "pmt_gateway_2": payment_gateway_db_new,
                    "rrn_2": rr_number_db_new,
                    "settle_status_2": settlement_status_db_new,
                    "bqr_pmt_status_2": bqr_status_db_new,
                    "bqr_pmt_state_2": bqr_state_db_new,
                    "bqr_txn_amt_2": bqr_amount_db_new,
                    "bqr_txn_type_2": bqr_txn_type_db_new,
                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                    "bqr_bank_code_2": bqr_bank_code_db_new,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                    "bqr_rrn_2": bqr_rrn_db_new,
                    "bqr_org_code_2": bqr_org_code_db_new,
                    "txn_amt_3": amount_db_new_3,
                    "pmt_mode_3": payment_mode_db_new_3,
                    "pmt_status_3": payment_status_db_new_3,
                    "pmt_state_3": payment_state_db_new_3,
                    "acquirer_code_3": acquirer_code_db_new_3,
                    "bank_name_3": bank_name_db_new_3,
                    "payer_name_3": payer_name_db_new_3,
                    "mid_3": mid_db_new_3,
                    "tid_3": tid_db_new_3,
                    "pmt_gateway_3": payment_gateway_db_new_3,
                    "rrn_3": rr_number_db_new_3,
                    "settle_status_3": settlement_status_db_new_3,
                    "bqr_pmt_status_3": bqr_status_db_new_3,
                    "bqr_pmt_state_3": bqr_state_db_new_3,
                    "bqr_txn_amt_3": bqr_amount_db_new_3,
                    "bqr_txn_type_3": bqr_txn_type_db_new_3,
                    "brq_terminal_info_id_3": brq_terminal_info_id_db_new_3,
                    "bqr_bank_code_3": bqr_bank_code_db_new_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_new_3,
                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_new_3,
                    "bqr_rrn_3": bqr_rrn_db_new_3,
                    "bqr_org_code_3": bqr_org_code_db_new_3,
                    "device_serial": str(device_serial_db),
                    "device_serial_2": str(device_serial_db_new),
                    "device_serial_3": str(device_serial_db_new_3)
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new)
                date_and_time_portal_3 = date_time_converter.to_portal_format(created_time_new_3)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new,
                    "auth_code_2": auth_code_new,
                    "rrn_2": rrn_new,
                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "BHARATQR",
                    "txn_amt_3": f"{str(amount)}.00",
                    "username_3": app_username,
                    "txn_id_3": txn_id_new_3,
                    "auth_code_3": auth_code_new_3,
                    "rrn_3": rrn_new_3
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                date_time_2 = transaction_details[1]['Date & Time']
                transaction_id_2 = transaction_details[1]['Transaction ID']
                total_amount_2 = transaction_details[1]['Total Amount'].split()
                auth_code_portal_2 = transaction_details[1]['Auth Code']
                rr_number_2 = transaction_details[1]['RR Number']
                transaction_type_2 = transaction_details[1]['Type']
                status_2 = transaction_details[1]['Status']
                username_2 = transaction_details[1]['Username']

                date_time_3 = transaction_details[0]['Date & Time']
                transaction_id_3 = transaction_details[0]['Transaction ID']
                total_amount_3 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_3 = transaction_details[0]['Auth Code']
                rr_number_3 = transaction_details[0]['RR Number']
                transaction_type_3 = transaction_details[0]['Type']
                status_3 = transaction_details[0]['Status']
                username_3 = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": username_2,
                    "txn_id_2": transaction_id_2,
                    "auth_code_2": auth_code_portal_2,
                    "rrn_2": rr_number_2,
                    "date_time_3": date_time_3,
                    "pmt_state_3": str(status_3),
                    "pmt_type_3": transaction_type_3,
                    "txn_amt_3": total_amount_3[1],
                    "username_3": username_3,
                    "txn_id_3": transaction_id_3,
                    "auth_code_3": auth_code_portal_3,
                    "rrn_3": rr_number_3
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_1, txn_time_1 = date_time_converter.to_chargeslip_format(created_time_new)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_new_3)

                expected_charge_slip_values_1 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_1,
                    'time': txn_time_1, 'AUTH CODE': str(auth_code_new)
                }

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_new_3),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_new_3)
                }

                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_1)

                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_new_3,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_2)

                if chargeslip_val_result_1 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

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