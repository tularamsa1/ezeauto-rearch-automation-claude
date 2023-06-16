import sys
import random
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
def test_common_100_102_314():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_BQRV4_BQR_Partial_Refund_API_YES_ATOS
    Sub Feature Description: Tid Dep - Verification of a BQRV4_BQR Partial Refund through API via YES_ATOS
    TC naming code description: 100: Payment Method, 102: BQRV4, 314: TC314
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

            rrn = "RE" + txn_id.split('E')[1]
            logger.debug(f"Value of rrn is : {rrn}")

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for BQR Stop Payment : {response}")

            refund_amount = amount - 100
            logger.debug(f"Value of refund amount is : {refund_amount}")

            api_details = DBProcessor.get_api_details('paymentRefund',request_body={
                "username": app_username,
                "password": app_password,
                "amount": refund_amount,
                "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for partial refund is: {response}")
            error_message = response["message"]
            logger.debug(f"Value of message obtained from partial refund response is: {error_message}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Value of auth_code obtained from txn table : {auth_code}")
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
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Value of acquirer_code obtained from txn table : {acquirer_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Value of bank_name obtained from txn table : {bank_name_db}")
            payer_name_db = result["payer_name"].iloc[0]
            logger.debug(f"Value of payer_name obtained from txn table : {payer_name_db}")
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
                    "date": date_and_time
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
                    "error message": "Partial Refund is not supported for YES transactions.",
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
                    "mid": mid_api,
                    "txn_type": txn_type_api,
                    "tid": tid_api,
                    "org_code": org_code_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "error message": error_message,
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
                    "txn_amt": float(amount),
                    "pmt_mode": "BHARATQR",
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "acquirer_code": "YES",
                    "bank_name": "Yes Bank",
                    "payer_name": payer_name,
                    "mid": mid, "tid": tid,
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
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of bharatqr_txn table : {result}")
                bqr_status_db = result["status_code"].iloc[0]
                logger.debug(f"Value of status obtained from bharatqr_txn table : {bqr_status_db}")
                bqr_state_db = result["state"].iloc[0]
                logger.debug(f"Value of state obtained from bharatqr_txn table : {bqr_state_db}")
                bqr_amount_db = float(result["txn_amount"].iloc[0])
                logger.debug(f"Value of txn_amount obtained from bharatqr_txn table : {bqr_amount_db}")
                bqr_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from bharatqr_txn table : {bqr_txn_type_db}")
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                logger.debug(f"Value of terminal_info_id obtained from bharatqr_txn table : {bqr_terminal_info_id_db}")
                bqr_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from bharatqr_txn table : {bqr_bank_code_db}")
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                logger.debug(f"Value of merchant_config_id obtained from bharatqr_txn table : {bqr_merchant_config_id_db}")
                bqr_txn_primary_id_db = result["transaction_primary_id"].iloc[0]
                logger.debug(f"Value of transaction_primary_id obtained from bharatqr_txn table : {bqr_txn_primary_id_db}")
                bqr_rrn_db = result['rrn'].values[0]
                logger.debug(f"Value of rrn obtained from bharatqr_txn table : {bqr_rrn_db}")
                bqr_org_code_db = result['org_code'].values[0]
                logger.debug(f"Value of org_code obtained from bharatqr_txn table : {bqr_org_code_db}")

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
                    "brq_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "device_serial": str(device_serial_db),
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
                expected_charge_slip_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)

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