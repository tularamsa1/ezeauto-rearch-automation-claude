import random
import string
import sys
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_101_181():
    """
    Sub Feature Code: Tid Dep - Tid Dep - UI_Common_PM_UPI_amount_mismatch_Via_UPI_Success_Callback_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Performing a amount mismatch using pure upi success callback via KOTAK_ATOS
    TC naming code description: 100: Payment method, 101: UPI, 181: Testcase ID
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table is : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'KOTAK_ATOS' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Fetching pgMerchantId from upi_merchant_config table : {pg_merchant_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, upi_mc_id)

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device_serial from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.info(f"Fetching device_serial from terminal_info table : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            logger.debug(f"Initiating UPI QR for the amount of {amount}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"order_id is : {order_id}")

            api_details = DBProcessor.get_api_details('TidDepUpiQRGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "qrCodeType": "UPI",
                "orderNumber": str(order_id),
                "deviceSerial": str(device_serial)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating dynamic qr for pure upi is : {response}")
            txn_id = response["txnId"]
            logger.debug(f"Value of txnId obtained from dynamic qr generation response : {txn_id}")

            query = "select * from upi_txn where org_code = '" + str(org_code) + "' AND txn_id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the upi_txn table for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for upi_txn table is : {result}")
            txn_ref = result['txn_ref'].iloc[0]
            logger.debug(f"Fetching txn_ref from the upi_txn table is : {txn_ref}")

            auth_code = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code : {auth_code}")
            ref_id = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id : {ref_id}")
            secondary_id = txn_ref.split("EA")[1]
            logger.debug(f" Value of secondary id is : {secondary_id}")
            amount = amount + 1
            logger.debug(f" Value of amount mismatch is : {amount}")
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + "@upi"
            logger.debug(f" Value of customer vpa is : {customer_vpa}")

            #callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": txn_ref,
                "auth_code": auth_code,
                "merchant_vpa": vpa,
                "customer_vpa": customer_vpa,
                "secondary_id": secondary_id,
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi callback is : {response}")

            query = "select * from invalid_pg_request where request_id ='" + str(txn_ref) + "';"
            logger.debug(f"Query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for invalid_pg_request table is : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f" Value of txn_id from invalid_pg_request table is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f" Value of payment_mode from invalid_pg_request table is : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f" Value of bank_code from invalid_pg_request table is : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f" Value of org_code from invalid_pg_request table is : {ipr_org_code}")
            ipr_auth_code = result["auth_code"].iloc[0]
            logger.debug(f" Value of auth_code from invalid_pg_request table is : {ipr_auth_code}")
            ipr_amount = result["amount"].iloc[0]
            logger.debug(f" Value of amount from invalid_pg_request table is : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f" Value of rrn from invalid_pg_request table is : {ipr_rrn}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f" Value of mid from invalid_pg_request table is : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f" Value of tid from invalid_pg_request table is : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f" Value of config_id from invalid_pg_request table is : {ipr_config_id}")
            ipr_vpa = result["vpa"].iloc[0]
            logger.debug(f" Value of vpa from invalid_pg_request table is : {ipr_vpa}")
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            logger.debug(f" Value of pg_merchant_id from invalid_pg_request table is : {ipr_pg_merchant_id}")
            ipr_error_message = result["error_message"].iloc[0]
            logger.debug(f" Value of error_message from invalid_pg_request table is : {ipr_error_message}")

            query = "select * from txn where id = '" + str(ipr_txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table for the {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table is : {customer_name}")
            username = result['username'].values[0]
            logger.debug(f"Fetching username from the txn table is : {username}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table is : {created_time}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from the txn table is : {external_ref}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code_db from the txn table is : {auth_code_db}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "rrn": str(ref_id),
                    # "order_id": external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                logger.info(f"Fetching payment_mode from txn history for the txn : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {ipr_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    # "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)

                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns is : {response_in_list}")

                for elements in response_in_list:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")

                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                device_serial_api = response["deviceSerial"]
                logger.debug(f"Value of device_serial is: {device_serial_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "device_serial": str(device_serial_api)
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "bank_name": "Kotak Mahindra",
                    "payer_name": payer_name,
                    "acquirer_code": "KOTAK",
                    "rrn": str(ref_id),
                    "txn_type": txn_type,
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "KOTAK",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(ref_id),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "ipr_error_msg": "Actual =" + str(amount) + " Expected =" + str(amount - 1) + ".00",
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + str(ipr_txn_id) + "'"
                logger.debug(f"Query to fetch data for actual db values from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table based on txn_id : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table based on txn_id : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table based on txn_id : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table based on txn_id : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table based on txn_id : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table based on txn_id : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table based on txn_id : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table based on txn_id : {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table based on txn_id : {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table based on txn_id : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table based on txn_id : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table based on txn_id : {mid_db}")
                txn_type_db = result['txn_type'].values[0]
                logger.debug(f"Fetching actual db txn_type value from the txn table based on txn_id : {txn_type_db}")
                payer_name_db = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table based on txn_id : {payer_name_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table based on txn_id : {rrn_db}")

                query = "select device_serial from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch device_serial from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                device_serial_db = result['device_serial'].values[0]

                query = "select * from upi_txn where txn_id='" + str(ipr_txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_txn_status": upi_status_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bank_name":bank_name_db,
                    "payer_name": payer_name_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "ipr_error_msg": ipr_error_message,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------
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
                    "username": username,
                    "txn_id": ipr_txn_id,
                    "auth_code": "-" if auth_code_db is None else auth_code_db,
                    "rrn": "-" if ref_id is None else ref_id
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)

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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.portalVal
@pytest.mark.chargeSlipVal
def test_common_100_101_182():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_UPG_AUTHORIZED_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a upg authorized txn using UPI Success Callback via Kotak_ATOS
    TC naming code description: 100: Payment method, 101: UPI, 182: Testcase ID
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
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table is : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency
        query = "update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='" + org_code + "' and payment_gateway = 'KOTAK_ATOS' and payment_mode = 'UPI';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password
        })

        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"Fetching pgMerchantId from upi_merchant_config table : {pg_merchant_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, upi_mc_id)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(301, 400)
            logger.debug(f"Generated random amount : {amount}")
            auth_code = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code : {auth_code}")
            ref_id = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id : {ref_id}")
            txn_id = '230306092416286E' + str(random.randint(111111111, 999999999))
            logger.debug(f"Generated random txn_id : {txn_id}")
            random_generated_primary_id = 'AGU0007921919182EA230306E' + str(random.randint(1111111111,9999999999))
            logger.debug(f"Generated random primary_id : {random_generated_primary_id}")
            random_generated_secondary_id = random_generated_primary_id.split("EA")[1]
            logger.debug(f"Generated random secondary_id : {random_generated_secondary_id}")
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + "@upi"
            logger.debug(f" Generated value of customer vpa is : {customer_vpa}")

            #callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": random_generated_primary_id,
                "auth_code": auth_code,
                "merchant_vpa": vpa,
                "customer_vpa": customer_vpa,
                "secondary_id": random_generated_secondary_id,
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi callback is : {response}")

            query = "select * from invalid_pg_request where request_id ='" + str(random_generated_primary_id) + "';"
            logger.debug(f"Query to fetch data from the invalid_pg_request table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for invalid_pg_request table is : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f" Value of txn_id from invalid_pg_request table is : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f" Value of payment_mode from invalid_pg_request table is : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f" Value of bank_code from invalid_pg_request table is : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f" Value of org_code from invalid_pg_request table is : {ipr_org_code}")
            ipr_auth_code = result["auth_code"].iloc[0]
            logger.debug(f" Value of auth_code from invalid_pg_request table is : {ipr_auth_code}")
            ipr_amount = result["amount"].iloc[0]
            logger.debug(f" Value of amount from invalid_pg_request table is : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f" Value of rrn from invalid_pg_request table is : {ipr_rrn}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f" Value of mid from invalid_pg_request table is : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f" Value of tid from invalid_pg_request table is : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f" Value of config_id from invalid_pg_request table is : {ipr_config_id}")
            ipr_vpa = result["vpa"].iloc[0]
            logger.debug(f" Value of vpa from invalid_pg_request table is : {ipr_vpa}")
            ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
            logger.debug(f" Value of pg_merchant_id from invalid_pg_request table is : {ipr_pg_merchant_id}")
            ipr_error_message = result["error_message"].iloc[0]
            logger.debug(f" Value of error_message from invalid_pg_request table is : {ipr_error_message}")

            query = "select * from txn where id = '" + str(ipr_txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table for the {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table is : {customer_name}")
            username = result['username'].values[0]
            logger.debug(f"Fetching username from the txn table is : {username}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table is : {created_time}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"Fetching external_ref from the txn table is : {external_ref}")
            auth_code_db = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code_db from the txn table is : {auth_code_db}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of App Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": ipr_txn_id,
                    "rrn": str(ref_id),
                    # "order_id": external_ref,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)

                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                # home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)

                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {ipr_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {ipr_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {ipr_txn_id}, {app_payment_msg}")
                # app_order_id = txn_history_page.fetch_order_id_text()
                # logger.info(f"Fetching txn order_id from txn history for the txn : {ipr_txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    # "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)

                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns is : {response_in_list}")

                for elements in response_in_list:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api is : {state_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api is : {rrn_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "bank_name": "Kotak Mahindra",
                    "payer_name": payer_name,
                    "acquirer_code": "KOTAK",
                    "rrn": str(ref_id),
                    "txn_type": txn_type,
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "KOTAK",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(ref_id),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": customer_vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "ipr_error_msg": "UPI PgTxnRef Tampered "+ str(random_generated_primary_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + str(ipr_txn_id) + "'"
                logger.debug(f"Query to fetch data for actual db values from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table based on txn_id : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table based on txn_id : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table based on txn_id : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table based on txn_id : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table based on txn_id : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table based on txn_id : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table based on txn_id : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table based on txn_id : {bank_code_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table based on txn_id : {bank_name_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table based on txn_id : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table based on txn_id : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table based on txn_id : {mid_db}")
                txn_type_db = result['txn_type'].values[0]
                logger.debug(f"Fetching actual db txn_type value from the txn table based on txn_id : {txn_type_db}")
                payer_name_db = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table based on txn_id : {payer_name_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table based on txn_id : {rrn_db}")

                query = "select * from upi_txn where txn_id='" + str(ipr_txn_id) + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_txn_status": upi_status_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bank_name":bank_name_db,
                    "payer_name": payer_name_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "ipr_pmt_mode": ipr_payment_mode,
                    "ipr_bank_code": ipr_bank_code,
                    "ipr_org_code": ipr_org_code,
                    "ipr_auth_code": ipr_auth_code,
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "ipr_error_msg": ipr_error_message
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------
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
                    "username": username,
                    "txn_id": ipr_txn_id,
                    "auth_code": "-" if auth_code_db is None else auth_code_db,
                    "rrn": "-" if ref_id is None else ref_id
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)

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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)