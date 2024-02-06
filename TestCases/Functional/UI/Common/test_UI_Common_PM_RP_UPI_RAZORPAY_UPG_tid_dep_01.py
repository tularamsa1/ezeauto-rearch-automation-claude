import random
import sys
from datetime import datetime
import pytest
from Configuration import TestSuiteSetup, Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner, \
    date_time_converter, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_285():
    """
    Sub Feature Code:UI_Common_PM_RP_UPI_UPG_REFUND_PENDING_VIA_Razorpay_when_UPGRefund_Enabled_&_UPGAutoRefund_Enabled_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a upg txn using success callback via Razorpay when upg refund and upg autorefund are enabled
    Sub Feature Code: UI_Common_PM_RP_UPI_Amount_Mismatch_Razorpay_Tid_dep
    Sub Feature Description: Tid Dep - Verification of a Remote Pay upi for amount mismatch
    TC naming code description: 100: Payment Method, 103: RemotePay, 285: TC285
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result is : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        api_details = DBProcessor.get_api_details('upgRefundEnabled', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upgRefundEnabled"] = "true"
        api_details["RequestBody"]["settings"]["upgAutoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund is : {response}")

        query = f"update remotepay_setting set setting_value=1 where setting_name='cnpTxnTimeoutDuration' and  org_code='{org_code}';"
        logger.info(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating remotepay_setting table: {result}")

        query = f"update terminal_dependency_config set terminal_dependent_enabled = 1 where org_code ='{org_code}' and payment_gateway = 'RAZORPAY' and payment_mode = 'UPI';"
        logger.debug(f"Query to update terminal_dependency_config table is: {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"RESULT of updating terminal_dependency_config table active: {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={
            "username": portal_username,
            "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"response for dp refresh : {response}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' and status = 'ACTIVE' and " \
                f"bank_code = 'RAZORPAY_PSP' and allowed_mode='HYBRID' and card_terminal_acquirer_code='HDFC';"
        logger.debug(f"Query to fetch data from upi_merchant_config table is : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result is : {result}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"pg_merchant_id is : {pg_merchant_id} ")
        mid_db = result['mid'].iloc[0]
        logger.debug(f"mid_db is : {mid_db} ")
        tid_db = result['tid'].iloc[0]
        logger.debug(f"tid_db is : {tid_db} ")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()

            amount1 = random.randint(601, 700)
            logger.info(f"Amount is {amount1}")
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")

            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=org_code, acquisition="HDFC",
                                                                           payment_gateway="HDFC")
            logger.debug(f"device_serial is  : {device_serial}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate_Tid_dependent', request_body={
                "amount": amount1,
                "externalRefNumber": order_id,
                "username": app_username,
                "password": app_password,
                "deviceSerial": device_serial
            })

            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                ui_browser = TestSuiteSetup.initialize_ui_browser()
                paymentLinkUrl = response['paymentLink']
                payment_intent_id = response.get('paymentIntentId')
                logger.info("Opening the link in the browser")
                ui_browser.goto(paymentLinkUrl)
                remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
                remotePayUpiCollectTxn.clickOnRemotePayUPI()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
                logger.info("Opening UPI Collect to start the txn.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
                logger.info("VPA validation completed.")
                remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

                query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}' order by created_time desc limit 1"
                logger.debug(f"Query to fetch Txn_id and rrn_expired from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result is : {result}")
                original_txn_id = result['id'].values[0]
                logger.debug(f"Query result, original_txn_id : {payment_intent_id}")
                txn_device_serial = result['device_serial'].values[0]
                logger.debug(f"Query result, device_serial from db : {txn_device_serial}")
                mid = result['mid'].values[0]
                logger.debug(f"Query result, mid from db : {mid}")
                tid = result['tid'].values[0]
                logger.debug(f"Query result, tid from db : {tid}")

                query = f"select * from upi_txn where txn_id='{original_txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                txn_ref = result['txn_ref'].values[0]
                logger.debug(f"txn_ref: {txn_ref}")
                txn_ref_3 = result['txn_ref3'].values[0]
                logger.debug(f"txn_ref_3: {txn_ref_3}")
                rrn = str(random.randint(1000000000000, 9999999999999))
                logger.info(f"generated rrn value is: {rrn}")
                mismatch_amount = 999
                logger.info(f"Mismatch amount is: {mismatch_amount}")

                api_details_hmac = DBProcessor.get_api_details('remote_pay_razorpay_callback_generator_HMAC_success')
                api_details_hmac['RequestBody']['account_id'] = pg_merchant_id
                api_details_hmac['RequestBody']['payload']['payment']['entity']['id'] = txn_ref
                api_details_hmac['RequestBody']['payload']['payment']['entity']['amount'] = mismatch_amount * 100
                api_details_hmac['RequestBody']['payload']['payment']['entity']['base_amount'] = mismatch_amount * 100
                api_details_hmac['RequestBody']['payload']['payment']['entity']['order_id'] = txn_ref_3
                api_details_hmac['RequestBody']['payload']['payment']['entity']['acquirer_data']['rrn'] = rrn

                response = APIProcessor.send_request(api_details_hmac)
                logger.debug(f"Response received for razorpay_callback_generator_HMAC api is : {response}")
                razorpay_signature = response['razorpay_signature']
                logger.debug(f"razorpay_signature received for razorpay_callback_generator_HMAC api is : "
                             f"{razorpay_signature}")
                logger.debug(f"performing upi callback for razorpay")

                api_details = DBProcessor.get_api_details('upi_confirm_razorpay',
                                                          request_body=api_details_hmac['RequestBody'])

                api_details['Header'] = {'x-razorpay-signature': razorpay_signature,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for upi_confirm_razorpay : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for upi_confirm_razorpay api is : {response}")

                query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
                logger.info(f"Query for invalid request is: {query}")
                q_result = DBProcessor.getValueFromDB(query)
                logger.info(f"Result is: {q_result}")
                txn_id = q_result['txn_id'].iloc[0]
                logger.info(f"txn_id is: {txn_id}")

                query = f"select * from txn where id = '{str(txn_id)}';"
                logger.debug(f"Query to fetch txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result is : {result}")
                external_ref = result['external_ref'].values[0]
                logger.debug(f"external_ref is : {external_ref}")
                org_code_txn = result['org_code'].values[0]
                logger.debug(f"org_code_txn is : {org_code_txn}")
                txn_type = result['txn_type'].values[0]
                logger.debug(f"txn_type is : {txn_type}")
                auth_code = result['auth_code'].values[0]
                logger.debug(f"auth_code is : {auth_code}")
                posting_date = result['posting_date'].values[0]
                logger.debug(f"posting_date is : {posting_date}")
                created_time = result['created_time'].values[0]
                logger.debug(f"created_time is : {created_time}")
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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "txn_amt": str(mismatch_amount) + ".00",
                    "rrn": str(rrn),
                    "payment_msg": "REFUND PENDING",
                    "date": date_and_time
                }

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)

                loginPage = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
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
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")

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
                    "pmt_status": "UPG_REFUND_PENDING",
                    "txn_amt": mismatch_amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "UPG_REFUND_PENDING",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status from api response is: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount from api response is: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment mode from api response is: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state from api response is: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn from api response is: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement status from api response is: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer code from api response is: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer code from api response is: {acquirer_code_api}")
                org_code_api = response["orgCode"]
                logger.debug(f"org_code from api response is: {org_code_api}")
                mid_api = response["mid"]
                logger.debug(f"mid from api response is: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid from api response is: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn type from api response is: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date from api response is: {date_api}")

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
                    "txn_amt": mismatch_amount,
                    "upi_txn_status": "UPG_REFUND_PENDING",
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "payment_gateway": "RAZORPAY",
                    "upi_txn_type": "UNKNOWN",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "mid": mid,
                    "tid": tid,
                    "ipr_pmt_mode": "UPI",
                    "ipr_bank_code": "RAZORPAY",
                    "ipr_org_code": org_code,
                    "ipr_auth_code": auth_code,
                    "ipr_rrn": str(rrn),
                    "ipr_txn_amt": mismatch_amount,
                    "ipr_mid": mid,
                    "ipr_tid": tid,
                    "ipr_pg_merchant_id": pg_merchant_id,
                    "device_serial": txn_device_serial
                }

                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"Fetching status: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching payment_mode: {status_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"Fetching amount: {status_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"Fetching state: {status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"Fetching payment_gateway: {payment_gateway_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"Fetching acquirer_code: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code: {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"Fetching settlement_status: {settlement_status_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"Fetching tid: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"Fetching mid: {mid_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"Fetching upi_status: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"Fetching upi_txn_type: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"Fetching upi_bank_code: {upi_bank_code_db}")

                query = f"select * from invalid_pg_request where request_id ='{txn_ref_3}';"
                logger.debug(f"query to fetch data from invalid_pg_request table is: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                ipr_payment_mode = result["payment_mode"].iloc[0]
                logger.debug(f"Fetching payment_mode: {ipr_payment_mode}")
                ipr_bank_code = result["bank_code"].iloc[0]
                logger.debug(f"Fetching bank_code: {ipr_bank_code}")
                ipr_org_code = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code: {ipr_org_code}")
                ipr_amount = result["amount"].iloc[0]
                logger.debug(f"Fetching amount: {ipr_amount}")
                ipr_rrn = result["rrn"].iloc[0]
                logger.debug(f"Fetching rrn: {ipr_rrn}")
                ipr_auth_code = result["auth_code"].iloc[0]
                logger.debug(f"Fetching auth_code: {ipr_auth_code}")
                ipr_mid = result["mid"].iloc[0]
                logger.debug(f"Fetching mid: {ipr_mid}")
                ipr_tid = result["tid"].iloc[0]
                logger.debug(f"Fetching tid: {ipr_tid}")
                ipr_pg_merchant_id = result["pg_merchant_id"].iloc[0]
                logger.debug(f"Fetching pg_merchant_id: {ipr_pg_merchant_id}")

                query = f"select * from terminal_info where tid ='{str(tid_db)}';"
                logger.debug(f"Query to fetch data from terminal_info table is : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query to fetch data from terminal_info table : {query}")
                device_serial_db = result['device_serial'].iloc[0]
                logger.debug(f"device_serial_db is : {device_serial_db}")

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
                    "ipr_pg_merchant_id": ipr_pg_merchant_id,
                    "device_serial": device_serial_db

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
                    "txn_amt": str(mismatch_amount) + ".00",
                    "username": "EZETAP",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, external_ref)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time from portal is: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id from portal is: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount from portal is: {total_amount}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number from portal is: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type from portal is: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status from portal is: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username from portal is: {username}")

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
        query = "update remotepay_setting set setting_value=2 where setting_name='cnpTxnTimeoutDuration' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)
