import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_111_039():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_COLLECT_Success_Via_Common_CheckStatus_MultiAcc_Razorpay
    Sub Feature Description: Multi Account - Performing a successful RP_UPI_COLLECT txn via Razorpay using check status
    TC naming code description: 100: Payment Method, 111: MultiAcc_RemotePay, 039: TC_039
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id : {upi_mc_id}")
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, acc_label_id : {acc_label_id}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid : {mid}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"tid : {tid}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(1001, 1101)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password,
                "accountLabel": str(account_label_name)})

            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            paymentLinkUrl = response['paymentLink']
            logger.debug(f" paymentLinkUrl is : {paymentLinkUrl}")
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
            remotePayUpiCollectTxn.clickOnRemotePayCancelUPI()
            remotePayUpiCollectTxn.clickOnRemotePayProceed()
            logger.info("UPI Collect txn is completed.")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Query result, posting_date : {posting_date}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Query result, label_ids : {label_ids}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time from db : {created_time}")
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
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,

                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
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
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "account_label": str(account_label_name)
                }
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn_api: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api: {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"orgCode_api: {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid: {tid}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api: {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"account_label_name_api: {account_label_name_api}")

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
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "account_label": str(account_label_name_api)
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
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "RAZORPAY",
                    "acc_label_id": str(acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}';"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db: {state_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db: {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db: {settlement_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"tid_db: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"mid_db: {mid_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}';"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db: {upi_mc_id_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}';"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "acc_label_id": str(label_ids)
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
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal,
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code: {auth_code}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time,
                    "acc_label": labels
                }
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,actualPortal=actual_portal_values)
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
                                   'BASE AMOUNT:': f"Rs.{amount:,}.00", 'date': txn_date,
                                   'time': txn_time,
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
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_111_040():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_COLLECT_Failed_Via_Common_CheckStatus_MultiAcc_Razorpay
    Sub Feature Description: Multi Account - Performing a failed RP_UPI_COLLECT txn via Razorpay using check status
    TC naming code description:100: Payment Method, 111: MultiAcc_RemotePay, 040: TC_040
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name1']
        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id : {upi_mc_id}")
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, acc_label_id : {acc_label_id}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid : {mid}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"tid : {tid}")
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

            amount = random.randint(710, 800)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password,
                "accountLabel": str(account_label_name)})
            response = APIProcessor.send_request(api_details)
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            paymentLinkUrl = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(paymentLinkUrl)
            remotePayUpiCollectTxn = RemotePayTxnPage(ui_browser)
            remotePayUpiCollectTxn.clickOnRemotePayUPI()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollect()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectAppSelection()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectId("abc")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectDropDown("okicici")
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectVpaValidation()
            remotePayUpiCollectTxn.clickOnRemotePayUpiCollectProceed()

            query = f"select * from txn where org_code = '{str(org_code)}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_id : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, created_time : {created_time}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Query result, label_ids : {label_ids}")
            # ---------------------------------------------------------------------------------------------------------
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
            try:
                logger.info(f"Started APP validation for the test case : {testcase_id}")
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "customer_name": "failure@razorpay",
                    "payer_name": "failure@razorpay",
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
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
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actual_app_values = {
                    "pmt_mode": payment_mode,
                    "pmt_status": payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "customer_name": app_customer_name,
                    "settle_status": app_settlement_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_and_time
                }
                logger.debug(f"actual_app_values: {actual_app_values}")

                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation-------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                logger.info(f"Started API validation for the test case : {testcase_id}")
                logger.info("Api Validation Started for the test case : test_common_100_103_005")
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status": "FAILED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "account_label": str(account_label_name)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = response["amount"]
                logger.debug(f"amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api: {state_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api: {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"orgCode_api: {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api: {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"account_label_name_api: {account_label_name_api}")

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
                    "org_code": orgCode_api,
                    "date": date_time_converter.from_api_to_datetime_format(date_api),
                    "account_label": str(account_label_name_api)
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                logger.info("DB Validation Started for the test case : test_common_100_103_005")
                expected_db_values = {
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "UPI",
                    "txn_amt": amount,
                    "upi_txn_status": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "ACTIVE",
                    "acc_label_id": str(acc_label_id),
                    "tid" : tid,
                    "mid": mid
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db: {state_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db: {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db: {settlement_status_db}")
                mid_db = result["mid"].values[0]
                logger.debug(f"mid: {mid}")
                tid_db = result["tid"].values[0]
                logger.debug(f"tid: {tid}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db: {upi_mc_id_db}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "acc_label_id": str(label_ids),
                    "tid": tid_db,
                    "mid": mid_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
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
                    "pmt_state": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal,
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")

                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "txn_id": transaction_id,
                    "date_time": date_time,
                    "acc_label": labels
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
@pytest.mark.chargeSlipVal
def test_common_100_111_047():
    """
    Sub Feature Code: UI_Common_PM_RP_UPI_COLLECT_Success_Via_Common_CheckStatus_with_2nd_label_MultiAcc_Razorpay
    Sub Feature Description: Multi Account - Performing a successful RP_UPI_COLLECT txn via Razorpay using check status second account (ex:acc2 label)
    TC naming code description:100: Payment Method, 111: MultiAcc_RemotePay, 047: TC_047
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
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='RAZORPAY_PSP', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        account_labels = testsuite_teardown.get_account_labels_and_set_default_account(
            org_code, portal_un=portal_username, portal_pw=portal_password)
        account_label_name = account_labels['name2']
        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'RAZORPAY_PSP' AND acc_label_id=(select id from label " \
                f"where name='{account_label_name}' AND org_code ='{org_code}')"
        logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Query result, upi_mc_id : {upi_mc_id}")
        acc_label_id = result['acc_label_id'].values[0]
        logger.debug(f"Query result, org_code : {acc_label_id}")
        mid = result['virtual_mid'].values[0]
        logger.debug(f"mid : {mid}")
        tid = result['virtual_tid'].values[0]
        logger.debug(f"tid : {tid}")
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
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1001, 1100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate_MultiAcc', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password,
                "accountLabel": str(account_label_name)})

            response = APIProcessor.send_request(api_details)
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
            remotePayUpiCollectTxn.clickOnRemotePayCancelUPI()
            remotePayUpiCollectTxn.clickOnRemotePayProceed()
            logger.info("UPI Collect txn is completed.")

            query = f"select * from txn where org_code = '{org_code}' AND external_ref = '{str(order_id)}';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {txn_id}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, auth_code : {auth_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, customer_name : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, payer_name : {payer_name}")
            posting_date = result['created_time'].values[0]
            logger.debug(f"Query result, posting_date : {posting_date}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Query result, org_code_txn : {org_code_txn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, txn_type : {txn_type}")
            label_ids = str(result['label_ids'].values[0]).strip(',')
            logger.debug(f"Query result, label_ids : {label_ids}")
            # ------------------------------------------------------------------------------------------------------
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
        # -----------------------------------------Start of App Validation-----------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "pmt_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
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
                logger.info(f"Fetching txn settlement_status from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching txn payer name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")

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
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date = date_time_converter.db_datetime(posting_date)
                expected_api_values = {
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": amount,
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "RAZORPAY",
                    "issuer_code": "RAZORPAY",
                    "txn_type": txn_type,
                    "mid": mid,
                    "tid": tid,
                    "org_code": org_code_txn,
                    "date": date,
                    "account_label": str(account_label_name)

                }
                api_details = DBProcessor.get_api_details('txnlist', request_body={
                    "username": app_username, "password": app_password})
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api = response["status"]
                logger.debug(f"status_api: {status_api}")
                amount_api = int(response["amount"])
                logger.debug(f"amount_api: {amount_api}")
                payment_mode_api = response["paymentMode"]
                logger.debug(f"payment_mode_api: {payment_mode_api}")
                state_api = response["states"][0]
                logger.debug(f"state_api: {state_api}")
                rrn_api = response["rrNumber"]
                logger.debug(f"rrn_api: {rrn_api}")
                settlement_status_api = response["settlementStatus"]
                logger.debug(f"settlement_status_api: {settlement_status_api}")
                issuer_code_api = response["issuerCode"]
                logger.debug(f"issuer_code_api: {issuer_code_api}")
                acquirer_code_api = response["acquirerCode"]
                logger.debug(f"acquirer_code_api: {acquirer_code_api}")
                orgCode_api = response["orgCode"]
                logger.debug(f"orgCode_api: {orgCode_api}")
                mid_api = response["mid"]
                logger.debug(f"mid_api: {mid_api}")
                tid_api = response["tid"]
                logger.debug(f"tid_api: {tid_api}")
                txn_type_api = response["txnType"]
                logger.debug(f"txn_type_api: {txn_type_api}")
                date_api = response["postingDate"]
                logger.debug(f"date_api: {date_api}")
                account_label_name_api = response["accountLabel"]
                logger.debug(f"account_label_name_api: {account_label_name_api}")

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
                    "account_label": str(account_label_name_api)
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
                    "acquirer_code": "RAZORPAY",
                    "bank_code": "RAZORPAY",
                    "upi_txn_type": "COLLECT",
                    "upi_bank_code": "RAZORPAY_PSP",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "mid": mid,
                    "tid": tid,
                    "pmt_gateway": "RAZORPAY",
                    "acc_label_id": str(acc_label_id)
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                logger.debug(f"status_db: {status_db}")
                payment_mode_db = result["payment_mode"].iloc[0]
                logger.debug(f"payment_mode_db: {payment_mode_db}")
                amount_db = int(result["amount"].iloc[0])
                logger.debug(f"amount_db: {amount_db}")
                state_db = result["state"].iloc[0]
                logger.debug(f"state_db: {state_db}")
                acquirer_code_db = result["acquirer_code"].iloc[0]
                logger.debug(f"acquirer_code_db: {acquirer_code_db}")
                bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"bank_code_db: {bank_code_db}")
                settlement_status_db = result["settlement_status"].iloc[0]
                logger.debug(f"settlement_status_db: {settlement_status_db}")
                payment_gateway_db = result["payment_gateway"].iloc[0]
                logger.debug(f"payment_gateway_db: {payment_gateway_db}")
                tid_db = result['tid'].values[0]
                logger.debug(f"tid_db: {tid_db}")
                mid_db = result['mid'].values[0]
                logger.debug(f"mid_db: {mid_db}")

                query = f"select * from upi_txn where txn_id='{txn_id}'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                logger.debug(f"upi_status_db: {upi_status_db}")
                upi_txn_type_db = result["txn_type"].iloc[0]
                logger.debug(f"upi_txn_type_db: {upi_txn_type_db}")
                upi_bank_code_db = result["bank_code"].iloc[0]
                logger.debug(f"upi_bank_code_db: {upi_bank_code_db}")
                upi_mc_id_db = result["upi_mc_id"].iloc[0]
                logger.debug(f"upi_mc_id_db: {upi_mc_id_db}")

                query = f"select * from payment_intent where id='{payment_intent_id}'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]
                logger.debug(f"payment_intent_status: {payment_intent_status}")

                actual_db_values = {
                    "pmt_status": status_db,
                    "pmt_state": state_db,
                    "pmt_mode": payment_mode_db,
                    "txn_amt": amount_db,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settlement_status_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code": bank_code_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "mid": mid_db,
                    "tid": tid_db,
                    "pmt_gateway": payment_gateway_db,
                    "acc_label_id": str(label_ids)
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
                date_and_time_portal = date_time_converter.to_portal_format(posting_date)
                expected_portal_values = {
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "auth_code": "-" if auth_code is None else auth_code,
                    "rrn": rrn,
                    "txn_id": txn_id,
                    "date_time": date_and_time_portal,
                    "acc_label": account_label_name
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                logger.debug(f"date_time: {date_time}")
                transaction_id = transaction_details[0]['Transaction ID']
                logger.debug(f"transaction_id: {transaction_id}")
                total_amount = transaction_details[0]['Total Amount'].split()
                logger.debug(f"total_amount: {total_amount}")
                auth_code_portal = transaction_details[0]['Auth Code']
                logger.debug(f"auth_code_portal: {auth_code_portal}")
                rr_number = transaction_details[0]['RR Number']
                logger.debug(f"rr_number: {rr_number}")
                transaction_type = transaction_details[0]['Type']
                logger.debug(f"transaction_type: {transaction_type}")
                status = transaction_details[0]['Status']
                logger.debug(f"status: {status}")
                username = transaction_details[0]['Username']
                logger.debug(f"username: {username}")
                labels = transaction_details[0]['Labels']
                logger.debug(f"labels: {labels}")
                actual_portal_values = {
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    "auth_code": auth_code_portal,
                    "rrn": rr_number,
                    "txn_id": transaction_id,
                    "date_time": date_time,
                    "acc_label": labels
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': f"Rs.{amount:,}.00", 'date': txn_date,
                                   'time': txn_time,
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
