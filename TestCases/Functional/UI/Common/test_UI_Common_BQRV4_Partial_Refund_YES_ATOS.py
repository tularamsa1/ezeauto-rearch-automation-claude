import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_102_065():
    """
    :Description: Verification of a BQRV4 Partial Refund via YES_ATOS
    :Sub Feature code: UI_Common_BQRV4_Partial_Refund_YES_ATOS
    :TC naming code description: 100->Payment Method, 102->BQR, 065-> TC65
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

        testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')

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

        query = "select * from upi_merchant_config where org_code='" + org_code + "' " \
                                                             "and status = 'ACTIVE' and bank_code='YES'"
        logger.debug(f"Query to fetch mid, tid, upi_mc_id and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        mid = result["mid"].iloc[0]
        tid = result["tid"].iloc[0]
        logger.debug(f"Fetching mid, tid from database for current merchant:{mid}, {tid}")
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching vpa, upi_mc_id from database for current merchant:{vpa}, {upi_mc_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(301, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.debug(f"Amount and order id for this txn is: {amount}, {order_id}")
            logger.debug("Generating QR using BQR QR generate API")
            api_details = DBProcessor.get_api_details('bqrGenerate',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": str(amount),
                                                                    "orderNumber": str(order_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Resonse recived for QR genration api is : {response}")
            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
            api_details = DBProcessor.get_api_details('stopPayment',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "orgCode":org_code ,"txnId": txn_id})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for stop payment api is : {response}")
            refund_amount = amount - 100
            logger.debug(f"Refund amount to perform partial refund is : {refund_amount}")
            api_details = DBProcessor.get_api_details('paymentRefund',
                                                      request_body={"username": app_username, "password": app_password,
                                                                    "amount": refund_amount,
                                                                    "originalTransactionId": str(txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            partial_refund_message = response["message"]
            logger.debug(f"Message for performing partial refund of txn is : {partial_refund_message}")

            query = "select * from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result["id"].iloc[0]
            auth_code = result['auth_code'].values[0]
            rrn = result['rr_number'].iloc[0]
            posting_date = result['posting_date'].values[0]
            customer_name = result['customer_name'].values[0]
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching auth_code, rrn, posting_date, customer name and payer name from database for "
                         f"current merchant:{auth_code}, {rrn}, {posting_date}, {customer_name}, {payer_name}")
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {"pmt_mode": "UPI", "pmt_status": "AUTHORIZED","txn_amt": str(amount)+".00",
                                       "settle_status": "SETTLED","txn_id": txn_id, "rrn": str(rrn),
                                       "customer_name": customer_name,"payer_name": payer_name,
                                       "order_id": order_id,"pmt_msg": "PAYMENT SUCCESSFUL",
                                       "auth_code": auth_code, "date": date_and_time}
                logger.debug(f"expectedAppValues: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.wait_for_navigation_to_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()

                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_order_id(order_id)
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
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_message_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"pmt_mode": payment_mode, "pmt_status": payment_status.split(':')[1],
                                     "txn_amt": app_amount.split(' ')[1], "txn_id": app_txn_id, "rrn": str(app_rrn),
                                     "customer_name": app_customer_name,"settle_status": app_settlement_status,
                                     "payer_name": app_payer_name,"order_id": app_order_id,"auth_code": app_auth_code,
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
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {"pmt_status": "AUTHORIZED","txn_amt": float(amount),"pmt_mode": "UPI",
                                       "pmt_state": "SETTLED", "rrn": str(rrn),"settle_status": "SETTLED",
                                       "acquirer_code": "YES", "issuer_code": "YES","txn_type": "CHARGE",
                                       "mid": mid, "tid": tid, "org_code": org_code, "auth_code": auth_code,
                                       "date": date,
                                       "refund_msg" : "Partial Refund is not supported for YES transactions." }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                    request_body={"username": app_username, "password": app_password})
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
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                auth_code_api = response["authCode"]
                date_api = response["postingDate"]

                actual_api_values = {"pmt_status": status_api, "txn_amt": amount_api,"pmt_mode": payment_mode_api,
                                     "pmt_state": state_api, "rrn": str(rrn_api),"settle_status": settlement_status_api,
                                     "acquirer_code": acquirer_code_api,"issuer_code": issuer_code_api,"mid": mid_api,
                                     "txn_type": txn_type_api, "tid": tid_api, "org_code": orgCode_api,
                                     "auth_code": auth_code_api,
                                     "date": date_time_converter.from_api_to_datetime_format(date_api),
                                     "refund_msg" : partial_refund_message
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
                expected_db_values = {"txn_amt": float(amount),"pmt_mode": "UPI","pmt_status": "AUTHORIZED",
                                      "pmt_state": "SETTLED","acquirer_code" : "YES", "bank_name" : "Yes Bank",
                                      "payer_name": payer_name, "mid" :mid, "tid" : tid, "pmt_gateway": "ATOS",
                                      "rrn" : str(rrn), "settle_status": "SETTLED","upi_pmt_status": "AUTHORIZED",
                                      "upi_txn_type": "PAY_BQR", "upi_mc_id": upi_mc_id, "upi_bank_code": "YES"}
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                amount_db = float(result["amount"].iloc[0])
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_status_db = result["status"].iloc[0]
                payment_state_db = result["state"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_name_db = result["bank_name"].iloc[0]
                payer_name_db = result["payer_name"].iloc[0]
                mid_db = result["mid"].iloc[0]
                tid_db = result["tid"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                rr_number_db = result["rr_number"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                actual_db_values = {"txn_amt": amount_db,"pmt_mode": payment_mode_db,
                                    "pmt_status": payment_status_db, "pmt_state": payment_state_db,
                                    "acquirer_code" : acquirer_code_db, "bank_name" : bank_name_db,
                                    "payer_name": payer_name_db, "mid" :mid_db, "tid" : tid_db,
                                    "pmt_gateway": payment_gateway_db, "rrn" : rr_number_db,
                                    "settle_status": settlement_status_db,"upi_pmt_status": upi_status_db,
                                    "upi_txn_type": upi_txn_type_db, "upi_mc_id": upi_mc_id_db, "upi_bank_code": upi_bank_code_db}
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
                expected_portal_values = {}
                #
                # Write the test case Portal validation code block here. Set this to pass if not required.
                #
                actual_portal_values = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00",  'date': txn_date,'time': txn_time,
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


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# @pytest.mark.chargeSlipVal
# def test_common_100_102_064():
#     """
#     :Description: Verification of a BQR Partial Refund transaction via YES_ATOS
#     :Sub Feature code: UI_Common_PM_BQR_Partial_Refund_API_YES_ATOS_038
#     :TC naming code description: 100->Payment Method
#                                 102->BQR
#                                 038-> TC38
#     """
#
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         print(
#             colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#         app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
#         logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
#         username = app_cred['Username']
#         password = app_cred['Password']
#         portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
#         logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
#         portal_username = portal_cred['Username']
#         portal_password = portal_cred['Password']
#         query = "select org_code from org_employee where username='" + str(username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         testsuite_teardown.revert_payment_settings_default(org_code, 'YES', portal_username, portal_password, 'BQRV4')
#
#         api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
#                                                                                "password": portal_password,
#                                                                                "settingForOrgCode": org_code})
#         api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
#         logger.debug(f"API details  : {api_details} ")
#         response = APIProcessor.send_request(api_details)
#         logger.debug(f"Response received for setting preconditions is : {response}")
#
#         GlobalVariables.setupCompletedSuccessfully = True
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#
#         # Set the below variables depending on the log capturing need of the test case.
#         Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
#         msg = ""
#         GlobalVariables.time_calc.setup.end()
#         print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             print(
#                 colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                         'cyan'))
#
#             amount = random.randint(301, 400)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#             logger.debug(f"Amount and order id for this txn is: {amount}, {order_id}")
#             logger.debug("Generating QR using BQR QR generate API")
#             api_details = DBProcessor.get_api_details('bqrGenerate',
#                                                       request_body={"username": username, "password": password,
#                                                                     "amount": str(amount),
#                                                                     "orderNumber": str(order_id)})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Resonse recived for QR genration api is : {response}")
#             query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
#             logger.debug(f"Query to fetch transaction id from database : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id = result["id"].iloc[0]
#             rrn = "RE" + txn_id.split('E')[1]
#             logger.debug(f"Fetching Transaction id from db query : {txn_id} ")
#             api_details = DBProcessor.get_api_details('stopPayment',
#                                                       request_body={"username": username, "password": password,
#                                                                     "orgCode":org_code ,"txnId": txn_id})
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Response received for stop payment api is : {response}")
#
#             logger.info("Opening Portal to perform refund of the transaction")
#             refund_amount = amount - 100
#             ui_driver = TestSuiteSetup.initialize_portal_driver()
#             loginPagePortal = PortalLoginPage(ui_driver)
#             logger.info(f"Logging in Portal using username : {portal_username}")
#             loginPagePortal.perform_login_to_portal(portal_username, portal_password)
#             homePagePortal = PortalHomePage(ui_driver)
#             homePagePortal.search_merchant_name(org_code)
#             logger.info(f"Switching to merchant : {org_code}")
#             homePagePortal.click_switch_button(org_code)
#             homePagePortal.click_transaction_search_menu()
#             logger.info("Clicking on transaction detail based on txn id to perform refund of the transaction")
#             homePagePortal.click_on_transaction_details_based_on_transaction_id(txn_id)
#             logger.debug("Clicking on refund button")
#             homePagePortal.click_on_refund_button()
#             partial_refund_message=homePagePortal.perform_refund_of_txn_and_fetch_alert_msg(refund_amount)
#             logger.debug(f"Message for performing partial refund of txn is : {partial_refund_message}")
#             query = "select id from txn where org_code='" + org_code + "' order by created_time desc limit 1"
#             logger.debug(f"Query to fetch transaction id of refunded txn from database : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             txn_id = result["id"].iloc[0]
#             logger.debug(f"Fetching Transaction id from db after performing partial refund : {txn_id} ")
#             #
#             # ------------------------------------------------------------------------------------------------
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             print(colored(
#                 "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
#                                                                                   "="), 'cyan'))
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
#                 GlobalVariables.time_calc.execution.pause()
#                 print(colored(
#                     "Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(
#                         shutil.get_terminal_size().columns, "="), 'cyan'))
#             GlobalVariables.time_calc.execution.resume()
#             print(colored("Execution Timer resumed in execpt block of testcase function".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             ReportProcessor.capture_ss_when_app_val_exe_failed()
#
#             GlobalVariables.EXCEL_TC_Execution = "Fail"
#             GlobalVariables.Incomplete_ExecutionCount += 1
#
#             GlobalVariables.time_calc.execution.pause()
#             print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
#                 shutil.get_terminal_size().columns, "="), 'cyan'))
#
#             logger.exception(f"Execution is completed for the test case : {testcase_id}")
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         # -----------------------------------------Start of App Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "app_validation")) == "True":
#             try:
#                 logger.info(f"Starting App Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedAppValues = {"Payment Status": "STATUS:AUTHORIZED", "Payment mode": "UPI",
#                                      "Payment Txn ID": txn_id, "Payment Amt": str(amount)}
#                 app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
#                 loginPage = LoginPage(app_driver)
#                 logger.info(f"Logging in the MPOSX application using username : {username}")
#                 loginPage.perform_login(username, password)
#                 homePage = HomePage(app_driver)
#                 homePage.check_home_page_logo()
#                 homePage.wait_for_home_page_load()
#                 logger.info(f"App homepage loaded successfully")
#                 homePage.click_on_history()
#                 transactionsHistoryPage = TransHistoryPage(app_driver)
#                 transactionsHistoryPage.click_on_transaction_by_txn_id(txn_id)
#                 app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
#                 logger.debug(
#                     f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
#                 app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
#                 logger.debug(
#                     f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
#                 app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
#                 logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
#                 app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
#                 logger.debug(
#                     f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
#
#                 actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
#                                    "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt)}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
#                 logger.info("App Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_app_val_exe_failed()
#                 print("App Validation failed due to exception - " + str(e))
#                 logger.exception(f"App Validation failed due to exception - {e}")
#                 msg = msg + "App Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_app_val_result = "Fail"
#             logger.info(f"Completed APP validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of App Validation---------------------------------------
#
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             try:
#                 logger.info(f"Starting API Validation for the test case :{testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#
#                 expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI","Acquirer Code":"YES"}
#                 api_details = DBProcessor.get_api_details('txnDetails',
#                                                           request_body={"username": username, "password": password,
#                                                                         "txnId": txn_id})
#                 print("API DETAILS:", api_details)
#                 response = APIProcessor.send_request(api_details)
#                 logger.debug(f"Response received for transaction details api is : {response}")
#                 print(response)
#                 status_api = response["status"]
#                 amount_api = response["amount"]
#                 payment_mode_api = response["paymentMode"]
#                 accuirer_code_api = response["acquirerCode"]
#                 logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
#                 logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
#                 logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
#                 #
#                 actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,"Acquirer Code":accuirer_code_api}
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
#                 logger.info("API Validation Completed successfully for test case")
#             except Exception as e:
#                 print("API Validation failed due to exception - " + str(e))
#                 logger.exception(f"API Validation failed due to exception : {e} ")
#                 msg = msg + "API Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_api_val_result = 'Fail'
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#         # -----------------------------------------End of API Validation---------------------------------------
#
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             try:
#                 logger.info(f"Starting DB Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment mode":"UPI" , "Payment amount":"{:.2f}".format(amount), "State":"SETTLED", "Acquirer Code":"YES","State Bharatqr": "SETTLED", "Amount Bharatqr": amount, "Status Bharatqr": "SUCCESS"}
#                 #
#                 query = "select status,amount,payment_mode,acquirer_code,state from txn where id='" + txn_id + "'"
#                 logger.debug(f"DB query to fetch status, amount,acquirer_code, payment mode and state from DB : {query}")
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from DB : {result} ")
#                 status_db = result["status"].iloc[0]
#                 payment_mode_db = result["payment_mode"].iloc[0]
#                 amount_db = "{:.2f}".format(result["amount"].iloc[0])
#                 state_db = result["state"].iloc[0]
#                 accuirer_code_db = result["acquirer_code"].iloc[0]
#                 logger.debug(f"Fetching Transaction status from DB : {status_db} ")
#                 logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db} ")
#                 logger.debug(f"Fetching Transaction amount from DB : {amount_db} ")
#                 logger.debug(f"Fetching Transaction state from DB : {state_db} ")
#
#                 query = "select state,txn_amount,status_code from bharatqr_txn where id='" + txn_id + "'"
#                 logger.debug(f"DB query to fetch state, txn amount and status_code from bahratqr_txn DB : {query}")
#                 result = DBProcessor.getValueFromDB(query)
#                 logger.debug(f"Fetching Query result from bharatqr txn table of DB : {result} ")
#                 state_bharatqr_db = result["state"].iloc[0]
#                 amount_bharatqr_db = result["txn_amount"].iloc[0]
#                 status_bharatqr_db = result["status_code"].iloc[0]
#                 logger.debug(f"Fetching Transaction state from bharatqr txn table of DB : {state_bharatqr_db} ")
#                 logger.debug(f"Fetching Transaction amount from bharatqr txn table of DB : {amount_bharatqr_db} ")
#                 logger.debug(f"Fetching Transaction status description from bharatqr txn table of DB : {status_bharatqr_db} ")
#                 #
#                 actualDBValues = {"Payment Status": status_db, "Payment mode":payment_mode_db , "Payment amount":amount_db, "State":state_db, "Acquirer Code":accuirer_code_db,"State Bharatqr": state_bharatqr_db, "Amount Bharatqr": amount_bharatqr_db, "Status Bharatqr": status_bharatqr_db}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
#                 logger.info("DB Validation Completed successfully for test case")
#             except Exception as e:
#                 print("DB Validation failed due to exception - " + str(e))
#                 logger.exception(f"DB Validation failed due to exception :  {e}")
#                 msg = msg + "DB Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_db_val_result = 'Fail'
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of DB Validation---------------------------------------
#
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             try:
#                 logger.info(f"Starting Portal Validation for the test case : {testcase_id}")
#                 # --------------------------------------------------------------------------------------------
#                 expectedPortalValues = {"Payment Status": "Settled", "Payment mode":"UPI" , "Payment amount":str(amount),"Partial Refund message": "ERROR: Partial refund is not supported."}
#                 #
#                 # portal_username = read_config("credentials", 'username_portal')
#                 # portal_password = read_config('credentials', 'password_portal')
#                 ui_driver.refresh()
#                 transactionsHistoryPagePortal = PortalTransHistoryPage(ui_driver)
#                 portalValuesDict = transactionsHistoryPagePortal.get_transaction_details_for_portal(txn_id)
#                 portal_status = portalValuesDict['Status']
#                 portal_txn_type = portalValuesDict['Type']
#                 portal_amt = portalValuesDict['Total Amount']
#                 logger.debug(f"Fetching Transaction status from portal : {portal_status} ")
#                 logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
#                 logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
#                 print("Status of txn:", portal_status)
#                 print("Portal txn type ", portal_txn_type)
#                 #
#                 actualPortalValues = {"Payment Status": portal_status, "Payment mode": portal_txn_type, "Payment amount":str(portal_amt.split('.')[1]), "Partial Refund message":partial_refund_message}
#
#                 # ---------------------------------------------------------------------------------------------
#                 Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
#                 logger.info("Portal Validation Completed successfully for test case")
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_portal_val_exe_failed()
#                 print("Portal Validation failed due to exception - " + str(e))
#                 logger.exception(f"Portal Validation failed due to exception : {e}")
#                 msg = msg + "Portal Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_portal_val_result = 'Fail'
#             logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of Portal Validation---------------------------------------
#         # -----------------------------------------Start of ChargeSlip Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
#             logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
#             try:
#                 expectedValues = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id),
#                                   'RRN': rrn,
#                                   'BASE AMOUNT:': 'Rs.' + str(amount) + '.00'}
#                 receipt_validator.perform_charge_slip_validations(txn_id,
#                                                                   {"username": username, "password": password},
#                                                                   expectedValues)
#
#             except Exception as e:
#                 ReportProcessor.capture_ss_when_chargeslip_val_exe_failed()
#                 print("Charge Slip Validation failed due to exception - " + str(e))
#                 msg = msg + "Charge Slip Validation did not complete due to exception.\n"
#                 GlobalVariables.bool_val_exe = False
#                 GlobalVariables.str_chargeslip_val_result = False
#             logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
#
#         # -----------------------------------------End of ChargeSlip Validation---------------------------------------
#         GlobalVariables.time_calc.validation.end()
#         print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
#                       'cyan'))
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#
#     # -------------------------------------------End of Validation---------------------------------------------
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)
