import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_311():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Cards_Enabled_Success_Transaction_via_UPI_via_HDFC
    Sub Feature Description: After entering the card details, select UPI and continue the success payment with UPI via HDFC
    TC naming code description: 100: Payment Method, 103: RemotePay, 311: TC311
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code = '{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from upi_merchant_config table :{result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            customer_mobile = '12345' + str(random.randint(10000, 12000))
            logger.debug(f"customer_mobile : {customer_mobile}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
                "customerMobileNumber": customer_mobile
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 1091")
            remote_pay_txn.enterCreditCardExpiryMonth("3")
            remote_pay_txn.enterCreditCardExpiryYear("2048")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnRemotePayUPI()
            remote_pay_txn.clickOnRemotePayLaunchUPI()
            remote_pay_txn.clickOnRemotePayCancelUPI()
            remote_pay_txn.clickOnRemotePayProceed()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table : {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table : {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table : {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table : {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table : {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table : {tid_txn}")
            bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the txn table : {bank_code}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from upi_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from upi_txn table :{result}")
            upi_status_db = result["status"].values[0]
            logger.debug(f"Fetching status from the upi_txn table : {upi_status_db}")
            upi_txn_type_db = result["txn_type"].values[0]
            logger.debug(f"Fetching txn_type from the upi_txn table : {upi_txn_type_db}")
            upi_bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the upi_txn table : {upi_bank_code_db}")
            upi_mc_id_db = result["upi_mc_id"].values[0]
            logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

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
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile,
                    "auth_code": "NA" if auth_code is None else auth_code,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer_name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")
                app_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the txn : {txn_id}, {app_auth_code}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settle_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "auth_code": app_auth_code
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
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code_txn,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": customer_name_txn,
                    "customer_mobile": customer_mobile
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile : {api_customer_mobile}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "bank_code": "HDFC",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "customer_mobile": customer_mobile
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "bank_code": bank_code,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "customer_mobile": customer_mobile_txn
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn
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
                expected_charge_slip_values = {
                    "PAID BY:": "UPI",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")

                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)

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
def test_common_100_103_312():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Cards_Enabled_Success_Transaction_via_Card_via_HDFC
    Sub Feature Description: Select the UPI payment mode, cancel it and then initiate a card payment to perform successful payment via HDFC
    TC naming code description: 100: Payment Method, 103: RemotePay, 312: TC312
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code = '{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from upi_merchant_config table :{result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            customer_mobile = '12345' + str(random.randint(10000, 12000))
            logger.debug(f"customer_mobile : {customer_mobile}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
                "customerMobileNumber": customer_mobile
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            remote_pay_txn.clickOnRemotePayUPI()
            remote_pay_txn.clickOnRemotePayLaunchUPI()
            remote_pay_txn.clickOnRemotePayCancelUPI()
            remote_pay_txn.clickOnRemotePayProceed()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            ui_browser.goto(payment_link_url)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 1091")
            remote_pay_txn.enterCreditCardExpiryMonth("3")
            remote_pay_txn.enterCreditCardExpiryYear("2048")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()
            remote_pay_txn.switch_to_iframe()

            success_message = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your expected success message is:  {success_message}")
            logger.info(f"Your expected message is:  {expected_message}")
            if success_message == expected_message:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch txn details from the txn table for failed txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for failed txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for failed txn: {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for failed txn: {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for failed txn: {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for failed txn: {payer_name}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for failed txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for failed txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for failed txn: {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for failed txn: {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for failed txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for failed txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for failed txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for failed txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for failed txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for failed txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for failed txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for failed txn: {tid_txn}")
            bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the txn table for failed txn: {bank_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for failed txn: {rrn}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch txn details from the txn table for success txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for success txn: {created_time_2}")
            acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for success txn: {acquirer_code_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for success txn: {auth_code_2}")
            customer_name_txn_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for success txn: {customer_name_txn_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for success txn: {payer_name_2}")
            settle_status_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for success txn: {settle_status_2}")
            pmt_status_2 = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for success txn: {pmt_status_2}")
            payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for success txn: {payment_mode_2}")
            issuer_code_txn_2 = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for success txn: {issuer_code_txn_2}")
            pmt_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for success txn: {pmt_state_2}")
            amount_txn_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for success txn: {amount_txn_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for success txn: {merchant_name_2}")
            order_id_txn_2 = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for success txn: {order_id_txn_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for success txn: {org_code_txn_2}")
            customer_mobile_txn_2 = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for success txn: {customer_mobile_txn_2}")
            mid_txn_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for success txn: {mid_txn_2}")
            tid_txn_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for success txn: {tid_txn_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for success txn: {rrn_2}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from upi_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from upi_txn table :{result}")
            upi_status_db = result["status"].values[0]
            logger.debug(f"Fetching status from the upi_txn table : {upi_status_db}")
            upi_txn_type_db = result["txn_type"].values[0]
            logger.debug(f"Fetching txn_type from the upi_txn table : {upi_txn_type_db}")
            upi_bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the upi_txn table : {upi_bank_code_db}")
            upi_mc_id_db = result["upi_mc_id"].values[0]
            logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

            query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table : {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table : {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table : {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table : {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table : {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table : {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table : {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table : {cnp_txn_payment_state}")
            cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from cnp_txn table : {cnp_txn_payment_card_bin}")
            cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from cnp_txn table : {cnp_txn_payment_card_brand}")
            cnp_txn_payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from cnp_txn table : {cnp_txn_payment_card_type}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table : {cnp_txn_acquirer_code}")
            cnp_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table : {cnp_txn_issuer_code}")
            cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from cnp_txn table : {cnp_txn_card_last_four_digit}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table : {cnp_txn_org_code}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table : {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table : {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table : {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table : {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table : {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table : {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table : {cnpware_txn_payment_gateway}")

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "rrn": str(rrn),
                    "pmt_mode_2": "PAY LINK",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(cnp_txn_rrn),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "customer_mobile_2": customer_mobile,
                    "card": "*1091",
                    "auth_code": auth_code_2,
                    "customer_name_2": customer_name_txn_2,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the failed txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the failed txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the failed txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the failed txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the failed txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the failed txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the failed txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the failed txn : {txn_id}, {app_settle_status}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the failed txn : {txn_id}, {app_customer_mobile}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the failed txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching customer_name from txn history for the failed txn : {txn_id}, {app_payer_name}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the failed txn : {txn_id}, {app_rrn}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the success txn : {txn_id}, {app_amount_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the success txn : {txn_id}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the success txn : {txn_id}, {app_payment_msg_2}")
                app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the success txn : {txn_id}, {app_payment_mode_2}")
                app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the success txn : {txn_id}, {app_payment_status_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the success txn : {txn_id}, {app_txn_id_2}")
                app_date_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the success txn : {txn_id}, {app_date_time_2}")
                app_settle_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the success txn : {txn_id}, {app_settle_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the success txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the success txn : {txn_id}, {app_auth_code_2}")
                app_card_2 = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the success txn : {txn_id}, {app_card_2}")
                app_customer_mobile_2 = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the success txn : {txn_id}, {app_customer_mobile_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the success txn : {txn_id}, {app_customer_name_2}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "customer_name": app_customer_name,
                    "payer_name": app_payer_name,
                    "rrn": str(app_rrn),
                    "pmt_mode_2": app_payment_mode_2,
                    "pmt_status_2": app_payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "settle_status_2": app_settle_status_2,
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_time_2,
                    "customer_mobile_2": app_customer_mobile_2,
                    "card": app_card_2,
                    "auth_code": app_auth_code_2,
                    "customer_name_2": app_customer_name_2
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
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code_txn,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": customer_name_txn,
                    "customer_mobile": customer_mobile,

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CNP",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(cnp_txn_rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "REMOTE_PAY",
                    "mid_2": mid_txn_2,
                    "tid_2": tid_txn_2,
                    "org_code_2": org_code_txn_2,
                    "date_2": date_2,
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "customer_name_2": customer_name_txn_2,
                    "payer_name_2": payer_name_2,
                    "name_on_card_2": payer_name_2,
                    "customer_mobile_2": customer_mobile
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of failed txn is : {response}")
                api_amount = response_1.get('amount')
                logger.debug(f"From response fetch amount for failed txn : {api_amount}")
                api_payment_mode = response_1.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for failed txn : {api_payment_mode}")
                api_payment_status = response_1.get('status')
                logger.debug(f"From response fetch payment_status for failed txn : {api_payment_status}")
                api_payment_state = response_1.get('states')[0]
                logger.debug(f"From response fetch payment_state for failed txn : {api_payment_state}")
                api_mid = response_1.get('mid')
                logger.debug(f"From response fetch mid for failed txn : {api_mid}")
                api_tid = response_1.get('tid')
                logger.debug(f"From response fetch tid for failed txn : {api_tid}")
                api_acquirer_code = response_1.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for failed txn : {api_acquirer_code}")
                api_settle_status = response_1.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for failed txn : {api_settle_status}")
                api_issuer_code = response_1.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for failed txn : {api_issuer_code}")
                api_txn_type = response_1.get('txnType')
                logger.debug(f"From response fetch txn_type for failed txn : {api_txn_type}")
                api_org_code = response_1.get('orgCode')
                logger.debug(f"From response fetch org_code for failed txn : {api_org_code}")
                api_date_time = response_1.get('createdTime')
                logger.debug(f"From response fetch date_time for failed txn : {api_date_time}")
                api_merchant_name = response_1.get('merchantName')
                logger.debug(f"From response fetch merchant_name for failed txn : {api_merchant_name}")
                api_ext_ref_number = response_1.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for failed txn : {api_ext_ref_number}")
                api_customer_name = response_1.get('customerName')
                logger.debug(f"From response fetch customer_name for failed txn : {api_customer_name}")
                api_payer_name = response_1.get('payerName')
                logger.debug(f"From response fetch payer_name for failed txn : {api_payer_name}")
                api_name_on_card = response_1.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for failed txn : {api_name_on_card}")
                api_customer_mobile = response_1.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for failed txn : {api_customer_mobile}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of success txn is : {response}")
                api_amount_2 = response_2.get('amount')
                logger.debug(f"From response fetch amount for success txn : {api_amount_2}")
                api_payment_mode_2 = response_2.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for success txn : {api_payment_mode_2}")
                api_payment_status_2 = response_2.get('status')
                logger.debug(f"From response fetch payment_status for success txn : {api_payment_status_2}")
                api_payment_state_2 = response_2.get('states')[0]
                logger.debug(f"From response fetch payment_state for success txn : {api_payment_state_2}")
                api_mid_2 = response_2.get('mid')
                logger.debug(f"From response fetch mid for success txn : {api_mid_2}")
                api_tid_2 = response_2.get('tid')
                logger.debug(f"From response fetch tid for success txn : {api_tid_2}")
                api_acquirer_code_2 = response_2.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for success txn : {api_acquirer_code_2}")
                api_settle_status_2 = response_2.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for success txn : {api_settle_status_2}")
                api_rrn_2 = response_2.get('rrNumber')
                logger.debug(f"From response fetch rrn for success txn : {api_rrn_2}")
                api_issuer_code_2 = response_2.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for success txn : {api_issuer_code_2}")
                api_txn_type_2 = response_2.get('txnType')
                logger.debug(f"From response fetch txn_type for success txn : {api_txn_type_2}")
                api_org_code_2 = response_2.get('orgCode')
                logger.debug(f"From response fetch org_code for success txn : {api_org_code_2}")
                api_date_time_2 = response_2.get('createdTime')
                logger.debug(f"From response fetch date_time for success txn : {api_date_time_2}")
                api_merchant_name_2 = response_2.get('merchantName')
                logger.debug(f"From response fetch merchant_name for success txn : {api_merchant_name_2}")
                api_ext_ref_number_2 = response_2.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for success txn : {api_ext_ref_number_2}")
                api_customer_name_2 = response_2.get('customerName')
                logger.debug(f"From response fetch customer_name for success txn : {api_customer_name_2}")
                api_payer_name_2 = response_2.get('payerName')
                logger.debug(f"From response fetch payer_name for success txn : {api_payer_name_2}")
                api_name_on_card_2 = response_2.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for success txn : {api_name_on_card_2}")
                api_customer_mobile_2 = response_2.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for success txn : {api_customer_mobile_2}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,

                    "pmt_status_2": api_payment_status_2,
                    "txn_amt_2": api_amount_2,
                    "pmt_mode_2": api_payment_mode_2,
                    "pmt_state_2": api_payment_state_2,
                    "rrn_2": str(api_rrn_2),
                    "settle_status_2": api_settle_status_2,
                    "acquirer_code_2": api_acquirer_code_2,
                    "issuer_code_2": api_issuer_code_2,
                    "txn_type_2": api_txn_type_2,
                    "mid_2": api_mid_2,
                    "tid_2": api_tid_2,
                    "org_code_2": api_org_code_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_2),
                    "ext_ref_number_2": api_ext_ref_number_2,
                    "merchant_name_2": api_merchant_name_2,
                    "customer_name_2": api_customer_name_2,
                    "payer_name_2": api_payer_name_2,
                    "name_on_card_2": api_name_on_card_2,
                    "customer_mobile_2": api_customer_mobile_2
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "FAILED",
                    "acquirer_code": "HDFC",
                    "issuer_code": "HDFC",
                    "bank_code": "HDFC",
                    "customer_mobile": customer_mobile,
                    "org_code": org_code,
                    "upi_txn_status": "FAILED",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "HDFC",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "customer_mobile_2": customer_mobile,
                    "org_code_2": org_code,

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "400000",
                    "cnp_pmt_card_brand": "VISA",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": issuer_code_txn_2,
                    "cnp_card_last_four_digit": "1091",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "CYBERSOURCE",
                    "cnpware_txn_type": "REMOTE_PAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "bank_code": bank_code,
                    "customer_mobile": customer_mobile_txn,
                    "org_code": org_code_txn,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "acquirer_code_2": acquirer_code_2,
                    "issuer_code_2": issuer_code_txn_2,
                    "customer_mobile_2": customer_mobile_txn_2,
                    "org_code_2": org_code_txn_2,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "customer_mobile": customer_mobile,
                    "rrn": str(rrn),
                    "auth_code": "NA" if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "customer_mobile_2": customer_mobile,
                    "rrn_2": "-" if rrn_2 is None else rrn_2,
                    "auth_code_2": auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']
                portal_customer_mobile = transaction_details[1]['Mobile No.']
                portal_rrn = transaction_details[1]['RR Number']
                portal_auth_code = transaction_details[1]['Auth Code']

                portal_date_time_2 = transaction_details[0]['Date & Time']
                portal_txn_id_2 = transaction_details[0]['Transaction ID']
                portal_total_amount_2 = transaction_details[0]['Total Amount']
                portal_auth_code_2 = transaction_details[0]['Auth Code']
                portal_txn_type_2 = transaction_details[0]['Type']
                portal_txn_status_2 = transaction_details[0]['Status']
                portal_user_2 = transaction_details[0]['Username']
                portal_customer_mobile_2 = transaction_details[1]['Mobile No.']
                portal_rrn_2 = transaction_details[0]['RR Number']

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "customer_mobile": portal_customer_mobile,
                    "rrn": str(portal_rrn),
                    "auth_code": portal_auth_code,

                    "date_time_2": portal_date_time_2,
                    "pmt_status_2": portal_txn_status_2,
                    "pmt_type_2": portal_txn_type_2,
                    "txn_amt_2": portal_total_amount_2.split(' ')[1],
                    "username_2": portal_user_2,
                    "txn_id_2": portal_txn_id_2,
                    "customer_mobile_2": portal_customer_mobile_2,
                    "rrn_2": str(portal_rrn_2),
                    "auth_code_2": portal_auth_code_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": str(cnp_txn_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-1091",
                    "CARD TYPE": "VISA",
                    "AUTH CODE": str(auth_code_2).strip(),

                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
def test_common_100_103_337():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Cards_Enabled_Success_Transaction_via_UPI_via_AXIS_DIRECT
    Sub Feature Description: After entering the card details, select UPI and continue the success payment with UPI via AXIS_DIRECT
    TC naming code description: 100: Payment Method, 103: RemotePay, 337: TC337
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code = '{org_code}' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from upi_merchant_config table :{result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            customer_mobile = '12345' + str(random.randint(10000, 12000))
            logger.debug(f"customer_mobile : {customer_mobile}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
                "customerMobileNumber": customer_mobile
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 1091")
            remote_pay_txn.enterCreditCardExpiryMonth("3")
            remote_pay_txn.enterCreditCardExpiryYear("2048")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnRemotePayUPI()
            remote_pay_txn.clickOnRemotePayLaunchUPI()
            remote_pay_txn.clickOnRemotePayCancelUPI()
            remote_pay_txn.clickOnRemotePayProceed()

            query = f"select * from txn where org_code = '{org_code}' And external_ref = '{order_id}'"
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table : {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table : {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table : {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table : {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table : {rrn}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table : {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table : {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table : {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table : {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table : {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table : {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table : {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table : {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table : {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table : {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table : {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table : {tid_txn}")
            bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the txn table : {bank_code}")
            payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from the txn table : {payment_gateway}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from upi_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from upi_txn table :{result}")
            upi_status_db = result["status"].values[0]
            logger.debug(f"Fetching status from the upi_txn table : {upi_status_db}")
            upi_txn_type_db = result["txn_type"].values[0]
            logger.debug(f"Fetching txn_type from the upi_txn table : {upi_txn_type_db}")
            upi_bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the upi_txn table : {upi_bank_code_db}")
            upi_mc_id_db = result["upi_mc_id"].values[0]
            logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

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
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "AUTHORIZED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "SETTLED",
                    "txn_id": txn_id,
                    "rrn": str(rrn),
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT SUCCESSFUL",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the txn : {txn_id}, {app_settle_status}")
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn}")
                app_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the txn : {txn_id}, {app_customer_name}")
                app_payer_name = txn_history_page.fetch_payer_name_text()
                logger.info(f"Fetching payer_name from txn history for the txn : {txn_id}, {app_payer_name}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the txn : {txn_id}, {app_customer_mobile}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "txn_id": app_txn_id,
                    "rrn": str(app_rrn),
                    "customer_name": app_customer_name,
                    "settle_status": app_settle_status,
                    "payer_name": app_payer_name,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile
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
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "SETTLED",
                    "rrn": str(rrn),
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code_txn,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": customer_name_txn,
                    "customer_mobile": customer_mobile
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS for original txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                api_amount = response.get('amount')
                logger.debug(f"From response fetch amount : {api_amount}")
                api_payment_mode = response.get('paymentMode')
                logger.debug(f"From response fetch payment_mode : {api_payment_mode}")
                api_payment_status = response.get('status')
                logger.debug(f"From response fetch payment_status : {api_payment_status}")
                api_payment_state = response.get('states')[0]
                logger.debug(f"From response fetch payment_state : {api_payment_state}")
                api_mid = response.get('mid')
                logger.debug(f"From response fetch mid : {api_mid}")
                api_tid = response.get('tid')
                logger.debug(f"From response fetch tid : {api_tid}")
                api_acquirer_code = response.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code : {api_acquirer_code}")
                api_settle_status = response.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status : {api_settle_status}")
                api_rrn = response.get('rrNumber')
                logger.debug(f"From response fetch rrn : {api_rrn}")
                api_issuer_code = response.get('issuerCode')
                logger.debug(f"From response fetch issuer_code : {api_issuer_code}")
                api_txn_type = response.get('txnType')
                logger.debug(f"From response fetch txn_type : {api_txn_type}")
                api_org_code = response.get('orgCode')
                logger.debug(f"From response fetch org_code : {api_org_code}")
                api_date_time = response.get('createdTime')
                logger.debug(f"From response fetch date_time : {api_date_time}")
                api_merchant_name = response.get('merchantName')
                logger.debug(f"From response fetch merchant_name : {api_merchant_name}")
                api_ext_ref_number = response.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number : {api_ext_ref_number}")
                api_customer_name = response.get('customerName')
                logger.debug(f"From response fetch customer_name : {api_customer_name}")
                api_payer_name = response.get('payerName')
                logger.debug(f"From response fetch payer_name : {api_payer_name}")
                api_name_on_card = response.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card : {api_name_on_card}")
                api_customer_mobile = response.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile : {api_customer_mobile}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "rrn": str(api_rrn),
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "upi_txn_status": "AUTHORIZED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "bank_code": "AXIS",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",
                    "customer_mobile": customer_mobile,
                    "pmt_gateway": "AXIS"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "upi_txn_status": upi_status_db,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "bank_code": bank_code,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,
                    "customer_mobile": customer_mobile_txn,
                    "pmt_gateway": payment_gateway
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
                    "pmt_status": "AUTHORIZED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "rrn": str(rrn)
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[0]['Date & Time']
                logger.info(f"Fetching date_time from portal txn history for the order_id : {order_id}, {portal_date_time}")
                portal_txn_id = transaction_details[0]['Transaction ID']
                logger.info(f"Fetching txn_id from portal txn history for the order_id : {order_id}, {portal_txn_id}")
                portal_total_amount = transaction_details[0]['Total Amount']
                logger.info(f"Fetching total_amount from portal txn history for the order_id : {order_id}, {portal_total_amount}")
                portal_rrn = transaction_details[0]['RR Number']
                logger.info(f"Fetching rrn from portal txn history for the order_id : {order_id}, {portal_rrn}")
                portal_txn_type = transaction_details[0]['Type']
                logger.info(f"Fetching txn_type from portal txn history for the order_id : {order_id}, {portal_txn_type}")
                portal_txn_status = transaction_details[0]['Status']
                logger.info(f"Fetching txn_status from portal txn history for the order_id : {order_id}, {portal_txn_status}")
                portal_user = transaction_details[0]['Username']
                logger.info(f"Fetching username from portal txn history for the order_id : {order_id}, {portal_user}")

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "rrn": portal_rrn
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
                expected_charge_slip_values = {
                    "PAID BY:": "UPI",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": str(rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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
def test_common_100_103_338():
    """
    Sub Feature Code: UI_Common_PM_RP_Payment_Modes_UPI_Cards_Enabled_Success_Transaction_via_Card_via_AXIS_DIRECT
    Sub Feature Description: Select the UPI payment mode, cancel it and then initiate a card payment to perform successful payment via AXIS_DIRECT
    TC naming code description: 100: Payment Method, 103: RemotePay, 338: TC338
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testCaseID=testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username = {app_username}"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query=query)
        logger.debug(f"Fetching result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from the org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='AXIS_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='CNP')

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from upi_merchant_config where org_code = '{org_code}' AND status = 'ACTIVE' AND bank_code = 'AXIS_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from upi_merchant_config table :{result}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"Fetching id from the upi_merchant_config table : {upi_mc_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-----------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1, 49)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            customer_mobile = '12345' + str(random.randint(10000, 12000))
            logger.debug(f"customer_mobile : {customer_mobile}")

            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "externalRefNumber": order_id,
                "amount": amount,
                "username": app_username,
                "password": app_password,
                "customerMobileNumber": customer_mobile
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            ui_browser = TestSuiteSetup.initialize_ui_browser()
            payment_link_url = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_browser.goto(payment_link_url)
            remote_pay_txn = RemotePayTxnPage(ui_browser)
            remote_pay_txn.clickOnRemotePayUPI()
            remote_pay_txn.clickOnRemotePayLaunchUPI()
            remote_pay_txn.clickOnRemotePayCancelUPI()
            remote_pay_txn.clickOnRemotePayProceed()

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

            ui_browser.goto(payment_link_url)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 1091")
            remote_pay_txn.enterCreditCardExpiryMonth("3")
            remote_pay_txn.enterCreditCardExpiryYear("2048")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()
            remote_pay_txn.switch_to_iframe()

            success_message = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your expected success message is:  {success_message}")
            logger.info(f"Your expected message is:  {expected_message}")
            if success_message == expected_message:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                    f"desc limit 1 "
            logger.debug(f"Query to fetch txn details from the txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            txn_id_2 = result['id'].values[0]
            logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")

            query = f"select * from txn where id='{txn_id}'"
            logger.debug(f"Query to fetch txn details from the txn table for failed txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for failed txn: {created_time}")
            acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for failed txn: {acquirer_code}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for failed txn: {auth_code}")
            customer_name_txn = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for failed txn: {customer_name_txn}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for failed txn: {payer_name}")
            settle_status = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for failed txn: {settle_status}")
            pmt_status = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for failed txn: {pmt_status}")
            payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for failed txn: {payment_mode}")
            issuer_code_txn = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for failed txn: {issuer_code_txn}")
            pmt_state = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for failed txn: {pmt_state}")
            amount_txn = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for failed txn: {amount_txn}")
            merchant_name = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for failed txn: {merchant_name}")
            order_id_txn = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for failed txn: {order_id_txn}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for failed txn: {org_code_txn}")
            customer_mobile_txn = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for failed txn: {customer_mobile_txn}")
            mid_txn = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for failed txn: {mid_txn}")
            tid_txn = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for failed txn: {tid_txn}")
            bank_code = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the txn table for failed txn: {bank_code}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for failed txn: {rrn}")

            query = f"select * from txn where id='{txn_id_2}'"
            logger.debug(f"Query to fetch txn details from the txn table for success txn: {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from txn table :{result}")
            created_time_2 = result['created_time'].values[0]
            logger.debug(f"Fetching created_time from the txn table for success txn: {created_time_2}")
            acquirer_code_2 = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from the txn table for success txn: {acquirer_code_2}")
            auth_code_2 = result['auth_code'].values[0]
            logger.debug(f"Fetching auth_code from the txn table for success txn: {auth_code_2}")
            customer_name_txn_2 = result['customer_name'].values[0]
            logger.debug(f"Fetching customer_name from the txn table for success txn: {customer_name_txn_2}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"Fetching payer_name from the txn table for success txn: {payer_name_2}")
            settle_status_2 = result['settlement_status'].values[0]
            logger.debug(f"Fetching settlement_status from the txn table for success txn: {settle_status_2}")
            pmt_status_2 = result['status'].values[0]
            logger.debug(f"Fetching status from the txn table for success txn: {pmt_status_2}")
            payment_mode_2 = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from the txn table for success txn: {payment_mode_2}")
            issuer_code_txn_2 = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from the txn table for success txn: {issuer_code_txn_2}")
            pmt_state_2 = result['state'].values[0]
            logger.debug(f"Fetching state from the txn table for success txn: {pmt_state_2}")
            amount_txn_2 = result['amount'].values[0]
            logger.debug(f"Fetching amount from the txn table for success txn: {amount_txn_2}")
            merchant_name_2 = result['merchant_name'].values[0]
            logger.debug(f"Fetching merchant_name from the txn table for success txn: {merchant_name_2}")
            order_id_txn_2 = result['external_ref'].values[0]
            logger.debug(f"Fetching order_id from the txn table for success txn: {order_id_txn_2}")
            org_code_txn_2 = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from the txn table for success txn: {org_code_txn_2}")
            customer_mobile_txn_2 = result['customer_mobile'].values[0]
            logger.debug(f"Fetching customer_mobile from the txn table for success txn: {customer_mobile_txn_2}")
            mid_txn_2 = result['mid'].values[0]
            logger.debug(f"Fetching mid from the txn table for success txn: {mid_txn_2}")
            tid_txn_2 = result['tid'].values[0]
            logger.debug(f"Fetching tid from the txn table for success txn: {tid_txn_2}")
            rrn_2 = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from the txn table for success txn: {rrn_2}")

            query = f"select * from payment_intent where id = '{payment_intent_id}'"
            logger.debug(f"Query to fetch data from the payment_intent table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from payment_intent table :{result}")
            payment_intent_status = result["status"].values[0]
            logger.debug(f"Fetching status from the payment_intent table : {payment_intent_status}")

            query = f"select * from upi_txn where txn_id = '{txn_id}'"
            logger.debug(f"Query to fetch data from upi_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result from upi_txn table :{result}")
            upi_status_db = result["status"].values[0]
            logger.debug(f"Fetching status from the upi_txn table : {upi_status_db}")
            upi_txn_type_db = result["txn_type"].values[0]
            logger.debug(f"Fetching txn_type from the upi_txn table : {upi_txn_type_db}")
            upi_bank_code_db = result["bank_code"].values[0]
            logger.debug(f"Fetching bank_code from the upi_txn table : {upi_bank_code_db}")
            upi_mc_id_db = result["upi_mc_id"].values[0]
            logger.debug(f"Fetching upi_mc_id from the upi_txn table : {upi_mc_id_db}")

            query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnp_txn table : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Fetching result for cnp_txn table : {result} ")
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Fetching rr_number from cnp_txn table : {cnp_txn_rrn}")
            cnp_txn_payment_option = result['payment_option'].values[0]
            logger.debug(f"Fetching payment_option from cnp_txn table : {cnp_txn_payment_option}")
            cnp_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnp_txn table : {cnp_txn_payment_flow}")
            cnp_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnp_txn table : {cnp_txn_payment_status}")
            cnp_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnp_txn table : {cnp_txn_type}")
            cnp_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnp_txn table : {cnp_txn_payment_mode}")
            cnp_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnp_txn table : {cnp_txn_payment_state}")
            cnp_txn_payment_card_bin = result['payment_card_bin'].values[0]
            logger.debug(f"Fetching payment_card_bin from cnp_txn table : {cnp_txn_payment_card_bin}")
            cnp_txn_payment_card_brand = result['payment_card_brand'].values[0]
            logger.debug(f"Fetching payment_card_brand from cnp_txn table : {cnp_txn_payment_card_brand}")
            cnp_txn_payment_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Fetching payment_card_type from cnp_txn table : {cnp_txn_payment_card_type}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Fetching acquirer_code from cnp_txn table : {cnp_txn_acquirer_code}")
            cnp_txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Fetching issuer_code from cnp_txn table : {cnp_txn_issuer_code}")
            cnp_txn_card_last_four_digit = result['card_last_four_digit'].values[0]
            logger.debug(f"Fetching card_last_four_digit from cnp_txn table : {cnp_txn_card_last_four_digit}")
            cnp_txn_org_code = result['org_code'].values[0]
            logger.debug(f"Fetching org_code from cnp_txn table : {cnp_txn_org_code}")

            query = f"select * from cnpware_txn where txn_id = '{txn_id_2}'"
            logger.debug(f"Query to fetch data from the cnpware_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            logger.debug(f"Fetching result for cnpware_txn table : {result} ")
            cnpware_txn_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Fetching payment_flow from cnpware_txn table : {cnpware_txn_payment_flow}")
            cnpware_txn_payment_status = result['payment_status'].values[0]
            logger.debug(f"Fetching payment_status from cnpware_txn table : {cnpware_txn_payment_status}")
            cnpware_txn_type = result['txn_type'].values[0]
            logger.debug(f"Fetching txn_type from cnpware_txn table : {cnpware_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Fetching payment_mode from cnpware_txn table : {cnpware_txn_payment_mode}")
            cnpware_txn_payment_state = result['state'].values[0]
            logger.debug(f"Fetching state from cnpware_txn table : {cnpware_txn_payment_state}")
            cnpware_txn_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Fetching payment_gateway from cnpware_txn table : {cnpware_txn_payment_gateway}")

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
                date_and_time_2 = date_time_converter.to_app_format(created_time_2)
                expected_app_values = {
                    "pmt_mode": "UPI",
                    "pmt_status": "FAILED",
                    "txn_amt": "{:,.2f}".format(amount),
                    "settle_status": "FAILED",
                    "txn_id": txn_id,
                    "order_id": order_id,
                    "payment_msg": "PAYMENT FAILED",
                    "date": date_and_time,
                    "customer_mobile": customer_mobile,
                    "pmt_mode_2": "PAY LINK",
                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "settle_status_2": "SETTLED",
                    "txn_id_2": txn_id_2,
                    "rrn_2": str(cnp_txn_rrn),
                    "order_id_2": order_id,
                    "payment_msg_2": "PAYMENT SUCCESSFUL",
                    "date_2": date_and_time_2,
                    "customer_mobile_2": customer_mobile,
                    "card": "*1091",
                    "auth_code": auth_code_2,
                    "customer_name": customer_name_txn_2,
                }
                logger.debug(f"expectedAppValues: {expected_app_values}")

                app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
                login_page = LoginPage(driver=app_driver)
                login_page.perform_login(username=app_username, password=app_password)
                logger.info(f"Logging in the MPOSX application using username : {app_username}")
                home_page = HomePage(driver=app_driver)
                home_page.check_home_page_logo()
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                logger.info(f"App homepage loaded successfully")
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the failed txn : {txn_id}, {app_amount}")
                app_order_id = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the failed txn : {txn_id}, {app_order_id}")
                app_payment_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the failed txn : {txn_id}, {app_payment_msg}")
                app_payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the failed txn : {txn_id}, {app_payment_mode}")
                app_payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the failed txn : {txn_id}, {app_payment_status}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the failed txn : {txn_id}, {app_txn_id}")
                app_date_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the failed txn : {txn_id}, {app_date_time}")
                app_settle_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the failed txn : {txn_id}, {app_settle_status}")
                app_customer_mobile = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the failed txn : {txn_id}, {app_customer_mobile}")

                txn_history_page.click_back_Btn_transaction_details()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id_2)
                app_amount_2 = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the success txn : {txn_id}, {app_amount_2}")
                app_order_id_2 = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching order_id from txn history for the success txn : {txn_id}, {app_order_id_2}")
                app_payment_msg_2 = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"Fetching payment_msg from txn history for the success txn : {txn_id}, {app_payment_msg_2}")
                app_payment_mode_2 = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment_mode from txn history for the success txn : {txn_id}, {app_payment_mode_2}")
                app_payment_status_2 = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching payment_status from txn history for the success txn : {txn_id}, {app_payment_status_2}")
                app_txn_id_2 = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the success txn : {txn_id}, {app_txn_id_2}")
                app_date_time_2 = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date_time from txn history for the success txn : {txn_id}, {app_date_time_2}")
                app_settle_status_2 = txn_history_page.fetch_settlement_status_text()
                logger.info(f"Fetching settlement_status from txn history for the success txn : {txn_id}, {app_settle_status_2}")
                app_rrn_2 = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching rrn from txn history for the success txn : {txn_id}, {app_rrn_2}")
                app_auth_code_2 = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching auth_code from txn history for the success txn : {txn_id}, {app_auth_code_2}")
                app_card_2 = txn_history_page.fetch_card_text()
                logger.info(f"Fetching card from txn history for the success txn : {txn_id}, {app_card_2}")
                app_customer_mobile_2 = txn_history_page.fetch_customer_mobile_text()
                logger.info(f"Fetching customer_mobile from txn history for the success txn : {txn_id}, {app_customer_mobile_2}")
                app_customer_name_2 = txn_history_page.fetch_customer_name_text()
                logger.info(f"Fetching customer_name from txn history for the success txn : {txn_id}, {app_customer_name_2}")

                actual_app_values = {
                    "pmt_mode": app_payment_mode,
                    "pmt_status": app_payment_status.split(':')[1],
                    "txn_amt": app_amount.split(' ')[1],
                    "settle_status": app_settle_status,
                    "txn_id": app_txn_id,
                    "order_id": app_order_id,
                    "payment_msg": app_payment_msg,
                    "date": app_date_time,
                    "customer_mobile": app_customer_mobile,
                    "pmt_mode_2": app_payment_mode_2,
                    "pmt_status_2": app_payment_status_2.split(':')[1],
                    "txn_amt_2": app_amount_2.split(' ')[1],
                    "settle_status_2": app_settle_status_2,
                    "txn_id_2": app_txn_id_2,
                    "rrn_2": str(app_rrn_2),
                    "order_id_2": app_order_id_2,
                    "payment_msg_2": app_payment_msg_2,
                    "date_2": app_date_time_2,
                    "customer_mobile_2": app_customer_mobile_2,
                    "card": app_card_2,
                    "auth_code": app_auth_code_2,
                    "customer_name": app_customer_name_2
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
                    "pmt_status": "FAILED",
                    "txn_amt": float(amount),
                    "pmt_mode": "UPI",
                    "pmt_state": "FAILED",
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "txn_type": "REMOTE_PAY",
                    "mid": mid_txn,
                    "tid": tid_txn,
                    "org_code": org_code_txn,
                    "date": date,
                    "ext_ref_number": order_id,
                    "merchant_name": merchant_name,
                    "customer_name": customer_name_txn,
                    "payer_name": payer_name,
                    "name_on_card": customer_name_txn,
                    "customer_mobile": customer_mobile,

                    "pmt_status_2": "AUTHORIZED",
                    "txn_amt_2": float(amount),
                    "pmt_mode_2": "CNP",
                    "pmt_state_2": "SETTLED",
                    "rrn_2": str(cnp_txn_rrn),
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "txn_type_2": "REMOTE_PAY",
                    "mid_2": mid_txn_2,
                    "tid_2": tid_txn_2,
                    "org_code_2": org_code_txn_2,
                    "date_2": date_2,
                    "ext_ref_number_2": order_id,
                    "merchant_name_2": merchant_name_2,
                    "customer_name_2": customer_name_txn_2,
                    "payer_name_2": payer_name_2,
                    "name_on_card_2": payer_name_2,
                    "customer_mobile_2": customer_mobile
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(api_name='txnlist', request_body={
                    "username": app_username,
                    "password": app_password
                })
                logger.debug(f"API DETAILS txn : {api_details}")
                response = APIProcessor.send_request(api_details=api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response_1 = [x for x in response["txns"] if x["txnId"] == txn_id][0]
                logger.debug(f"Response after filtering data of failed txn is : {response}")
                api_amount = response_1.get('amount')
                logger.debug(f"From response fetch amount for failed txn : {api_amount}")
                api_payment_mode = response_1.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for failed txn : {api_payment_mode}")
                api_payment_status = response_1.get('status')
                logger.debug(f"From response fetch payment_status for failed txn : {api_payment_status}")
                api_payment_state = response_1.get('states')[0]
                logger.debug(f"From response fetch payment_state for failed txn : {api_payment_state}")
                api_mid = response_1.get('mid')
                logger.debug(f"From response fetch mid for failed txn : {api_mid}")
                api_tid = response_1.get('tid')
                logger.debug(f"From response fetch tid for failed txn : {api_tid}")
                api_acquirer_code = response_1.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for failed txn : {api_acquirer_code}")
                api_settle_status = response_1.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for failed txn : {api_settle_status}")
                api_issuer_code = response_1.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for failed txn : {api_issuer_code}")
                api_txn_type = response_1.get('txnType')
                logger.debug(f"From response fetch txn_type for failed txn : {api_txn_type}")
                api_org_code = response_1.get('orgCode')
                logger.debug(f"From response fetch org_code for failed txn : {api_org_code}")
                api_date_time = response_1.get('createdTime')
                logger.debug(f"From response fetch date_time for failed txn : {api_date_time}")
                api_merchant_name = response_1.get('merchantName')
                logger.debug(f"From response fetch merchant_name for failed txn : {api_merchant_name}")
                api_ext_ref_number = response_1.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for failed txn : {api_ext_ref_number}")
                api_customer_name = response_1.get('customerName')
                logger.debug(f"From response fetch customer_name for failed txn : {api_customer_name}")
                api_payer_name = response_1.get('payerName')
                logger.debug(f"From response fetch payer_name for failed txn : {api_payer_name}")
                api_name_on_card = response_1.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for failed txn : {api_name_on_card}")
                api_customer_mobile = response_1.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for failed txn : {api_customer_mobile}")

                response_2 = [x for x in response["txns"] if x["txnId"] == txn_id_2][0]
                logger.debug(f"Response after filtering data of success txn is : {response}")
                api_amount_2 = response_2.get('amount')
                logger.debug(f"From response fetch amount for success txn : {api_amount_2}")
                api_payment_mode_2 = response_2.get('paymentMode')
                logger.debug(f"From response fetch payment_mode for success txn : {api_payment_mode_2}")
                api_payment_status_2 = response_2.get('status')
                logger.debug(f"From response fetch payment_status for success txn : {api_payment_status_2}")
                api_payment_state_2 = response_2.get('states')[0]
                logger.debug(f"From response fetch payment_state for success txn : {api_payment_state_2}")
                api_mid_2 = response_2.get('mid')
                logger.debug(f"From response fetch mid for success txn : {api_mid_2}")
                api_tid_2 = response_2.get('tid')
                logger.debug(f"From response fetch tid for success txn : {api_tid_2}")
                api_acquirer_code_2 = response_2.get('acquirerCode')
                logger.debug(f"From response fetch acquirer_code for success txn : {api_acquirer_code_2}")
                api_settle_status_2 = response_2.get('settlementStatus')
                logger.debug(f"From response fetch settlement_status for success txn : {api_settle_status_2}")
                api_rrn_2 = response_2.get('rrNumber')
                logger.debug(f"From response fetch rrn for success txn : {api_rrn_2}")
                api_issuer_code_2 = response_2.get('issuerCode')
                logger.debug(f"From response fetch issuer_code for success txn : {api_issuer_code_2}")
                api_txn_type_2 = response_2.get('txnType')
                logger.debug(f"From response fetch txn_type for success txn : {api_txn_type_2}")
                api_org_code_2 = response_2.get('orgCode')
                logger.debug(f"From response fetch org_code for success txn : {api_org_code_2}")
                api_date_time_2 = response_2.get('createdTime')
                logger.debug(f"From response fetch date_time for success txn : {api_date_time_2}")
                api_merchant_name_2 = response_2.get('merchantName')
                logger.debug(f"From response fetch merchant_name for success txn : {api_merchant_name_2}")
                api_ext_ref_number_2 = response_2.get('externalRefNumber')
                logger.debug(f"From response fetch external_ref_number for success txn : {api_ext_ref_number_2}")
                api_customer_name_2 = response_2.get('customerName')
                logger.debug(f"From response fetch customer_name for success txn : {api_customer_name_2}")
                api_payer_name_2 = response_2.get('payerName')
                logger.debug(f"From response fetch payer_name for success txn : {api_payer_name_2}")
                api_name_on_card_2 = response_2.get('nameOnCard')
                logger.debug(f"From response fetch name_on_card for success txn : {api_name_on_card_2}")
                api_customer_mobile_2 = response_2.get('customerMobile')
                logger.debug(f"From response fetch customer_mobile for success txn : {api_customer_mobile_2}")

                actual_api_values = {
                    "pmt_status": api_payment_status,
                    "txn_amt": api_amount,
                    "pmt_mode": api_payment_mode,
                    "pmt_state": api_payment_state,
                    "settle_status": api_settle_status,
                    "acquirer_code": api_acquirer_code,
                    "issuer_code": api_issuer_code,
                    "txn_type": api_txn_type,
                    "mid": api_mid,
                    "tid": api_tid,
                    "org_code": api_org_code,
                    "date": date_time_converter.from_api_to_datetime_format(api_date_time),
                    "ext_ref_number": api_ext_ref_number,
                    "merchant_name": api_merchant_name,
                    "customer_name": api_customer_name,
                    "payer_name": api_payer_name,
                    "name_on_card": api_name_on_card,
                    "customer_mobile": api_customer_mobile,

                    "pmt_status_2": api_payment_status_2,
                    "txn_amt_2": api_amount_2,
                    "pmt_mode_2": api_payment_mode_2,
                    "pmt_state_2": api_payment_state_2,
                    "rrn_2": str(api_rrn_2),
                    "settle_status_2": api_settle_status_2,
                    "acquirer_code_2": api_acquirer_code_2,
                    "issuer_code_2": api_issuer_code_2,
                    "txn_type_2": api_txn_type_2,
                    "mid_2": api_mid_2,
                    "tid_2": api_tid_2,
                    "org_code_2": api_org_code_2,
                    "date_2": date_time_converter.from_api_to_datetime_format(api_date_time_2),
                    "ext_ref_number_2": api_ext_ref_number_2,
                    "merchant_name_2": api_merchant_name_2,
                    "customer_name_2": api_customer_name_2,
                    "payer_name_2": api_payer_name_2,
                    "name_on_card_2": api_name_on_card_2,
                    "customer_mobile_2": api_customer_mobile_2
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
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "FAILED",
                    "acquirer_code": "AXIS",
                    "issuer_code": "AXIS",
                    "bank_code": "AXIS",
                    "customer_mobile": customer_mobile,
                    "org_code": org_code,
                    "upi_txn_status": "FAILED",
                    "upi_txn_type": "REMOTE_PAY_UPI_INTENT",
                    "upi_bank_code": "AXIS_DIRECT",
                    "upi_mc_id": upi_mc_id,
                    "pmt_intent_status": "COMPLETED",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "acquirer_code_2": "HDFC",
                    "issuer_code_2": "HDFC",
                    "customer_mobile_2": customer_mobile,
                    "org_code_2": org_code,

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_COMPLETED",
                    "cnp_pmt_state": "SETTLED",
                    "cnp_pmt_card_bin": "400000",
                    "cnp_pmt_card_brand": "VISA",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_acquirer_code": "HDFC",
                    "cnp_issuer_code": issuer_code_txn_2,
                    "cnp_card_last_four_digit": "1091",
                    "cnp_org_code": org_code,
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",

                    "cnpware_pmt_status": "PAYMENT_COMPLETED",
                    "cnpware_pmt_state": "SETTLED",
                    "cnpware_pmt_mode": "CNP",
                    "cnpware_pmt_flow": "REMOTEPAY",
                    "cnpware_pmt_gateway": "CYBERSOURCE",
                    "cnpware_txn_type": "REMOTE_PAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "acquirer_code": acquirer_code,
                    "issuer_code": issuer_code_txn,
                    "bank_code": bank_code,
                    "customer_mobile": customer_mobile_txn,
                    "org_code": org_code_txn,
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type": upi_txn_type_db,
                    "upi_bank_code": upi_bank_code_db,
                    "upi_mc_id": upi_mc_id_db,
                    "pmt_intent_status": payment_intent_status,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "acquirer_code_2": acquirer_code_2,
                    "issuer_code_2": issuer_code_txn_2,
                    "customer_mobile_2": customer_mobile_txn_2,
                    "org_code_2": org_code_txn_2,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_bin": cnp_txn_payment_card_bin,
                    "cnp_pmt_card_brand": cnp_txn_payment_card_brand,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_acquirer_code": cnp_txn_acquirer_code,
                    "cnp_issuer_code": cnp_txn_issuer_code,
                    "cnp_card_last_four_digit": cnp_txn_card_last_four_digit,
                    "cnp_org_code": cnp_txn_org_code,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,

                    "cnpware_pmt_status": cnpware_txn_payment_status,
                    "cnpware_pmt_state": cnpware_txn_payment_state,
                    "cnpware_pmt_mode": cnpware_txn_payment_mode,
                    "cnpware_pmt_flow": cnpware_txn_payment_flow,
                    "cnpware_pmt_gateway": cnpware_txn_payment_gateway,
                    "cnpware_txn_type": cnpware_txn_type
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
                date_and_time_portal_2 = date_time_converter.to_portal_format(created_time_2)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_status": "FAILED",
                    "pmt_type": "UPI",
                    "txn_amt": "{:,.2f}".format(amount),
                    "username": app_username,
                    "txn_id": txn_id,
                    "customer_mobile": customer_mobile,
                    "rrn": "-" if rrn is None else rrn,
                    "auth_code": "-" if auth_code is None else auth_code,

                    "date_time_2": date_and_time_portal_2,
                    "pmt_status_2": "AUTHORIZED",
                    "pmt_type_2": "CNP",
                    "txn_amt_2": "{:,.2f}".format(amount),
                    "username_2": app_username,
                    "txn_id_2": txn_id_2,
                    "customer_mobile_2": customer_mobile,
                    "rrn_2": "-" if rrn_2 is None else rrn_2,
                    "auth_code_2": auth_code_2
                }
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(app_un=app_username, app_pw=app_password,
                                                                         order_id=order_id)
                portal_date_time = transaction_details[1]['Date & Time']
                portal_txn_id = transaction_details[1]['Transaction ID']
                portal_total_amount = transaction_details[1]['Total Amount']
                portal_txn_type = transaction_details[1]['Type']
                portal_txn_status = transaction_details[1]['Status']
                portal_user = transaction_details[1]['Username']
                portal_customer_mobile = transaction_details[1]['Mobile No.']
                portal_rrn = transaction_details[1]['RR Number']
                portal_auth_code = transaction_details[1]['Auth Code']

                portal_date_time_2 = transaction_details[0]['Date & Time']
                portal_txn_id_2 = transaction_details[0]['Transaction ID']
                portal_total_amount_2 = transaction_details[0]['Total Amount']
                portal_auth_code_2 = transaction_details[0]['Auth Code']
                portal_txn_type_2 = transaction_details[0]['Type']
                portal_txn_status_2 = transaction_details[0]['Status']
                portal_user_2 = transaction_details[0]['Username']
                portal_customer_mobile_2 = transaction_details[1]['Mobile No.']
                portal_rrn_2 = transaction_details[0]['RR Number']

                actual_portal_values = {
                    "date_time": portal_date_time,
                    "pmt_status": portal_txn_status,
                    "pmt_type": portal_txn_type,
                    "txn_amt": portal_total_amount.split(' ')[1],
                    "username": portal_user,
                    "txn_id": portal_txn_id,
                    "customer_mobile": portal_customer_mobile,
                    "rrn": portal_rrn,
                    "auth_code": portal_auth_code,

                    "date_time_2": portal_date_time_2,
                    "pmt_status_2": portal_txn_status_2,
                    "pmt_type_2": portal_txn_type_2,
                    "txn_amt_2": portal_total_amount_2.split(' ')[1],
                    "username_2": portal_user_2,
                    "txn_id_2": portal_txn_id_2,
                    "customer_mobile_2": portal_customer_mobile_2,
                    "rrn_2": portal_rrn_2,
                    "auth_code_2": portal_auth_code_2
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
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_time_2)
                expected_charge_slip_values = {
                    "payment_option": "SALE",
                    "merchant_ref_no": 'Ref # ' + str(order_id),
                    "RRN": str(cnp_txn_rrn),
                    "BASE AMOUNT:": "Rs." + "{:,.2f}".format(amount),
                    "date": txn_date,
                    "time": txn_time,
                    "CARD": f"XXXX-XXXX-XXXX-1091",
                    "CARD TYPE": "VISA",
                    "AUTH CODE": str(auth_code_2).strip(),
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(txn_id=txn_id_2, credentials={
                    "username": app_username,
                    "password": app_password
                }, expected_details=expected_charge_slip_values)
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