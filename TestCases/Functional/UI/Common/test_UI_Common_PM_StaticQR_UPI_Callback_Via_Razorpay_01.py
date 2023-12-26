import random
import sys
import pytest
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal, \
    get_txn_details_for_diff_order_id
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, date_time_converter, \
    receipt_validator
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_042():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Success_Callback_Via_Razorpay_Auto_Refund_Disabled
    Sub Feature Description: Performing a upi success callback via Razorpay when autorefund is disabled
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 042: TC042
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
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

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = 618
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

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
                            "id": publish_id,
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
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
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
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
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
                order_id_api = response["externalRefNumber"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_state": "SETTLED",
                    "pmt_mode": "UPI",
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
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
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
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

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time)
                expected_values = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'date': txn_date,
                    'time': txn_time,
                    'AUTH CODE': "" if auth_code is None else auth_code
                }
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_043():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_2_UPI_Success_Callback_Via_Razorpay_Auto_Refund_Disabled
    Sub Feature Description: Performing two upi success callback via Razorpay when autorefund is disabled.
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 043: TC043
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
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

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_axisfc', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_axisfc api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = 618
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

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
                            "id": publish_id,
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
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            logger.debug(f"preparing data to perform the hash generation 2nd time")
            rrn_2 = str(random.randint(1000000000000, 9999999999999))
            amount_2 = amount + 1
            amount_api_2 = amount_2 * 100

            api_details_hmac_2 = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
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
                            "amount": amount_api_2,
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
                                "rrn": rrn_2
                            },
                            "created_at": 1689868958
                        }
                    },
                    "qr_code": {
                        "entity": {
                            "id": publish_id,
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
            logger.debug(f"api_details for razorpay_callback_generator_HMAC second time is: {api_details_hmac_2}")

            response = APIProcessor.send_request(api_details_hmac_2)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api second time is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api second time is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay second time")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac_2['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay second time: {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api second time is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn_2}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn_2}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name_2}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id_2}")
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
            order_id_2 = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref_2 from txn table is : {order_id_2}")

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
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "pmt_mode_2": "UPI",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(amount_2),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(rrn_2),
                    "customer_name_2": customer_name_2,
                    "payer_name_2": payer_name_2,
                    "pmt_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id_2)
                payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id_2}, {payment_status_2}")
                app_date_and_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id_2}, {app_date_and_time_2}")
                payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id_2}, {payment_mode_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id_2}, {app_txn_id_2}")
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id_2}, {app_amount_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id_2}, {app_customer_name_2}")
                app_settlement_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id_2}, {app_settlement_status_2}")
                app_payer_name_2 = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id_2}, {app_payer_name_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id_2}, {app_payment_msg_2}")
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
                    "payer_name": app_payer_name,
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
                    "pmt_msg_2": app_payment_msg_2,
                    "date_2": app_date_and_time_2
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
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "date": date,
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": str(amount_2), "pmt_mode_2": "UPI",
                    "pmt_state_2": "SETTLED", "rrn_2": str(rrn_2),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "issuer_code_2": "RAZORPAY",
                    "txn_type_2": txn_type_2,
                    "mid_2": mid,
                    "tid_2": tid,
                    "org_code_2": org_code_txn_2,
                    "order_id_2": order_id_2,
                    "date_2": date_2
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
                order_id_api = response["externalRefNumber"]
                date_api = response["createdTime"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_2 = response["status"]
                amount_api_2 = int(response["amount"])
                payment_mode_api_2 = response["paymentMode"]
                state_api_2 = response["states"][0]
                rrn_api_2 = response["rrNumber"]
                settlement_status_api_2 = response["settlementStatus"]
                issuer_code_api_2 = response["issuerCode"]
                acquirer_code_api_2 = response["acquirerCode"]
                orgCode_api_2 = response["orgCode"]
                mid_api_2 = response["mid"]
                tid_api_2 = response["tid"]
                txn_type_api_2 = response["txnType"]
                order_id_api_2 = response["externalRefNumber"]
                date_api_2 = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "pmt_status_2": status_api_2, "txn_amt_2": str(amount_api_2),
                    "pmt_mode_2": payment_mode_api_2,
                    "pmt_state_2": state_api_2, "rrn_2": str(rrn_api_2),
                    "settle_status_2": settlement_status_api_2,
                    "acquirer_code_2": acquirer_code_api_2,
                    "issuer_code_2": issuer_code_api_2,
                    "txn_type_2": txn_type_api_2,
                    "mid_2": mid_api_2,
                    "tid_2": tid_api_2,
                    "org_code_2": orgCode_api_2,
                    "order_id_2": order_id_api_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_2)
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "UPI",
                    "txn_amt_2": str(amount_2),
                    "upi_txn_status_2": "AUTHORIZED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "RAZORPAY",
                    "bank_code_2": "RAZORPAY",
                    "pmt_gateway_2": "RAZORPAY",
                    "upi_txn_type_2": "STATIC_QR",
                    "upi_bank_code_2": "RAZORPAY_PSP",
                    "upi_mc_id_2": upi_mc_id,
                    "mid_2": mid,
                    "tid_2": tid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
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

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].values[0]
                upi_txn_type_db = result["txn_type"].values[0]
                upi_bank_code_db = result["bank_code"].values[0]
                upi_mc_id_db = result["upi_mc_id"].values[0]

                query = f"select * from txn where id='{txn_id_2}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db_2 = result["status"].values[0]
                payment_mode_db_2 = result["payment_mode"].values[0]
                amount_db_2 = int(result["amount"].values[0])
                state_db_2 = result["state"].values[0]
                payment_gateway_db_2 = result["payment_gateway"].values[0]
                acquirer_code_db_2 = result["acquirer_code"].values[0]
                bank_code_db_2 = result["bank_code"].values[0]
                settlement_status_db_2 = result["settlement_status"].values[0]
                tid_db_2 = result['tid'].values[0]
                mid_db_2 = result['mid'].values[0]

                query = f"select * from upi_txn where txn_id='{txn_id_2}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db_2 = result["status"].values[0]
                upi_txn_type_db_2 = result["txn_type"].values[0]
                upi_bank_code_db_2 = result["bank_code"].values[0]
                upi_mc_id_db_2 = result["upi_mc_id"].values[0]

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": str(amount_db),
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
                    "pmt_status_2": status_db_2,
                    "pmt_state_2": state_db_2,
                    "pmt_mode_2": payment_mode_db_2,
                    "txn_amt_2": str(amount_db_2),
                    "upi_txn_status_2": upi_status_db_2,
                    "settle_status_2": settlement_status_db_2,
                    "acquirer_code_2": acquirer_code_db_2,
                    "bank_code_2": bank_code_db_2,
                    "pmt_gateway_2": payment_gateway_db_2,
                    "upi_txn_type_2": upi_txn_type_db_2,
                    "upi_bank_code_2": upi_bank_code_db_2,
                    "upi_mc_id_2": upi_mc_id_db_2,
                    "mid_2": mid_db_2,
                    "tid_2": tid_db_2
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                date_and_time_portal_new = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": "-" if rrn is None else rrn,
                    "date_time_2": date_and_time_portal_new,
                    "pmt_state_2": "AUTHORIZED",
                    "pmt_type_2": "UPI",
                    "txn_amt_2": "{:,.2f}".format(amount_2),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "auth_code_2": "-" if auth_code_2 is None else auth_code_2,
                    "rrn_2": "-" if rrn_2 is None else rrn_2,
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

                transaction_details = get_txn_details_for_diff_order_id(order_id=order_id_2)
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
                    "pmt_state_2": str(status_2),
                    "pmt_type_2": transaction_type_2,
                    "txn_amt_2": total_amount_2[1],
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
            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                new_txn_date_1, new_txn_time_1 = date_time_converter.to_chargeslip_format(created_time)
                new_txn_date_2, new_txn_time_2 = date_time_converter.to_chargeslip_format(created_time_2)

                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'date': new_txn_date_1, 'time': new_txn_time_1,
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'AUTH CODE': "" if auth_code is None else auth_code
                }

                expected_charge_slip_values_2 = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn_2), 'date': new_txn_date_2, 'time': new_txn_time_2,
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount_2),
                    'AUTH CODE': "" if auth_code_2 is None else auth_code_2
                }

                charge_slip_val_result_1 = receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)

                charge_slip_val_result_2 = receipt_validator.perform_charge_slip_validations(
                    txn_id_2, {"username": app_username, "password": app_password}, expected_charge_slip_values_2)

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
@pytest.mark.appVal
@pytest.mark.portalVal
def test_common_100_107_044():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_Failed_Callback_Via_Razorpay_Auto_Refund_Disabled
    Sub Feature Description: Performing a upi failed callback via Razorpay when autorefund is disabled
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 044: TC044
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_razorpay api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = 618
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

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
                            "id": publish_id,
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
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

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
                    "pmt_status": "FAILED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
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
                    "pmt_status": "FAILED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "FAILED", "rrn": str(rrn),
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
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
                order_id_api = response["externalRefNumber"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
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
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": str(amount),
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from txn where id='" + txn_id + "'"
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

                query = "select * from upi_txn where txn_id='" + txn_id + "'"
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
                    "txn_amt": str(amount_db),
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "pmt_gateway": payment_gateway_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "mid": mid_db,
                    "tid": tid_db
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn),

                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
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
                    "rrn": rr_number,

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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
@pytest.mark.portalVal
def test_common_100_107_047():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_2_UPI_Success_Callback_With_Same_RRN_Via_Razorpay_Auto_Refund_Disabled
    Sub Feature Description: Duplicate Callback case for Static QR - we should not create new txn when duplicate callback is received. Same rrn and same txn ref.
    TC naming code description: 100: Payment Method, 107: UPI STATIC QR, 047: TC047
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
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

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

            api_details = DBProcessor.get_api_details('static_qrcode_generate_razorpay', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")
            logger.debug(f"Response received for static_qrcode_generate_axisfc api is : {response}")

            query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='NONE';"
            logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            vpa_new = result['vpa'].values[0]
            logger.info(f"fetched vpa_new is : {vpa_new}")

            logger.debug(f"preparing data to perform the hash generation")
            rrn = str(random.randint(1000000000000, 9999999999999))
            amount = 618
            amount_api = amount * 100
            payment_id = publish_id.replace("qr_", "pay_")

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
                            "id": publish_id,
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
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

            query = f"select * from txn where org_code = '{org_code}' and rr_number = '{rrn}'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            txn_id = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id}")
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
            order_id = result['external_ref'].values[0]
            logger.debug(f"fetched external_ref from txn table is : {order_id}")

            logger.debug(f"preparing data to perform the hash generation 2nd time")

            api_details_hmac_2 = DBProcessor.get_api_details('razorpay_callback_generator_HMAC', request_body={
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
                            "id": publish_id,
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
            logger.debug(f"api_details for razorpay_callback_generator_HMAC second time is: {api_details_hmac_2}")

            response = APIProcessor.send_request(api_details_hmac_2)
            logger.debug(f"Response received for razorpay_callback_generator_HMAC api second time is : {response}")
            razorpay_signature = response['razorpay_signature']
            logger.debug(
                f"razorpay_signature received for razorpay_callback_generator_HMAC api second time is : {razorpay_signature}")
            logger.debug(f"performing upi callback for razorpay second time")
            api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                      request_body=api_details_hmac_2['RequestBody'])
            api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for upi_confirm_razorpay second time: {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi_confirm_razorpay api second time is : {response}")

            query = f"select * from txn where org_code = '{org_code}' order by created_time desc limit 1; "
            logger.debug(f"Query to fetch txn data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_2 = result['id'].values[0]
            logger.debug(f"fetched txn_id from txn table is : {txn_id_2}")

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
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                }

                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
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
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str(amount), "pmt_mode": "UPI",
                    "pmt_state": "SETTLED", "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "order_id": order_id,
                    "date": date,
                    "txn_id": str(txn_id)
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
                order_id_api = response["externalRefNumber"]
                date_api = response["createdTime"]

                actual_api_values = {
                    "pmt_status": status_api, "txn_amt": str(amount_api),
                    "pmt_mode": payment_mode_api,
                    "pmt_state": state_api, "rrn": str(rrn_api),
                    "settle_status": settlement_status_api,
                    "acquirer_code": acquirer_code_api,
                    "issuer_code": issuer_code_api,
                    "txn_type": txn_type_api,
                    "mid": mid_api,
                    "tid": tid_api,
                    "org_code": orgCode_api,
                    "order_id": order_id_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "txn_id": str(txn_id_2)
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
                    "txn_amt": str(amount),
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "pmt_gateway": "RAZORPAY",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "mid": mid,
                    "tid": tid,
                    "txn_id": str(txn_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
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
                    "txn_amt": str(amount_db),
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
                    "txn_id": str(txn_id_2)
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
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "auth_code": "-" if auth_code is None else auth_code,
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password,
                                                                         order_id)
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

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                new_txn_date_1, new_txn_time_1 = date_time_converter.to_chargeslip_format(created_time)
                expected_charge_slip_values_1 = {
                    'PAID BY:': 'UPI', 'RRN': str(rrn), 'date': new_txn_date_1, 'time': new_txn_time_1,
                    'BASE AMOUNT:': "Rs." + "{:,.2f}".format(amount),
                    'AUTH CODE': "" if auth_code is None else auth_code
                }
                receipt_validator.perform_charge_slip_validations(
                    txn_id, {"username": app_username, "password": app_password}, expected_charge_slip_values_1)

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
