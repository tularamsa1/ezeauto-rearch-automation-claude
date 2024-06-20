import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_392():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Callback_Success_HDFC_MINTOAK
    Sub Feature Description: Tid Dep -  Verification of  a  BQR Callback Success via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 392: TC392
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code from txn table is : {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"rrn from txn table is : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created_time from txn table is : {created_time}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"amount_db from txn table is : {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"payment_mode_db from txn table is : {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"payment_status_db from txn table is : {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"payment_state_db from txn table is : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"bank_name_db from txn table is : {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"mid_db from txn table is : {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"tid_db from txn table is : {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"payment_gateway_db from txn table is : {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"rr_number_db from txn table is : {rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"settlement_status_db from txn table is : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"device_serial_db from txn table is : {device_serial_db}")

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
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "AUTHORIZED",
                                       "txn_amt": "{:.2f}".format(amount),
                                       "settle_status": "SETTLED", "txn_id": txn_id, "rrn": str(rrn),
                                       "order_id": order_id, "pmt_msg": "PAYMENT SUCCESSFUL",
                                       "date": date_and_time}
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
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time}
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
                expected_api_values = {"pmt_status": "AUTHORIZED", "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED", "rrn": str(rrn), "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC", "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date, "device_serial": str(device_serial)}
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
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
                device_serial_api = response["deviceSerial"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": str(device_serial_api)}
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
                expected_db_values = {"txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED", "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid, "pmt_gateway": "MINTOAK",
                                      "rrn": str(rrn), "settle_status": "SETTLED",
                                      "device_serial": str(device_serial),
                                      "bqr_pmt_status": "Success", "bqr_pmt_state": "SETTLED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = int(result["txn_amount"].values[0])
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn": rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial": str(device_serial_db),
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db
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
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn
                }
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
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
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date, 'time': txn_time,
                                   'AUTH CODE': "" if auth_code is None else auth_code}
                logger.debug(f"expected_values : {expected_values}")
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_393():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Callback_Failed_HDFC_MINTOAK
    Sub Feature Description: Tid Dep - Verification of  a  failed BQR Callaback via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 393: TC393
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"initiating upi qr for the amount of {amount}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_failed')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code from txn table is: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"rrn from txn table is: {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created_time from txn table is: {created_time}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"amount_db from txn table is: {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"payment_mode_db from txn table is: {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"payment_status_db from txn table is: {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"payment_state_db from txn table is: {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"acquirer_code_db from txn table is: {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"bank_name_db from txn table is: {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"mid_db from txn table is: {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"tid_db from txn table is: {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"payment_gateway_db from txn table is: {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"rr_number_db from txn table is: {rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"settlement_status_db from txn table is: {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"device_serial_db from txn table is: {device_serial_db}")

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
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "FAILED",
                                       "txn_amt": "{:.2f}".format(amount),
                                       "settle_status": "FAILED", "txn_id": txn_id,
                                       "order_id": order_id, "pmt_msg": "PAYMENT FAILED",
                                       "date": date_and_time}
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
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time}
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
                expected_api_values = {"pmt_status": "FAILED", "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                                       "pmt_state": "FAILED", "settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC", "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date, "device_serial": str(device_serial)}
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
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
                device_serial_api = response["deviceSerial"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": org_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": str(device_serial_api)}
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
                expected_db_values = {"txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "FAILED",
                                      "pmt_state": "FAILED", "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid, "pmt_gateway": "MINTOAK",
                                      "rrn": str(rrn), "settle_status": "FAILED",
                                      "device_serial": str(device_serial),
                                      "bqr_pmt_status": "Failed", "bqr_pmt_state": "FAILED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = int(result["txn_amount"].values[0])
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn": rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial": str(device_serial_db),
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']
                rr_number = transaction_details[0]['RR Number']
                auth_code = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": str(rr_number),
                    "auth_code": auth_code
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation------------------------------------

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
@pytest.mark.chargeSlipVal
def test_common_100_102_398():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Two_Callback_Success_AutoRefund_Disbaled_HDFC_MINTOAK
    Sub Feature Description: Tid Dep -  Verification of a BQRV4 BQR two Callback Success when auto refund is disabled via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 398: TC398
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

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

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.debug(f"Txn id for this transaction is: {txn_id}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetched auth_code from txn table is : {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetched rrn from txn table is : {rrn}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetched created_time from txn table is : {created_time}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"Fetched amount_db from txn table is : {amount_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"Fetched payment_mode_db from txn table is : {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"Fetched payment_status_db from txn table is : {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"Fetched payment_state_db from txn table is : {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"Fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"Fetched bank_name_db from txn table is : {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"Fetched mid_db from txn table is : {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"Fetched tid_db from txn table is : {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"Fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            rr_number_db = result["rr_number"].values[0]
            logger.debug(f"Fetched rr_number_db from txn table is : {rr_number_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"Fetched settlement_status_db from txn table is : {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"Fetched device_serial_db from txn table is : {device_serial_db}")

            logger.info(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].values[0]
            logger.debug(f"Fetched txn_id_new from txn table is : {txn_id_new}")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"Fetched auth_code_new from txn table is : {auth_code_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"Fetched rrn_new from txn table is : {rrn_new}")
            created_time_new = result['created_time'].values[0]
            logger.debug(f"Fetched created_time_new from txn table is : {created_time_new}")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "AUTHORIZED",
                                       "txn_amt": "{:.2f}".format(amount),
                                       "settle_status": "SETTLED", "txn_id": txn_id, "rrn": str(rrn),
                                       "order_id": order_id, "pmt_msg": "PAYMENT SUCCESSFUL",
                                       "date": date_and_time,
                                       "pmt_mode_2": "BHARAT QR", "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": "{:.2f}".format(amount), "rrn_2": str(rrn_new),
                                       "settle_status_2": "SETTLED", "txn_id_2": txn_id_new,
                                       "order_id_2": order_id, "pmt_msg_2": "PAYMENT SUCCESSFUL",
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)

                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                actual_app_values = {
                    "pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg, "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_new, "pmt_status_2": payment_status_new.split(':')[1],
                    "txn_amt_2": app_amount_new.split(' ')[1],
                    "txn_id_2": app_txn_id_new, "rrn_2": str(app_rrn_new),
                    "settle_status_2": app_settlement_status_new,
                    "order_id_2": app_order_id_new,
                    "pmt_msg_2": app_payment_msg_new, "date_2": app_date_and_time_new
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
                expected_api_values = {"pmt_status": "AUTHORIZED", "txn_amt": float(amount), "pmt_mode": "BHARATQR",
                                       "pmt_state": "SETTLED", "rrn": str(rrn), "settle_status": "SETTLED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC", "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date, "device_serial": str(device_serial),
                                       "pmt_status_2": "AUTHORIZED", "txn_amt_2": float(amount),
                                       "pmt_mode_2": "BHARATQR", "pmt_state_2": "SETTLED",
                                       "rrn_2": str(rrn_new), "settle_status_2": "SETTLED", "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC", "txn_type_2": "CHARGE",
                                       "mid_2": mid, "tid_2": tid, "org_code_2": org_code,
                                       "date_2": date_new,
                                       "device_serial_2": str(device_serial),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"responseInList is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = float(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        rrn_api = elements["rrNumber"]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]
                        device_serial_api = elements["deviceSerial"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_new:
                        status_api_new = elements["status"]
                        amount_api_new = float(elements["amount"])
                        payment_mode_api_new = elements["paymentMode"]
                        state_api_new = elements["states"][0]
                        rrn_api_new = elements["rrNumber"]
                        settlement_status_api_new = elements["settlementStatus"]
                        issuer_code_api_new = elements["issuerCode"]
                        acquirer_code_api_new = elements["acquirerCode"]
                        org_code_api_new = elements["orgCode"]
                        mid_api_new = elements["mid"]
                        tid_api_new = elements["tid"]
                        txn_type_api_new = elements["txnType"]
                        date_api_new = elements["createdTime"]
                        device_serial_api_new = elements["deviceSerial"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": str(device_serial_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new, "mid_2": mid_api_new,
                                     "txn_type_2": txn_type_api_new, "tid_2": tid_api_new,
                                     "org_code_2": org_code_api_new,
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
                expected_db_values = {"txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED", "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid, "pmt_gateway": "MINTOAK",
                                      "rrn": str(rrn), "settle_status": "SETTLED",
                                      "device_serial": str(device_serial),
                                      "bqr_pmt_status": "Success", "bqr_pmt_state": "SETTLED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_rrn": str(rrn), "bqr_org_code": org_code,
                                      "txn_amt_2": amount, "pmt_mode_2": "BHARATQR", "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED", "acquirer_code_2": "HDFC",
                                      "bank_name_2": "HDFC Bank",
                                      "mid_2": mid, "tid_2": tid, "pmt_gateway_2": "MINTOAK",
                                      "rrn_2": str(rrn_new), "settle_status_2": "SETTLED",
                                      "device_serial_2": str(device_serial),
                                      "bqr_pmt_status_2": "Success", "bqr_pmt_state_2": "SETTLED",
                                      "bqr_txn_amt_2": amount,
                                      "bqr_txn_type_2": "DYNAMIC_QR", "brq_terminal_info_id_2": terminal_info_id,
                                      "bqr_bank_code_2": "HDFC",
                                      "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_new,
                                      "bqr_rrn_2": str(rrn_new), "bqr_org_code_2": org_code
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = int(result["amount"].values[0])
                payment_mode_db_new = result["payment_mode"].values[0]
                payment_status_db_new = result["status"].values[0]
                payment_state_db_new = result["state"].values[0]
                acquirer_code_db_new = result["acquirer_code"].values[0]
                bank_name_db_new = result["bank_name"].values[0]
                mid_db_new = result["mid"].values[0]
                tid_db_new = result["tid"].values[0]
                payment_gateway_db_new = result["payment_gateway"].values[0]
                rr_number_db_new = result["rr_number"].values[0]
                settlement_status_db_new = result["settlement_status"].values[0]
                device_serial_db_new = result['device_serial'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = int(result["txn_amount"].values[0])
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_rrn_db = result['rrn'].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].values[0]
                bqr_state_db_new = result["state"].values[0]
                bqr_amount_db_new = int(result["txn_amount"].values[0])
                bqr_txn_type_db_new = result["txn_type"].values[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].values[0]
                bqr_bank_code_db_new = result["bank_code"].values[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].values[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn": rr_number_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial": str(device_serial_db),
                                    "bqr_pmt_status": bqr_status_db, "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_rrn": bqr_rrn_db, "bqr_org_code": bqr_org_code_db,
                                    "txn_amt_2": amount_db_new, "pmt_mode_2": payment_mode_db_new,
                                    "pmt_status_2": payment_status_db_new, "pmt_state_2": payment_state_db_new,
                                    "acquirer_code_2": acquirer_code_db_new, "bank_name_2": bank_name_db_new,
                                    "mid_2": mid_db_new, "tid_2": tid_db_new,
                                    "pmt_gateway_2": payment_gateway_db_new, "rrn_2": rr_number_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "device_serial_2": str(device_serial_db_new),
                                    "bqr_pmt_status_2": bqr_status_db_new, "bqr_pmt_state_2": bqr_state_db_new,
                                    "bqr_txn_amt_2": bqr_amount_db_new,
                                    "bqr_txn_type_2": bqr_txn_type_db_new,
                                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                                    "bqr_bank_code_2": bqr_bank_code_db_new,
                                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                                    "bqr_rrn_2": bqr_rrn_db_new, "bqr_org_code_2": bqr_org_code_db_new
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code,
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": str(rrn_new),
                    "auth_code_2": "-" if auth_code_new is None else auth_code_new,
                    "txn_id_2": txn_id_new
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                rrn_2 = transaction_details[0]['RR Number']
                auth_code_portal_2 = transaction_details[0]['Auth Code']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                rrn = transaction_details[1]['RR Number']
                auth_code_portal = transaction_details[1]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "rrn": rrn,
                    "auth_code": auth_code_portal,
                    "txn_id": transaction_id,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": str(username_2),
                    "rrn_2": rrn_2,
                    "auth_code_2": auth_code_portal_2,
                    "txn_id_2": transaction_id_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")
                # ---------------------------------------------------------------------------------------------
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
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_new)
                expected_values_1 = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                     'RRN': str(rrn),
                                     'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date, 'time': txn_time,
                                     'AUTH CODE': "" if auth_code is None else auth_code
                                     }
                expected_values_2 = {'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id),
                                     'RRN': str(rrn_new),
                                     'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                                     'time': txn_time_2,
                                     'AUTH CODE': "" if auth_code_new is None else auth_code_new
                                     }
                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id,
                                                                                             {"username": app_username,
                                                                                              "password": app_password},
                                                                                             expected_values_1)
                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_new,
                                                                                             {"username": app_username,
                                                                                              "password": app_password},
                                                                                             expected_values_2)

                if charge_slip_val_result_1 and charge_slip_val_result_2:
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_400():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Callback_AfterExpiry_AutoRefund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Tid Dep - Verification of a BQRV4 BQR Callback After QR code gets expired when auto refund is Disabled via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 400: TC400
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

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

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.debug("Waiting for QR code to get expired")
            time.sleep(75)

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table: {created_time} ")
            amount_db = float(result["amount"].values[0])
            logger.debug(f"fetched amount_db from txn table: {amount_db} ")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table: {auth_code} ")
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table: {rrn} ")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"fetched payment_mode_db from txn table: {payment_mode_db} ")
            payment_status_db = result["status"].values[0]
            logger.debug(f"fetched payment_status_db from txn table: {payment_status_db} ")
            payment_state_db = result["state"].values[0]
            logger.debug(f"fetched payment_state_db from txn table: {payment_state_db} ")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"fetched acquirer_code_db from txn table: {acquirer_code_db} ")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"fetched bank_name_db from txn table: {bank_name_db} ")
            mid_db = result["mid"].values[0]
            logger.debug(f"fetched mid_db from txn table: {mid_db} ")
            tid_db = result["tid"].values[0]
            logger.debug(f"fetched tid_db from txn table: {tid_db} ")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"fetched payment_gateway_db from txn table: {payment_gateway_db} ")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"fetched settlement_status_db from txn table: {settlement_status_db} ")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"fetched device_serial_db from txn table: {device_serial_db} ")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' " \
                    "order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].values[0]
            logger.debug(f"fetched txn_id_new from txn table: {txn_id_new} ")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code_new from txn table: {auth_code_new} ")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"fetched rrn_new from txn table: {rrn_new} ")
            created_time_new = result['created_time'].values[0]
            logger.debug(f"fetched created_time_new from txn table: {created_time_new} ")

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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                expected_app_values = {"pmt_mode": "BHARAT QR",
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
                                       "rrn_2": str(rrn_new),
                                       "settle_status_2": "SETTLED",
                                       "txn_id_2": txn_id_new,
                                       "order_id_2": order_id,
                                       "pmt_msg_2": "PAYMENT SUCCESSFUL",
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                actual_app_values = {"pmt_mode": payment_mode,
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
                                     "settle_status_2": app_settlement_status_new,
                                     "order_id_2": app_order_id_new,
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
                expected_api_values = {"pmt_status": "EXPIRED",
                                       "txn_amt": amount,
                                       "pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED",
                                       "settle_status": "FAILED",
                                       "acquirer_code": "HDFC",
                                       "issuer_code": "HDFC",
                                       "txn_type": "CHARGE",
                                       "mid": mid,
                                       "tid": tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "device_serial": str(device_serial),
                                       "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": amount,
                                       "pmt_mode_2": "BHARATQR",
                                       "pmt_state_2": "SETTLED",
                                       "rrn_2": str(rrn_new),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC",
                                       "txn_type_2": "CHARGE",
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "org_code_2": org_code,
                                       "date_2": date_new,
                                       "device_serial_2": str(device_serial),
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                logger.debug(f"Response received for transaction details api is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = float(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]
                        device_serial_api = elements["deviceSerial"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_new:
                        status_api_new = elements["status"]
                        amount_api_new = float(elements["amount"])
                        payment_mode_api_new = elements["paymentMode"]
                        state_api_new = elements["states"][0]
                        rrn_api_new = elements["rrNumber"]
                        settlement_status_api_new = elements["settlementStatus"]
                        issuer_code_api_new = elements["issuerCode"]
                        acquirer_code_api_new = elements["acquirerCode"]
                        org_code_api_new = elements["orgCode"]
                        mid_api_new = elements["mid"]
                        tid_api_new = elements["tid"]
                        txn_type_api_new = elements["txnType"]
                        date_api_new = elements["createdTime"]
                        device_serial_api_new = elements["deviceSerial"]

                actual_api_values = {"pmt_status": status_api,
                                     "txn_amt": amount_api,
                                     "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api,
                                     "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,
                                     "issuer_code": issuer_code_api,
                                     "mid": mid_api,
                                     "txn_type": txn_type_api,
                                     "tid": tid_api,
                                     "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": str(device_serial_api),
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
                expected_db_values = {"txn_amt": amount,
                                      "pmt_mode": "BHARATQR",
                                      "pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED",
                                      "acquirer_code": "HDFC",
                                      "bank_name": "HDFC Bank",
                                      "mid": mid,
                                      "tid": tid,
                                      "pmt_gateway": "MINTOAK",
                                      "settle_status": "FAILED",
                                      "device_serial": str(device_serial),
                                      "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR",
                                      "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id,
                                      "bqr_txn_primary_id": txn_id,
                                      "bqr_org_code": org_code,
                                      "txn_amt_2": amount,
                                      "pmt_mode_2": "BHARATQR",
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED",
                                      "acquirer_code_2": "HDFC",
                                      "bank_name_2": "HDFC Bank",
                                      "mid_2": mid,
                                      "tid_2": tid,
                                      "pmt_gateway_2": "MINTOAK",
                                      "rrn_2": str(rrn_new),
                                      "settle_status_2": "SETTLED",
                                      "device_serial_2": str(device_serial),
                                      "bqr_pmt_status_2": "Success",
                                      "bqr_pmt_state_2": "SETTLED",
                                      "bqr_txn_amt_2": amount,
                                      "bqr_txn_type_2": "DYNAMIC_QR",
                                      "brq_terminal_info_id_2": terminal_info_id,
                                      "bqr_bank_code_2": "HDFC",
                                      "bqr_merchant_config_id_2": bqr_mc_id,
                                      "bqr_txn_primary_id_2": txn_id_new,
                                      "bqr_rrn_2": str(rrn_new),
                                      "bqr_org_code_2": org_code
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = float(result["amount"].values[0])
                payment_mode_db_new = result["payment_mode"].values[0]
                payment_status_db_new = result["status"].values[0]
                payment_state_db_new = result["state"].values[0]
                acquirer_code_db_new = result["acquirer_code"].values[0]
                bank_name_db_new = result["bank_name"].values[0]
                mid_db_new = result["mid"].values[0]
                tid_db_new = result["tid"].values[0]
                payment_gateway_db_new = result["payment_gateway"].values[0]
                rr_number_db_new = result["rr_number"].values[0]
                settlement_status_db_new = result["settlement_status"].values[0]
                device_serial_db_new = result['device_serial'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = float(result["txn_amount"].values[0])
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].values[0]
                bqr_state_db_new = result["state"].values[0]
                bqr_amount_db_new = float(result["txn_amount"].values[0])
                bqr_txn_type_db_new = result["txn_type"].values[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].values[0]
                bqr_bank_code_db_new = result["bank_code"].values[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].values[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db,
                                    "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db,
                                    "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db,
                                    "bank_name": bank_name_db,
                                    "mid": mid_db,
                                    "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial": str(device_serial_db),
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
                                    "mid_2": mid_db_new,
                                    "tid_2": tid_db_new,
                                    "pmt_gateway_2": payment_gateway_db_new,
                                    "rrn_2": rr_number_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "device_serial_2": str(device_serial_db),
                                    "bqr_pmt_status_2": bqr_status_db_new,
                                    "bqr_pmt_state_2": bqr_state_db_new,
                                    "bqr_txn_amt_2": bqr_amount_db_new,
                                    "bqr_txn_type_2": bqr_txn_type_db_new,
                                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                                    "bqr_bank_code_2": bqr_bank_code_db_new,
                                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                                    "bqr_rrn_2": bqr_rrn_db_new,
                                    "bqr_org_code_2": bqr_org_code_db_new
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "txn_id": txn_id,
                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "rrn_2": "-" if rrn_new is None else rrn_new,
                    "auth_code_2": "-" if auth_code_new is None else auth_code_new,
                    "txn_id_2": txn_id_new
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                rrn_2 = transaction_details[0]['RR Number']
                auth_code_2 = transaction_details[0]['Auth Code']

                date_time = transaction_details[1]['Date & Time']
                transaction_id = transaction_details[1]['Transaction ID']
                total_amount = transaction_details[1]['Total Amount'].split()
                transaction_type = transaction_details[1]['Type']
                status = transaction_details[1]['Status']
                username = transaction_details[1]['Username']
                rrn = transaction_details[1]['RR Number']
                auth_code = transaction_details[1]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "rrn": rrn,
                    "auth_code": auth_code,
                    "txn_id": transaction_id,
                    "date_time_2": date_time_2,
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
                    "username_2": str(username_2),
                    "rrn_2": rrn_2,
                    "auth_code_2": auth_code_2,
                    "txn_id_2": transaction_id_2
                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")

                # ---------------------------------------------------------------------------------------------
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
                expected_values = {'PAID BY:': 'BHARATQR',
                                   'merchant_ref_no': 'Ref # ' + str(order_id),
                                   'RRN': str(rrn_new),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                   'date': txn_date,
                                   'time': txn_time,
                                   'AUTH CODE': "" if auth_code_new is None else auth_code_new
                                   }
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_402():
    """
    Sub Feature Code: Tid_Dep_UI_Common_PM_BQRV4_BQR_Two_Callback_AfterExpiry_AutoRefund_Disabled_HDFC_MINTOAK
    Sub Feature Description: Tid Dep -  Verification of a BQRV4 BQR two Callback After QR code gets expired when auto refund is Disabled via HDFC_MINTOAK
    TC naming code description: 100: Payment Method, 102: BQR, 402: TC402
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username, portal_pw=portal_password,
                                                           payment_mode='BQRV4')

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

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled=1 where " \
                f"org_code ='{org_code}' and acquirer_code='HDFC' and payment_gateway='MINTOAK'"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table inactive: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        query = f"select * from bharatqr_merchant_config where org_code='{org_code}' and " \
                f"status = 'ACTIVE' and bank_code='HDFC_MINTOAK'"
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].values[0]
        tid = result["tid"].values[0]
        terminal_info_id = result["terminal_info_id"].values[0]
        bqr_mc_id = result["id"].values[0]
        bqr_m_pan = result["merchant_pan"].values[0]
        logger.debug(f"Fetching mid, tid,terminal_info_id,bqr_mc_id,bqr_m_pan  from database for current merchant:"
                     f"{mid}, {tid}, {terminal_info_id}, {bqr_mc_id}, {bqr_m_pan}")

        query = f"select device_serial from terminal_info where tid = '{tid}';"
        logger.debug(f"Query to fetch device serial number from the terminal_info for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        device_serial = result['device_serial'].values[0]
        logger.info(f"fetched device_serial is : {device_serial}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(251, 300)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            api_details = DBProcessor.get_api_details('TidDepBqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount), "orderNumber": str(order_id),
                                                                    "deviceSerial": str(device_serial)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response revived for QR generation is : {response}")
            txn_id = str(response["txnId"])
            logger.debug(f"Fetching Txn_id from the API_OUTPUT, Txn_id : {txn_id}")
            logger.debug(f"Txn id for this transaction is : {txn_id} ")
            logger.debug("Waiting for QR code to get expired")
            time.sleep(65)

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is: {created_time}")
            amount_db = float(result["amount"].values[0])
            logger.debug(f"fetched amount_db from txn table is: {amount_db}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is: {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is: {rrn}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"fetched payment_mode_db from txn table is: {payment_mode_db}")
            payment_status_db = result["status"].values[0]
            logger.debug(f"fetched payment_status_db from txn table is: {payment_status_db}")
            payment_state_db = result["state"].values[0]
            logger.debug(f"fetched payment_state_db from txn table is: {payment_state_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"fetched acquirer_code_db from txn table is: {acquirer_code_db}")
            bank_name_db = result["bank_name"].values[0]
            logger.debug(f"fetched bank_name_db from txn table is: {bank_name_db}")
            mid_db = result["mid"].values[0]
            logger.debug(f"fetched mid_db from txn table is: {mid_db}")
            tid_db = result["tid"].values[0]
            logger.debug(f"fetched tid_db from txn table is: {tid_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"fetched payment_gateway_db from txn table is: {payment_gateway_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"fetched settlement_status_db from txn table is: {settlement_status_db}")
            device_serial_db = result['device_serial'].values[0]
            logger.debug(f"fetched device_serial_db from txn table is: {device_serial_db}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new = result["id"].values[0]
            logger.debug(f"fetched txn_id_new from txn table is: {txn_id_new}")
            auth_code_new = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code_new from txn table is: {auth_code_new}")
            rrn_new = result['rr_number'].values[0]
            logger.debug(f"fetched rrn_new from txn table is: {rrn_new}")
            created_time_new = result['created_time'].values[0]
            logger.debug(f"fetched created_time_new from txn table is: {created_time_new}")

            logger.debug(f"preparing data to perform the encryption generation")
            mtxn_id = str(random.randint(10000000000000000000, 99999999999999999999))
            issuer_ref_number = str(random.randint(10000000, 99999999))

            api_details_encryption = DBProcessor.get_api_details('mintoak_encryption_callback_success')
            api_details_encryption['RequestBody']['terminalId'] = tid
            api_details_encryption['RequestBody']['payload']['mTxnid'] = mtxn_id
            api_details_encryption['RequestBody']['payload']['issuerRefNo'] = issuer_ref_number
            api_details_encryption['RequestBody']['payload']['partnerTxnid'] = txn_id
            api_details_encryption['RequestBody']['payload']['amount'] = amount
            api_details_encryption['RequestBody']['payload']['subType'] = "BharatQR-Cards"

            logger.debug(f"api_details for mintoak_encryption_callback API is: {api_details_encryption}")
            response = APIProcessor.send_request(api_details_encryption)
            logger.debug(f"Response received for  mintoak_encryption_callback API  is : {response}")
            encrypted_data = response['encryptedData']
            logger.debug(
                f"encryptedData received for mintoak_encryption_callback api is : {encrypted_data}")
            logger.debug(f"performing  callback for mintoak")
            api_details = DBProcessor.get_api_details('callback_confirm_mintoak', request_body={
                "terminalId": tid,
                "transactionDetail": encrypted_data
            })
            logger.debug(f"api details for callback_confirm_mintoak : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for callback_confirm_mintoak api is : {response}")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_new_2 = result["id"].values[0]
            logger.debug(f"fetched txn_id_new_2 from txn table is: {txn_id_new_2}")
            auth_code_new_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code_new_2 from txn table is: {auth_code_new_2}")
            rrn_new_2 = result['rr_number'].values[0]
            logger.debug(f"fetched rrn_new_2 from txn table is: {rrn_new_2}")
            created_time_new_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time_new_2 from txn table is: {created_time_new_2}")
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
                date_and_time = date_time_converter.to_app_format(created_time)
                date_and_time_new = date_time_converter.to_app_format(created_time_new)
                date_and_time_new_2 = date_time_converter.to_app_format(created_time_new_2)
                expected_app_values = {"pmt_mode": "BHARAT QR", "pmt_status": "EXPIRED",
                                       "txn_amt": "{:.2f}".format(amount),
                                       "settle_status": "FAILED", "txn_id": txn_id,
                                       "order_id": order_id, "pmt_msg": "PAYMENT FAILED",
                                       "date": date_and_time,
                                       "pmt_mode_2": "BHARAT QR", "pmt_status_2": "AUTHORIZED",
                                       "txn_amt_2": "{:.2f}".format(amount), "rrn_2": str(rrn_new),
                                       "settle_status_2": "SETTLED", "txn_id_2": txn_id_new,
                                       "order_id_2": order_id, "pmt_msg_2": "PAYMENT SUCCESSFUL",
                                       "date_2": date_and_time_new,
                                       "pmt_mode_3": "BHARAT QR", "pmt_status_3": "AUTHORIZED",
                                       "txn_amt_3": "{:.2f}".format(amount), "rrn_3": str(rrn_new_2),
                                       "settle_status_3": "SETTLED", "txn_id_3": txn_id_new_2,
                                       "order_id_3": order_id, "pmt_msg_3": "PAYMENT SUCCESSFUL",
                                       "date_3": date_and_time_new_2
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new)
                payment_status_new = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new}, {payment_status_new}")
                payment_mode_new = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_new}, {payment_mode_new}")
                app_txn_id_new = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_txn_id_new}")
                app_amount_new = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new}, {app_amount_new}")
                app_date_and_time_new = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new}, {app_date_and_time_new}")
                app_settlement_status_new = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new}, {app_settlement_status_new}")
                app_payment_msg_new = txn_history_page.fetch_txn_payment_message_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new}, {app_payment_msg_new}")
                app_order_id_new = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_new}, {app_order_id_new}")
                app_rrn_new = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new}, {app_rrn_new}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_new_2)
                payment_status_new_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_new_2}, {payment_status_new_2}")
                payment_mode_new_2 = txn_history_page.fetch_txn_type_text()
                logger.info(
                    f"Fetching payment mode from txn history for the txn : {txn_id_new_2}, {payment_mode_new_2}")
                app_txn_id_new_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_txn_id_new_2}")
                app_amount_new_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_new_2}, {app_amount_new_2}")
                app_date_and_time_new_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_new_2}, {app_date_and_time_new_2}")
                app_settlement_status_new_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_new_2}, {app_settlement_status_new_2}")
                app_payment_msg_new_2 = txn_history_page.fetch_txn_payment_message_text()
                logger.info(
                    f"Fetching txn status msg from txn history for the txn : {txn_id_new_2}, {app_payment_msg_new_2}")
                app_order_id_new_2 = txn_history_page.fetch_order_id_text()
                logger.info(
                    f"Fetching txn order_id from txn history for the txn : {txn_id_new_2}, {app_order_id_new_2}")
                app_rrn_new_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_new_2}, {app_rrn_new_2}")

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id,
                                     "settle_status": app_settlement_status,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg, "date": app_date_and_time,
                                     "pmt_mode_2": payment_mode_new, "pmt_status_2": payment_status_new.split(':')[1],
                                     "txn_amt_2": app_amount_new.split(' ')[1],
                                     "txn_id_2": app_txn_id_new, "rrn_2": str(app_rrn_new),
                                     "settle_status_2": app_settlement_status_new,
                                     "order_id_2": app_order_id_new,
                                     "pmt_msg_2": app_payment_msg_new, "date_2": app_date_and_time_new,
                                     "pmt_mode_3": payment_mode_new_2,
                                     "pmt_status_3": payment_status_new_2.split(':')[1],
                                     "txn_amt_3": app_amount_new_2.split(' ')[1],
                                     "txn_id_3": app_txn_id_new_2, "rrn_3": str(app_rrn_new_2),
                                     "settle_status_3": app_settlement_status_new_2,
                                     "order_id_3": app_order_id_new_2,
                                     "pmt_msg_3": app_payment_msg_new_2, "date_3": app_date_and_time_new_2
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
                date_new_2 = date_time_converter.db_datetime(created_time_new_2)
                expected_api_values = {"pmt_status": "EXPIRED", "txn_amt": amount, "pmt_mode": "BHARATQR",
                                       "pmt_state": "EXPIRED", "settle_status": "FAILED",
                                       "acquirer_code": "HDFC", "issuer_code": "HDFC", "txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code,
                                       "date": date, "device_serial": str(device_serial),
                                       "pmt_status_2": "AUTHORIZED", "txn_amt_2": amount,
                                       "pmt_mode_2": "BHARATQR", "pmt_state_2": "SETTLED",
                                       "rrn_2": str(rrn_new), "settle_status_2": "SETTLED", "acquirer_code_2": "HDFC",
                                       "issuer_code_2": "HDFC", "txn_type_2": "CHARGE",
                                       "mid_2": mid, "tid_2": tid, "org_code_2": org_code,
                                       "date_2": date_new,
                                       "device_serial_2": str(device_serial),
                                       "pmt_status_3": "AUTHORIZED", "txn_amt_3": amount,
                                       "pmt_mode_3": "BHARATQR", "pmt_state_3": "SETTLED",
                                       "rrn_3": str(rrn_new_2), "settle_status_3": "SETTLED",
                                       "acquirer_code_3": "HDFC",
                                       "issuer_code_3": "HDFC", "txn_type_3": "CHARGE",
                                       "mid_3": mid, "tid_3": tid, "org_code_3": org_code,
                                       "date_3": date_new_2,
                                       "device_serial_3": str(device_serial)
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"value of responseInList is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = float(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
                        state_api = elements["states"][0]
                        settlement_status_api = elements["settlementStatus"]
                        issuer_code_api = elements["issuerCode"]
                        acquirer_code_api = elements["acquirerCode"]
                        orgCode_api = elements["orgCode"]
                        mid_api = elements["mid"]
                        tid_api = elements["tid"]
                        txn_type_api = elements["txnType"]
                        date_api = elements["createdTime"]
                        device_serial_api = elements["deviceSerial"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_new:
                        status_api_new = elements["status"]
                        amount_api_new = float(elements["amount"])
                        payment_mode_api_new = elements["paymentMode"]
                        state_api_new = elements["states"][0]
                        rrn_api_new = elements["rrNumber"]
                        settlement_status_api_new = elements["settlementStatus"]
                        issuer_code_api_new = elements["issuerCode"]
                        acquirer_code_api_new = elements["acquirerCode"]
                        org_code_api_new = elements["orgCode"]
                        mid_api_new = elements["mid"]
                        tid_api_new = elements["tid"]
                        txn_type_api_new = elements["txnType"]
                        date_api_new = elements["createdTime"]
                        device_serial_api_new = elements["deviceSerial"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_new_2:
                        status_api_new_2 = elements["status"]
                        amount_api_new_2 = float(elements["amount"])
                        payment_mode_api_new_2 = elements["paymentMode"]
                        state_api_new_2 = elements["states"][0]
                        rrn_api_new_2 = elements["rrNumber"]
                        settlement_status_api_new_2 = elements["settlementStatus"]
                        issuer_code_api_new_2 = elements["issuerCode"]
                        acquirer_code_api_new_2 = elements["acquirerCode"]
                        org_code_api_new_2 = elements["orgCode"]
                        mid_api_new_2 = elements["mid"]
                        tid_api_new_2 = elements["tid"]
                        txn_type_api_new_2 = elements["txnType"]
                        date_api_new_2 = elements["createdTime"]
                        device_serial_api_new_2 = elements["deviceSerial"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api, "pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api, "issuer_code": issuer_code_api, "mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "device_serial": str(device_serial_api),
                                     "pmt_status_2": status_api_new, "txn_amt_2": amount_api_new,
                                     "pmt_mode_2": payment_mode_api_new,
                                     "pmt_state_2": state_api_new, "rrn_2": str(rrn_api_new),
                                     "settle_status_2": settlement_status_api_new,
                                     "acquirer_code_2": acquirer_code_api_new,
                                     "issuer_code_2": issuer_code_api_new, "mid_2": mid_api_new,
                                     "txn_type_2": txn_type_api_new, "tid_2": tid_api_new,
                                     "org_code_2": org_code_api_new,
                                     "date_2": date_time_converter.from_api_to_datetime_format(date_api_new),
                                     "device_serial_2": str(device_serial_api_new),
                                     "pmt_status_3": status_api_new_2, "txn_amt_3": amount_api_new_2,
                                     "pmt_mode_3": payment_mode_api_new_2,
                                     "pmt_state_3": state_api_new_2, "rrn_3": str(rrn_api_new_2),
                                     "settle_status_3": settlement_status_api_new_2,
                                     "acquirer_code_3": acquirer_code_api_new_2,
                                     "issuer_code_3": issuer_code_api_new_2, "mid_3": mid_api_new_2,
                                     "txn_type_3": txn_type_api_new_2, "tid_3": tid_api_new_2,
                                     "org_code_3": org_code_api_new_2,
                                     "date_3": date_time_converter.from_api_to_datetime_format(date_api_new_2),
                                     "device_serial_3": str(device_serial_api_new_2)
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
                expected_db_values = {"txn_amt": amount, "pmt_mode": "BHARATQR", "pmt_status": "EXPIRED",
                                      "pmt_state": "EXPIRED", "acquirer_code": "HDFC", "bank_name": "HDFC Bank",
                                      "mid": mid, "tid": tid, "pmt_gateway": "MINTOAK",
                                      "settle_status": "FAILED",
                                      "device_serial": str(device_serial),
                                      "bqr_pmt_state": "EXPIRED",
                                      "bqr_txn_amt": amount,
                                      "bqr_txn_type": "DYNAMIC_QR", "brq_terminal_info_id": terminal_info_id,
                                      "bqr_bank_code": "HDFC",
                                      "bqr_merchant_config_id": bqr_mc_id, "bqr_txn_primary_id": txn_id,
                                      "bqr_org_code": org_code,
                                      "txn_amt_2": amount, "pmt_mode_2": "BHARATQR",
                                      "pmt_status_2": "AUTHORIZED",
                                      "pmt_state_2": "SETTLED", "acquirer_code_2": "HDFC",
                                      "bank_name_2": "HDFC Bank",
                                      "mid_2": mid, "tid_2": tid, "pmt_gateway_2": "MINTOAK",
                                      "rrn_2": str(rrn_new), "settle_status_2": "SETTLED",
                                      "bqr_pmt_status_2": "Success", "bqr_pmt_state_2": "SETTLED",
                                      "bqr_txn_amt_2": amount,
                                      "bqr_txn_type_2": "DYNAMIC_QR", "brq_terminal_info_id_2": terminal_info_id,
                                      "bqr_bank_code_2": "HDFC",
                                      "bqr_merchant_config_id_2": bqr_mc_id, "bqr_txn_primary_id_2": txn_id_new,
                                      "bqr_rrn_2": str(rrn_new), "bqr_org_code_2": org_code,
                                      "device_serial_2": str(device_serial),
                                      "txn_amt_3": amount, "pmt_mode_3": "BHARATQR",
                                      "pmt_status_3": "AUTHORIZED",
                                      "pmt_state_3": "SETTLED", "acquirer_code_3": "HDFC",
                                      "bank_name_3": "HDFC Bank",
                                      "mid_3": mid, "tid_3": tid, "pmt_gateway_3": "MINTOAK",
                                      "rrn_3": str(rrn_new_2), "settle_status_3": "SETTLED",
                                      "bqr_pmt_status_3": "Success", "bqr_pmt_state_3": "SETTLED",
                                      "bqr_txn_amt_3": amount,
                                      "bqr_txn_type_3": "DYNAMIC_QR",
                                      "brq_terminal_info_id_3": terminal_info_id,
                                      "bqr_bank_code_3": "HDFC",
                                      "bqr_merchant_config_id_3": bqr_mc_id,
                                      "bqr_txn_primary_id_3": txn_id_new_2,
                                      "bqr_rrn_3": str(rrn_new_2), "bqr_org_code_3": org_code,
                                      "device_serial_3": str(device_serial)
                                      }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new = float(result["amount"].values[0])
                payment_mode_db_new = result["payment_mode"].values[0]
                payment_status_db_new = result["status"].values[0]
                payment_state_db_new = result["state"].values[0]
                acquirer_code_db_new = result["acquirer_code"].values[0]
                bank_name_db_new = result["bank_name"].values[0]
                mid_db_new = result["mid"].values[0]
                tid_db_new = result["tid"].values[0]
                payment_gateway_db_new = result["payment_gateway"].values[0]
                rr_number_db_new = result["rr_number"].values[0]
                settlement_status_db_new = result["settlement_status"].values[0]
                device_serial_db_new = result['device_serial'].values[0]

                query = f"select * from txn where id='{txn_id_new_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db_new_2 = float(result["amount"].values[0])
                payment_mode_db_new_2 = result["payment_mode"].values[0]
                payment_status_db_new_2 = result["status"].values[0]
                payment_state_db_new_2 = result["state"].values[0]
                acquirer_code_db_new_2 = result["acquirer_code"].values[0]
                bank_name_db_new_2 = result["bank_name"].values[0]
                mid_db_new_2 = result["mid"].values[0]
                tid_db_new_2 = result["tid"].values[0]
                payment_gateway_db_new_2 = result["payment_gateway"].values[0]
                rr_number_db_new_2 = result["rr_number"].values[0]
                settlement_status_db_new_2 = result["settlement_status"].values[0]
                device_serial_db_new_2 = result['device_serial'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db = result["status_desc"].values[0]
                bqr_state_db = result["state"].values[0]
                bqr_amount_db = float(result["txn_amount"].values[0])
                bqr_txn_type_db = result["txn_type"].values[0]
                brq_terminal_info_id_db = result["terminal_info_id"].values[0]
                bqr_bank_code_db = result["bank_code"].values[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db = result["transaction_primary_id"].values[0]
                bqr_org_code_db = result['org_code'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id_new}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new = result["status_desc"].values[0]
                bqr_state_db_new = result["state"].values[0]
                bqr_amount_db_new = float(result["txn_amount"].values[0])
                bqr_txn_type_db_new = result["txn_type"].values[0]
                brq_terminal_info_id_db_new = result["terminal_info_id"].values[0]
                bqr_bank_code_db_new = result["bank_code"].values[0]
                bqr_merchant_config_id_db_new = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db_new = result["transaction_primary_id"].values[0]
                bqr_rrn_db_new = result['rrn'].values[0]
                bqr_org_code_db_new = result['org_code'].values[0]

                query = f"select * from bharatqr_txn where id='{txn_id_new_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_db_new_2 = result["status_desc"].values[0]
                bqr_state_db_new_2 = result["state"].values[0]
                bqr_amount_db_new_2 = float(result["txn_amount"].values[0])
                bqr_txn_type_db_new_2 = result["txn_type"].values[0]
                brq_terminal_info_id_db_new_2 = result["terminal_info_id"].values[0]
                bqr_bank_code_db_new_2 = result["bank_code"].values[0]
                bqr_merchant_config_id_db_new_2 = result["merchant_config_id"].values[0]
                bqr_txn_primary_id_db_new_2 = result["transaction_primary_id"].values[0]
                bqr_rrn_db_new_2 = result['rrn'].values[0]
                bqr_org_code_db_new_2 = result['org_code'].values[0]

                actual_db_values = {"txn_amt": amount_db, "pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code": acquirer_code_db, "bank_name": bank_name_db,
                                    "mid": mid_db, "tid": tid_db,
                                    "pmt_gateway": payment_gateway_db,
                                    "settle_status": settlement_status_db,
                                    "device_serial": str(device_serial_db),
                                    "bqr_pmt_state": bqr_state_db,
                                    "bqr_txn_amt": bqr_amount_db,
                                    "bqr_txn_type": bqr_txn_type_db, "brq_terminal_info_id": brq_terminal_info_id_db,
                                    "bqr_bank_code": bqr_bank_code_db,
                                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                                    "bqr_txn_primary_id": bqr_txn_primary_id_db,
                                    "bqr_org_code": bqr_org_code_db,
                                    "txn_amt_2": amount_db_new, "pmt_mode_2": payment_mode_db_new,
                                    "pmt_status_2": payment_status_db_new, "pmt_state_2": payment_state_db_new,
                                    "acquirer_code_2": acquirer_code_db_new, "bank_name_2": bank_name_db_new,
                                    "mid_2": mid_db_new, "tid_2": tid_db_new,
                                    "pmt_gateway_2": payment_gateway_db_new, "rrn_2": rr_number_db_new,
                                    "settle_status_2": settlement_status_db_new,
                                    "device_serial_2": str(device_serial_db_new),
                                    "bqr_pmt_status_2": bqr_status_db_new, "bqr_pmt_state_2": bqr_state_db_new,
                                    "bqr_txn_amt_2": bqr_amount_db_new,
                                    "bqr_txn_type_2": bqr_txn_type_db_new,
                                    "brq_terminal_info_id_2": brq_terminal_info_id_db_new,
                                    "bqr_bank_code_2": bqr_bank_code_db_new,
                                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_new,
                                    "bqr_txn_primary_id_2": bqr_txn_primary_id_db_new,
                                    "bqr_rrn_2": bqr_rrn_db_new, "bqr_org_code_2": bqr_org_code_db_new,
                                    "txn_amt_3": amount_db_new_2, "pmt_mode_3": payment_mode_db_new_2,
                                    "pmt_status_3": payment_status_db_new_2,
                                    "pmt_state_3": payment_state_db_new_2,
                                    "acquirer_code_3": acquirer_code_db_new_2,
                                    "bank_name_3": bank_name_db_new_2,
                                    "mid_3": mid_db_new_2, "tid_3": tid_db_new_2,
                                    "pmt_gateway_3": payment_gateway_db_new_2, "rrn_3": rr_number_db_new_2,
                                    "settle_status_3": settlement_status_db_new_2,
                                    "device_serial_3": str(device_serial_db_new_2),
                                    "bqr_pmt_status_3": bqr_status_db_new_2,
                                    "bqr_pmt_state_3": bqr_state_db_new_2,
                                    "bqr_txn_amt_3": bqr_amount_db_new_2,
                                    "bqr_txn_type_3": bqr_txn_type_db_new_2,
                                    "brq_terminal_info_id_3": brq_terminal_info_id_db_new_2,
                                    "bqr_bank_code_3": bqr_bank_code_db_new_2,
                                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_new_2,
                                    "bqr_txn_primary_id_3": bqr_txn_primary_id_db_new_2,
                                    "bqr_rrn_3": bqr_rrn_db_new_2, "bqr_org_code_3": bqr_org_code_db_new_2
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
                # --------------------------------------------------------------------------------------------
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_new)
                date_and_time_portal_3 = date_time_converter.to_portal_format(created_time_new_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "EXPIRED",
                    "pmt_type": "BHARATQR",
                    "txn_amt": f"{str(amount)}.00",
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "BHARATQR",
                    "txn_amt_2": f"{str(amount)}.00",
                    "username_2": app_username,
                    "txn_id_2": txn_id_new,
                    "auth_code_2": "-" if auth_code_new is None else auth_code_new,
                    "rrn_2": "-" if rrn_new is None else rrn_new,

                    "date_time_3": date_and_time_portal_3,
                    "pmt_state_3": "AUTHORIZED",
                    "pmt_type_3": "BHARATQR",
                    "txn_amt_3": f"{str(amount)}.00",
                    "username_3": app_username,
                    "txn_id_3": txn_id_new_2,
                    "auth_code_3": "-" if auth_code_new_2 is None else auth_code_new_2,
                    "rrn_3": "-" if rrn_new_2 is None else rrn_new_2

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time_2 = transaction_details[0]['Date & Time']
                transaction_id_2 = transaction_details[0]['Transaction ID']
                total_amount_2 = transaction_details[0]['Total Amount'].split()
                transaction_type_2 = transaction_details[0]['Type']
                status_2 = transaction_details[0]['Status']
                username_2 = transaction_details[0]['Username']
                rrn_2 = transaction_details[0]['RR Number']
                auth_code_2 = transaction_details[0]['Auth Code']

                date_time_1 = transaction_details[1]['Date & Time']
                transaction_id_1 = transaction_details[1]['Transaction ID']
                total_amount_1 = transaction_details[1]['Total Amount'].split()
                transaction_type_1 = transaction_details[1]['Type']
                status_1 = transaction_details[1]['Status']
                username_1 = transaction_details[1]['Username']
                rrn_1 = transaction_details[1]['RR Number']
                auth_code_1 = transaction_details[1]['Auth Code']

                date_time = transaction_details[2]['Date & Time']
                transaction_id = transaction_details[2]['Transaction ID']
                total_amount = transaction_details[2]['Total Amount'].split()
                transaction_type = transaction_details[2]['Type']
                status = transaction_details[2]['Status']
                username = transaction_details[2]['Username']
                auth_code = transaction_details[2]['Auth Code']
                rrn = transaction_details[2]['RR Number']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "auth_code": auth_code,
                    "rrn": str(rrn),
                    "date_time_2": date_time_1,
                    "pmt_state_2": str(status_1),
                    "pmt_type_2": transaction_type_1,
                    "txn_amt_2": total_amount_1[1],
                    "username_2": username_1,
                    "txn_id_2": transaction_id_1,
                    "auth_code_2": auth_code_1,
                    "rrn_2": str(rrn_1),
                    "date_time_3": date_time_2,
                    "pmt_state_3": str(status_2),
                    "pmt_type_3": transaction_type_2,
                    "txn_amt_3": total_amount_2[1],
                    "username_3": str(username_2),
                    "txn_id_3": transaction_id_2,
                    "auth_code_3": auth_code_2,
                    "rrn_3": str(rrn_2)

                }
                logger.debug(f"actual_portal_values : {actual_portal_values} for the testcase_id : {testcase_id}")
                # ---------------------------------------------------------------------------------------------
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
                                   'AUTH CODE': "" if auth_code_new is None else auth_code_new}
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
