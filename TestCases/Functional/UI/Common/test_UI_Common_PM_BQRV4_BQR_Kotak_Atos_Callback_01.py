import random
import sys
import time
from datetime import datetime

import pytest

from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    receipt_validator, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_237():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_Success_Callback_KOTAK_ATOS
    Sub Feature Description: Verification of a successful bqr txn using BQRV4 BQR Success Callback via Kotak_ATOS
    TC naming code description:
    100: Payment Method
    102: BQRV4
    237: TC237
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info("Home page loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provider_ref_id = result["provider_ref_id"].iloc[0]
            txn_secondary_id = result["transaction_secondary_id"].iloc[0]
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + str(random.randint(110000000, 110099999))
            rrn = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "auth_code": auth_code, "ref_no": rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
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

            logger.info(f"Execution is completed for the test case : {testcase_id}")

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
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    # "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    # "payer_name": app_payer_name,
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
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
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
                        auth_code_api = elements["authCode"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
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
                    # "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    # "upi_txn_type": "PAY_BQR",
                    # "upi_bank_code": "KOTAK_WL",
                    # "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "KOTAK",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                # query = "select * from upi_txn where txn_id='" + txn_id + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db = result["status"].iloc[0]
                # upi_txn_type_db = result["txn_type"].iloc[0]
                # upi_bank_code_db = result["bank_code"].iloc[0]
                # upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    # "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    # "upi_txn_type": upi_txn_type_db,
                    # "upi_bank_code": upi_bank_code_db,
                    # "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
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
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_238():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_2_Success_Callback_KOTAK_ATOS
    Sub Feature Description: Verification of a successful bqr txn using 2 BQRV4 BQR Success Callback via Kotak_ATOS
    TC naming code description:
    100: Payment Method
    102: BQRV4
    238: TC238
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info("Home page loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")

            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provider_ref_id = result["provider_ref_id"].iloc[0]
            txn_secondary_id = result["transaction_secondary_id"].iloc[0]
            txn_id = result["id"].iloc[0]
            auth_code = "AE" + str(random.randint(110000000, 110099999))
            rrn = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "auth_code": auth_code, "ref_no": rrn,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
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

            auth_code_2 = "AE" + str(random.randint(110000000, 110099999))
            rrn_2 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "auth_code": auth_code_2, "ref_no": rrn_2,
                "mpan": merchant_pan
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_txn_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time_2 : {created_time_2}")

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
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    # "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    # "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                # app_payer_name = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                # app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")
                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    # "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "pmt_mode_2": payment_mode_2,
                    "pmt_status_2": payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "customer_name_2": app_customer_name_2,
                    "settle_status_2": app_settlement_status_2,
                    # "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
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
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "auth_code": auth_code,
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount, "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": txn_type_2, "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "auth_code_2": auth_code_2,
                    "date_2": date_2,
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
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
                        auth_code_api = elements["authCode"]
                        date_api = elements["createdTime"]
                        customer_name_api = elements["customerName"]
                        payer_name_api = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id_2} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        amount_api_2 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api_2 = elements["paymentMode"]
                        state_api_2 = elements["states"][0]
                        rrn_api_2 = elements["rrNumber"]
                        settlement_status_api_2 = elements["settlementStatus"]
                        issuer_code_api_2 = elements["issuerCode"]
                        acquirer_code_api_2 = elements["acquirerCode"]
                        orgCode_api_2 = elements["orgCode"]
                        mid_api_2 = elements["mid"]
                        tid_api_2 = elements["tid"]
                        txn_type_api_2 = elements["txnType"]
                        auth_code_api_2 = elements["authCode"]
                        date_api_2 = elements["createdTime"]
                        customer_name_api_2 = elements["customerName"]
                        payer_name_api_2 = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "auth_code": auth_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "customer_name_2": customer_name_api_2,
                    "payer_name_2": payer_name_api_2,
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
                    # "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    # "upi_txn_type": "PAY_BQR",
                    # "upi_bank_code": "KOTAK_WL",
                    # "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "bqr_pmt_status_code": "SUCCESS",
                    "bqr_pmt_state": "SETTLED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "KOTAK",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount,
                    # "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "KOTAK_ATOS",
                    # "upi_txn_type_2": "PAY_BQR",
                    # "upi_bank_code_2": "KOTAK_WL",
                    # "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_status_code_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": amount,
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "bqr_terminal_info_id_2": terminal_info_id,
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_2,
                    # "bqr_merchant_pan_2": merchant_pan,
                    "bqr_rrn_2": rrn_2,
                    "bqr_org_code_2": org_code,
                    "bqr_bank_code_2": "KOTAK",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                # query = "select * from upi_txn where txn_id='" + txn_id + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db = result["status"].iloc[0]
                # upi_txn_type_db = result["txn_type"].iloc[0]
                # upi_bank_code_db = result["bank_code"].iloc[0]
                # upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].iloc[0]
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                amount_db_2 = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_2 = result["state"].iloc[0]
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                bank_code_db_2 = result["bank_code"].iloc[0]
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]

                # query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db_2 = result["status"].iloc[0]
                # upi_txn_type_db_2 = result["txn_type"].iloc[0]
                # upi_bank_code_db_2 = result["bank_code"].iloc[0]
                # upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db_2 = result["status_code"].iloc[0]
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_txn_amt_db_2 = result["txn_amount"].iloc[0]
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_2 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_2 = result["rrn"].iloc[0]
                bqr_org_code_db_2 = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    # "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    # "upi_txn_type": upi_txn_type_db,
                    # "upi_bank_code": upi_bank_code_db,
                    # "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    # "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    # "upi_txn_type_2": upi_txn_type_db_2,
                    # "upi_bank_code_2": upi_bank_code_db_2,
                    # "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "bqr_pmt_status_code_2": bqr_status_code_db_2,
                    "bqr_pmt_state_2": bqr_state_db_2,
                    "bqr_txn_amt_2": bqr_txn_amt_db_2,
                    "bqr_txn_type_2": bqr_txn_type_db_2,
                    "bqr_terminal_info_id_2": bqr_terminal_info_id_db_2,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id_2": bqr_transaction_primary_id_db_2,
                    # "bqr_merchant_pan_2": bqr_merchant_pan_db_2,
                    "bqr_rrn_2": bqr_rrn_db_2,
                    "bqr_org_code_2": bqr_org_code_db_2,
                    "bqr_bank_code_2": bqr_bank_code_db_2,
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
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date,
                    'time': txn_time, 'AUTH CODE': str(auth_code)
                }
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }
                chargeslip_val_result_1 = receipt_validator.perform_charge_slip_validations(txn_id,
                    {"username": app_username, "password": app_password}, expected_charge_slip_values_1)
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                     {"username": app_username, "password": app_password}, expected_charge_slip_values_2)
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_244():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_BQR_Success_Callback_After_QR_Expiry_KOTAK_ATOS
    Sub Feature Description: Verification of a successful bqr txn using BQRV4 BQR Success Callback after QR expiry via Kotak_ATOS
    TC naming code description:
    100: Payment Method
    102: BQRV4
    244: TC244
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.choice([i for i in range(1, 100) if i not in [45, 46]])
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info("Home page loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)
            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provider_ref_id = result["provider_ref_id"].iloc[0]
            txn_secondary_id = result["transaction_secondary_id"].iloc[0]
            txn_id = result["id"].iloc[0]

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : rrn : {rrn}")

            auth_code_2 = "AE" + str(random.randint(110000000, 110099999))
            rrn_2 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code}, RRN : {rrn}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                # "tr_id": txn_secondary_id,
                "auth_code": auth_code_2, "ref_no": rrn_2,
                "mpan": merchant_pan,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_txn_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time_2 : {created_time_2}")

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
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    # "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                # login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                # home_page = HomePage(app_driver)
                # payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                # app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")
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
                    # "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
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
                date_2 = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount, "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": txn_type_2, "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "auth_code_2": auth_code_2,
                    "date_2": date_2,
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
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

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id_2} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        amount_api_2 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api_2 = elements["paymentMode"]
                        state_api_2 = elements["states"][0]
                        rrn_api_2 = elements["rrNumber"]
                        settlement_status_api_2 = elements["settlementStatus"]
                        issuer_code_api_2 = elements["issuerCode"]
                        acquirer_code_api_2 = elements["acquirerCode"]
                        orgCode_api_2 = elements["orgCode"]
                        mid_api_2 = elements["mid"]
                        tid_api_2 = elements["tid"]
                        txn_type_api_2 = elements["txnType"]
                        auth_code_api_2 = elements["authCode"]
                        date_api_2 = elements["createdTime"]
                        customer_name_api_2 = elements["customerName"]
                        payer_name_api_2 = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "customer_name_2": customer_name_api_2,
                    "payer_name_2": payer_name_api_2,
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    # "upi_txn_status": "AUTHORIZED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    # "upi_txn_type": "PAY_BQR",
                    # "upi_bank_code": "KOTAK_WL",
                    # "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    # "bqr_pmt_status_code": "EXPIRED",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "KOTAK",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount,
                    # "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "KOTAK_ATOS",
                    # "upi_txn_type_2": "PAY_BQR",
                    # "upi_bank_code_2": "KOTAK_WL",
                    # "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_status_code_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": amount,
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "bqr_terminal_info_id_2": terminal_info_id,
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_2,
                    "bqr_merchant_pan_2": merchant_pan,
                    "bqr_rrn_2": rrn_2,
                    "bqr_org_code_2": org_code,
                    "bqr_bank_code_2": "KOTAK",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                # query = "select * from upi_txn where txn_id='" + txn_id + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db = result["status"].iloc[0]
                # upi_txn_type_db = result["txn_type"].iloc[0]
                # upi_bank_code_db = result["bank_code"].iloc[0]
                # upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].iloc[0]
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                amount_db_2 = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_2 = result["state"].iloc[0]
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                bank_code_db_2 = result["bank_code"].iloc[0]
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]

                # query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db_2 = result["status"].iloc[0]
                # upi_txn_type_db_2 = result["txn_type"].iloc[0]
                # upi_bank_code_db_2 = result["bank_code"].iloc[0]
                # upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db_2 = result["status_code"].iloc[0]
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_txn_amt_db_2 = result["txn_amount"].iloc[0]
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_2 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_2 = result["rrn"].iloc[0]
                bqr_org_code_db_2 = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    # "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    # "upi_txn_type": upi_txn_type_db,
                    # "upi_bank_code": upi_bank_code_db,
                    # "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    # "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    # "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    # "upi_txn_type_2": upi_txn_type_db_2,
                    # "upi_bank_code_2": upi_bank_code_db_2,
                    # "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "bqr_pmt_status_code_2": bqr_status_code_db_2,
                    "bqr_pmt_state_2": bqr_state_db_2,
                    "bqr_txn_amt_2": bqr_txn_amt_db_2,
                    "bqr_txn_type_2": bqr_txn_type_db_2,
                    "bqr_terminal_info_id_2": bqr_terminal_info_id_db_2,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id_2": bqr_transaction_primary_id_db_2,
                    "bqr_merchant_pan_2": bqr_merchant_pan_db_2,
                    "bqr_rrn_2": bqr_rrn_db_2,
                    "bqr_org_code_2": bqr_org_code_db_2,
                    "bqr_bank_code_2": bqr_bank_code_db_2,
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
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }
                receipt_validator.perform_charge_slip_validations(txn_id_2,
                     {"username": app_username, "password": app_password}, expected_charge_slip_values_2)
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
def test_common_100_102_250():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_2_BQR_Success_Callback_After_QR_Expiry_KOTAK_ATOS
    Sub Feature Description: Verification of 2 successful bqr txn using BQRV4 BQR Success Callback after QR expiry via Kotak_ATOS
    TC naming code description:
    100: Payment Method
    102: BQRV4
    250: TC250
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        api_details["RequestBody"]["settings"]["bharatQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            query = "select * from upi_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_mc_id = result['id'].values[0]
            pg_merchant_id = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            query = "select * from bharatqr_merchant_config where org_code ='" + str(
                org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL'"
            logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            mid = result['mid'].values[0]
            logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
            terminal_info_id = result['terminal_info_id'].values[0]
            logger.debug(
                f"Fetching terminal_info_id from the bharatqr_merchant_config table : terminal_info_id : {terminal_info_id}")
            merchant_config_id = result['id'].values[0]
            logger.debug(
                f"Fetching merchant_config_id from the bharatqr_merchant_config table : merchant_config_id : {merchant_config_id}")
            merchant_pan = result['merchant_pan'].values[0]
            logger.debug(
                f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            logger.info("Home page loaded successfully")
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Bqr_paymentMode()
            logger.info("Selected payment mode is BQR")
            payment_page.validate_upi_bqr_payment_screen()
            logger.info("Payment QR generated and displayed successfully")
            app_driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)
            query = "select * from bharatqr_txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            provider_ref_id = result["provider_ref_id"].iloc[0]
            txn_secondary_id = result["transaction_secondary_id"].iloc[0]
            txn_id = result["id"].iloc[0]

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to auth code from database : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rrn from the txn table : rrn : {rrn}")

            auth_code_2 = "AE" + str(random.randint(110000000, 110099999))
            rrn_2 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code_2}, RRN : {rrn_2}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "auth_code": auth_code_2, "ref_no": rrn_2,
                "mpan": merchant_pan,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_2 : {txn_id_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_2 : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_2 : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_txn_2 : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_2 : {txn_type_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_2 : {auth_code_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time_2 : {created_time_2}")

            auth_code_3 = "AE" + str(random.randint(110000000, 110099999))
            rrn_3 = "RE" + str(random.randint(110000000, 110099999))
            logger.debug(
                f"Fetching Txn_id,Auth code,RRN, primary id and secondary id from data base : Txn_id : {txn_id}, Auth code : {auth_code_3}, RRN : {rrn_3}, Primary id : {provider_ref_id}, Secondary id : {txn_secondary_id}")
            api_details = DBProcessor.get_api_details('callbackBQRKotakAtos', request_body={
                "primary_id": provider_ref_id,
                "secondary_id": txn_secondary_id,
                "txn_amount": str(amount),
                "settlement_amount": str(amount),
                "auth_code": auth_code_3, "ref_no": rrn_3,
                "mpan": merchant_pan,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Fetching API Response for call back : {response}")
            query = "select * from txn where org_code='" + org_code + "' and id LIKE '" + datetime.utcnow().strftime(
                '%y%m%d') + "%' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_3 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : txn_id_3 : {txn_id_3}")
            customer_name_3 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : customer_name_3 : {customer_name_3}")
            payer_name_3 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : payer_name_3 : {payer_name_3}")
            org_code_txn_3 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : org_code_txn_3 : {org_code_txn_3}")
            txn_type_3 = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from the txn table : txn_type_3 : {txn_type_3}")
            auth_code_3 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : auth_code_3 : {auth_code_3}")
            created_time_3 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : created_time_3 : {created_time_3}")

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
                date_and_time_3 = date_time_converter.to_app_format(created_time_3)
                expected_app_values = {
                    "pmt_mode": "BHARAT QR",
                    "pmt_status": "EXPIRED",
                    "txn_amt": str(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "pmt_mode_2": "BHARAT QR",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    # "payer_name_2": payer_name_2,
                    "order_id_2": order_id,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "auth_code_2": auth_code_2,
                    "date_2": date_and_time_2,
                    "pmt_mode_3": "BHARAT QR",
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": str(amount),
                    "settle_status_3": "SETTLED",
                    "txn_id_3": txn_id_3,
                    "rrn_3": str(rrn_3),
                    "customer_name_3": customer_name_3,
                    # "payer_name_3": payer_name_3,
                    "order_id_3": order_id,
                    "pmt_msg_3": "PAYMENT SUCCESSFUL",
                    "auth_code_3": auth_code_3,
                    "date_3": date_and_time_3
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                # login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                # home_page = HomePage(app_driver)
                # payment_page.click_on_proceed_homepage()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                logger.debug("Homepage of MPOSX app loaded successfully")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                # app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_2}, {app_order_id_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_2}")

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
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_3}, {app_customer_name_3}")
                app_settlement_status_3 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_3}, {app_settlement_status_3}")
                # app_payer_name_3 = txn_history_page.fetch_payer_name_text()
                # logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_3}, {app_payer_name_3}")
                app_payment_msg_3 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_3}, {app_payment_msg_3}")
                app_order_id_3 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id_3}, {app_order_id_3}")
                app_rrn_3 = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id_3}, {app_rrn_3}")

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
                    # "payer_name_2": app_payer_name_2,
                    "order_id_2": app_order_id_2,
                    "pmt_msg_2": app_payment_msg_2,
                    "auth_code_2": app_auth_code_2,
                    "date_2": app_date_and_time_2,
                    "pmt_mode_3": payment_mode_3,
                    "pmt_status_3": payment_status_3.split(':')[1],
                    "txn_amt_3": app_amount_2.split(' ')[1],
                    "settle_status_3": app_settlement_status_3,
                    "txn_id_3": app_txn_id_3,
                    "rrn_3": str(app_rrn_3),
                    "customer_name_3": app_customer_name_2,
                    # "payer_name_3": payer_name_3,
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
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                date_2 = date_time_converter.db_datetime(created_time_2)
                date_3 = date_time_converter.db_datetime(created_time_3)
                expected_api_values = {
                    "pmt_status": "EXPIRED",
                    "txn_amt": amount, "pmt_mode": "BHARATQR",
                    "pmt_state": "EXPIRED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "issuer_code": "KOTAK",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": amount, "pmt_mode_2": "BHARATQR",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "issuer_code_2": "KOTAK",
                    "txn_type_2": txn_type_2, "mid_2": mid, "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "auth_code_2": auth_code_2,
                    "date_2": date_2,
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_status_3": "AUTHORIZED",
                    "txn_amt_3": amount, "pmt_mode_3": "BHARATQR",
                    "pmt_state_3": "SETTLED", "rrn_3": str(rrn_3),
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "issuer_code_3": "KOTAK",
                    "txn_type_3": txn_type_3, "mid_3": mid, "tid_3": tid,
                    "org_code_3": org_code_txn_3,
                    "auth_code_3": auth_code_3,
                    "date_3": date_3,
                    "customer_name_3": customer_name_3,
                    "payer_name_3": payer_name_3,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',request_body={"username": app_username,
                                                                        "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # actual=345.00, expected should be in the same format
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

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id_2} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id_2:
                        status_api_2 = elements["status"]
                        amount_api_2 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api_2 = elements["paymentMode"]
                        state_api_2 = elements["states"][0]
                        rrn_api_2 = elements["rrNumber"]
                        settlement_status_api_2 = elements["settlementStatus"]
                        issuer_code_api_2 = elements["issuerCode"]
                        acquirer_code_api_2 = elements["acquirerCode"]
                        orgCode_api_2 = elements["orgCode"]
                        mid_api_2 = elements["mid"]
                        tid_api_2 = elements["tid"]
                        txn_type_api_2 = elements["txnType"]
                        auth_code_api_2 = elements["authCode"]
                        date_api_2 = elements["createdTime"]
                        customer_name_api_2 = elements["customerName"]
                        payer_name_api_2 = elements["payerName"]

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password, })
                logger.debug(f"API DETAILS for txn_id {txn_id_3} is : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for txnlist api is : {response}")
                responseInList = response["txns"]
                logger.debug(f"list of txns is : {responseInList}")
                for elements in responseInList:
                    if elements["txnId"] == txn_id_3:
                        status_api_3 = elements["status"]
                        amount_api_3 = int(elements["amount"])  # actual=345.00, expected should be in the same format
                        payment_mode_api_3 = elements["paymentMode"]
                        state_api_3 = elements["states"][0]
                        rrn_api_3 = elements["rrNumber"]
                        settlement_status_api_3 = elements["settlementStatus"]
                        issuer_code_api_3 = elements["issuerCode"]
                        acquirer_code_api_3 = elements["acquirerCode"]
                        orgCode_api_3 = elements["orgCode"]
                        mid_api_3 = elements["mid"]
                        tid_api_3 = elements["tid"]
                        txn_type_api_3 = elements["txnType"]
                        auth_code_api_3 = elements["authCode"]
                        date_api_3 = elements["createdTime"]
                        customer_name_api_3 = elements["customerName"]
                        payer_name_api_3 = elements["payerName"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api,
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2, "txn_amt_2": amount_api_2,
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2, "mid_2": mid_api_2, "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    "auth_code_2": auth_code_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2),
                    "customer_name_2": customer_name_api_2,
                    "payer_name_2": payer_name_api_2,
                    "pmt_status_3": status_api_3,
                    "txn_amt_3": amount_api_3, "pmt_mode_3": payment_mode_api_3,
                    "pmt_state_3": state_api_3, "rrn_3": str(rrn_api_3),
                    "settle_status_3": settlement_status_api_3,
                    "acquirer_code_3": acquirer_code_api_3,
                    "issuer_code_3": issuer_code_api_3,
                    "txn_type_3": txn_type_api_3, "mid_3": mid_api_3, "tid_3": tid_api_3,
                    "org_code_3": orgCode_api_3,
                    "auth_code_3": auth_code_api_3,
                    "date_3": date_time_converter.from_api_to_datetime_format(date_api_3),
                    "customer_name_3": customer_name_api_3,
                    "payer_name_3": payer_name_api_3,
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
                    "pmt_mode": "BHARATQR",
                    "txn_amt": amount,
                    # "upi_txn_status": "AUTHORIZED",
                    "settle_status": "FAILED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    # "upi_txn_type": "PAY_BQR",
                    # "upi_bank_code": "KOTAK_WL",
                    # "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    # "bqr_pmt_status_code": "EXPIRED",
                    "bqr_pmt_state": "EXPIRED",
                    "bqr_txn_amt": amount,
                    "bqr_txn_type": "DYNAMIC_QR",
                    "bqr_terminal_info_id": terminal_info_id,
                    "bqr_merchant_config_id": merchant_config_id,
                    "bqr_txn_primary_id": txn_id,
                    # "bqr_merchant_pan": merchant_pan,
                    "bqr_rrn": rrn,
                    "bqr_org_code": org_code,
                    "bqr_bank_code": "KOTAK",
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "BHARATQR",
                    "txn_amt_2": amount,
                    # "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "KOTAK",
                    "bank_code_2": "KOTAK",
                    "pmt_gateway_2": "KOTAK_ATOS",
                    # "upi_txn_type_2": "PAY_BQR",
                    # "upi_bank_code_2": "KOTAK_WL",
                    # "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                    "bqr_pmt_status_code_2": "SUCCESS",
                    "bqr_pmt_state_2": "SETTLED",
                    "bqr_txn_amt_2": amount,
                    "bqr_txn_type_2": "DYNAMIC_QR",
                    "bqr_terminal_info_id_2": terminal_info_id,
                    "bqr_merchant_config_id_2": merchant_config_id,
                    "bqr_txn_primary_id_2": txn_id_2,
                    # "bqr_merchant_pan_2": merchant_pan,
                    "bqr_rrn_2": rrn_2,
                    "bqr_org_code_2": org_code,
                    "bqr_bank_code_2": "KOTAK",
                    "pmt_status_3": "AUTHORIZED",
                    "pmt_state_3": "SETTLED",
                    "pmt_mode_3": "BHARATQR",
                    "txn_amt_3": amount,
                    # "upi_txn_status_3": "AUTHORIZED",
                    "settle_status_3": "SETTLED",
                    "acquirer_code_3": "KOTAK",
                    "bank_code_3": "KOTAK",
                    "pmt_gateway_3": "KOTAK_ATOS",
                    # "upi_txn_type_3": "PAY_BQR",
                    # "upi_bank_code_3": "KOTAK_WL",
                    # "upi_mc_id_3": upi_mc_id,
                    "mid_3": mid,
                    "tid_3": tid,
                    "bqr_pmt_status_code_3": "SUCCESS",
                    "bqr_pmt_state_3": "SETTLED",
                    "bqr_txn_amt_3": amount,
                    "bqr_txn_type_3": "DYNAMIC_QR",
                    "bqr_terminal_info_id_3": terminal_info_id,
                    "bqr_merchant_config_id_3": merchant_config_id,
                    "bqr_txn_primary_id_3": txn_id_3,
                    # "bqr_merchant_pan_3": merchant_pan,
                    "bqr_rrn_3": rrn_3,
                    "bqr_org_code_3": org_code,
                    "bqr_bank_code_3": "KOTAK",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
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

                # query = "select * from upi_txn where txn_id='" + txn_id + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db = result["status"].iloc[0]
                # upi_txn_type_db = result["txn_type"].iloc[0]
                # upi_bank_code_db = result["bank_code"].iloc[0]
                # upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db = result["status_code"].iloc[0]
                bqr_state_db = result["state"].iloc[0]
                bqr_txn_amt_db = result["txn_amount"].iloc[0]
                bqr_txn_type_db = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db = result["merchant_pan"].iloc[0]
                bqr_rrn_db = result["rrn"].iloc[0]
                bqr_org_code_db = result["org_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].iloc[0]
                payment_mode_db_2 = result["payment_mode"].iloc[0]
                amount_db_2 = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_2 = result["state"].iloc[0]
                payment_gateway_db_2 = result["payment_gateway"].iloc[0]
                acquirer_code_db_2 = result["acquirer_code"].iloc[0]
                bank_code_db_2 = result["bank_code"].iloc[0]
                settlement_status_db_2 = result["settlement_status"].iloc[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]

                # query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db_2 = result["status"].iloc[0]
                # upi_txn_type_db_2 = result["txn_type"].iloc[0]
                # upi_bank_code_db_2 = result["bank_code"].iloc[0]
                # upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_2 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db_2 = result["status_code"].iloc[0]
                bqr_state_db_2 = result["state"].iloc[0]
                bqr_txn_amt_db_2 = result["txn_amount"].iloc[0]
                bqr_txn_type_db_2 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_2 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_2 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_2 = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db_2 = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_2 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_2 = result["rrn"].iloc[0]
                bqr_org_code_db_2 = result["org_code"].iloc[0]

                query = "select * from txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_3 = result["status"].iloc[0]
                payment_mode_db_3 = result["payment_mode"].iloc[0]
                amount_db_3 = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db_3 = result["state"].iloc[0]
                payment_gateway_db_3 = result["payment_gateway"].iloc[0]
                acquirer_code_db_3 = result["acquirer_code"].iloc[0]
                bank_code_db_3 = result["bank_code"].iloc[0]
                settlement_status_db_3 = result["settlement_status"].iloc[0]
                tid_db_3 = result['tid'].values[0]
                mid_db_3 = result['mid'].values[0]

                # query = "select * from upi_txn where txn_id='" + txn_id_2 + "'"
                # logger.debug(f"Query to fetch data from upi_txn table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # upi_status_db_2 = result["status"].iloc[0]
                # upi_txn_type_db_2 = result["txn_type"].iloc[0]
                # upi_bank_code_db_2 = result["bank_code"].iloc[0]
                # upi_mc_id_db_2 = result["upi_mc_id"].iloc[0]

                query = "select * from bharatqr_txn where id='" + txn_id_3 + "'"
                logger.debug(f"Query to fetch data from bharatqr_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                bqr_status_code_db_3 = result["status_code"].iloc[0]
                bqr_state_db_3 = result["state"].iloc[0]
                bqr_txn_amt_db_3 = result["txn_amount"].iloc[0]
                bqr_txn_type_db_3 = result["txn_type"].iloc[0]
                bqr_terminal_info_id_db_3 = result["terminal_info_id"].iloc[0]
                bqr_bank_code_db_3 = result["bank_code"].iloc[0]
                bqr_merchant_config_id_db_3 = result["merchant_config_id"].iloc[0]
                bqr_transaction_primary_id_db_3 = result["transaction_primary_id"].iloc[0]
                bqr_merchant_pan_db_3 = result["merchant_pan"].iloc[0]
                bqr_rrn_db_3 = result["rrn"].iloc[0]
                bqr_org_code_db_3 = result["org_code"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    # "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    # "upi_txn_type": upi_txn_type_db,
                    # "upi_bank_code": upi_bank_code_db,
                    # "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    # "bqr_pmt_status_code": bqr_status_code_db,
                    "bqr_pmt_state": bqr_state_db,
                    "bqr_txn_amt": bqr_txn_amt_db,
                    "bqr_txn_type": bqr_txn_type_db,
                    "bqr_terminal_info_id": bqr_terminal_info_id_db,
                    "bqr_merchant_config_id": bqr_merchant_config_id_db,
                    "bqr_txn_primary_id": bqr_transaction_primary_id_db,
                    # "bqr_merchant_pan": bqr_merchant_pan_db,
                    "bqr_rrn": bqr_rrn_db,
                    "bqr_org_code": bqr_org_code_db,
                    "bqr_bank_code": bqr_bank_code_db,
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": amount_db_2,
                    # "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    # "upi_txn_type_2": upi_txn_type_db_2,
                    # "upi_bank_code_2": upi_bank_code_db_2,
                    # "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2,
                    "bqr_pmt_status_code_2": bqr_status_code_db_2,
                    "bqr_pmt_state_2": bqr_state_db_2,
                    "bqr_txn_amt_2": bqr_txn_amt_db_2,
                    "bqr_txn_type_2": bqr_txn_type_db_2,
                    "bqr_terminal_info_id_2": bqr_terminal_info_id_db_2,
                    "bqr_merchant_config_id_2": bqr_merchant_config_id_db_2,
                    "bqr_txn_primary_id_2": bqr_transaction_primary_id_db_2,
                    # "bqr_merchant_pan_2": bqr_merchant_pan_db_2,
                    "bqr_rrn_2": bqr_rrn_db_2,
                    "bqr_org_code_2": bqr_org_code_db_2,
                    "bqr_bank_code_2": bqr_bank_code_db_2,
                    "pmt_status_3": status_db_3,
                    "pmt_state_3": state_db_3,
                    "pmt_mode_3": payment_mode_db_3,
                    "txn_amt_3": amount_db_3,
                    "settle_status_3": settlement_status_db_3,
                    "acquirer_code_3": acquirer_code_db_3,
                    "bank_code_3": bank_code_db_3,
                    "pmt_gateway_3": payment_gateway_db_3,
                    "mid_3": mid_db_3,
                    "tid_3": tid_db_3,
                    "bqr_pmt_status_code_3": bqr_status_code_db_3,
                    "bqr_pmt_state_3": bqr_state_db_3,
                    "bqr_txn_amt_3": bqr_txn_amt_db_3,
                    "bqr_txn_type_3": bqr_txn_type_db_3,
                    "bqr_terminal_info_id_3": bqr_terminal_info_id_db_3,
                    "bqr_merchant_config_id_3": bqr_merchant_config_id_db_3,
                    "bqr_txn_primary_id_3": bqr_transaction_primary_id_db_3,
                    # "bqr_merchant_pan_3": bqr_merchant_pan_db_3,
                    "bqr_rrn_3": bqr_rrn_db_3,
                    "bqr_org_code_3": bqr_org_code_db_3,
                    "bqr_bank_code_3": bqr_bank_code_db_3,
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
                expected_portal_values = {
                    "pmt_state": "Settled", "pmt_type": "UPI",
                    "txn_amt": "Rs." + str(amount) + ".00", "username": app_username}
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                portal_driver = TestSuiteSetup.initialize_portal_driver()
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {
                    "pmt_state": str(portal_status), "pmt_type": portal_type,
                    "txn_amt": portal_amount, "username": portal_username}
                logger.debug(f"actual_portal_values : {actual_portal_values}")

                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date_3, txn_time_3 = date_time_converter.to_chargeslip_format(created_time_3)
                txn_date_2, txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values_2 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_2),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_2,
                    'time': txn_time_2, 'AUTH CODE': str(auth_code_2)
                }
                chargeslip_val_result_2 = receipt_validator.perform_charge_slip_validations(txn_id_2,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_2)
                expected_charge_slip_values_3 = {
                    'PAID BY:': 'BHARATQR', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn_3),
                    'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': txn_date_3,
                    'time': txn_time_3, 'AUTH CODE': str(auth_code_3)
                }

                chargeslip_val_result_3 = receipt_validator.perform_charge_slip_validations(txn_id_3,
                                                                                            {"username": app_username,
                                                                                             "password": app_password},
                                                                                            expected_charge_slip_values_3)
                if chargeslip_val_result_3 and chargeslip_val_result_2:
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