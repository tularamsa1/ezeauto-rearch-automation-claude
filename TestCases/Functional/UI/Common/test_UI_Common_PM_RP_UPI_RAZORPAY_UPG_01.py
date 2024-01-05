import random
import string
import sys
import pytest
from datetime import datetime
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_228():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_UPG_success_VIA_Razorpay_when_UPGRefund_&_UPGAutoRefund_Disabled
    Sub Feature Description: Performing a upg txn using success callback via Razorpay when upg refund and upg autor efund are enabled
    TC naming code description: 100: Payment Method, 103: RemotePay, 228: TC228
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "false"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        query = "select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                f"org_code = '{org_code}' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        upi_mc_id = result['id'].values[0]
        logger.debug(f"upi_mc_id from txn table are : {upi_mc_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            char = string.ascii_letters + string.digits
            txn_ref = "qr_" + ''.join(random.choice(char) for _ in range(14))
            txn_ref_3 = "order_" + ''.join(random.choice(char) for _ in range(14))
            logger.debug(f"generated random request_id is : {txn_ref_3} and id : {txn_ref}")
            amount = random.randint(2050, 2500)
            logger.debug(f"generated random amount is : {amount}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                                                                              "entity": "event",
                                                                              "account_id": pg_merchant_id,
                                                                              "event": "payment.captured",
                                                                              "contains": [
                                                                                "payment"
                                                                              ],
                                                                              "payload": {
                                                                                "payment": {
                                                                                  "entity": {
                                                                                    "id": txn_ref,
                                                                                    "entity": "payment",
                                                                                    "amount": amount * 100,
                                                                                    "currency": "INR",
                                                                                    "base_amount": amount * 100,
                                                                                    "status": "captured",
                                                                                    "order_id": txn_ref_3,
                                                                                    "invoice_id": None,
                                                                                    "international": None,
                                                                                    "method": "upi",
                                                                                    "amount_refunded": 0,
                                                                                    "amount_transferred": 0,
                                                                                    "refund_status": None,
                                                                                    "captured": True,
                                                                                    "description": None,
                                                                                    "card_id": None,
                                                                                    "bank": None,
                                                                                    "wallet": None,
                                                                                    "vpa": "gaurav.kumar@upi",
                                                                                    "email": "gaurav.kumar@example.com",
                                                                                    "contact": "+919876543210",
                                                                                    "notes": {
                                                                                        "receiver_type":"offline"
                                                                                    },
                                                                                    "fee": 2,
                                                                                    "tax": 0,
                                                                                    "error_code": None,
                                                                                    "error_description": None,
                                                                                    "error_source": None,
                                                                                    "error_step": None,
                                                                                    "error_reason": None,
                                                                                    "acquirer_data": {
                                                                                      "rrn": rrn
                                                                                    },
                                                                                    "created_at": 1567675356
                                                                                  }}},
                                                                              "created_at": 1567675356
                                                                            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where pg_txn_ref ='{txn_ref}';"
            logger.debug(f"Query to fetch data from invalid pg request table : {query}")
            q_result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = q_result['txn_id'].iloc[0]

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn table are : {result}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"External Ref from txn table are : {external_ref}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Org Code from txn table are : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from txn table are : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code from txn table are : {auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"posting_date from txn table are : {posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from txn table are : {created_time}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from txn table are : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from txn table are : {tid}")

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
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "rrn": str(rrn),
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
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
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type, "mid": mid, "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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
                date_api = response["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "payment_gateway": "RAZORPAY",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "RAZORPAY",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_auth_code = result["auth_code"].iloc[0]
                ipr_mid = result["mid"].iloc[0]
                ipr_tid = result["tid"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
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
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            date_and_time_portal = date_time_converter.to_portal_format(created_time)
            try:
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn)
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
                    "rrn": rr_number
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
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
def test_common_100_103_229():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_UPG_FAILED_VIA_Razorpay_when_UPGRefund_&_UPGAutoRefund_Disabled
    Sub Feature Description: Performing a upg txn using failed callback when upg refund and upg auto refund are disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    229: TC229
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "false"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND " \
                f"bank_code = 'RAZORPAY_PSP' and card_terminal_acquirer_code = 'NONE'"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"upi_mc_id from txn table are : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"fetching vpa from db: {vpa}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            char = string.ascii_letters + string.digits
            txn_ref = "qr_" + ''.join(random.choice(char) for _ in range(14))
            txn_ref_3 = "order_" + ''.join(random.choice(char) for _ in range(14))
            logger.debug(f"generated random request_id is : {txn_ref_3} and id : {txn_ref}")
            amount = random.randint(2050, 2500)
            logger.debug(f"generated random amount is : {amount}")
            rrn = random.randint(1111110, 9999999)
            logger.debug(f"generated random rrn number is : {rrn}")
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random ref_id number is : {ref_id}")

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                                                                              "entity": "event",
                                                                              "account_id": pg_merchant_id,
                                                                              "event": "payment.captured",
                                                                              "contains": [
                                                                                "payment"
                                                                              ],
                                                                              "payload": {
                                                                                "payment": {
                                                                                  "entity": {
                                                                                    "id": txn_ref,
                                                                                    "entity": "payment",
                                                                                    "amount": amount * 100,
                                                                                    "currency": "INR",
                                                                                    "base_amount": amount * 100,
                                                                                    "status": "failed",
                                                                                    "order_id": txn_ref_3,
                                                                                    "invoice_id": None,
                                                                                    "international": None,
                                                                                    "method": "upi",
                                                                                    "amount_refunded": 0,
                                                                                    "amount_transferred": 0,
                                                                                    "refund_status": None,
                                                                                    "captured": True,
                                                                                    "description": None,
                                                                                    "card_id": None,
                                                                                    "bank": None,
                                                                                    "wallet": None,
                                                                                    "vpa": "gaurav.kumar@upi",
                                                                                    "email": "gaurav.kumar@example.com",
                                                                                    "contact": "+919876543210",
                                                                                    "notes": {
                                                                                        "receiver_type":"offline"
                                                                                    },
                                                                                    "fee": 2,
                                                                                    "tax": 0,
                                                                                    "error_code": None,
                                                                                    "error_description": None,
                                                                                    "error_source": None,
                                                                                    "error_step": None,
                                                                                    "error_reason": None,
                                                                                    "acquirer_data": {
                                                                                      "rrn": rrn
                                                                                    },
                                                                                    "created_at": 1567675356
                                                                                  }}},
                                                                              "created_at": 1567675356
                                                                            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            # calling confirm razorpay callback
            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where pg_txn_ref ='{txn_ref}';"
            logger.debug(f"Query to fetch data from invalid pg request table : {query}")
            q_result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_id = q_result['txn_id'].iloc[0]

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Results from txn table are : {result}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"External Ref from txn table are : {external_ref}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Org Code from txn table are : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"txn_type from txn table are : {txn_type}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"auth_code from txn table are : {auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"posting_date from txn table are : {posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"created time from txn table are : {created_time}")
            mid = result['mid'].values[0]
            logger.debug(f"mid from txn table are : {mid}")
            tid = result['tid'].values[0]
            logger.debug(f"tid from txn table are : {tid}")

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
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "rrn": str(rrn),
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }

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
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {app_payment_status}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {app_date_and_time}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actualAppValues: {actual_app_values}")
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
                expected_api_values = {
                    "pmt_status": "UPG_FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_FAILED",
                    "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
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
                date_api = response["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": org_code_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
                }
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "UPG_FAILED",
                    "pmt_state": "UPG_FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "payment_gateway": "RAZORPAY",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "RAZORPAY",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_auth_code = result["auth_code"].iloc[0]
                ipr_mid = result["mid"].iloc[0]
                ipr_tid = result["tid"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "payment_gateway": payment_gateway_db,
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
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                }
                logger.debug(f"actualDBValues : {actual_db_values}")
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            date_and_time_portal = date_time_converter.to_portal_format(created_time)
            try:
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn)
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
                    "rrn": rr_number
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
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
def test_common_100_103_230():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_UPG_REFUNDED_VIA_Razorpay_when_UPGRefund_Enabled_&_UPGAutoRefund_Enabled_REFUND_via_API
    Sub Feature Description:Performing a upg txn using success callback when upg refund and upg autorefund is enabled and refund the same txn using api
    and refund the same txn using api
    TC naming code description: 100: Payment Method, 103: Remote Pay, 230: TC230
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                f"org_code= '{org_code}' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            txn_ref = "pay_BgIMt2Gz" + str(random.randint(111111, 999999))
            logger.debug(f"txn_ref id : {txn_ref}")
            txn_ref_3 = "order_sPb7lAZz23459190" + str(random.randint(111111, 999999))
            logger.debug(f"txn_ref_3 account id : {txn_ref_3}")
            amount = random.randint(2050, 2500)
            logger.debug(f"amount {amount}")
            rrn = str(random.randint(1111110, 9999999))
            logger.debug(f"generated random rrn number is : {rrn}")

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount * 100,
                            "currency": "INR",
                            "base_amount": amount * 100,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
            logger.debug(f"Query to fetch details from the invalid_pg_request is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result['txn_id'].iloc[0]
            logger.debug(f"query result, txn_id_original is : {txn_id_original} ")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={"username": "5445377999",
                                                                                     "password": portal_password,
                                                                                     "amount": amount,
                                                                                     "originalTransactionId": str(
                                                                                         txn_id_original)})

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_refunded = response['txnId']
            logger.debug(f"refund txn id :{txn_id_refunded}")

            query = f"select * from txn where id='{txn_id_original}';"
            logger.debug(f"Query to fetch rr_number of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            rr_number_original = result['rr_number'].iloc[0]
            created_time_original = result['created_time'].values[0]
            txn_type_original = result['txn_type'].values[0]
            logger.debug(f"query result, rr_number : {rr_number_original} ")
            auth_code_original = result['auth_code'].values[0]

            query = f"select * from txn where id='{txn_id_refunded}';"
            logger.debug(f"Query to fetch rr_number of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            rr_number_refunded = result['rr_number'].iloc[0]
            created_time_refunded = result['created_time'].values[0]
            txn_type_refunded = result['txn_type'].values[0]
            logger.debug(f"query result, rr_number : {rr_number_refunded} ")
            auth_code_refunded = result['auth_code'].values[0]
            external_ref = result['external_ref'].values[0]

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
                date_and_time_original = date_time_converter.to_app_format(created_time_original)
                date_and_time_refunded = date_time_converter.to_app_format(created_time_refunded)
                expected_app_values = {
                                       "pmt_status": "UPG_AUTH_REFUNDED",
                                       "pmt_mode": "UPI",
                                       "txn_id": txn_id_original,
                                       "txn_amt": "{:,.2f}".format(amount) ,
                                       "settle_status": "SETTLED",
                                       "payment_msg": "PAYMENT VOIDED/REFUNDED",
                                       "date": date_and_time_original,
                                       "rrn": str(rr_number_original),
                                       "pmt_status_2": "UPG_REFUNDED",
                                       "pmt_mode_2": "UPI",
                                       "txn_id_2": txn_id_refunded,
                                       "txn_amt_2": "{:,.2f}".format(amount) ,
                                       "rrn_2": str(rr_number_refunded),
                                       "settle_status_2": "SETTLED",
                                       "payment_msg_2": "PAYMENT VOIDED/REFUNDED",
                                       "date_2": date_and_time_refunded
                                       }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_refunded)
                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching refunded rrn from txn history for the txn : {app_rrn_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching app refunded status from MPOS txn details : {app_payment_status_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching app refunded payment mode from MPOS txn details : {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching app refunded txn_id is from MPOS txn details : {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching app refunded amount from MPOS txn details : {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"App refunded settle status from MPOS txn details:{app_settlement_status_refunded}")
                app_payment_msg_refunded = transactions_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching app refunded payment msg from MPOS txn details : {app_payment_msg_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.debug(f"Fetching app refunded date and time from MPOS txn details :{app_date_and_time_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching app rrn from MPOS txn details : {app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching app payment status from MPOS txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching app payment mode from MPOS txn details : {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching app txn id from MPOS txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching app amount from MPOS txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching app settle status from MPOS txn details :{app_settlement_status_original}")
                app_payment_msg_original = transactions_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching app payment msg from MPOS txn details : {app_payment_msg_original}")
                app_date_and_time_original = transactions_history_page.fetch_date_time_text()
                logger.debug(f"Fetching app date and time from MPOS txn details : {app_date_and_time_original}")

                actual_app_values = {
                                     "pmt_status": app_payment_status_original.split(':')[1],
                                     "pmt_mode": app_payment_mode_original,
                                     "txn_id": txn_id_original,
                                     "txn_amt": str(app_payment_amt_original),
                                     "settle_status": app_settlement_status_original,
                                     "payment_msg": app_payment_msg_original,
                                     "date": app_date_and_time_original,
                                     "rrn": str(app_rrn_original),
                                     "pmt_status_2": app_payment_status_refunded.split(':')[1],
                                     "pmt_mode_2": app_payment_mode_refunded,
                                     "txn_id_2": app_txn_id_refunded,
                                     "txn_amt_2": str(app_payment_amt_refunded),
                                     "rrn_2": str(app_rrn_refunded),
                                     "settle_status_2": app_settlement_status_refunded,
                                     "payment_msg_2": app_payment_msg_refunded,
                                     "date_2": date_and_time_refunded
                                     }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                                       "pmt_status": "UPG_AUTH_REFUNDED",
                                       "pmt_mode": "UPI",
                                       "pmt_amt": str(amount),
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "RAZORPAY",
                                       "txn_type": txn_type_original,
                                       "pmt_status_2": "UPG_REFUNDED",
                                       "pmt_mode_2": "UPI",
                                       "pmt_amt_2": str(amount),
                                       "settle_status_2": "SETTLED",
                                       "acquirer_code_2": "RAZORPAY",
                                       "txn_type_2": txn_type_refunded,
                                       "rrn_2": str(rr_number_refunded)
                }

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_original][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settle_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settle_status_api_original}")
                acq_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acq_code_api_original}")
                txn_type_code_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_code_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_refunded][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                logger.debug(f"Status received for transaction details api is : {status_api_refunded}")
                amount_api_refunded = int(response["amount"])
                logger.debug(f"Refunded Amount received for transaction details api is : {amount_api_refunded}")
                payment_mode_api_refunded = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {amount_api_refunded}")
                rrn_api_refunded = response["rrNumber"]
                logger.debug(f"Fetching Transaction rrn of original txn mode from transaction api : {rrn_api_refunded}")
                settle_status_api_refunded = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settle_status_api_refunded}")
                acq_code_api_refunded = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acq_code_api_refunded}")
                txn_type_code_api_refunded = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_code_api_refunded}")
                date_api_refunded = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_refunded}")

                actual_api_values = {
                                     "pmt_status": status_api_original,
                                     "pmt_mode": payment_mode_api_original,
                                     "pmt_amt": str(amount_api_original),
                                     "settle_status": settle_status_api_original,
                                     "acquirer_code": acq_code_api_original,
                                     "txn_type": txn_type_code_api_original,
                                     "pmt_status_2": status_api_refunded,
                                     "pmt_mode_2": payment_mode_api_refunded,
                                     "pmt_amt_2": str(amount_api_refunded),
                                     "settle_status_2": settle_status_api_refunded,
                                     "acquirer_code_2": acq_code_api_refunded,
                                     "txn_type_2": txn_type_code_api_refunded,
                                     "rrn_2": str(rrn_api_refunded)
                }
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                                      "pmt_status": "UPG_AUTH_REFUNDED",
                                      "txn_amt": amount,
                                      "pmt_mode": "UPI",
                                      "pmt_state": "UPG_REFUNDED",
                                      "pmt_status_2": "UPG_REFUNDED",
                                      "pmt_mode_2": "UPI",
                                      "pmt_amt_2": amount,
                                      "pmt_state_2": "UPG_REFUNDED",
                                      }

                query = f"select * from txn where id='{txn_id_refunded}';"
                logger.debug(f"DB query to fetch state, status, amount, payment mode and external reference of "
                             f"refunded txn from DB : {query}")
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB : {result} ")
                status_db_refunded = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_refunded} ")
                payment_mode_db_refunded = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_refunded} ")
                amount_db_refunded = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_refunded} ")
                state_db_refunded = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_refunded} ")

                query = f"select * from txn where id='{txn_id_original}'"
                logger.debug(f"DB query to fetch state, status, amount, payment mode and external reference of "
                             f"orginal txn from DB : {query}")
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching Query result from DB of original txn : {result} ")
                status_db_original = result["status"].iloc[0]
                logger.debug(f"Fetching Transaction status from DB : {status_db_original} ")
                payment_mode_db_original = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching Transaction payment mode from DB : {payment_mode_db_original} ")
                amount_db_original = int(result["amount"].iloc[0])
                logger.debug(f"Fetching Transaction amount from DB : {amount_db_original} ")
                state_db_original = result["state"].iloc[0]
                logger.debug(f"Fetching Transaction state from DB : {state_db_original} ")

                actual_db_values = {
                                    "pmt_status": status_db_original,
                                    "txn_amt": amount_db_original,
                                    "pmt_mode": payment_mode_db_original,
                                    "pmt_state": state_db_original,
                                    "pmt_status_2": status_db_refunded,
                                    "pmt_mode_2": payment_mode_db_refunded,
                                    "pmt_amt_2": amount_db_refunded,
                                    "pmt_state_2": state_db_refunded,
                                    }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_original = date_time_converter.to_portal_format(created_time_original)
                date_and_time_refunded = date_time_converter.to_portal_format(created_time_refunded)
                query = f"select * from txn where id='{txn_id_original}';"
                logger.debug(f" rr_number of original txn after sending refund api from database : {query}")
                result = DBProcessor.getValueFromDB(query)
                rr_number_original_2 = result['rr_number'].iloc[0]
                expected_portal_values = {
                    "date_time": date_and_time_original,
                    "pmt_state": "UPG_AUTH_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "txn_id": txn_id_original,
                    "rrn": str(rr_number_original_2),
                    "auth_code": "-" if auth_code_original is None else auth_code_original,
                    "date_time_2": date_and_time_refunded,
                    "pmt_state_2": "UPG_REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": "EZETAP",
                    "txn_id_2": txn_id_refunded,
                    "rrn_2": str(rr_number_refunded),
                    "auth_code_2": "-" if auth_code_refunded is None else auth_code_refunded
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                auth_code = transaction_details[0]['Auth Code']
                original_date_time = transaction_details[1]['Date & Time']
                original_transaction_id = transaction_details[1]['Transaction ID']
                original_total_amount = transaction_details[1]['Total Amount'].split()
                original_rr_number = transaction_details[1]['RR Number']
                original_transaction_type = transaction_details[1]['Type']
                original_status = transaction_details[1]['Status']
                original_auth_code = transaction_details[1]['Auth Code']
                original_username = transaction_details[1]['Username']
                actual_portal_values = {
                    "date_time": original_date_time,
                    "pmt_state": str(original_status),
                    "pmt_type": original_transaction_type,
                    "txn_amt": original_total_amount[1],
                    "txn_id": original_transaction_id,
                    "rrn": original_rr_number,
                    "auth_code": original_auth_code,
                    "date_time_2": date_time,
                    "pmt_state_2": str(status),
                    "pmt_type_2": transaction_type,
                    "txn_amt_2": total_amount[1],
                    "username_2": original_username,
                    "txn_id_2": transaction_id,
                    "rrn_2": rr_number,
                    "auth_code_2": auth_code
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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_231():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_UPI_UPG_REFUND_PENDING_VIA_Razorpay_when_UPGRefund_Enabled_&_UPGAutoRefund_Enabled
    Sub Feature Description: Performing a upg refund pending via Razorpay when upg refund and upg autorefund are enabled
    and refund the same txn using api
    TC naming code description:100: Payment Method, 103: Remote Pay, 231: TC231
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

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = f"select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                f"org_code='{org_code}' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pg_merchant_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            txn_ref = "pay_BgIMt2Gz" + str(random.randint(111111, 999999))
            logger.debug(f"txn_ref id : {txn_ref}")
            txn_ref_3 = "order_sPb7lAZz23459190" + str(random.randint(111111, 999999))
            logger.debug(f"txn_ref_3 account id : {txn_ref_3}")
            amount = random.randint(1310, 1390)
            logger.debug(f"amount {amount}")
            rrn = str(random.randint(1111110, 9999999))
            logger.debug(f"generated random rrn number is : {rrn}")

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "payment.captured",
                "contains": [
                    "payment"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "payment",
                            "amount": amount * 100,
                            "currency": "INR",
                            "base_amount": amount * 100,
                            "status": "captured",
                            "order_id": txn_ref_3,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "amount_transferred": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": None,
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "gaurav.kumar@upi",
                            "email": "gaurav.kumar@example.com",
                            "contact": "+919876543210",
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 2,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1567675356
                        }}},
                "created_at": 1567675356
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
            logger.debug(f"Query to fetch details from the invalid_pg_request is: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_original = result['txn_id'].iloc[0]
            logger.debug(f"query result, txn_id_original is : {txn_id_original} ")

            query = f"select * from txn where id='{txn_id_original}';"
            logger.debug(f"Query to fetch rr_number of refunded txn from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            rr_number_original = result['rr_number'].iloc[0]
            created_time_original = result['created_time'].values[0]
            logger.debug(f"query result, rr_number : {rr_number_original} ")
            auth_code_original = result['auth_code'].values[0]
            external_ref = result['external_ref'].values[0]
            mid = result['mid'].values[0]
            tid = result['tid'].values[0]

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
                date_and_time_original = date_time_converter.to_app_format(created_time_original)
                expected_app_values = {
                                       "pmt_status": "UPG_REFUND_PENDING",
                                       "pmt_mode": "UPI",
                                       "txn_id": txn_id_original,
                                       "txn_amt": "{:,.2f}".format(amount) ,
                                       "settle_status": "SETTLED",
                                       "payment_msg": "REFUND PENDING",
                                       "date": date_and_time_original,
                                       "rrn": str(rr_number_original)
                                       }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_original)
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching app rrn from MPOS txn details : {app_rrn_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(f"Fetching app payment status from MPOS txn details : {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(f"Fetching app payment mode from MPOS txn details : {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(f"Fetching app txn id from MPOS txn details : {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(f"Fetching app amount from MPOS txn details : {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(f"Fetching app settle status from MPOS txn details :{app_settlement_status_original}")
                app_payment_msg_original = transactions_history_page.fetch_txn_payment_message_text()
                logger.debug(f"Fetching app payment msg from MPOS txn details : {app_payment_msg_original}")
                app_date_and_time_original = transactions_history_page.fetch_date_time_text()
                logger.debug(f"Fetching app date and time from MPOS txn details : {app_date_and_time_original}")

                actual_app_values = {
                                     "pmt_status": app_payment_status_original.split(':')[1],
                                     "pmt_mode": app_payment_mode_original,
                                     "txn_id": txn_id_original,
                                     "txn_amt": str(app_payment_amt_original),
                                     "settle_status": app_settlement_status_original,
                                     "payment_msg": app_payment_msg_original,
                                     "date": app_date_and_time_original,
                                     "rrn": str(app_rrn_original)
                                     }
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                                       "pmt_status": "UPG_REFUND_PENDING",
                                       "txn_amt": amount,
                                       "pmt_state": "UPG_REFUND_PENDING",
                                       "pmt_mode": "UPI",
                                       "settle_status": "SETTLED",
                                       "acquirer_code": "RAZORPAY",
                                       "txn_type": "CHARGE",
                                       "mid": mid,
                                       "tid": tid
                                       }
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_original][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                logger.debug(f"status received for transaction details api is : {status_api_original}")
                amount_api_original = int(response["amount"])
                logger.debug(f"Amount received for transaction details api is : {amount_api_original}")
                payment_mode_api_original = response["paymentMode"]
                logger.debug(f"Payment mode received for transaction details api is : {payment_mode_api_original}")
                settle_status_api_original = response["settlementStatus"]
                logger.debug(f"Settlement status received for transaction details api is :{settle_status_api_original}")
                payment_state = response['states']
                logger.debug(f"payment state from api : {payment_state}")
                acq_code_api_original = response["acquirerCode"]
                logger.debug(f"Acquirer code received for transaction details api is : {acq_code_api_original}")
                txn_type_code_api_original = response["txnType"]
                logger.debug(f"Txn Type received for transaction details api is : {txn_type_code_api_original}")
                date_api_original = response["postingDate"]
                logger.debug(f"Date received for transaction details api is : {date_api_original}")
                rrn_api_original = response['rrNumber']
                logger.debug(f"rrn api original : {rrn_api_original}")
                mid_api = response['mid']
                tid_api = response['tid']

                actual_api_values = {
                                     "pmt_status": status_api_original,
                                     "txn_amt": amount_api_original,
                                     "pmt_state": payment_state[0],
                                     "pmt_mode": payment_mode_api_original,
                                     "settle_status": settle_status_api_original,
                                     "acquirer_code": acq_code_api_original,
                                     "txn_type": txn_type_code_api_original,
                                     "mid": mid_api,
                                     "tid": tid_api
                                     }
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                                      "pmt_status": "UPG_REFUND_PENDING",
                                      "pmt_state": "UPG_REFUND_PENDING",
                                      "upi_txn_status": "UPG_REFUND_PENDING",
                                      "pmt_mode": "UPI",
                                      "txn_amt": amount,
                                      "settle_status": "SETTLED",
                                      "acquirer_code": "RAZORPAY",
                                      "bank_code": "RAZORPAY",
                                      "payment_gateway": "RAZORPAY",
                                      "upi_txn_type": "UNKNOWN",
                                      "upi_bank_code": "RAZORPAY_PSP",
                                      "upi_mc_id": upi_mc_id,
                                      "ipr_pmt_mode": "UPI",
                                      "ipr_bank_code": "RAZORPAY",
                                      "ipr_org_code": org_code,
                                      "ipr_rrn": str(rrn),
                                      "ipr_txn_amt": amount,
                                      "ipr_config_id": upi_mc_id,
                                      "ipr_pg_merchant_id": pg_merchant_id
                                      }

                query = f"select * from txn where id='{txn_id_original}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]
                acquirer_code_db = result["acquirer_code"].iloc[0]
                bank_code_db = result["bank_code"].iloc[0]
                settlement_status_db = result["settlement_status"].iloc[0]

                query = f"select * from upi_txn where txn_id='{txn_id_original}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                ipr_bank_code = result["bank_code"].iloc[0]
                ipr_org_code = result["org_code"].iloc[0]
                ipr_amount = result["amount"].iloc[0]
                ipr_rrn = result["rrn"].iloc[0]
                ipr_config_id = result["config_id"].iloc[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]

                actual_db_values = {
                                    "pmt_status": status_db,
                                    "pmt_state": state_db,
                                    "pmt_mode": payment_mode_db,
                                    "txn_amt": amount_db,
                                    "settle_status": settlement_status_db,
                                    "acquirer_code": acquirer_code_db,
                                    "bank_code": bank_code_db,
                                    "payment_gateway": payment_gateway_db,
                                    "upi_txn_status": upi_status_db,
                                    "upi_txn_type": upi_txn_type_db,
                                    "upi_bank_code": upi_bank_code_db,
                                    "upi_mc_id": upi_mc_id_db,
                                    "ipr_pmt_mode": ipr_payment_mode,
                                    "ipr_bank_code": ipr_bank_code,
                                    "ipr_org_code": ipr_org_code,
                                    "ipr_rrn": str(ipr_rrn),
                                    "ipr_txn_amt": ipr_amount,
                                    "ipr_config_id": ipr_config_id,
                                    "ipr_pg_merchant_id": ipr_pg_merchant_id
                                    }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                date_and_time_original = date_time_converter.to_portal_format(created_time_original)
                query = f"select * from txn where id='{txn_id_original}';"
                logger.debug(f" rr_number of original txn after sending refund api from database : {query}")
                result = DBProcessor.getValueFromDB(query)
                rr_number_original_2 = result['rr_number'].iloc[0]
                expected_portal_values = {
                    "date_time": date_and_time_original,
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount) ,
                    "username": "EZETAP",
                    "txn_id": txn_id_original,
                    "rrn": str(rr_number_original_2),
                    "auth_code": "-" if auth_code_original is None else auth_code_original
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                original_date_time = transaction_details[0]['Date & Time']
                original_transaction_id = transaction_details[0]['Transaction ID']
                original_total_amount = transaction_details[0]['Total Amount'].split()
                original_rr_number = transaction_details[0]['RR Number']
                original_transaction_type = transaction_details[0]['Type']
                original_status = transaction_details[0]['Status']
                original_username = transaction_details[0]['Username']
                original_auth_code = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": original_date_time,
                    "pmt_state": str(original_status),
                    "pmt_type": original_transaction_type,
                    "txn_amt": original_total_amount[1],
                    "username": original_username,
                    "txn_id": original_transaction_id,
                    "rrn": original_rr_number,
                    "auth_code": original_auth_code,
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
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_232():
    """
    Sub Feature Code: UI_Common_PM_RP_RP_upi_collect_Callback_Amount_Mismatch_Razorpay_UPGRefund_&_UPGAutoRefund_Disabled
    Sub Feature Description: Verification a Remote Pay upi collect callback for upg txn using amount mismatch UPGRefund_&_UPGAutoRefund_Disabled
    TC naming code description:
    100: Payment Method
    103: RemotePay
    220: TC232
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                               portal_un=portal_username, portal_pw=portal_password,
                                                               payment_gateway='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})

        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "false"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "false"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = "update remotepay_setting set setting_value= '2' where setting_name='cnpTxnTimeoutDuration' and " \
                "org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        query = f"select * from upi_merchant_config where bank_code = 'RAZORPAY_PSP' AND status = 'ACTIVE' AND " \
                f"org_code = '{org_code}' and card_terminal_acquirer_code = 'NONE' order by created_time desc limit 1"
        logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        pg_merchant_id = result['pgMerchantId'].values[0]
        vpa = result['vpa'].values[0]
        upi_mc_id = result['id'].values[0]
        upi_account_id = result['pgMerchantId'].values[0]
        logger.debug(f" upi account id from db : {upi_account_id}")
        logger.debug(f"Query result, vpa : {vpa}, pgMerchantId : {pg_merchant_id} and upi_mc_id: {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            amount = 650
            mismatch_amount = 651
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                payment_link_url = response['paymentLink']
                logger.info("Opening the link in the browser")
                ui_browser.goto(payment_link_url)
                remote_pay_upi_collect_txn = RemotePayTxnPage(ui_browser)
                remote_pay_upi_collect_txn.clickOnRemotePayUPI()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectAppSelection()
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectId("abc")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectDropDown("okicici")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remote_pay_upi_collect_txn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{order_id}' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"Query result, original_txn_id : {original_txn_id}")

            query = f"select * from upi_txn where txn_id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            txn_ref = result['txn_ref'].values[0]
            txn_ref_3 = result['txn_ref3'].values[0]

            api_details = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                                                                              "entity": "event",
                                                                              "account_id": upi_account_id,
                                                                              "event": "payment.captured",
                                                                              "contains": [
                                                                                "payment"
                                                                              ],
                                                                              "payload": {
                                                                                "payment": {
                                                                                  "entity": {
                                                                                    "id": txn_ref,
                                                                                    "entity": "payment",
                                                                                    "amount": mismatch_amount * 100,
                                                                                    "currency": "INR",
                                                                                    "base_amount": mismatch_amount * 100,
                                                                                    "status": "captured",
                                                                                    "order_id": txn_ref_3,
                                                                                    "invoice_id": None,
                                                                                    "international": None,
                                                                                    "method": "upi",
                                                                                    "amount_refunded": 0,
                                                                                    "amount_transferred": 0,
                                                                                    "refund_status": None,
                                                                                    "captured": True,
                                                                                    "description": None,
                                                                                    "card_id": None,
                                                                                    "bank": None,
                                                                                    "wallet": None,
                                                                                    "vpa": "gaurav.kumar@upi",
                                                                                    "email": "gaurav.kumar@example.com",
                                                                                    "contact": "+919876543210",
                                                                                    "notes": {
                                                                                        "receiver_type":"offline"
                                                                                    },
                                                                                    "fee": 2,
                                                                                    "tax": 0,
                                                                                    "error_code": None,
                                                                                    "error_description": None,
                                                                                    "error_source": None,
                                                                                    "error_step": None,
                                                                                    "error_reason": None,
                                                                                    "acquirer_data": {
                                                                                      "rrn": order_id
                                                                                    },
                                                                                    "created_at": 1567675356
                                                                                  }}},
                                                                              "created_at": 1567675356
                                                                            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                         f"{razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")

            api_details = DBProcessor.get_api_details('confirm_upi_callback_razorpay',
                                                      request_body=api_details['RequestBody'])

            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")
            error_message = response['message']
            logger.debug(f"amount miss match error message :{error_message}")

            query = f"select * from txn where id='{original_txn_id}'"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            new_txn_id = result['id'].values[0]
            logger.debug(f"Query result new_txn_id : {new_txn_id}")
            original_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_txn_id and original_rrn : {original_txn_id} and {original_rrn}")
            original_customer_name = result['customer_name'].values[0]
            logger.debug(f"generated random customer_name is : {original_customer_name}")
            original_payer_name = result['payer_name'].values[0]
            logger.debug(f"generated random payer_name is : {original_payer_name}")
            original_status = result['status'].values[0]
            logger.debug(f"generated random status is : {original_status}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"generated random original_posting_date is : {original_posting_date}")
            original_mid = result['mid'].values[0]
            logger.debug(f"MID is : {original_mid}")
            original_tid = result['tid'].values[0]
            logger.debug(f"TID is : {original_tid}")
            original_bank_code = result['bank_code'].values[0]
            logger.debug(f"bank code from txn is : {original_bank_code}")
            original_state = result['state'].values[0]
            logger.debug(f"State of txn is : {original_state}")
            original_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Payment mode from txn is : {original_payment_mode}")
            original_settlement_status = result['settlement_status'].values[0]
            logger.debug(f"Settlement status from txn is : {original_settlement_status}")
            original_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Settlement status from txn is : {original_acquirer_code}")
            original_posting_date = result['posting_date'].values[0]
            logger.debug(f"Posting date from txn is : {original_posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Posting created_time from txn is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Posting auth_code from txn is : {auth_code}")

            query = f"select * from payment_intent where org_code = '{org_code}' AND external_ref = '{order_id}' and payment_mode='UPI';"
            logger.debug(f"Query to fetch payment_intent_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            payment_intent_id = result['id'].values[0]
            logger.info(f"generated random rrn number is : {payment_intent_id}")
            intent_status = result['status'].values[0]
            logger.info(f"Payment intent status for UPI is: {intent_status}")

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
                date_and_time = date_time_converter.to_app_format(original_posting_date)
                expected_app_values = {
                                       "pmt_mode": "UPI",
                                       "pmt_status": "PENDING",
                                       "txn_amt": str(amount) + ".00",
                                       "settle_status": "PENDING",
                                       "txn_id": original_txn_id,
                                       "order_id": order_id,
                                       "pmt_msg": "PAYMENT PENDING",
                                       "date": date_and_time,
                                       }
                logger.debug(f"expected_app_values: {expected_app_values}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()

                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_payment_status = transactions_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {original_txn_id}, {app_payment_status}")
                app_payment_status = app_payment_status.split(':')[1]
                app_payment_mode = transactions_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {app_payment_mode}")
                app_txn_id = transactions_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn  {app_txn_id}")
                app_amount = transactions_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {app_amount}")
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_settlement_status = transactions_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn :  {app_settlement_status}")
                app_customer_name = transactions_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {app_customer_name}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {original_txn_id}, {app_order_id}")
                app_payment_msg = transactions_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {app_payment_msg}")

                actual_app_values = {
                                     "pmt_mode": app_payment_mode,
                                     "pmt_status": app_payment_status,
                                     "txn_amt": app_amount.split(' ')[1],
                                     "settle_status": app_settlement_status,
                                     "txn_id": app_txn_id,
                                     "order_id": app_order_id,
                                     "pmt_msg": app_payment_msg,
                                     "date": app_date_and_time,
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
                date = date_time_converter.db_datetime(original_posting_date)
                expected_api_values = {"pmt_status": "PENDING",
                                       "txn_amt": amount,
                                       "pmt_mode": "UPI",
                                       "pmt_state": "PENDING",
                                       "settle_status": "PENDING",
                                       "acquirer_code": "RAZORPAY",
                                       "issuer_code": "RAZORPAY",
                                       "txn_type": "REMOTE_PAY",
                                       "mid": original_mid,
                                       "tid": original_tid,
                                       "org_code": org_code,
                                       "date": date,
                                       "error_msg": f"AMOUNT MISMATCH. razorpay_payment_id = {str(txn_ref)}, txn "
                                                    f"Amount = {str(amount)}.00, callback amount = {str(mismatch_amount)}"
                                       }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                settlement_status_api = response["settlementStatus"]
                issuer_code_api = response["issuerCode"]
                acquirer_code_api = response["acquirerCode"]
                org_code_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

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
                                     "error_msg": error_message
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
                    "pmt_status": "PENDING",
                    "pmt_state": "PENDING",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "PENDING",
                    "settle_status": "PENDING",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "intent_status": "ACTIVE"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")
                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                upi_txn_type_db = result["txn_type"].iloc[0]
                upi_bank_code_db = result["bank_code"].iloc[0]
                upi_mc_id_db = result["upi_mc_id"].iloc[0]

                actual_db_values = {
                    "pmt_status": original_status,
                    "pmt_state": original_state,
                    "pmt_mode": original_payment_mode,
                    "txn_amt": amount,
                    "settle_status": original_settlement_status,
                    "acquirer_code": original_acquirer_code,
                    "bank_code": original_bank_code,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "intent_status": intent_status
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
                    "pmt_state": "PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    "txn_id": original_txn_id,
                    "auth_code": "-" if auth_code is None else auth_code
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                auth_code = transaction_details[0]['Auth Code']
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
                    "auth_code": auth_code
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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)