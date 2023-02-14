import random
import sys
import pytest
import time

from datetime import datetime
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_101_177():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Success_Via_API_CheckStatus_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a successful upi txn via KOTAK_ATOS using check status api
    TC naming code description: 100: Payment method, 101: UPI, 177: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
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
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {upi_mc_id}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device_serial from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.info(f"Fetching device_serial from terminal_info table : {device_serial}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Stop Payment : {response}")

            # now hit payment status
            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Payment Status : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table based on txn_id  : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is based on txn_id : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table based on txn_id : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table based on txn_id : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table based on txn_id : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from the txn table based on txn_id : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table based on txn_id : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table based on txn_id : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table based on txn_id : {created_time}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
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
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
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
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {app_rrn}")

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
        # -----------------------------------------End of App Validation------------------------------------------------

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)

                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
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
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "mid": mid,
                    "tid": tid,
                    "device_serial": str(device_serial),
                    "bank_name": "Kotak Mahindra",
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "txn_type": txn_type,
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "AUTHORIZED"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "';"
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
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table based on txn_id : {bank_name_db}")

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
                    "bank_name": bank_name_db,
                    "pmt_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "txn_type": txn_type_db,
                    "payer_name": payer_name_db,
                    "rrn": str(rrn_db),
                    "device_serial": str(device_serial_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_txn_status": upi_status_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)

                expected_charge_slip_values = {
                    'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
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
def test_common_100_101_178():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Failed_Via_API_CheckStatus_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a failed upi txn via KOTAK_ATOS using check status api
    TC naming code description: 100: Payment method, 101: UPI, 178: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
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

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency_config
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(101, 150)
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

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Stop Payment : {response}")

            # now hit payment status
            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Payment Status : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table based on txn_id  : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is based on txn_id : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table based on txn_id : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table based on txn_id : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table based on txn_id : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from the txn table based on txn_id : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table based on txn_id : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table based on txn_id : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table based on txn_id : {created_time}")

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
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
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
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
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
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {app_rrn}")

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
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "mid": mid,
                    "tid": tid,
                    "device_serial": str(device_serial),
                    "bank_name": "Kotak Mahindra",
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "txn_type": "CHARGE",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": upi_mc_id,
                    "upi_txn_status": "FAILED"
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
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table based on txn_id : {bank_name_db}")

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
                    "bank_name": bank_name_db,
                    "pmt_gateway": payment_gateway_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "txn_type": txn_type_db,
                    "payer_name": payer_name_db,
                    "rrn": str(rrn_db),
                    "device_serial": str(device_serial_db),
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "upi_txn_status": upi_status_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

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
def test_common_100_101_179():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Pending_Via_API_CheckStatus_KOTAK_ATOS
    Sub Feature Description: Tid Dep - Verification of a pending upi txn via UPI via KOTAK_ATOS using check status api
    TC naming code description: 100: Payment method, 101: UPI, 179: Testcase ID
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

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency_config
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
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {upi_mc_id}")

        query = "select device_serial from terminal_info where tid = '" + str(tid) + "';"
        logger.debug(f"Query to fetch device_serial from terminal_info table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of terminal_info table : {result}")
        device_serial = result['device_serial'].values[0]
        logger.info(f"Fetching device_serial from terminal_info table : {device_serial}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.choice([i for i in range(1, 100) if i not in [45,46]])
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

            #hit payment status
            api_details = DBProcessor.get_api_details('paymentStatus',request_body={
                "username": app_username, "password": app_password,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Payment Status : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table based on txn_id  : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table based on txn_id : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table based on txn_id : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table based on txn_id : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table based on txn_id : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from the txn table based on txn_id : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table based on txn_id : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table based on txn_id : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table based on txn_id : {created_time}")
            bank_name = result['bank_name'].values[0]
            logger.debug(f"Fetching bank_name from the txn table based on txn_id : {bank_name}")

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
                    "pmt_status": "PENDING",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "PENDING",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT PENDING",
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

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
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
                    "pmt_status": "PENDING",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "device_serial": str(device_serial),
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
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api is : {device_serial_api}")

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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "PAY_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "mid": mid,
                    "tid": tid,
                    "upi_mc_id": upi_mc_id,
                    "txn_type": "CHARGE",
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "device_serial": str(device_serial),
                    "bank_name": bank_name,
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
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching actual db bank_name value from the txn table based on txn_id : {bank_name_db}")

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
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "upi_mc_id": upi_mc_id_db,
                    "txn_type": txn_type_db,
                    "payer_name": payer_name_db,
                    "rrn": str(rrn_db),
                    "device_serial": str(device_serial_db),
                    "bank_name": bank_name_db,
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

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
def test_common_100_101_180():
    """
    Sub Feature Code: Tid Dep - UI_Common_PM_UPI_Via_API_CheckStatus_After_Expiry_KOTAK_ATOS
    Sub Feature Description: Tid Dep -  Verification of a successful upi txn after QR expiry for KOTAK_ATOS using check status api
    TC naming code description: 100: Payment method, 101: UPI, 180: Testcase ID
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

        # Based on org_code, payment_gateway and payment_mode we will enable the terminal_dependency_config
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
        logger.debug(f"Response received from UPI QR Expiry time is : {response}")

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

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            # hit the stop payment
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "username": app_username,
                "password": app_password,
                "orgCode": org_code,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Stop Payment : {response}")

            # now hit payment status
            api_details = DBProcessor.get_api_details('paymentStatus', request_body={
                "username": app_username,
                "password": app_password,
                "txnId": txn_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for upi Payment Status : {response}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch data from the txn table based on txn_id  : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result for txn table is based on txn_id : {result}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn_number from the txn table based on txn_id : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table based on txn_id : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table based on txn_id : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code_txn from the txn table based on txn_id : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table based on txn_id : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table based on txn_id : {auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table based on txn_id : {created_time}")

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
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount) + ".00",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
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

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
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
                        device_serial_api = elements["deviceSerial"]
                        logger.debug(f"Value of deviceSerial obtained from txnlist api is : {device_serial_api}")

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
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from the txn table for actual value for dynamic qr generation is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual value from txn table for dynamic qr generation is : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status for actual value from txn table for dynamic qr generation is : {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching payment_mode for actual value from txn table for dynamic qr generation is : {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching amount for actual value from txn table for dynamic qr generation is : {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching state for actual value from txn table for dynamic qr generation is : {state_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway for actual value from txn table for dynamic qr generation is : {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code for actual value from txn table for dynamic qr generation is : {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code for actual value from txn table for dynamic qr generation is : {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status for actual value from txn table for dynamic qr generation is : {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching tid for actual value from txn table for dynamic qr generation is : {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching mid for actual value from txn table for dynamic qr generation is : {mid_db}")
                bank_name_db = result["bank_name"].iloc[0]
                logger.debug(f"Fetching bank_name for actual value from txn table based on txn_id : {bank_name_db}")
                payer_name_db = result['payer_name'].values[0]
                logger.debug(f"Fetching payer_name for actual value from txn table based on txn_id : {payer_name_db}")
                rrn_db = result['rr_number'].values[0]
                logger.debug(f"Fetching rr_number for actual value from txn table based on txn_id : {rrn_db}")

                query = "select * from upi_txn where txn_id='" + txn_id + "';"
                logger.debug(f"Query to fetch data from the upi_txn table for actual value for dynamic qr generation is : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for actual value from upi_txn table for dynamic qr generation is : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status for actual value from upi_txn table for dynamic qr generation is : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type for actual value from upi_txn table for dynamic qr generation is : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code for actual value from upi_txn table for dynamic qr generation is : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id for actual value from upi_txn table for dynamic qr generation is : {upi_mc_id_db}")

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
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)