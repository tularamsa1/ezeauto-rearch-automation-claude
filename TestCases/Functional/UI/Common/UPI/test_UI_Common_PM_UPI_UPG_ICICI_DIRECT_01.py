import sys
import pytest
import random
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_312():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_AUTHORIZED_When_UPGAutoRefund_Disabled_Via_ICICI_DIRECT
    Sub Feature Description: Performing a upg txn using upi success callback when upg auto refund disabled via ICICI DIRECT PG.
    TC naming code description: 100: Payment Method, 101: UPI, 312: TC312
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query to result for org_employee table : {query}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code obtained from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' " \
                f"AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id obtained from upi_merchant_config table is : {upi_mc_id}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of virtual_tid obtained from upi_merchant_config table is : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of virtual_mid obtained from upi_merchant_config table is : {virtual_mid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa obtained from upi_merchant_config table is : {vpa}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Value of amount and order_id is: {amount}, {order_id}")

            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating upi qr : {response}")
            txn_id = str(response["txnId"]).split('E')[0] + 'E' + str(random.randint(111111111, 999999999))
            logger.debug(f"Fetching txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            rrn = txn_id.split('E')[1]
            logger.debug(f"generated random rrn number to perform first callback is : {rrn}")

            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn,
                "merchantTranId": str(txn_id),
                "PayerVA": str(vpa)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_id}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result obtained from invalid_pg_request table : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"Value of txn_id obtained from invalid_pg_request table : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from invalid_pg_request table : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from invalid_pg_request table : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f"Value of org_code obtained from invalid_pg_request table : {ipr_org_code}")
            ipr_amount = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from invalid_pg_request table : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f"Value of rrn obtained from invalid_pg_request table : {ipr_rrn}")
            ipr_auth_code = result["auth_code"].iloc[0]
            logger.debug(f"Value of auth_code obtained from invalid_pg_request table : {ipr_auth_code}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from invalid_pg_request table : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from invalid_pg_request table : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f"Value of config_id obtained from invalid_pg_request table : {ipr_config_id}")
            ipr_vpa = result["vpa"].iloc[0]
            logger.debug(f"Value of vpa obtained from invalid_pg_request table : {ipr_vpa}")

            query = f"select * from txn where id = '{str(ipr_txn_id)}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result obtained from txn table is : {query}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")

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
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "txn_id": ipr_txn_id,
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for txn_id : {ipr_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn_id  : {ipr_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn_id  : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn_id  : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn_id  : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn_id  : {ipr_txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn_id  : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rrn": str(app_rrn),
                    "pmt_state": app_settlement_status
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
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"List of txns received from transaction list api is : {response_in_list}")
                for elements in response_in_list:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for qr generation is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for qr generation is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for qr generation is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for qr generation is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for qr generation is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for qr generation is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for qr generation is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for qr generation is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for qr generation is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for qr generation is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for qr generation is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for qr generation is : {date_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for qr generation is : {rrn_api}")

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
                    "rrn": rrn_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                    "txn_amt": float(amount),
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "ICICI",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": float(amount),
                    "ipr_mid": virtual_mid,
                    "ipr_tid": virtual_tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{ipr_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result obtained from upi_txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table  : {upi_mc_id_db}")

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
                    "upi_mc_id": upi_mc_id_db,
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
                    "ipr_config_id": ipr_config_id
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        #-----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
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

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                portal_rrn = transaction_details[0]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": str(portal_rrn),
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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
def test_common_100_101_313():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_AUTHORIZED_when_UPGAutoRefund_Enabled_Via_ICICI_DIRECT
    Sub Feature Description: Performing a upg txn using upi success callback when upg auto refund enabled via ICICI DIRECT PG.
    TC naming code description: 100: Payment Method, 101: UPI, 313: TC313
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch data from org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query to result for org_employee table : {query}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Value of org_code obtained from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
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
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' " \
                f"AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for upi_merchant_config table is : {result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Value of upi_mc_id obtained from upi_merchant_config table is : {upi_mc_id}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.debug(f"Value of virtual_tid obtained from upi_merchant_config table is : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.debug(f"Value of virtual_mid obtained from upi_merchant_config table is : {virtual_mid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Value of vpa obtained from upi_merchant_config table is : {vpa}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, middlewareLog=True, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Value of amount and order_id is: {amount}, {order_id}")

            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "username": app_username,
                "password": app_password,
                "amount": str(amount),
                "orderNumber": str(order_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received after initiating upi qr : {response}")
            txn_id = str(response["txnId"]).split('E')[0] + 'E' + str(random.randint(111111111, 999999999))
            logger.debug(f"Fetching txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            rrn = txn_id.split('E')[1]
            logger.debug(f"generated random rrn number to perform first callback is : {rrn}")

            api_details = DBProcessor.get_api_details('callbackgeneratorUpiICICI', request_body={
                "merchantId": virtual_mid,
                "subMerchantId": virtual_mid,
                "terminalId": virtual_tid,
                "PayerAmount": str(amount),
                "BankRRN": rrn,
                "merchantTranId": str(txn_id),
                "PayerVA": str(vpa)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback generator api is : {response}")

            api_details = DBProcessor.get_api_details('callbackUpiICICI', request_body=response)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for callback api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_id}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result obtained from invalid_pg_request table : {result}")
            ipr_txn_id = result['txn_id'].iloc[0]
            logger.debug(f"Value of txn_id obtained from invalid_pg_request table : {ipr_txn_id}")
            ipr_payment_mode = result["payment_mode"].iloc[0]
            logger.debug(f"Value of payment_mode obtained from invalid_pg_request table : {ipr_payment_mode}")
            ipr_bank_code = result["bank_code"].iloc[0]
            logger.debug(f"Value of bank_code obtained from invalid_pg_request table : {ipr_bank_code}")
            ipr_org_code = result["org_code"].iloc[0]
            logger.debug(f"Value of org_code obtained from invalid_pg_request table : {ipr_org_code}")
            ipr_amount = float(result["amount"].iloc[0])
            logger.debug(f"Value of amount obtained from invalid_pg_request table : {ipr_amount}")
            ipr_rrn = result["rrn"].iloc[0]
            logger.debug(f"Value of rrn obtained from invalid_pg_request table : {ipr_rrn}")
            ipr_auth_code = result["auth_code"].iloc[0]
            logger.debug(f"Value of auth_code obtained from invalid_pg_request table : {ipr_auth_code}")
            ipr_mid = result["mid"].iloc[0]
            logger.debug(f"Value of mid obtained from invalid_pg_request table : {ipr_mid}")
            ipr_tid = result["tid"].iloc[0]
            logger.debug(f"Value of tid obtained from invalid_pg_request table : {ipr_tid}")
            ipr_config_id = result["config_id"].iloc[0]
            logger.debug(f"Value of config_id obtained from invalid_pg_request table : {ipr_config_id}")
            ipr_vpa = result["vpa"].iloc[0]
            logger.debug(f"Value of vpa obtained from invalid_pg_request table : {ipr_vpa}")

            query = f"select * from txn where id ='{str(ipr_txn_id)}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result obtained from txn table is : {query}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].iloc[0]
            logger.debug(f"fetched status from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"fetched payment_mode from txn table is : {payment_mode_db}")
            amount_db = float(result["amount"].iloc[0])
            logger.debug(f"fetched amount from txn table is : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"fetched state from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"fetched payment_gateway from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"fetched acquirer_code from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"fetched bank_code from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"fetched settlement_status from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid from txn table is : {mid_db}")

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
                    "pmt_msg": "REFUND PENDING",
                    "txn_id": ipr_txn_id,
                    "pmt_status": "UPG_REFUND_PENDING",
                    "txn_amt": "{:.2f}".format(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(ipr_txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for txn_id : {ipr_txn_id}, {payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn_id  : {ipr_txn_id}, {app_date_and_time}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn_id  : {ipr_txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn_id  : {ipr_txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn_id  : {ipr_txn_id}, {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {ipr_txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn_id  : {ipr_txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn_id  : {ipr_txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "rrn": str(app_rrn),
                    "pmt_state": app_settlement_status
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
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUND_PENDING",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code": "ICICI",
                    "txn_type": txn_type,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "org_code": org_code,
                    "date": date
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_in_list = response["txns"]
                logger.debug(f"List of txns received from transaction list api is : {response_in_list}")
                for elements in response_in_list:
                    if elements["txnId"] == ipr_txn_id:
                        status_api = elements["status"]
                        logger.debug(f"Value of status obtained from txnlist api for qr generation is : {status_api}")
                        amount_api = int(elements["amount"])
                        logger.debug(f"Value of amount obtained from txnlist api for qr generation is : {amount_api}")
                        payment_mode_api = elements["paymentMode"]
                        logger.debug(f"Value of paymentMode obtained from txnlist api for qr generation is : {payment_mode_api}")
                        state_api = elements["states"][0]
                        logger.debug(f"Value of states obtained from txnlist api for qr generation is : {state_api}")
                        settlement_status_api = elements["settlementStatus"]
                        logger.debug(f"Value of settlementStatus obtained from txnlist api for qr generation is : {settlement_status_api}")
                        issuer_code_api = elements["issuerCode"]
                        logger.debug(f"Value of issuerCode obtained from txnlist api for qr generation is : {issuer_code_api}")
                        acquirer_code_api = elements["acquirerCode"]
                        logger.debug(f"Value of acquirerCode obtained from txnlist api for qr generation is : {acquirer_code_api}")
                        org_code_api = elements["orgCode"]
                        logger.debug(f"Value of orgCode obtained from txnlist api for qr generation is : {org_code_api}")
                        mid_api = elements["mid"]
                        logger.debug(f"Value of mid obtained from txnlist api for qr generation is : {mid_api}")
                        tid_api = elements["tid"]
                        logger.debug(f"Value of tid obtained from txnlist api for qr generation is : {tid_api}")
                        txn_type_api = elements["txnType"]
                        logger.debug(f"Value of txnType obtained from txnlist api for qr generation is : {txn_type_api}")
                        date_api = elements["createdTime"]
                        logger.debug(f"Value of createdTime obtained from txnlist api for qr generation is : {date_api}")
                        rrn_api = elements["rrNumber"]
                        logger.debug(f"Value of rrNumber obtained from txnlist api for qr generation is : {rrn_api}")

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
                    "rrn": rrn_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": float(amount),
                    "upi_txn_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "bank_code": "ICICI",
                    "pmt_gateway": "ICICI",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "ICICI_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "ICICI",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": float(amount),
                    "ipr_mid": virtual_mid,
                    "ipr_tid": virtual_tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{ipr_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result obtained from upi_txn table : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Value of status obtained from upi_txn table : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Value of txn_type obtained from upi_txn table : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Value of bank_code obtained from upi_txn table : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Value of upi_mc_id obtained from upi_txn table  : {upi_mc_id_db}")

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
                    "upi_mc_id": upi_mc_id_db,
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
                    "ipr_config_id": ipr_config_id
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        #-----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": f"{str(amount)}.00",
                    "username": "EZETAP",
                    "txn_id": ipr_txn_id,
                    "rrn": str(rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                portal_rrn = transaction_details[0]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": str(portal_rrn),
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

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