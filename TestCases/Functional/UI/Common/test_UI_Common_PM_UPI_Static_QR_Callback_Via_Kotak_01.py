import random
import string
import sys
import pytest

from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from Utilities.execution_log_processor import EzeAutoLogger
from PageFactory.App_TransHistoryPage import TransHistoryPage
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from Utilities import DBProcessor, APIProcessor, Validator, ConfigReader, ResourceAssigner,receipt_validator, date_time_converter

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_107_033():
    """
    Sub Feature Code: UI_Common_PM_UPI_Static_QR_Callback_Success_AutoRefund_enabled_Via_KOTAK
    Sub Feature Description: Verifying a upi success callback via Kotak when autorefund is enabled
    TC naming code description: 100: Payment method, 107: UPI Static QR, 033: Testcase ID
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

        # Enable AutoRefund
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund enabled is : {response}")

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
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_audit_table_entry(portal_username, portal_password, org_code)

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

            # generating UPI STATIC QR
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation response : {generateqr_publish_id}")

            amount = random.randint(201, 400)
            logger.debug(f"amount is : {amount}")
            auth_code = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random auth_code is : {auth_code}")
            ref_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random ref_id is : {ref_id}")
            generate_random_secondary_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random secondary id is : {generate_random_secondary_id}")
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + "@upi"
            logger.debug(f" Value of customer vpa is : {customer_vpa}")

            # UPI Success Callback , transaction_type: 2 is for upi
            api_details = DBProcessor.get_api_details('callbackKotak', request_body={
                "mid": mid,
                "ref_no": ref_id,
                "txn_amount": "{:.2f}".format(amount),
                "tr_id": generateqr_publish_id,
                "transaction_type": "2",
                "tid": tid,
                "txn_currency": "356",
                "merchant_vpa": vpa,
                "settlement_amount": str(amount),
                "primary_id": generateqr_publish_id,
                "auth_code": auth_code,
                "customer_vpa": customer_vpa,
                "secondary_id": generate_random_secondary_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for static qr pure upi callback is : {response}")
            status = response['status']
            logger.debug(f"Value of status obtained from static qr pure upi callback is : {status}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(ref_id) + "'order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching id from txn table : {txn_id}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from txn table : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode from txn table : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from txn table : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway from txn table : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Fetching bank_code from txn table : {bank_code_db}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Fetching bank_name from txn table : {bank_name_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status from txn table : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn_db}")

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
            date_and_time = date_time_converter.to_app_format(created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(ref_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging into the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
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
            date = date_time_converter.db_datetime(created_time)
            try:
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
                    "status": "SUCCESS",
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                # hit txnlist api
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password,
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
                    "status": status,
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
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
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": config_id,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "status": "AUTHORIZED",
                    "additional_field1": generateqr_publish_id,
                    "additional_field3": generateqr_publish_id,
                    "resp_code": "SUCCESS",
                    "txn_type": "STATIC_QR",
                    "publish_id": generateqr_publish_id,
                    "vpa": vpa,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "bank_name": "Kotak Mahindra",
                    "rrn": str(ref_id),
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

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
                upi_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from upi_txn table : {upi_org_code_db}")
                upi_txn_additional_field1_db = result["additional_field1"].iloc[0]
                logger.debug(f"Fetching additional_field1 from upi_txn table : {upi_txn_additional_field1_db}")
                upi_txn_additional_field3_db = result["additional_field3"].iloc[0]
                logger.debug(f"Fetching additional_field3 from upi_txn table : {upi_txn_additional_field3_db}")
                upi_txn_resp_code_db = result["resp_code"].iloc[0]
                logger.debug(f"Fetching resp_code from upi_txn table : {upi_txn_resp_code_db}")
                upi_txn_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {upi_txn_txn_type_db}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

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
                    "org_code": upi_org_code_db,
                    "status": upi_status_db,
                    "additional_field1": upi_txn_additional_field1_db,
                    "additional_field3": upi_txn_additional_field3_db,
                    "resp_code": upi_txn_resp_code_db,
                    "txn_type": upi_txn_txn_type_db,
                    "publish_id": staticqr_intent_publish_id_db,
                    "vpa": staticqr_intent_vpa_db,
                    "qr_type": staticqr_intent_qrtype_db,
                    "intent_type": staticqr_intent_intent_type_db,
                    "user_mobile": staticqr_intent_user_mobile_db,
                    "user_name": staticqr_intent_user_name_db,
                    "bank_name": bank_name_db,
                    "rrn": rrn_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

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
                    'PAID BY:': 'UPI', 'RRN': str(ref_id),
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_107_034():
    """
    Sub Feature Code: UI_Common_PM_UPI_Static_QR_Callback_Success_AutoRefund_disabled_Via_KOTAK
    Sub Feature Description: Verifying a upi success callback via Kotak when autorefund is disabled
    TC naming code description: 100: Payment method, 107: UPI Static QR, 034: Testcase ID
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

        # Disable AutoRefund
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "settingForOrgCode": org_code
        })

        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "false"
        logger.debug(f"API details : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund enabled is : {response}")

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
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_audit_table_entry(portal_username, portal_password, org_code)

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

            # generating UPI STATIC QR
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation response : {generateqr_publish_id}")

            amount = random.randint(201, 400)
            logger.debug(f"amount is : {amount}")
            auth_code = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random auth_code is : {auth_code}")
            ref_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random ref_id is : {ref_id}")
            generate_random_secondary_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random secondary id is : {generate_random_secondary_id}")
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + "@upi"
            logger.debug(f" Value of customer vpa is : {customer_vpa}")

            # UPI Success Callback    #transaction_type: 2 is for upi
            api_details = DBProcessor.get_api_details('callbackKotak', request_body={
                "mid": mid,
                "ref_no": ref_id,
                "txn_amount": "{:.2f}".format(amount),
                "tr_id": generateqr_publish_id,
                "transaction_type": "2",
                "tid": tid,
                "txn_currency": "356",
                "merchant_vpa": vpa,
                "settlement_amount": str(amount),
                "primary_id": generateqr_publish_id,
                "auth_code": auth_code,
                "customer_vpa": customer_vpa,
                "secondary_id": generate_random_secondary_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for static qr pure upi callback is : {response}")
            status = response['status']
            logger.debug(f"Value of status obtained from static qr pure upi callback is : {status}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(ref_id) + "'order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching id from txn table : {txn_id}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from txn table : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode from txn table : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from txn table : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway from txn table : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Fetching bank_code from txn table : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status from txn table : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Fetching bank_name from the txn table : {bank_name_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn_db}")

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
            date_and_time = date_time_converter.to_app_format(created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(ref_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging into the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                }

                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            date = date_time_converter.db_datetime(created_time)
            try:
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
                    "status": "SUCCESS",
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                # hit txnlist api
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password,
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
                    "status": status,
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
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": config_id,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "status": "AUTHORIZED",
                    "additional_field1": generateqr_publish_id,
                    "additional_field3": generateqr_publish_id,
                    "resp_code": "SUCCESS",
                    "txn_type": "STATIC_QR",
                    "publish_id": generateqr_publish_id,
                    "vpa": vpa,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "bank_name": "Kotak Mahindra",
                    "rrn": str(ref_id),
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

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
                upi_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from upi_txn table : {upi_org_code_db}")
                upi_txn_additional_field1_db = result["additional_field1"].iloc[0]
                logger.debug(f"Fetching additional_field1 from upi_txn table : {upi_txn_additional_field1_db}")
                upi_txn_additional_field3_db = result["additional_field3"].iloc[0]
                logger.debug(f"Fetching additional_field3 from upi_txn table : {upi_txn_additional_field3_db}")
                upi_txn_resp_code_db = result["resp_code"].iloc[0]
                logger.debug(f"Fetching resp_code from upi_txn table : {upi_txn_resp_code_db}")
                upi_txn_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {upi_txn_txn_type_db}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

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
                    "org_code": upi_org_code_db,
                    "status": upi_status_db,
                    "additional_field1": upi_txn_additional_field1_db,
                    "additional_field3": upi_txn_additional_field3_db,
                    "resp_code": upi_txn_resp_code_db,
                    "txn_type": upi_txn_txn_type_db,
                    "publish_id": staticqr_intent_publish_id_db,
                    "vpa": staticqr_intent_vpa_db,
                    "qr_type": staticqr_intent_qrtype_db,
                    "intent_type": staticqr_intent_intent_type_db,
                    "user_mobile": staticqr_intent_user_mobile_db,
                    "user_name": staticqr_intent_user_name_db,
                    "bank_name": bank_name_db,
                    "rrn": rrn_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

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
                    'PAID BY:': 'UPI', 'RRN': str(ref_id),
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
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_107_035():
    """
    Sub Feature Code: UI_Common_UPI_Static_QR_KOTAK_2_Success_Callback_with_Same_REF_ID
    Sub Feature Description: Initiate UPI static QR via api and perform 2 UPI success callback with same ref_id
    TC naming code description: 100: Payment method, 107: UPI Static QR, 035: Testcase ID
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
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_audit_table_entry(portal_username, portal_password, org_code)

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

            # generating UPI STATIC QR
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation response : {generateqr_publish_id}")

            amount = random.randint(201, 400)
            logger.debug(f"amount is : {amount}")
            auth_code = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random auth_code is : {auth_code}")
            ref_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random ref_id is : {ref_id}")
            generate_random_secondary_id = str(random.randint(110000000, 110099999))
            logger.debug(f"generated random secondary id is : {generate_random_secondary_id}")
            customer_vpa = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7)) + "@upi"
            logger.debug(f" Value of customer vpa is : {customer_vpa}")

            # UPI Success Callback
            api_details = DBProcessor.get_api_details('callbackKotak', request_body={
                "mid": mid,
                "ref_no": ref_id,
                "txn_amount": "{:.2f}".format(amount),
                "tr_id": generateqr_publish_id,
                "transaction_type": "2",
                "tid": tid,
                "txn_currency": "356",
                "merchant_vpa": vpa,
                "settlement_amount": str(amount),
                "primary_id": generateqr_publish_id,
                "auth_code": auth_code,
                "customer_vpa": customer_vpa,
                "secondary_id": generate_random_secondary_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for static qr pure upi callback is : {response}")
            status = response['status']
            logger.debug(f"Value of status obtained from static qr pure upi callback is : {status}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(ref_id) + "'order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result of txn table : {result}")
            txn_id = result["id"].iloc[0]
            logger.debug(f"Fetching id from txn table : {txn_id}")
            status_db = result["status"].iloc[0]
            logger.debug(f"Fetching status from txn table : {status_db}")
            payment_mode_db = result["payment_mode"].iloc[0]
            logger.debug(f"Fetching payment_mode from txn table : {payment_mode_db}")
            amount_db = int(result["amount"].iloc[0])
            logger.debug(f"Fetching amount from txn table : {amount_db}")
            state_db = result["state"].iloc[0]
            logger.debug(f"Fetching state from txn table : {state_db}")
            payment_gateway_db = result["payment_gateway"].iloc[0]
            logger.debug(f"Fetching payment_gateway from txn table : {payment_gateway_db}")
            acquirer_code_db = result["acquirer_code"].iloc[0]
            logger.debug(f"Fetching acquirer_code from txn table : {acquirer_code_db}")
            bank_code_db = result["bank_code"].iloc[0]
            logger.debug(f"Fetching bank_code from txn table : {bank_code_db}")
            settlement_status_db = result["settlement_status"].iloc[0]
            logger.debug(f"Fetching settlement_status from txn table : {settlement_status_db}")
            tid_db = result['tid'].values[0]
            logger.debug(f"Fetching tid from txn table : {tid_db}")
            mid_db = result['mid'].values[0]
            logger.debug(f"Fetching mid from txn table : {mid_db}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from txn table : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from txn table : {txn_type}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from txn table : {created_time}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            bank_name_db = result["bank_name"].iloc[0]
            logger.debug(f"Fetching bank_name from the txn table : {bank_name_db}")
            payer_name_db = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table: {payer_name_db}")
            rrn_db = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn_db}")

            # 2nd callback for UPI with same ref_id
            api_details = DBProcessor.get_api_details('callbackKotak', request_body={
                "mid": mid,
                "ref_no": ref_id,
                "txn_amount": "{:.2f}".format(amount),
                "tr_id": generateqr_publish_id,
                "transaction_type": "2",
                "tid": tid,
                "txn_currency": "356",
                "merchant_vpa": vpa,
                "settlement_amount": str(amount),
                "primary_id": generateqr_publish_id,
                "auth_code": auth_code,
                "secondary_id": generate_random_secondary_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for static qr pure upi second callback is : {response}")
            status_2 = response['status']
            logger.debug(f"Value of status obtained from static qr pure upi second callback is : {status_2}")

            query = "select * from txn where org_code = '" + str(org_code) + "' and rr_number = '" + str(ref_id) + "'order by created_time desc limit 1; "
            logger.debug(f"Query to fetch data from txn table after second callback  : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result fetched from txn table after second callback : {result}")
            txn_id_2 = result["id"].iloc[0]
            logger.debug(f"Fetching id from txn table after second callback : {created_time}")

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
            date_and_time = date_time_converter.to_app_format(created_time)
            try:
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": str("%.2f" % amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id_2,
                    "rrn": str(ref_id),
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "auth_code": auth_code,
                    "date": date_and_time,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.info(f"Logging into the MPOSX application using username : {app_username} and password : {app_password}")
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
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_settlement_status}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "settle_status": app_settlement_status,
                    "pmt_msg": app_payment_msg,
                    "auth_code": app_auth_code,
                    "date": app_date_and_time,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
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
            date = date_time_converter.db_datetime(created_time)
            try:
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
                    "status": status_2,
                    "txn_id": txn_id,
                    "date": date,
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                # hitting the txnlist api
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username,
                    "password": app_password,
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
                    "status": status,
                    "txn_id": txn_id_2,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "customer_name": customer_name_api,
                    "payer_name": payer_name_api,
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
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "KOTAK",
                    "bank_code": "KOTAK",
                    "pmt_gateway": "KOTAK_ATOS",
                    "upi_txn_type": "STATIC_QR",
                    "upi_bank_code": "KOTAK_WL",
                    "upi_mc_id": config_id,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code,
                    "status": "AUTHORIZED",
                    "additional_field1": generateqr_publish_id,
                    "additional_field3": generateqr_publish_id,
                    "resp_code": "SUCCESS",
                    "txn_type": "STATIC_QR",
                    "publish_id": generateqr_publish_id,
                    "vpa": vpa,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    "txn_id": txn_id,
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "bank_name": "Kotak Mahindra",
                    "rrn": str(ref_id)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from upi_txn where txn_id='" + txn_id_2 + "';"
                logger.debug(f"Query to fetch data from upi_txn table : {txn_id_2} : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of upi_txn table : {txn_id_2} : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status from upi_txn table : {txn_id_2} : {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {txn_id_2} : {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code from upi_txn table : {txn_id_2} : {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"Fetching upi_mc_id from upi_txn table : {txn_id_2} : {upi_mc_id_db}")
                upi_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from upi_txn table : {txn_id_2} : {upi_org_code_db}")
                upi_txn_additional_field1_db = result["additional_field1"].iloc[0]
                logger.debug(f"Fetching additional_field1 from upi_txn table : {txn_id_2} : {upi_txn_additional_field1_db}")
                upi_txn_additional_field3_db = result["additional_field3"].iloc[0]
                logger.debug(f"Fetching additional_field3 from upi_txn table : {txn_id_2} : {upi_txn_additional_field3_db}")
                upi_txn_resp_code_db = result["resp_code"].iloc[0]
                logger.debug(f"Fetching resp_code from upi_txn table : {txn_id_2} : {upi_txn_resp_code_db}")
                upi_txn_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching txn_type from upi_txn table : {txn_id_2} : {upi_txn_txn_type_db}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

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
                    "org_code": upi_org_code_db,
                    "status": upi_status_db,
                    "additional_field1": upi_txn_additional_field1_db,
                    "additional_field3": upi_txn_additional_field3_db,
                    "resp_code": upi_txn_resp_code_db,
                    "txn_type": upi_txn_txn_type_db,
                    "publish_id": staticqr_intent_publish_id_db,
                    "vpa": staticqr_intent_vpa_db,
                    "qr_type": staticqr_intent_qrtype_db,
                    "intent_type": staticqr_intent_intent_type_db,
                    "txn_id": txn_id_2,
                    "user_mobile": staticqr_intent_user_mobile_db,
                    "user_name": staticqr_intent_user_name_db,
                    "bank_name": bank_name_db,
                    "rrn": rrn_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

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
                    'PAID BY:': 'UPI', 'RRN': str(ref_id),
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