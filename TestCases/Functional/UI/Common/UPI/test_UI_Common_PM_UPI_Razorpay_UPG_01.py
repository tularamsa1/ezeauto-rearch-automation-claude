import random
import string
import sys
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_273():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_AUTHORIZED_VIA_Razorpay_when_UPGRefund_&_UPGAutoRefund_Disabled
    Sub Feature Description: Performing a upg txn using upi success callback when upg refund and upg autorefund disabled
    TC naming code description:
    100: Payment Method
    101: UPI
    273: TC273
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

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.debug(f"preparing data to perform the hash generation")
            characters = string.ascii_letters + string.digits
            txn_ref = 'qr_' + ''.join(random.choice(characters) for _ in range(14))
            logger.debug(f"randomly generated txn_ref is: {txn_ref}")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(300, 399)
            amount_api = amount * 100
            payment_id = txn_ref.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "qr_code.credited",
                "contains": [
                    "payment",
                    "qr_code"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": payment_id,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "status": "captured",
                            "order_id": None,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": "QRv2 Payment",
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "random@icici",
                            "email": None,
                            "contact": None,
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 1,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1689868958
                        }
                    },
                    "qr_code": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "qr_code",
                            "created_at": 1689168867,
                            "name": None,
                            "usage": "multiple_use",
                            "type": "upi_qr",
                            "image_url": "https:\/\/api-web.dev.razorpay.in\/v1\/t\/qrcode\/qr_MCuMM7hc1QCMxa",
                            "payment_amount": None,
                            "status": "active",
                            "description": None,
                            "fixed_amount": False,
                            "payments_amount_received": 200,
                            "payments_count_received": 1,
                            "notes": [],
                            "customer_id": None,
                            "close_by": None,
                            "closed_at": None,
                            "close_reason": None,
                            "image_content": "upi:\/\/pay?ver=01&mode=01&pa=random@razorpay&pn=PeoplinkServicesPrivateLimited&tr=RZPMCuMM7hc1QCMxaqrv2&cu=INR&mc=8062&qrMedium=04&tn=PaymenttoPeoplinkServicesPrivateLimited",
                            "tax_invoice": [],
                            "request_source": "ezetap"
                        }
                    }

                },
                "created_at": 1689168959
            })
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay', request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_ref}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")
            ipr_payment_mode = result["payment_mode"].values[0]
            ipr_bank_code = result["bank_code"].values[0]
            ipr_org_code = result["org_code"].values[0]
            ipr_amount = result["amount"].values[0]
            ipr_rrn = result["rrn"].values[0]
            ipr_auth_code = result["auth_code"].values[0]
            ipr_mid = result["mid"].values[0]
            ipr_tid = result["tid"].values[0]
            ipr_config_id = result["config_id"].values[0]
            ipr_vpa = result["vpa"].values[0]
            ipr_pg_merchant_id = result["pg_merchant_id"].values[0]

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].values[0]
            payment_mode_db = result["payment_mode"].values[0]
            amount_db = int(result["amount"].values[0])
            state_db = result["state"].values[0]
            payment_gateway_db = result["payment_gateway"].values[0]
            acquirer_code_db = result["acquirer_code"].values[0]
            bank_code_db = result["bank_code"].values[0]
            settlement_status_db = result["settlement_status"].values[0]
            tid_db = result['tid'].values[0]
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching status_db,payment_mode_db, amount_db, state_db, payment_gateway_db, acquirer_code_db, bank_code_db, settlement_status_db, mid_db, tid_db from database for "
                f"current merchant:{status_db},{payment_mode_db}, {amount_db}, {state_db}, {payment_gateway_db}, {acquirer_code_db}, {bank_code_db}, {settlement_status_db}, {mid_db}, {tid_db}")

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
                    "pmt_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)

                loginPage = LoginPage(app_driver)
                logger.info( f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "UPG_AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_AUTHORIZED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

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
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["postingDate"]

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
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
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
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

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
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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
                    "pmt_state": "UPG_AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code
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
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal
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
def test_common_100_101_274():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_FAILED_VIA_Razorpay_when_UPGRefund_UPGAutoRefund_Disabled
    Sub Feature Description: Performing a upg txn using upi failed callback when upg refund and upg autorefund are disabled
    TC naming code description:
    100: Payment Method
    101: UPI
    274: TC274
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

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.debug(f"preparing data to perform the hash generation")
            characters = string.ascii_letters + string.digits
            txn_ref = 'qr_' + ''.join(random.choice(characters) for _ in range(14))
            logger.debug(f"randomly generated txn_ref is: {txn_ref}")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(300, 399)
            amount_api = amount * 100
            payment_id = txn_ref.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "qr_code.credited",
                "contains": [
                    "payment",
                    "qr_code"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": payment_id,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "status": "failed",
                            "order_id": None,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": "QRv2 Payment",
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "random@icici",
                            "email": None,
                            "contact": None,
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 1,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1689868958
                        }
                    },
                    "qr_code": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "qr_code",
                            "created_at": 1689168867,
                            "name": None,
                            "usage": "multiple_use",
                            "type": "upi_qr",
                            "image_url": "https:\/\/api-web.dev.razorpay.in\/v1\/t\/qrcode\/qr_MCuMM7hc1QCMxa",
                            "payment_amount": None,
                            "status": "active",
                            "description": None,
                            "fixed_amount": False,
                            "payments_amount_received": 200,
                            "payments_count_received": 1,
                            "notes": [],
                            "customer_id": None,
                            "close_by": None,
                            "closed_at": None,
                            "close_reason": None,
                            "image_content": "upi:\/\/pay?ver=01&mode=01&pa=random@razorpay&pn=PeoplinkServicesPrivateLimited&tr=RZPMCuMM7hc1QCMxaqrv2&cu=INR&mc=8062&qrMedium=04&tn=PaymenttoPeoplinkServicesPrivateLimited",
                            "tax_invoice": [],
                            "request_source": "ezetap"
                        }
                    }

                },
                "created_at": 1689168959
            })
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay', request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_ref}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")
            ipr_payment_mode = result["payment_mode"].values[0]
            ipr_bank_code = result["bank_code"].values[0]
            ipr_org_code = result["org_code"].values[0]
            ipr_amount = result["amount"].values[0]
            ipr_rrn = result["rrn"].values[0]
            ipr_auth_code = result["auth_code"].values[0]
            ipr_mid = result["mid"].values[0]
            ipr_tid = result["tid"].values[0]
            ipr_config_id = result["config_id"].values[0]
            ipr_vpa = result["vpa"].values[0]
            ipr_pg_merchant_id = result["pg_merchant_id"].values[0]

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].values[0]
            logger.debug(f"fetched status_db from txn table is : {status_db}")
            payment_mode_db = result["payment_mode"].values[0]
            logger.debug(f"fetched payment_mode_db from txn table is : {payment_mode_db}")
            amount_db = int(result["amount"].values[0])
            logger.debug(f"fetched amount_db from txn table is : {amount_db}")
            state_db = result["state"].values[0]
            logger.debug(f"fetched state_db from txn table is : {state_db}")
            payment_gateway_db = result["payment_gateway"].values[0]
            logger.debug(f"fetched payment_gateway_db from txn table is : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].values[0]
            logger.debug(f"fetched acquirer_code_db from txn table is : {acquirer_code_db}")
            bank_code_db = result["bank_code"].values[0]
            logger.debug(f"fetched bank_code_db from txn table is : {bank_code_db}")
            settlement_status_db = result["settlement_status"].values[0]
            logger.debug(f"fetched settlement_status_db from txn table is : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"fetched tid_db from txn table is : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"fetched mid_db from txn table is : {mid_db}")

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
                    "pmt_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }

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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "UPG_FAILED",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

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
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "pmt_status": "UPG_FAILED",
                    "pmt_state": "UPG_FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
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
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

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
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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
                    "pmt_state": "UPG_FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code
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
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal
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
def test_common_100_101_275():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_REFUNDED_VIA_Razorpay_when_UPGRefund_Enabled_UPGAutoRefund_Enabled_REFUND_via_API
    Sub Feature Description: Performing a upg txn using upi success callback when upg refund and upg autorefund is enabled and refund the same txn using api
    TC naming code description:
    100: Payment Method
    101: UPI
    275: TC275
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

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
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

            logger.debug(f"preparing data to perform the hash generation")
            characters = string.ascii_letters + string.digits
            txn_ref = 'qr_' + ''.join(random.choice(characters) for _ in range(14))
            logger.debug(f"randomly generated txn_ref is: {txn_ref}")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(1600, 1700)
            amount_api = amount * 100
            payment_id = txn_ref.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "qr_code.credited",
                "contains": [
                    "payment",
                    "qr_code"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": payment_id,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "status": "captured",
                            "order_id": None,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": "QRv2 Payment",
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "random@icici",
                            "email": None,
                            "contact": None,
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 1,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1689868958
                        }
                    },
                    "qr_code": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "qr_code",
                            "created_at": 1689168867,
                            "name": None,
                            "usage": "multiple_use",
                            "type": "upi_qr",
                            "image_url": "https:\/\/api-web.dev.razorpay.in\/v1\/t\/qrcode\/qr_MCuMM7hc1QCMxa",
                            "payment_amount": None,
                            "status": "active",
                            "description": None,
                            "fixed_amount": False,
                            "payments_amount_received": 200,
                            "payments_count_received": 1,
                            "notes": [],
                            "customer_id": None,
                            "close_by": None,
                            "closed_at": None,
                            "close_reason": None,
                            "image_content": "upi:\/\/pay?ver=01&mode=01&pa=random@razorpay&pn=PeoplinkServicesPrivateLimited&tr=RZPMCuMM7hc1QCMxaqrv2&cu=INR&mc=8062&qrMedium=04&tn=PaymenttoPeoplinkServicesPrivateLimited",
                            "tax_invoice": [],
                            "request_source": "ezetap"
                        }
                    }

                },
                "created_at": 1689168959
            })
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay', request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = ("select * from invalid_pg_request where request_id ='" + txn_ref + "';")
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")

            query = "select * from txn where id = '" + str(txn_id) + "';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")

            api_details = DBProcessor.get_api_details('paymentRefund', request_body={
                "username": app_username, "password": app_password,
                "amount": amount, "originalTransactionId": str(txn_id)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for paymentRefund api is : {response}")
            txn_id_2 = response['txnId']
            logger.debug(f"fetching txn id from the response after triggering the refund api is : {txn_id_2}")

            query = "select * from txn where id = '" + str(txn_id_2) + "';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            external_ref_2 = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn_2}")
            txn_type_2 = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type_2}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {rrn_2}")

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
                    "pmt_mode": "UPI",
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "rrn": str(rrn),
                    "pmt_msg": "PAYMENT VOIDED/REFUNDED",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "UPG_REFUNDED",
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "rrn_2": str(rrn_2),
                    "pmt_msg_2": "PAYMENT VOIDED/REFUNDED",
                    "date_2": date_and_time_2
                }

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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                app_rrn_refunded = txn_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_rrn_refunded}")
                app_date_and_time_refunded = txn_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_refunded}")
                app_payment_status_refunded = txn_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                app_payment_mode_refunded = txn_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = txn_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = txn_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = txn_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = txn_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "date": app_date_and_time,
                    "pmt_status_2": app_payment_status_refunded.split(':')[1],
                    "pmt_mode_2": app_payment_mode_refunded,
                    "settle_status_2": app_settlement_status_refunded,
                    "txn_id_2": app_txn_id_refunded,
                    "txn_amt_2": str(app_payment_amt_refunded),
                    "pmt_msg_2": payment_msg_refunded,
                    "rrn_2": str(app_rrn_refunded),
                    "date_2": app_date_and_time_refunded
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
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(created_time_2)
                expected_api_values = {
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUNDED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "pmt_status_2": "UPG_REFUNDED",
                    "txn_amt_2": amount, "pmt_mode_2": "UPI",
                    "pmt_state_2": "UPG_REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    # "issuer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "date_2": refund_date
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
                        amount_api = int(elements["amount"])
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
                        date_api = elements["postingDate"]

                for elements in responseInList:
                    if elements["txnId"] == txn_id_2:
                        refund_status_api = elements["status"]
                        refund_amount_api = int(elements["amount"])
                        refund_payment_mode_api = elements["paymentMode"]
                        refund_state_api = elements["states"][0]
                        refund_settlement_status_api = elements["settlementStatus"]
                        # refund_issuer_code_api = response["issuerCode"]
                        refund_acquirer_code_api = elements["acquirerCode"]
                        refund_orgCode_api = elements["orgCode"]
                        refund_mid_api = elements["mid"]
                        refund_tid_api = elements["tid"]
                        refund_txn_type_api = elements["txnType"]
                        refund_date_api = elements["postingDate"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api, "mid": mid_api, "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": refund_status_api,
                    "txn_amt_2": refund_amount_api, "pmt_mode_2": refund_payment_mode_api,
                    "pmt_state_2": refund_state_api,
                    "settle_status_2": refund_settlement_status_api,
                    "acquirer_code_2": refund_acquirer_code_api,
                    # "issuer_code_2": refund_issuer_code_api,
                    "txn_type_2": refund_txn_type_api, "mid_2": refund_mid_api, "tid_2": refund_tid_api,
                    "org_code_2": refund_orgCode_api,
                    "date_2": date_time_converter.from_api_to_datetime_format(refund_date_api)
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
                    "pmt_status": "UPG_AUTH_REFUNDED",
                    "pmt_state": "UPG_REFUNDED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_AUTH_REFUNDED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
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
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "rrn": str(rrn),
                    "pmt_status_2": "UPG_REFUNDED",
                    "pmt_state_2": "UPG_REFUNDED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": amount,
                    "upi_txn_status_2": "UPG_REFUNDED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    # "bank_code_2": "RAZORPAY",
                    "payment_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "REFUND",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid,
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].values[0]
                payment_mode_db = result["payment_mode"].values[0]
                amount_db = int(result["amount"].values[0])
                state_db = result["state"].values[0]
                payment_gateway_db = result["payment_gateway"].values[0]
                acquirer_code_db = result["acquirer_code"].values[0]
                bank_code_db = result["bank_code"].values[0]
                settlement_status_db = result["settlement_status"].values[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                rrn_db = result['rr_number'].values[0]
                issuer_code = result['issuer_code'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from invalid_pg_request where request_id ='{txn_ref}';"
                logger.debug(f"query : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].values[0]
                ipr_bank_code = result["bank_code"].values[0]
                ipr_org_code = result["org_code"].values[0]
                ipr_amount = result["amount"].values[0]
                ipr_rrn = result["rrn"].values[0]
                ipr_mid = result["mid"].values[0]
                ipr_tid = result["tid"].values[0]
                ipr_config_id = result["config_id"].values[0]
                ipr_vpa = result["vpa"].values[0]
                ipr_pg_merchant_id = result["pg_merchant_id"].values[0]

                query = f"select * from txn where id='{txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                refund_status_db = result["status"].values[0]
                refund_payment_mode_db = result["payment_mode"].values[0]
                refund_amount_db = int(result["amount"].values[0])
                refund_state_db = result["state"].values[0]
                refund_payment_gateway_db = result["payment_gateway"].values[0]
                refund_acquirer_code_db = result["acquirer_code"].values[0]
                refund_bank_code_db = result["bank_code"].values[0]
                refund_settlement_status_db = result["settlement_status"].values[0]
                refund_tid_db = result['tid'].values[0]
                refund_mid_db = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                refund_upi_status_db = result["status"].values[0]
                refund_upi_txn_type_db = result["txn_type"].values[0]
                refund_upi_bank_code_db = result["bank_code"].values[0]
                refund_upi_mc_id_db = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "issuer_code": issuer_code,
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
                    "ipr_rrn": str(ipr_rrn),
                    "ipr_txn_amt": ipr_amount,
                    "ipr_mid": ipr_mid,
                    "ipr_tid": ipr_tid,
                    "ipr_vpa": ipr_vpa,
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "rrn": str(rrn_db),
                    "pmt_status_2": refund_status_db,
                    "pmt_state_2": refund_state_db,
                    "pmt_mode_2": refund_payment_mode_db,
                    "txn_amt_2": refund_amount_db,
                    "upi_txn_status_2": refund_upi_status_db,
                    "settle_status_2": refund_settlement_status_db,
                    "acquirer_code_2": refund_acquirer_code_db,
                    # "bank_code_2": refund_bank_code_db,
                    "payment_gateway_2": refund_payment_gateway_db,
                    "upi_txn_type_2": refund_upi_txn_type_db,
                    "upi_bank_code_2": refund_upi_bank_code_db,
                    "upi_mc_id_2": refund_upi_mc_id_db,
                    "mid_2": refund_mid_db,
                    "tid_2": refund_tid_db,
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
                refund_date_and_time_portal = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "UPG_AUTH_REFUNDED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": str(rrn),
                    "date_time_2": refund_date_and_time_portal,
                    "pmt_state_2": "UPG_REFUNDED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2" : "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": rrn_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
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
                    "pmt_state_2": status_2,
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": str(total_amount_2[1]),
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
def test_common_100_101_276():
    """
    Sub Feature Code: UI_Common_PM_UPI_UPG_REFUND_PENDING_VIA_Razorpay_when_UPGRefund_Enabled_UPGAutoRefund_Enabled
    Sub Feature Description: Performing a upg txn using upi success callback via Razorpay when upg refund and upg autorefund are enabled
    TC naming code description:
    100: Payment Method
    101: UPI
    276: TC276
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

        query = f"update upi_merchant_config set status = 'INACTIVE' where org_code='{org_code}';"
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating upi_merchant_config table inactive: {result}")

        query = f"update upi_merchant_config set status = 'ACTIVE' where org_code='{org_code}' and bank_code='RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"RESULT of updating DB setting active: {result}")

        refresh_db
        logger.info(f"DB refreshed ")

        query = f"select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
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

            logger.debug(f"preparing data to perform the hash generation")
            characters = string.ascii_letters + string.digits
            txn_ref = 'qr_' + ''.join(random.choice(characters) for _ in range(14))
            logger.debug(f"randomly generated txn_ref is: {txn_ref}")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = random.randint(300, 399)
            amount_api = amount * 100
            payment_id = txn_ref.replace("qr_", "pay_")

            api_details_hmac = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
                "entity": "event",
                "account_id": pg_merchant_id,
                "event": "qr_code.credited",
                "contains": [
                    "payment",
                    "qr_code"
                ],
                "payload": {
                    "payment": {
                        "entity": {
                            "id": payment_id,
                            "entity": "payment",
                            "amount": amount_api,
                            "currency": "INR",
                            "status": "captured",
                            "order_id": None,
                            "invoice_id": None,
                            "international": None,
                            "method": "upi",
                            "amount_refunded": 0,
                            "refund_status": None,
                            "captured": True,
                            "description": "QRv2 Payment",
                            "card_id": None,
                            "bank": None,
                            "wallet": None,
                            "vpa": "random@icici",
                            "email": None,
                            "contact": None,
                            "notes": {
                                "receiver_type": "offline"
                            },
                            "fee": 1,
                            "tax": 0,
                            "error_code": None,
                            "error_description": None,
                            "error_source": None,
                            "error_step": None,
                            "error_reason": None,
                            "acquirer_data": {
                                "rrn": rrn
                            },
                            "created_at": 1689868958
                        }
                    },
                    "qr_code": {
                        "entity": {
                            "id": txn_ref,
                            "entity": "qr_code",
                            "created_at": 1689168867,
                            "name": None,
                            "usage": "multiple_use",
                            "type": "upi_qr",
                            "image_url": "https:\/\/api-web.dev.razorpay.in\/v1\/t\/qrcode\/qr_MCuMM7hc1QCMxa",
                            "payment_amount": None,
                            "status": "active",
                            "description": None,
                            "fixed_amount": False,
                            "payments_amount_received": 200,
                            "payments_count_received": 1,
                            "notes": [],
                            "customer_id": None,
                            "close_by": None,
                            "closed_at": None,
                            "close_reason": None,
                            "image_content": "upi:\/\/pay?ver=01&mode=01&pa=random@razorpay&pn=PeoplinkServicesPrivateLimited&tr=RZPMCuMM7hc1QCMxaqrv2&cu=INR&mc=8062&qrMedium=04&tn=PaymenttoPeoplinkServicesPrivateLimited",
                            "tax_invoice": [],
                            "request_source": "ezetap"
                        }
                    }

                },
                "created_at": 1689168959
            })
            logger.debug(f"api_details for razorpay_callback_generator_HMAC is: {api_details_hmac}")

            response = APIProcessor.send_request(api_details_hmac)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api is : {razorpay_signature}")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from invalid_pg_request where request_id ='{txn_ref}';"
            logger.debug(f"query to fetch data from invalid_pg_request table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"query result : {result}")
            txn_id = result['txn_id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")
            ipr_payment_mode = result["payment_mode"].values[0]
            ipr_bank_code = result["bank_code"].values[0]
            ipr_org_code = result["org_code"].values[0]
            ipr_amount = result["amount"].values[0]
            ipr_rrn = result["rrn"].values[0]
            ipr_auth_code = result["auth_code"].values[0]
            ipr_mid = result["mid"].values[0]
            ipr_tid = result["tid"].values[0]
            ipr_config_id = result["config_id"].values[0]
            ipr_vpa = result["vpa"].values[0]
            ipr_pg_merchant_id = result["pg_merchant_id"].values[0]

            query = f"select * from txn where id = '{txn_id}';"
            logger.debug(f"Query to fetch txn data from the txn table is : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id is : {txn_id}")
            external_ref = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {external_ref}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            status_db = result["status"].values[0]
            payment_mode_db = result["payment_mode"].values[0]
            amount_db = int(result["amount"].values[0])
            state_db = result["state"].values[0]
            payment_gateway_db = result["payment_gateway"].values[0]
            acquirer_code_db = result["acquirer_code"].values[0]
            bank_code_db = result["bank_code"].values[0]
            settlement_status_db = result["settlement_status"].values[0]
            tid_db = result['tid'].values[0]
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching status_db,payment_mode_db, amount_db, state_db, payment_gateway_db, acquirer_code_db, bank_code_db, settlement_status_db, mid_db, tid_db from database for "
                f"current merchant: {status_db},{payment_mode_db}, {amount_db}, {state_db}, {payment_gateway_db}, {acquirer_code_db}, {bank_code_db}, {settlement_status_db}, {mid_db}, {tid_db}")

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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": "{:,.2f}".format(amount),
                    "rrn": str(rrn),
                    "pmt_msg": "REFUND PENDING",
                    "date": date_and_time
                }

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
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_status": app_payment_status.split(':')[1],
                    "pmt_mode": app_payment_mode,
                    "txn_id": app_txn_id,
                    "txn_amt": str(app_amount).split(' ')[1],
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "UPG_REFUND_PENDING",
                    "txn_amt": amount, "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUND_PENDING", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

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
                orgCode_api = response["orgCode"]
                mid_api = response["mid"]
                tid_api = response["tid"]
                txn_type_api = response["txnType"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": amount_api,
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api)
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
                    "txn_amt": amount,
                    "upi_txn_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
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
                    "ipr_vpa": vpa,
                    "ipr_config_id": upi_mc_id,
                    "ipr_pg_merchant_id": pg_merchant_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

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
                    "ipr_config_id": ipr_config_id,
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
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
                    "pmt_state": "UPG_REFUND_PENDING",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code
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
                auth_code_portal = transaction_details[0]['Auth Code']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code_portal
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
