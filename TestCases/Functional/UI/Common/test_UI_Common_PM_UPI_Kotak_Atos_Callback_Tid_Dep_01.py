import sys
import time
import pytest
import random
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
def test_common_100_101_174():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Success_Callback_KOTAK_ATOS_Tid_Dep
    Sub Feature Description: Tid Dep - Verification of a successful upi txn using UPI Success Callback via Kotak_ATOS
    TC naming code description: 100: Payment method, 101: UPI, 174: Testcase ID
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

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

            amount = random.randint(301, 400)
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
                "merchant_vpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi callback is : {response}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from the txn table for the {txn_id} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table is : {created_time}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(ref_id),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
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
                home_page.check_home_page_logo()
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
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
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
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(ref_id),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "device_serial": str(device_serial),
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
                    if elements["txnId"] == txn_id:
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
                        auth_code_api = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api is : {auth_code_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api is : {date_api}")
                        customer_name_api = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api is : {customer_name_api}")
                        payer_name_api = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api is : {payer_name_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api is : {device_serial_api}")

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
                    "device_serial": str(device_serial_api),
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
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
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "AUTHORIZED",
                    "mid": mid,
                    "tid": tid,
                    "device_serial": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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
                device_serial_db = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table based on txn_id : {device_serial_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
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
                    "bank_name": bank_name_db,
                    "payer_name": payer_name_db,
                    "rrn": rrn_db,
                    "txn_type": txn_type_db,
                    "device_serial": str(device_serial_db)
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

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
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if ref_id is None else ref_id
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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)

                expected_charge_slip_values = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(ref_id),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': str(auth_code)
                }

                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_charge_slip_values)
            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation-----------------------------------------

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
def test_common_100_101_175():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_2_Success_Callback_After_QR_Expiry_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a successful upi txn using 2 UPI Success Callback after QR expiry via Kotak_ATOS
    TC naming code description: 100: Payment method, 101: UPI, 175: Testcase ID
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

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

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details for QR Exipry Time : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received from UPI QR Expiry time : {response}")

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

            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
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

            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            query = "select * from upi_txn where org_code = '" + str(org_code) + "' AND txn_id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the upi_txn table for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for upi_txn table is : {result}")
            txn_ref = result['txn_ref'].iloc[0]
            logger.debug(f"Fetching txn_ref from the upi_txn table is : {txn_ref}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from the txn table for dynamic qr generation is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from the txn table for dynamic qr generation : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for dynamic qr generation : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for dynamic qr generation : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for dynamic qr generation : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for dynamic qr generation : {txn_type}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table for dynamic qr generation : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for dynamic qr generation : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for dynamic qr generation : {created_time}")

            auth_code_2 = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code for first callback is : {auth_code_2}")
            ref_id_2 = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id for first callback is : {ref_id_2}")

            #first callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id_2,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": txn_ref,
                "auth_code": auth_code_2,
                "merchant_vpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi first callback is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for first callback is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for the txn table from first callback is : {result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching id from the txn table from first callback is : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table from first callback is : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table from first callback is : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table from first callback is : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table from first callback is : {txn_type_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table from first callback is : {created_time_2}")

            auth_code_3 = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code for second callback is : {auth_code_3}")
            ref_id_3 = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id for second callback is : {ref_id_3}")

            #second callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id_3,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": txn_ref,
                "auth_code": auth_code_3,
                "merchant_vpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi second callback is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for second callback is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for the txn table from second callback is : {result}")
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching id from the txn table from second callback is : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table from second callback is : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table from second callback is : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table from second callback is : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table from second callback is : {txn_type_3}")
            created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table from second callback is : {created_time_3}")
            status_db_3 = result["status"].iloc[0]
            logger.debug(f"Fetching actual db status value from the txn table for second callback : {status_db_3}")
            payment_mode_db_3 = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching actual db payment_mode value from the txn table for second callback : {payment_mode_db_3}")
            amount_db_3 = int(result["amount"].iloc[0])
            logger.debug(f"Fetching actual db amount value from the txn table for second callback : {amount_db_3}")
            state_db_3 = result["state"].iloc[0]
            logger.debug(f"Fetching actual db state value from the txn table for second callback : {state_db_3}")
            payment_gateway_db_3 = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching actual db payment_gateway value from the txn table for second callback : {payment_gateway_db_3}")
            acquirer_code_db_3 = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching actual db acquirer_code value from the txn table for second callback : {acquirer_code_db_3}")
            settlement_status_db_3 = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching actual db settlement_status value from the txn table for second callback : {settlement_status_db_3}")
            bank_code_db_3 = result["bank_code"].iloc[0]
            logger.debug(f"Fetching actual db bank_code value from the txn table for second callback : {bank_code_db_3}")
            mid_db_3 = result['mid'].values[0]
            logger.debug(f"Fetching actual db mid value from the txn table for second callback : {mid_db_3}")
            tid_db_3 = result['tid'].values[0]
            logger.debug(f"Fetching actual db tid value from the txn table for second callback : {tid_db_3}")
            bank_name_db_3 = result["bank_name"].iloc[0]
            logger.debug(f"Fetching actual db bank_name value from the txn table for second callback : {bank_name_db_3}")
            payer_name_db_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching actual db payer_name value from the txn table for second callback : {payer_name_db_3}")
            rrn_db_3 = result['rr_number'].values[0]
            logger.debug(f"Fetching actual db rr_number value from the txn table for second callback : {rrn_db_3}")
            device_serial_db_3 = result['device_serial'].values[0]
            logger.debug(f"Fetching actual db device_serial value from the txn table for second callback : {device_serial_db_3}")

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(created_time_3)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(ref_id_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,

                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount) + ".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "rrn_3": str(ref_id_3),
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "auth_code_3": auth_code_3,
                    "date_3": date_and_time_3
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")

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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_2}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_rrn_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,

                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,

                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "settle_status_3": app_settlement_status_3,
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    "customer_name_3": app_customer_name_3,
                    "payer_name_3": payer_name_3,
                    "order_id_3": app_order_id_3,
                    "pmt_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_2 = date_time_converter.db_datetime(created_time_2)
                date_3 = date_time_converter.db_datetime(created_time_3)

                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "device_serial": str(device_serial),

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(ref_id_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": txn_type_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "auth_code_2": auth_code_2,
                    "date_2": date_2,
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "device_serial_2": str(device_serial),

                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": amount,
                    "pmt_mode_3": "UPI",
                    "pmt_state_3": "SETTLED",
                    "rrn_3": str(ref_id_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "issuer_code_3": "KOTAK",
                    "txn_type_3": txn_type_3,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code_txn_3,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                #txn list for QR Generation
                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id {txn_id} for dynamic qr generation is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received from txnlist api for dynamic qr generation is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns after dynamic qr generation is : {response_in_list}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for dynamic qr generation is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for dynamic qr generation is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for dynamic qr generation is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for dynamic qr generation is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for dynamic qr generation is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for dynamic qr generation is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for dynamic qr generation is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for dynamic qr generation is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for dynamic qr generation is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for dynamic qr generation is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for dynamic qr generation is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for dynamic qr generation is : {date_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for dynamic qr generation is : {device_serial_api}")

                #txn list for 1st callback
                for elements in response_in_list:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for first callback is : {status_api_2}")
                        amount_api_2 = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for first callback is : {amount_api_2}")
                        payment_mode_api_2 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for first callback is : {payment_mode_api_2}")
                        state_api_2 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for first callback is : {state_api_2}")
                        rrn_api_2 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for first callback is : {rrn_api_2}")
                        settlement_status_api_2 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for first callback is : {settlement_status_api_2}")
                        issuer_code_api_2 = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for first callback is : {issuer_code_api_2}")
                        acquirer_code_api_2 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for first callback is : {acquirer_code_api_2}")
                        org_code_api_2 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for first callback is : {org_code_api_2}")
                        mid_api_2 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for first callback is : {mid_api_2}")
                        tid_api_2 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for first callback is : {tid_api_2}")
                        txn_type_api_2 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for first callback is : {txn_type_api_2}")
                        auth_code_api_2 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for first callback is : {auth_code_api_2}")
                        date_api_2 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for first callback is : {date_api_2}")
                        customer_name_api_2 = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api for first callback is : {customer_name_api_2}")
                        payer_name_api_2 = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api for first callback is : {payer_name_api_2}")
                        device_serial_api_2 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for first callback is : {device_serial_api_2}")

                #txn list for 2nd callback
                for elements in response_in_list:
                    if elements["txnId"] == txn_id_3:
                        status_api_3 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for second callback is : {status_api_3}")
                        amount_api_3 = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for second callback is : {amount_api_3}")
                        payment_mode_api_3 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for second callback is : {payment_mode_api_3}")
                        state_api_3 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for second callback is : {state_api_3}")
                        rrn_api_3 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for second callback is : {rrn_api_3}")
                        settlement_status_api_3 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for second callback is : {settlement_status_api_3}")
                        issuer_code_api_3 = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for second callback is : {issuer_code_api_3}")
                        acquirer_code_api_3 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for second callback is : {acquirer_code_api_3}")
                        org_code_api_3 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for second callback is : {org_code_api_3}")
                        mid_api_3 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for second callback is : {mid_api_3}")
                        tid_api_3 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for second callback is : {tid_api_3}")
                        txn_type_api_3 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for second callback is : {txn_type_api_3}")
                        auth_code_api_3 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for second callback is : {auth_code_api_3}")
                        date_api_3 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for second callback is : {date_api_3}")
                        customer_name_api_3 = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api for second callback is : {customer_name_api_3}")
                        payer_name_api_3 = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api for second callback is : {payer_name_api_3}")
                        device_serial_api_3 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for second callback is : {device_serial_api_3}")

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
                    "device_serial": str(device_serial_api),

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code_2": auth_code_api_2,
                    "customer_name_2": customer_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "device_serial_2": str(device_serial_api_2),

                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3,
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "txn_type_3": txn_type_api_3,
                    "mid_3": mid_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "auth_code_3": auth_code_api_3,
                    "customer_name_3": customer_name_api_3,
                    "payer_name_3": payer_name_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "device_serial_3": str(device_serial_api_3)
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
                    "pmt_status": "EXPIRED",
                    "pmt_state": "EXPIRED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "EXPIRED",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": txn_type,
                    "bank_name": "Kotak Mahindra",
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "device_serial": str(device_serial),

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "KOTAK_ATOS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "KOTAK_WL",
                    "upi_mc_id_2": upi_mc_id,
                    "txn_type_2": txn_type_2,
                    "bank_name_2": "Kotak Mahindra",
                    "payer_name_2": payer_name_2,
                    "rrn_2": str(ref_id_2),
                    "device_serial_2": str(device_serial),

                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": amount,
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "bank_code_3": "KOTAK",
                    "pmt_gateway_3": "KOTAK_ATOS",
                    "mid_3": mid,
                    "tid_3": tid,
                    "upi_txn_status_3": "AUTHORIZED",
                    "upi_txn_type_3": "PAY_QR",
                    "upi_bank_code_3": "KOTAK_WL",
                    "upi_mc_id_3": upi_mc_id,
                    "txn_type_3": txn_type_3,
                    "bank_name_3": "Kotak Mahindra",
                    "payer_name_3": payer_name_3,
                    "rrn_3": str(ref_id_3),
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data for actual db values from txn table for dynamic qr generation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table for dynamic qr generation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table for dynamic qr generation : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table for dynamic qr generation : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table for dynamic qr generation : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table for dynamic qr generation : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table for dynamic qr generation : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table for dynamic qr generation : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table for dynamic qr generation : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table for dynamic qr generation : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table for dynamic qr generation : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table for dynamic qr generation : {mid_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table for dynamic qr generation : {bank_name_db}")
                payer_name_db = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table for dynamic qr generation : {payer_name_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table for dynamic qr generation : {rrn_db}")
                device_serial_db = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table for dynamic qr generation : {device_serial_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for dynamic qr generation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for dynamic qr generation : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for dynamic qr generation : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for dynamic qr generation : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for dynamic qr generation : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for dynamic qr generation : {upi_mc_id_db}")

                query = "select * from txn where id='" + txn_id_2 + "';"
                logger.debug(f"Query to fetch data for actual db values from txn table for first callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table for first callback : {result}")
                status_db_2 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table for first callback : {status_db_2}")
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table for first callback : {payment_mode_db_2}")
                amount_db_2 = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table for first callback : {amount_db_2}")
                state_db_2 = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table for first callback : {state_db_2}")
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table for first callback : {payment_gateway_db_2}")
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table for first callback : {acquirer_code_db_2}")
                bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table for first callback : {bank_code_db_2}")
                tid_db_2 = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table for first callback : {tid_db_2}")
                mid_db_2 = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table for first callback : {mid_db_2}")
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table for first callback : {settlement_status_db_2}")
                bank_name_db_2 = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table for first callback : {bank_name_db_2}")
                payer_name_db_2 = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table for first callback : {payer_name_db_2}")
                rrn_db_2 = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table for first callback : {rrn_db_2}")
                device_serial_db_2 = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table for first callback : {device_serial_db_2}")

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for first callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for first callback : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for first callback : {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for first callback : {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for first callback : {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for first callback : {upi_mc_id_db_2}")

                query = "select * from upi_txn where txn_id='" + txn_id_3 + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for second callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for second callback : {result}")
                upi_status_db_3 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for second callback : {upi_status_db_3}")
                upi_txn_type_db_3 = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for second callback : {upi_txn_type_db_3}")
                upi_bank_code_db_3 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for second callback : {upi_bank_code_db_3}")
                upi_mc_id_db_3 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for second callback : {upi_mc_id_db_3}")

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type,
                    "bank_name": bank_name_db,
                    "payer_name": payer_name_db,
                    "rrn": str(rrn_db),
                    "device_serial": str(device_serial_db),

                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "txn_type_2": txn_type_2,
                    "bank_name_2": bank_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "rrn_2": str(rrn_db_2),
                    "device_serial_2": str(device_serial_db_2),

                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "txn_amt_3": amount_db_3,
                    "upi_txn_status_3": upi_status_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "upi_txn_type_3": upi_txn_type_db_3,
                    "upi_bank_code_3": upi_bank_code_db_3,
                    "upi_mc_id_3": upi_mc_id_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "txn_type_3": txn_type_3,
                    "bank_name_3": bank_name_db_3,
                    "payer_name_3": payer_name_db_3,
                    "rrn_3": str(rrn_db_3),
                    "device_serial_3": str(device_serial_db_3)
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
                date_and_time_portal_new = date_time_converter.to_portal_format(created_time_2)
                date_and_time_portal_new_3 = date_time_converter.to_portal_format(created_time_3)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
                    "date_time_2": date_and_time_portal_new,

                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": "-" if rrn_db_2 is None else rrn_db_2,
                    "date_time_3": date_and_time_portal_new_3,

                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "UPI",
                    "txn_amt_3": f"{str(amount)}.00",
                    "username_3": app_username,
                    "txn_id_3": txn_id_3,
                    "auth_code_3": "-" if auth_code_3 is None else auth_code_3,
                    "rrn_3": "-" if rrn_db_3 is None else rrn_db_3,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_new_3 = transaction_details[0]['Date & Time']
                transaction_id_new_3 = transaction_details[0]['Transaction ID']
                total_amount_new_3 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_new_3 = transaction_details[0]['Auth Code']
                rr_number_new_3 = transaction_details[0]['RR Number']
                transaction_type_new_3 = transaction_details[0]['Type']
                status_new_3 = transaction_details[0]['Status']
                username_new_3 = transaction_details[0]['Username']

                date_time_new = transaction_details[1]['Date & Time']
                transaction_id_new = transaction_details[1]['Transaction ID']
                total_amount_new = transaction_details[1]['Total Amount'].split()
                auth_code_portal_new = transaction_details[1]['Auth Code']
                rr_number_new = transaction_details[1]['RR Number']
                transaction_type_new = transaction_details[1]['Type']
                status_new = transaction_details[1]['Status']
                username_new = transaction_details[1]['Username']

                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                auth_code_portal = transaction_details[2]['Auth Code']
                rr_number = transaction_details[2]['RR Number']
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_new,
                    "pmt_state_2": str(status_new),
                    "pmt_type_2": transaction_type_new,
                    "txn_amt_2": total_amount_new[1],
                    "username_2": username_new,
                    "txn_id_2": transaction_id_new,
                    "auth_code_2": auth_code_portal_new,
                    "rrn_2": rr_number_new,
                    "date_time_3": date_time_new_3,
                    "pmt_state_3": str(status_new_3),
                    "pmt_type_3": transaction_type_new_3,
                    "txn_amt_3": total_amount_new_3[1],
                    "username_3": username_new_3,
                    "txn_id_3": transaction_id_new_3,
                    "auth_code_3": auth_code_portal_new_3,
                    "rrn_3": rr_number_new_3
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # ------------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(ref_id_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date_2,
                    'time': txn_time_2,
                    'AUTH CODE': str(auth_code_2)
                }
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_2)
                expected_charge_slip_values_3 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(ref_id_3),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date_3,
                    'time': txn_time_3,
                    'AUTH CODE': str(auth_code_3)
                }

                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_3)
                if chargeslip_val_result_3 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation-------------------------

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
def test_common_100_101_176():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UP_2_Success_Callback_Before_QR_Expiry_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a successful upi txn using 2 UPI Success Callback before QR expiry via Kotak_ATOS
    TC naming code description: 100: Payment method, 101: UPI, 176: Testcase ID
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
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

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

            amount = random.randint(301, 400)
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

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch data from the txn table for dynamic qr generation is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result from the txn table for dynamic qr generation : {result}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for dynamic qr generation : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for dynamic qr generation : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for dynamic qr generation : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table for dynamic qr generation : {txn_type}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table for dynamic qr generation : {rrn}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for dynamic qr generation : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for dynamic qr generation : {created_time}")

            auth_code_2 = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code for first callback is : {auth_code_2}")
            ref_id_2 = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id for first callback is : {ref_id_2}")

            #first callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id_2,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": txn_ref,
                "auth_code": auth_code_2,
                "merchant_vpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi first callback is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for first callback is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for the txn table from first callback is : {result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching id from the txn table from first callback is : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table from first callback is : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table from first callback is : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table from first callback is : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table from first callback is : {txn_type_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table from first callback is : {created_time_2}")

            auth_code_3 = str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random auth_code for second callback is : {auth_code_3}")
            ref_id_3 = "R" + str(random.randint(110000000, 110099999))
            logger.debug(f"Generated random ref_id for second callback is : {ref_id_3}")

            #second callback for pure UPI
            api_details = DBProcessor.get_api_details('callbackUpiKotakAtos', request_body={
                "mid": mid,
                "tid": tid,
                "ref_no": ref_id_3,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "tr_id": txn_id,
                "transaction_type": "2",
                "primary_id": txn_ref,
                "auth_code": auth_code_3,
                "merchant_vpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for dynamic qr pure upi second callback is : {response}")

            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime('%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from the txn table for second callback is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for the txn table from second callback is : {result}")
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching id from the txn table from second callback is : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table from second callback is : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table from second callback is : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table from second callback is : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table from second callback is : {txn_type_3}")
            created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table from second callback is : {created_time_3}")

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                date_and_time_3 = date_time_converter.to_app_format(created_time_3)

                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,

                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount) + ".00",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(ref_id_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,

                    "pmt_mode_3": "UPI",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount) + ".00",
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "rrn_3": str(ref_id_3),
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "auth_code_3": auth_code_3,
                    "date_3": date_and_time_3
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")

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
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
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
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_2}, {app_auth_code_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_3)
                payment_status_3 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_3}, {payment_status_3}")
                app_date_and_time_3 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_3}, {app_date_and_time_3}")
                app_auth_code_3 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching AUTH CODE from txn history for the txn : {txn_id_3}, {app_auth_code_3}")
                payment_mode_3 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_3}, {payment_mode_3}")
                app_txn_id_3 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_txn_id_3}")
                app_amount_3 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_3}, {app_amount_3}")
                app_customer_name_3 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_rrn_3}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,

                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,

                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_3.split(' ')[1],
                    "settle_status_3": app_settlement_status_3,
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    "customer_name_3": app_customer_name_3,
                    "payer_name_3": payer_name_3,
                    "order_id_3": app_order_id_3,
                    "pmt_msg_3": app_payment_msg_3,
                    "auth_code_3": app_auth_code_3,
                    "date_3": app_date_and_time_3
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
                date_2 = date_time_converter.db_datetime(created_time_2)
                date_3 = date_time_converter.db_datetime(created_time_3)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "device_serial": str(device_serial),

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount,
                    "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(ref_id_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": txn_type_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "auth_code_2": auth_code_2,
                    "date_2": date_2,
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "device_serial_2": str(device_serial),

                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": amount,
                    "pmt_mode_3": "UPI",
                    "pmt_state_3": "SETTLED",
                    "rrn_3": str(ref_id_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "issuer_code_3": "KOTAK",
                    "txn_type_3": txn_type_3,
                    "mid_3": mid,
                    "tid_3": tid,
                    "org_code_3": org_code_txn_3,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                #txn list for QR Generation
                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })

                logger.debug(f"API DETAILS for txn_id {txn_id} for dynamic qr generation is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received from txnlist api for dynamic qr generation is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"list of txns after dynamic qr generation is : {response_in_list}")

                for elements in response_in_list:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for dynamic qr generation is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for dynamic qr generation is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for dynamic qr generation is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for dynamic qr generation is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for dynamic qr generation is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for dynamic qr generation is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for dynamic qr generation is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for dynamic qr generation is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for dynamic qr generation is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for dynamic qr generation is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for dynamic qr generation is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for dynamic qr generation is : {date_api}")
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for dynamic qr generation is : {device_serial_api}")

                #txn list for 1st callback
                for elements in response_in_list:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for first callback is : {status_api_2}")
                        amount_api_2 = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for first callback is : {amount_api_2}")
                        payment_mode_api_2 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for first callback is : {payment_mode_api_2}")
                        state_api_2 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for first callback is : {state_api_2}")
                        rrn_api_2 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for first callback is : {rrn_api_2}")
                        settlement_status_api_2 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for first callback is : {settlement_status_api_2}")
                        issuer_code_api_2 = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for first callback is : {issuer_code_api_2}")
                        acquirer_code_api_2 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for first callback is : {acquirer_code_api_2}")
                        org_code_api_2 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for first callback is : {org_code_api_2}")
                        mid_api_2 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for first callback is : {mid_api_2}")
                        tid_api_2 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for first callback is : {tid_api_2}")
                        txn_type_api_2 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for first callback is : {txn_type_api_2}")
                        auth_code_api_2 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for first callback is : {auth_code_api_2}")
                        date_api_2 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for first callback is : {date_api_2}")
                        customer_name_api_2 = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api for first callback is : {customer_name_api_2}")
                        payer_name_api_2 = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api for first callback is : {payer_name_api_2}")
                        device_serial_api_2 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for first callback is : {device_serial_api_2}")

                #txn list for 2nd callback
                for elements in response_in_list:
                    if elements["txnId"] == txn_id_3:
                        status_api_3 = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for second callback is : {status_api_3}")
                        amount_api_3 = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for second callback is : {amount_api_3}")
                        payment_mode_api_3 = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for second callback is : {payment_mode_api_3}")
                        state_api_3 = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for second callback is : {state_api_3}")
                        rrn_api_3 = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for second callback is : {rrn_api_3}")
                        settlement_status_api_3 = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for second callback is : {settlement_status_api_3}")
                        issuer_code_api_3 = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for second callback is : {issuer_code_api_3}")
                        acquirer_code_api_3 = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for second callback is : {acquirer_code_api_3}")
                        org_code_api_3 = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for second callback is : {org_code_api_3}")
                        mid_api_3 = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for second callback is : {mid_api_3}")
                        tid_api_3 = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for second callback is : {tid_api_3}")
                        txn_type_api_3 = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for second callback is : {txn_type_api_3}")
                        auth_code_api_3 = elements["authCode"]
                        logger.debug(f"Value of authCode obtained from txnlist api for second callback is : {auth_code_api_3}")
                        date_api_3 = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for second callback is : {date_api_3}")
                        customer_name_api_3 = elements["customerName"]
                        logger.debug(f"Value of customerName obtained from txnlist api for second callback is : {customer_name_api_3}")
                        payer_name_api_3 = elements["payerName"]
                        logger.debug(f"Value of payerName obtained from txnlist api for second callback is : {payer_name_api_3}")
                        device_serial_api_3 = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api for second callback is : {device_serial_api_3}")

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
                    "device_serial": str(device_serial_api),

                    "pmt_status_2": status_api_2,
                    "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2,
                    "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": org_code_api_2,
                    "auth_code_2": auth_code_api_2,
                    "customer_name_2": customer_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "device_serial_2": str(device_serial_api_2),

                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3,
                    "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3,
                    "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "txn_type_3": txn_type_api_3,
                    "mid_3": mid_api_3,
                    "tid_3": tid_api_3,
                    "org_code_3": org_code_api_3,
                    "auth_code_3": auth_code_api_3,
                    "customer_name_3": customer_name_api_3,
                    "payer_name_3": payer_name_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "device_serial_3": str(device_serial_api_3)
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "mid": mid,
                    "tid": tid,
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "txn_type": txn_type,
                    "bank_name": "Kotak Mahindra",
                    "device_serial": str(device_serial),

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "KOTAK_ATOS",
                    "mid_2": mid,
                    "tid_2": tid,
                    "upi_txn_status_2": "AUTHORIZED",
                    "upi_txn_type_2": "PAY_QR",
                    "upi_bank_code_2": "KOTAK_WL",
                    "upi_mc_id_2": upi_mc_id,
                    "txn_type_2": txn_type_2,
                    "bank_name_2": "Kotak Mahindra",
                    "payer_name_2": payer_name_2,
                    "rrn_2": str(ref_id_2),
                    "device_serial_2": str(device_serial),

                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "UPI",
                    "txn_amt_3": amount,
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "bank_code_3": "KOTAK",
                    "pmt_gateway_3": "KOTAK_ATOS",
                    "mid_3": mid,
                    "tid_3": tid,
                    "upi_txn_status_3": "AUTHORIZED",
                    "upi_txn_type_3": "PAY_QR",
                    "upi_bank_code_3": "KOTAK_WL",
                    "upi_mc_id_3": upi_mc_id,
                    "txn_type_3": txn_type_3,
                    "bank_name_3": "Kotak Mahindra",
                    "payer_name_3": payer_name_3,
                    "rrn_3": str(ref_id_3),
                    "device_serial_3": str(device_serial)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data for actual db values from txn table for dynamic qr generation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table for dynamic qr generation : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table for dynamic qr generation : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table for dynamic qr generation : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table for dynamic qr generation : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table for dynamic qr generation : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table for dynamic qr generation : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table for dynamic qr generation : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table for dynamic qr generation : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table for dynamic qr generation : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table for dynamic qr generation : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table for dynamic qr generation : {mid_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table for dynamic qr generation : {bank_name_db}")
                device_serial_db = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table for dynamic qr generation : {device_serial_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for dynamic qr generation : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for dynamic qr generation : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for dynamic qr generation : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for dynamic qr generation : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for dynamic qr generation : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for dynamic qr generation : {upi_mc_id_db}")

                query = "select * from txn where id='" + txn_id_2 + "';"
                logger.debug(f"Query to fetch data for actual db values from txn table for first callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table for first callback : {result}")
                status_db_2 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table for first callback : {status_db_2}")
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table for first callback : {payment_mode_db_2}")
                amount_db_2 = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table for first callback : {amount_db_2}")
                state_db_2 = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table for first callback : {state_db_2}")
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table for first callback : {payment_gateway_db_2}")
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table for first callback : {acquirer_code_db_2}")
                bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table for first callback : {bank_code_db_2}")
                tid_db_2 = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table for first callback : {tid_db_2}")
                mid_db_2 = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table for first callback : {mid_db_2}")
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table for first callback : {settlement_status_db_2}")
                bank_name_db_2 = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table for first callback : {bank_name_db_2}")
                payer_name_db_2 = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table for first callback : {payer_name_db_2}")
                rrn_db_2 = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table for first callback : {rrn_db_2}")
                device_serial_db_2 = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table for first callback : {device_serial_db_2}")

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for first callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for first callback : {result}")
                upi_status_db_2 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for first callback : {upi_status_db_2}")
                upi_txn_type_db_2 = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for first callback : {upi_txn_type_db_2}")
                upi_bank_code_db_2 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for first callback : {upi_bank_code_db_2}")
                upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for first callback : {upi_mc_id_db_2}")

                query = "select * from txn where id='" + txn_id_3 + "';"
                logger.debug(f"Query to fetch data for actual db values from txn table for second callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from txn table for second callback : {result}")
                status_db_3 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the txn table for second callback : {status_db_3}")
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching actual db payment_mode value from the txn table for second callback : {payment_mode_db_3}")
                amount_db_3 = int(result["amount"].iloc[0])
                logger.debug(f"Fetching actual db amount value from the txn table for second callback : {amount_db_3}")
                state_db_3 = result["state"].iloc[0]
                logger.debug(f"Fetching actual db state value from the txn table for second callback : {state_db_3}")
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching actual db payment_gateway value from the txn table for second callback : {payment_gateway_db_3}")
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching actual db acquirer_code value from the txn table for second callback : {acquirer_code_db_3}")
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching actual db settlement_status value from the txn table for second callback : {settlement_status_db_3}")
                bank_code_db_3 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the txn table for second callback : {bank_code_db_3}")
                mid_db_3 = result['mid'].values[0]
                logger.debug(f"Fetching actual db mid value from the txn table for second callback : {mid_db_3}")
                tid_db_3 = result['tid'].values[0]
                logger.debug(f"Fetching actual db tid value from the txn table for second callback : {tid_db_3}")
                bank_name_db_3 = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table for second callback : {bank_name_db_3}")
                payer_name_db_3 = result['payer_name'].values[0]
                logger.debug(f"Fetching actual db payer_name value from the txn table for second callback : {payer_name_db_3}")
                rrn_db_3 = result['rr_number'].values[0]
                logger.debug(f"Fetching actual db rr_number value from the txn table for second callback : {rrn_db_3}")
                device_serial_db_3 = result['device_serial'].values[0]
                logger.debug(f"Fetching actual db device_serial value from the txn table for second callback : {device_serial_db_3}")

                query = "select * from upi_txn where txn_id='" + txn_id_3 + "';"
                logger.debug(f"Query to fetch data for actual db values from upi_txn table for second callback : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual db values from upi_txn table for second callback : {result}")
                upi_status_db_3 = result["status"].iloc[0]
                logger.debug(f"Fetching actual db status value from the upi_txn table for second callback : {upi_status_db_3}")
                upi_txn_type_db_3 = result["txn_type"].iloc[0]
                logger.debug(f"Fetching actual db txn_type value from the upi_txn table for second callback : {upi_txn_type_db_3}")
                upi_bank_code_db_3 = result["bank_code"].iloc[0]
                logger.debug(f"Fetching actual db bank_code value from the upi_txn table for second callback : {upi_bank_code_db_3}")
                upi_mc_id_db_3 = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching actual db upi_mc_id value from the upi_txn table for second callback : {upi_mc_id_db_3}")

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
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type,
                    "bank_name": bank_name_db,
                    "device_serial": str(device_serial_db),

                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "txn_type_2": txn_type_2,
                    "bank_name_2": bank_name_db_2,
                    "payer_name_2": payer_name_db_2,
                    "rrn_2": str(rrn_db_2),
                    "device_serial_2": str(device_serial_db_2),

                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "txn_amt_3": amount_db_3,
                    "upi_txn_status_3": upi_status_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "upi_txn_type_3": upi_txn_type_db_3,
                    "upi_bank_code_3": upi_bank_code_db_3,
                    "upi_mc_id_3": upi_mc_id_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "txn_type_3": txn_type_3,
                    "bank_name_3": bank_name_db_3,
                    "payer_name_3": payer_name_db_3,
                    "rrn_3": str(rrn_db_3),
                    "device_serial_3": str(device_serial_db_3)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time_2)
                date_and_time_portal_new = date_time_converter.to_portal_format(created_time_3)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id_2,
                    "auth_code": "-" if auth_code_2 is None else auth_code_2,
                    "rrn": "-" if rrn_db_2 is None else rrn_db_2,

                    "date_time_2": date_and_time_portal_new,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_3,
                    "auth_code_2": "-" if auth_code_3 is None else auth_code_3,
                    "rrn_2": "-" if rrn_db_3 is None else rrn_db_3,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_new_2 = transaction_details[0]['Date & Time']
                transaction_id_new_2 = transaction_details[0]['Transaction ID']
                total_amount_new_2 = transaction_details[0]['Total Amount'].split()
                auth_code_portal_new_2 = transaction_details[0]['Auth Code']
                rr_number_new_2 = transaction_details[0]['RR Number']
                transaction_type_new_2 = transaction_details[0]['Type']
                status_new_2 = transaction_details[0]['Status']
                username_new_2 = transaction_details[0]['Username']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                auth_code_portal = transaction_details[1]['Auth Code']
                rr_number = transaction_details[1]['RR Number']
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "date_time_2": date_time_new_2,
                    "pmt_state_2": str(status_new_2),
                    "pmt_type_2": transaction_type_new_2,
                    "txn_amt_2": total_amount_new_2[1],
                    "username_2": username_new_2,
                    "txn_id_2": transaction_id_new_2,
                    "auth_code_2": auth_code_portal_new_2,
                    "rrn_2": rr_number_new_2,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # ------------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(ref_id_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date_2,
                    'time': txn_time_2,
                    'AUTH CODE': str(auth_code_2)
                }
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_2)
                expected_charge_slip_values_3 = {
                    'PAID BY:': 'UPI',
                    'merchant_ref_no': 'Ref # ' + str(order_id),
                    'RRN': str(ref_id_3),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                    'date': txn_date_3,
                    'time': txn_time_3,
                    'AUTH CODE': str(auth_code_3)
                }

                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3,
                                                                                            {
                                                                                                "username": app_username,
                                                                                                "password": app_password},
                                                                                            expected_charge_slip_values_3)
                if chargeslip_val_result_3 and chargeslip_val_result_2:
                    GlobalVariables.str_chargeslip_val_result = 'Pass'
                else:
                    GlobalVariables.str_chargeslip_val_result = 'Fail'

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation-------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)