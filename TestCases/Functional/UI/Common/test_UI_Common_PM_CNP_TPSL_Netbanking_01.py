import random
import shutil
import sys
import time
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
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
def test_common_100_103_038():
    """
    Sub Feature Code: UI_Common_PM_CNP_NetBanking_Successful_TPSL
    Sub Feature Description: Verification successful netbanking txn for TPSL pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    038: TC038
    """
    expectedMessage = "Your payment is successfully completed! You may close the browser now."
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='TPSL', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='TPSL')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            paymentLinkUrl = response.get('paymentLink')
            payment_intent_id = response.get('paymentIntentId')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            ui_driver.get(paymentLinkUrl)
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.remote_pay_netbanking()
            remote_pay_txn.remote_pay_click_and_expand_netbanking()
            remote_pay_txn.remote_pay_select_netbanking()
            remote_pay_txn.remote_pay_proceed_netbanking()
            remote_pay_txn.remote_pay_netbanking_customerId("test")
            remote_pay_txn.remote_pay_netbanking_customerpwd("test")
            remote_pay_txn.remote_pay_netbanking_proceed()
            remote_pay_txn.remote_pay_netbanking_proceed()

            successMessage = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your expected success message is:  {successMessage}")
            logger.info(f"Your expiryMessage is:  {expectedMessage}")
            if successMessage == expectedMessage:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, cnpware_txn_payment_mode : {cnpware_txn_payment_mode}")
            cnpware_txn_state = result['state'].values[0]
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "AUTHORIZED",
                                     "txn_amt": str(amount),
                                     "txn_id": txn_id,
                                     "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT SUCCESSFUL",
                                     "customer_name": txn_customer_name,
                                     "settle_status": "SETTLED",
                                     "auth_code": txn_auth_code,
                                     "date": date_and_time}

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
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
                payment_rrn = txn_history_page.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_orderId = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_orderId}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txn_history_page.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],  # santo's implementation needs to be added
                                   "txn_id": app_txn_id, "rrn": payment_rrn,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "auth_code": payment_auth_code,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of App Validation---------------------------------------
            # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "AUTHORIZED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": cnp_txn_state,
                                     "acquirer_code": cnp_txn_acquirer_code,
                                     "settle_status": txn_settle_status,
                                     "rrn": cnp_txn_rrn,
                                     "txn_type": cnpware_txn_txn_type,
                                     "org_code": org_code,
                                     "date": date_and_time,
                                     # "issuer_code"="" NULL
                                     # "nonce_status" NA
                                     # qr_code_uri NA
                                     # "issuer_code": txn_issuer_code, #Was not getting in the reponse
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        rrNumber_api = elements["rrNumber"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   "rrn": rrNumber_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of API Validation---------------------------------------
            # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # Add other tables for validation as well.
                expectedDBValues = {"pmt_status": "AUTHORIZED",
                                    "pmt_state": "SETTLED",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "SETTLED",
                                    "pmt_gateway": "TPSL",
                                    "payment_mode": "PAY LINK",
                                    "auth_code": txn_auth_code,
                                    # "acquirer_code":HDFC
                                    # "bank_name" NA
                                    # "payer_name" NA
                                    # "mid" NA
                                    # "tid" NA
                                    "cnpware_rrn": cnp_txn_rrn,
                                    "cnpware_txn_id": app_txn_id,
                                    "cnpware_txn_amt": amount,
                                    "cnpware_pmt_mode": "CNP",
                                    "cnpware_pmt_state": "SETTLED",
                                    # "acquirer_code":
                                    "cnp_pmt_gateway": "TPSL",
                                    "cnpware_pmt_gateway": "TPSL",
                                    "cnpware_pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "COMPLETED"
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                # Handle in the posting datetime method.
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])  # Amount should not be converted to int
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {"pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": txn_amt_db,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "payment_mode": payment_mode,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnpware_rrn": cnp_txn_rrn,
                                  "cnpware_txn_id": app_txn_id,
                                  "cnpware_txn_amt": amount,
                                  "cnpware_pmt_mode": cnpware_txn_payment_mode,
                                  "cnpware_pmt_state": cnpware_txn_state,
                                  "cnpware_pmt_flow":cnpware_payment_flow,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------
            # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                expectedPortalValues = {"pmt_state": "Settled",
                                        "pmt_type": "CNP",
                                        "txn_amt": "Rs." + str(amount) + ".00",
                                        "username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")
                expectedValues = {"Net Banking": "TPSL Bank",
                                  'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': str(cnp_txn_rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                  'date': txn_date,
                                  'time': txn_time,
                                  "AUTH CODE": txn_auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
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
def test_common_100_103_039():
    """
    Sub Feature Code: UI_Common_PM_CNP_NetBanking_Failed_TPSL
    Sub Feature Description: Verification failed netbanking txn for TPSL pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    038: TC038
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='TPSL', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='TPSL')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            paymentLinkUrl = response.get('paymentLink')
            payment_intent_id = response.get('paymentIntentId')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            ui_driver.get(paymentLinkUrl)
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.remote_pay_netbanking()
            remote_pay_txn.remote_pay_click_and_expand_netbanking()
            remote_pay_txn.remote_pay_select_netbanking()
            remote_pay_txn.remote_pay_proceed_netbanking()
            remote_pay_txn.remote_pay_netbanking_customerId("test")
            remote_pay_txn.remote_pay_netbanking_customerpwd("test")
            remote_pay_txn.remote_pay_netbanking_proceed()
            remote_pay_txn.remote_pay_netbanking_cancel()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, cnpware_txn_payment_mode : {cnpware_txn_payment_mode}")
            cnpware_txn_state = result['state'].values[0]
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount),
                                     "txn_id": txn_id,
                                     # "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     "customer_name": txn_customer_name,
                                     "settle_status": "FAILED",
                                     # "auth_code": txn_auth_code,
                                     "date": date_and_time}

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                # Add loggers to each steps.
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                # add prefix as app in variable names.
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                # payment_rrn = txn_history_page.fetch_RRN_text()
                # logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_orderId = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_orderId}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                # payment_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],  # santo's implementation needs to be added
                                   "txn_id": app_txn_id,
                                   # "rrn": payment_rrn,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   # "auth_code": payment_auth_code,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of App Validation---------------------------------------
            # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": "FAILED",
                                     "acquirer_code": cnp_txn_acquirer_code,
                                     "settle_status": "FAILED",
                                     # "rrn": cnp_txn_rrn,
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date_and_time,
                                     # "issuer_code"="" NULL
                                     # "nonce_status" NA
                                     # qr_code_uri NA
                                     # "issuer_code": txn_issuer_code, #Was not getting in the reponse
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        # rrNumber_api = elements["rrNumber"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   # "rrn": rrNumber_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of API Validation---------------------------------------
            # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # Add other tables for validation as well.
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_gateway": "TPSL",
                                    "payment_mode": "PAY LINK",
                                    "auth_code": str(0),
                                    # "acquirer_code":HDFC
                                    # "bank_name" NA
                                    # "payer_name" NA
                                    # "mid" NA
                                    # "tid" NA
                                    "cnpware_rrn": cnp_txn_rrn,
                                    "cnpware_txn_id": app_txn_id,
                                    "cnpware_txn_amt": amount,
                                    "cnpware_pmt_mode": "CNP",
                                    "cnpware_pmt_state": "FAILED",
                                    # "acquirer_code": NA
                                    "cnp_pmt_gateway": "TPSL",
                                    "cnpware_pmt_gateway": "TPSL",
                                    "cnpware_pmt_flow": "REMOTEPAY",
                                    # "pmt_intent_status": "COMPLETED" NA
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                # Handle in the posting datetime method.
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])  # Amount should not be converted to int
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {"pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": txn_amt_db,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "payment_mode": payment_mode,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnpware_rrn": cnp_txn_rrn,
                                  "cnpware_txn_id": app_txn_id,
                                  "cnpware_txn_amt": amount,
                                  "cnpware_pmt_mode": cnpware_txn_payment_mode,
                                  "cnpware_pmt_state": cnpware_txn_state,
                                  "cnpware_pmt_flow":cnpware_payment_flow,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  # "pmt_intent_status": payment_intent_status
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------
            # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                expectedPortalValues = {"pmt_state": "Settled",
                                        "pmt_type": "CNP",
                                        "txn_amt": "Rs." + str(amount) + ".00",
                                        "username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
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
def test_common_100_103_040():
    """
    Sub Feature Code: UI_Common_PM_CNP_NetBanking_Timeout_TPSL
    Sub Feature Description: Verification netbanking txn after timeout for TPSL pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    038: TC038
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='TPSL', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='TPSL')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(1, 10)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            paymentLinkUrl = response.get('paymentLink')
            payment_intent_id = response.get('paymentIntentId')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            ui_driver.get(paymentLinkUrl)
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.remote_pay_netbanking()
            remote_pay_txn.remote_pay_click_and_expand_netbanking()
            remote_pay_txn.remote_pay_select_netbanking()
            remote_pay_txn.remote_pay_proceed_netbanking()
            remote_pay_txn.remote_pay_netbanking_customerId("test")
            remote_pay_txn.remote_pay_netbanking_customerpwd("test")
            remote_pay_txn.remote_pay_netbanking_proceed()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch max Attempts from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"max upi attempt for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"max upi attempt is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Value for max upi attempt is: {org_setting_value} min.")
                time.sleep(3 + (org_setting_value * 60))
            else:
                logger.info(f"Value for Ezetap org is: {org_setting_value} min.")
                time.sleep(3 + (setting_value * 60))

            remote_pay_txn.remote_pay_netbanking_proceed()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_payer_name = result['payer_name'].values[0]
            logger.debug(f"Query result, txn_payer_name : {txn_payer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")

            query = "select * from cnp_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_payment_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, cnpware_txn_payment_mode : {cnpware_txn_payment_mode}")
            cnpware_txn_state = result['state'].values[0]
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount),
                                     "txn_id": txn_id,
                                     # "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     # "auth_code": txn_auth_code,
                                     "date": date_and_time}

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                # Add loggers to each steps.
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                login_page = LoginPage(app_driver)
                login_page.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.check_home_page_logo()
                home_page.wait_for_home_page_load()
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)

                # add prefix as app in variable names.
                txn_history_page.click_on_transaction_by_txn_id(txn_id)
                payment_status = txn_history_page.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txn_history_page.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txn_history_page.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txn_history_page.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                # payment_rrn = txn_history_page.fetch_RRN_text()
                # logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_orderId = txn_history_page.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_orderId}")
                payment_status_msg = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txn_history_page.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                # payment_auth_code = txn_history_page.fetch_auth_code_text()
                # logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txn_history_page.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],  # santo's implementation needs to be added
                                   "txn_id": app_txn_id,
                                   # "rrn": payment_rrn,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   # "auth_code": payment_auth_code,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of App Validation---------------------------------------
            # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": "TIME_OUT_SETTLED",
                                     "acquirer_code": cnp_txn_acquirer_code,
                                     "settle_status": "FAILED",
                                     # "rrn": cnp_txn_rrn,
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date_and_time,
                                     # "issuer_code"="" NULL
                                     # "nonce_status" NA
                                     # qr_code_uri NA
                                     # "issuer_code": txn_issuer_code, #Was not getting in the reponse
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        # rrNumber_api = elements["rrNumber"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   # "rrn": rrNumber_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of API Validation---------------------------------------
            # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "TIME_OUT_SETTLED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_gateway": "TPSL",
                                    "payment_mode": "PAY LINK",
                                    # "auth_code": txn_auth_code,
                                    # "acquirer_code":HDFC
                                    # "bank_name" NA
                                    # "payer_name" NA
                                    # "mid" NA
                                    # "tid" NA
                                    "cnpware_rrn": cnp_txn_rrn,
                                    "cnpware_txn_id": app_txn_id,
                                    "cnpware_txn_amt": amount,
                                    "cnpware_pmt_mode": "CNP",
                                    "cnpware_pmt_state": "SETTLED",
                                    # "acquirer_code": NA
                                    "cnp_pmt_gateway": "TPSL",
                                    "cnpware_pmt_gateway": "TPSL",
                                    "cnpware_pmt_flow": "REMOTEPAY",
                                    # "pmt_intent_status": "COMPLETED" NA
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                # Handle in the posting datetime method.
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])  # Amount should not be converted to int
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {"pmt_status": pmt_status_db,
                                  "pmt_state": pmt_state_db,
                                  "pmt_mode": pmt_mode_db,
                                  "txn_amt": txn_amt_db,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "payment_mode": payment_mode,
                                  # "auth_code": cnp_txn_auth_code,
                                  "cnpware_rrn": cnp_txn_rrn,
                                  "cnpware_txn_id": app_txn_id,
                                  "cnpware_txn_amt": amount,
                                  "cnpware_pmt_mode": cnpware_txn_payment_mode,
                                  "cnpware_pmt_state": cnpware_txn_state,
                                  "cnpware_pmt_flow":cnpware_payment_flow,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  # "pmt_intent_status": payment_intent_status
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of DB Validation---------------------------------------
            # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                expectedPortalValues = {"pmt_state": "Settled",
                                        "pmt_type": "CNP",
                                        "txn_amt": "Rs." + str(amount) + ".00",
                                        "username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")
                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']
                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
            # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
            # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
