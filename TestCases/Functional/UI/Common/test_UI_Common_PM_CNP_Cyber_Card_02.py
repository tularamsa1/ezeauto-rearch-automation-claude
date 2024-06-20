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
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
from PageFactory.portal_remotePayPage import RemotePayTxnPage
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
def test_common_100_103_007():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Success_Cyber
    Sub Feature Description: Verification of a successful debit card txn via CNP link
    Sub Feature Code: UI_Common_PM_CNP_ChargeSlip_Val_debit_Card_Success_Cyber
    Sub Feature Description: Verification of a charge slip validation for debit card txn via CNP link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    007: TC_007
    """
    expectedSuccessMessage = "Your payment is successfully completed! You may close the browser now."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            # verify whether link is generated or not
            if response['success'] == False:
                raise Exception ("Api could not initiate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnCreditCardToExpand()
                remotePayTxn.enterNameOnTheCard("EzeAuto Debit")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                remotePayTxn.enterCreditCardExpiryMonth("3")
                remotePayTxn.enterCreditCardExpiryYear("2048")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()
                remotePayTxn.switch_to_iframe()
                remotePayTxn.wait_for_success_message()
                success_message = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected success message is:  {expectedSuccessMessage}")
                if success_message == expectedSuccessMessage:
                    pass
                else:
                    raise Exception("Success messages are not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_txn_id = result['id'].values[0]
            txn_customer_name = result['customer_name'].values[0]
            txn_settle_status = result['settlement_status'].values[0]
            txn_auth_code = result['auth_code'].values[0]
            txn_issuer_code = result['issuer_code'].values[0]
            txn_posting_date = result['posting_date'].values[0]

            logger.debug(f"Query result, txn_txn_id : {txn_txn_id}")
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")

            query = "select * from cnp_txn where txn_id='" + txn_txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            cnp_txn_state = result['state'].values[0]
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            cnp_txn_auth_code = result['auth_code'].values[0]
            cnp_payment_gateway = result['payment_gateway'].values[0]
            cnp_payment_flow = result['payment_flow'].values[0]

            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")

            query = "select * from cnpware_txn where txn_id='" + txn_txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_rrn_number = result['rr_number'].values[0]
            logger.debug(f"Query result, cnpware_txn_rrn_number : {cnpware_txn_rrn_number}")
            cnpware_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_acquirer_code : {cnpware_txn_acquirer_code}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            cnpware_txn_external_ref = result['external_ref'].values[0]
            logger.debug(f"Query result, cnpware_txn_external_ref : {cnpware_txn_external_ref}")
            cnpware_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnpware_txn_auth_code : {cnpware_txn_auth_code}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            query = "select * from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['txn_id'].values[0]
            org_code = result['org_code'].values[0]
            rrn = result['rr_number'].values[0]
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")

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
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(txn_posting_date)
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "AUTHORIZED",
                                     "txn_amt": str(amount)+".00",
                                     "txn_id": txn_txn_id,
                                     "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT SUCCESSFUL",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "auth_code": txn_auth_code,
                                     "date": date_and_time
                                     }
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                # homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_txn_id(txn_txn_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_txn_id}, {app_amount}")
                payment_rrn = txnHistoryPage.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_txn_id}, {payment_rrn}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_txn_id}, {payment_status_msg}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_txn_id}, {payment_settlement_status}")

                payment_auth_code = txnHistoryPage.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_txn_id}, {payment_auth_code}")
                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "rrn": payment_rrn,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "auth_code": payment_auth_code,
                                   "date": app_date_and_time}

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                date = date_time_converter.db_datetime(txn_posting_date)
                logger.info(f"Started API validation for the test case : {testcase_id}")
                expectedAPIValues = {"pmt_status": "AUTHORIZED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": cnp_txn_state,
                                     "acquirer_code": cnp_txn_acquirer_code,
                                     "settle_status": txn_settle_status,
                                     "rrn": cnp_txn_rrn,
                                     "issuer_code": txn_issuer_code,
                                     "txn_type": cnpware_txn_txn_type,
                                     "org_code": org_code,
                                     "date": date
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                # Use txn details
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        rrNumber_api = elements["rrNumber"]
                        issuerCode_api = elements["issuerCode"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   "rrn": rrNumber_api,
                                   "issuer_code": issuerCode_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date}

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # Add other tables for validation as well.
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expectedDBValues = {"pmt_status": "AUTHORIZED",
                                    "pmt_state": "SETTLED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "SETTLED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": cnpware_payment_flow,
                                    "pmt_intent_status":"COMPLETED"
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0])
                bank_name_db = result["bank_name"].iloc[0]
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
                                  "txn_amt": amount,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status":payment_intent_status
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time" : date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username,
                    'AUTH CODE': txn_auth_code
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                mobile_no = transaction_details[0]['Mobile No.']
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time" : date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username,
                    'AUTH CODE': auth_code
                }
                # ---------------------------------------------------------------------------------------------
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -----------------------------------------Start of Chargeslip Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(txn_posting_date)
                expectedValues = {'CARD TYPE': 'VISA',
                                  'merchant_ref_no': 'Ref # ' + str(order_id),
                                  'RRN': str(cnp_txn_rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                  'date': txn_date, "time":txn_time,
                                  "AUTH CODE": txn_auth_code}

                receipt_validator.perform_charge_slip_validations(txn_txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expectedValues)
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
def test_common_100_103_008():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_Failed_Cyber
    Sub Feature Description: Verification debit card failed txn for cybersource pg
    TC naming code description:
    100: Payment Method
    103: RemotePay
    008: TC_008
    """
    ExpectedfailedMessage = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_008')
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from cnp initiate api is: {response}")
            # verify whether link is generated or not
            if response['success'] == False:
                raise Exception ("Api could not initate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remotePayTxn.enterNameOnTheCard("EzeAuto")
                remotePayTxn.enterCreditCardNumber("4111 1111 1111 1111")
                remotePayTxn.enterDebitCardExpiryMonth("12")
                remotePayTxn.enterDebitCardExpiryYear("2050")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()

                actualFailedMessage = str(remotePayTxn.failedScreenMessage())
                logger.info(f"After txn message is:  : {actualFailedMessage}")
                if ExpectedfailedMessage == actualFailedMessage:
                    pass
                else:
                    print("Failed Message is not matching")

            query = "select * from payment_intent where id='" + payment_intent_id + "'"
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query result : {result}")
            payment_intent_status = result["status"].iloc[0]

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")

            query = "select rr_number from cnp_txn where txn_id='"+Txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")

            query = "select * from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_flow}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
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
            try:
                # --------------------------------------------------------------------------------------------
                date_and_time = date_time_converter.to_app_format(created_time)
                logger.info("Started APP validation for the test case : test_common_100_103_008")
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount)+".00",
                                     "txn_id": Txn_id,
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "date": date_and_time,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                # homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {Txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {Txn_id}, {payment_settlement_status}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {Txn_id}, {payment_settlement_status}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {Txn_id}, {app_date_and_time}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {Txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {Txn_id}, {payment_status_msg}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "date": app_date_and_time,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                date = date_time_converter.db_datetime(created_time)
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_common_100_103_008")
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": "FAILED",
                                     "acquirer_code": "HDFC",
                                     "settle_status": "FAILED",
                                     "issuer_code": "HDFC",
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": Txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                for elements in responseInList:
                    if elements["txnId"] == Txn_id:
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        issuerCode_api = elements["issuerCode"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": payment_mode_api,
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   "issuer_code": issuerCode_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started DB validation for the test case : test_common_100_103_008")
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "ACTIVE"
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                settle_status_db = result["settlement_status"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from cnpware_txn where txn_id='" + Txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

                actualDBValues = {"pmt_status": status_db,
                                  "pmt_state": state_db,
                                  "pmt_mode": payment_mode_db,
                                  "txn_amt": amount,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status
                                  }
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time" : date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                mobile_no = transaction_details[0]['Mobile No.']
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time" : date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username
                }
                # ---------------------------------------------------------------------------------------------
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_011():
    """
    Sub Feature Code: UI_Common_PM_CNP_Debit_Card_After_Timeout_Cyber
    Sub Feature Description: Verification of debit card txn after timeout via CNP link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    011: TC_011
    """
    expected_Timeout_Message = "Sorry! Your payment could not be processed. Any amount if debited will be reversed. Please click on the payment link sent by the merchant to you via SMS."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, cnpwareLog = True)
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from cnp initiate api is: {response}")
            if response['success'] == False:
                raise Exception ("Api could not initate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnDebitCardToExpand()
                logger.info("Enter Debit card details")
                remotePayTxn.enterNameOnTheCard("EzeAuto")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                remotePayTxn.enterDebitCardExpiryMonth("12")
                remotePayTxn.enterDebitCardExpiryYear("2050")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch cnpTxnTimeoutDuration for {org_code} is: {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"Timeout for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value = None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = 'EZETAP'"
            logger.debug(f"Timeout for Ezetap is : {query1}")
            try:
                defaultValue = DBProcessor.getValueFromDB(query1)
                setting_value = int(defaultValue['setting_value'].values[0])
                logger.info(f"max timeout duration for Ezetap org_code is: {setting_value}")
            except NameError as e:
                setting_value = None
                print(e)
            except IndexError as e:
                setting_value = None
                print(e)
            except Exception as e:
                print(e)

            if org_setting_value:
                logger.info(f"Value of timeout at org level is: {org_setting_value} min.")
                time.sleep(10 + (org_setting_value * 60))
            else:
                logger.info(f"Value of timeout at Ezetap org is: {org_setting_value} min.")
                time.sleep(10 + (setting_value * 60))

            remotePayTxn = RemotePayTxnPage(page)
            remotePayTxn.switch_to_iframe()
            remotePayTxn.wait_for_failed_message()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            created_time = result['created_time'].values[0]
            logger.debug(f"Query result, db date from db : {created_time}")

            query = "select * from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = "select * from cnpware_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
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
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                # --------------------------------------------------------------------------------------------
                logger.info("Started APP validation for the test case : test_common_100_103_011")
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount)+".00",
                                     "txn_id": Txn_id,
                                     "order_id": order_id,
                                     "msg": "PAYMENT FAILED",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     "date": date_and_time
                                     }
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                # homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)
                txnHistoryPage.click_on_transaction_by_order_id(order_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {Txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {Txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {Txn_id}, {app_amount}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {Txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {Txn_id}, {payment_status_msg}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {Txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {Txn_id}, {payment_settlement_status}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {Txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],
                                   "txn_id": app_txn_id,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
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
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_common_100_103_011")
                date = date_time_converter.db_datetime(created_time)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode":"CNP",
                                     "cnp_pmt_card_brand": "VISA",
                                     "cnp_pmt_card_type": "CREDIT",
                                     "pmt_state": "TIME_OUT_PENDING",
                                     "acquirer_code": "HDFC",
                                     "settle_status": "FAILED",
                                     "issuer_code": "HDFC",
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date
                                     }

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": Txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                payment_Card_Brand = response["paymentCardBrand"]
                payment_Card_Type = response["paymentCardType"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_Card_Brand} ")
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_Card_Type} ")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                for elements in responseInList:
                    if elements["txnId"] == Txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # Not a correct way of doing it.
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        issuerCode_api = elements["issuerCode"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "cnp_pmt_card_brand": payment_Card_Brand,
                                   "cnp_pmt_card_type": payment_Card_Type,
                                   "pmt_state": cnp_txn_state,
                                   "acquirer_code": acquirer_code__api,
                                   "settle_status": settlementStatus_api,
                                   "issuer_code": issuerCode_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }

                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started DB validation for the test case : test_common_100_103_011")
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "TIME_OUT_PENDING",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "ACTIVE"
                                    }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                settle_status_db = result["settlement_status"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                actualDBValues = {"pmt_status": status_db,
                                  "pmt_state": state_db,
                                  "pmt_mode": payment_mode_db,
                                  "txn_amt": amount,
                                  "settle_status": settle_status_db,
                                  "pmt_gateway": payment_gateway_db,
                                  "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status
                                  }
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "FAILED",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                mobile_no = transaction_details[0]['Mobile No.']
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username
                }
                # ---------------------------------------------------------------------------------------------
                logger.debug(f"expected_portal_values : {expected_portal_values}")
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_013():
    """
    Sub Feature Code: UI_Common_PM_CNP_Cyber_maxAttempts_CnpSettigs
    Sub Feature Description: Verification of the max attempts for a cnp txn.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    0013: TC013
    """
    expectedMessage = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response from remote pay api : {response}")
            paymentLinkUrl = response.get('paymentLink')
            payment_intent_id = response.get('paymentIntentId')

            query = "select * from remotepay_setting where setting_name='maximumPayAttemptsAllowed' and org_code = '" + str(org_code) + "';"
            logger.debug(f"Query to fetch max Attempts from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ",result)
                print("type of result: ", type(result))
                org_setting_value = int(result['setting_value'].values[0])
                logger.info(f"max upi attempt for {org_code} is {org_setting_value}")
            except Exception as e:
                org_setting_value=None
                print(e)

            query1 = "select * from remotepay_setting where setting_name='maximumPayAttemptsAllowed' and org_code = 'EZETAP'"
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
                while org_setting_value >= 0:
                    if org_setting_value == 0:
                        page = TestSuiteSetup.initialize_ui_browser()
                        page.goto(paymentLinkUrl)
                        break
                    else:
                        logger.debug(f"Running with org code max attempts.")
                        payment_intent_id = response.get('paymentIntentId')
                        page = TestSuiteSetup.initialize_ui_browser()
                        page.goto(paymentLinkUrl)
                        remotePayTxn = RemotePayTxnPage(page)
                        remotePayTxn.clickOnCreditCardToExpand()
                        logger.info("Enter Debit card details")
                        remotePayTxn.enterNameOnTheCard("EzeAuto")
                        remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                        remotePayTxn.enterCreditCardExpiryMonth("12")
                        remotePayTxn.enterCreditCardExpiryYear("2050")
                        remotePayTxn.enterCreditCardCvv("111")
                        remotePayTxn.clickOnProceedToPay()
                        # ui_driver.execute_script("window.open('');")
                        org_setting_value -= 1
                    print("setting value is :", org_setting_value)

            elif setting_value:
                while setting_value >= 0:
                    if setting_value == 0:
                        page = TestSuiteSetup.initialize_ui_browser()
                        page.goto(paymentLinkUrl)
                        break
                    else:
                        payment_intent_id = response.get('paymentIntentId')
                        page = TestSuiteSetup.initialize_ui_browser()
                        page.goto(paymentLinkUrl)
                        remotePayTxn = RemotePayTxnPage(page)
                        remotePayTxn.clickOnDebitCardToExpand()
                        logger.info("Enter Debit card details")
                        remotePayTxn.enterNameOnTheCard("EzeAuto")
                        remotePayTxn.enterCreditCardNumber("4000 0000 0000 1091")
                        remotePayTxn.enterCreditCardExpiryMonth("12")
                        remotePayTxn.enterCreditCardExpiryYear("2050")
                        remotePayTxn.enterCreditCardCvv("111")
                        remotePayTxn.clickOnProceedToPay()
                        setting_value-=1
                    print("setting value is :", setting_value)

            else:
                pass
            logger.info("Timeout execution completed.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
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
            created_time = result['created_time'].values[0]


            query = "select * from cnp_txn where txn_id='"+txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnp_payment_flow : {cnp_payment_flow}")


            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]
            logger.debug(f"Query result, cnpware_payment_flow : {cnpware_payment_flow}")

            cnpware_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"Query result, cnpware_payment_flow : {cnpware_pmt_mode}")

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
                # follow python naming convention.
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "PENDING",
                                     "txn_amt": str(amount)+".00",
                                     "txn_id": txn_id,
                                     # "rrn": cnp_txn_rrn,
                                     "order_id": order_id,
                                     "msg": "PAYMENT PENDING",
                                     "customer_name": txn_customer_name,
                                     "settle_status": txn_settle_status,
                                     # "auth_code": txn_auth_code,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                # Add loggers to each steps.
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)

                # add prefix as app in variable names.
                txnHistoryPage.click_on_transaction_by_txn_id(txn_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                # payment_rrn = txnHistoryPage.fetch_RRN_text()
                # logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1],  # santo's implementation needs to be added
                                   "txn_id": app_txn_id,
                                   "order_id": payment_orderId,
                                   "msg": payment_status_msg,
                                   "customer_name": payment_customer_name,
                                   "settle_status": payment_settlement_status,
                                   "date": app_date_and_time
                                   }

                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                # add app screenshot method
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # Add date variable as date and time
                date = date_time_converter.db_datetime(created_time)
                expectedAPIValues = {"pmt_status": "PENDING",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state": cnp_txn_state,
                                     "acquirer_code": "HDFC",
                                     "settle_status": "PENDING",
                                     # "rrn": cnp_txn_rrn,
                                     "issuer_code": "HDFC",
                                     "txn_type": "REMOTE_PAY",
                                     "org_code": org_code,
                                     "date": date
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                # Use txn details
                #
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username,
                                                                                   "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                # Remove jo nahi chaiye
                payment_mode_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])  # Not a correct way of doing it.
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        # rrNumber_api = elements["rrNumber"]
                        issuerCode_api = elements["issuerCode"]
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
                                   "issuer_code": issuerCode_api,
                                   "txn_type": txnType_api,
                                   "org_code": orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                # msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # Add other tables for validation as well.
                expectedDBValues = {"pmt_status": "PENDING",
                                    "pmt_state": "PENDING",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "PENDING",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_mode": "CNP",
                                    # "auth_code": txn_auth_code,
                                    "cnp_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow": cnpware_payment_flow,
                                    "pmt_intent_status": "ACTIVE"
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
                bank_name_db = result["bank_name"].iloc[0]
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
                                  "cnpware_pmt_mode": cnpware_pmt_mode,
                                  # "auth_code": cnp_txn_auth_code,
                                  "cnp_pmt_gateway": cnp_payment_gateway,
                                  "cnpware_pmt_gateway": cnpware_payment_gateway,
                                  "pmt_flow": cnp_payment_flow,
                                  "pmt_intent_status": payment_intent_status
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                # msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started Portal validation for the test case : {testcase_id}")
                date_and_time_portal = date_time_converter.to_portal_format(created_time)

                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "PENDING",
                    "pmt_type": "CNP",
                    "txn_amt": str(amount) + ".00",
                    "username": app_username
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                logger.debug(f"expected_portal_values : {expected_portal_values}")
                transaction_details = get_transaction_details_for_portal(app_username, app_password, order_id)
                date_time = transaction_details[0]['Date & Time']
                transaction_id = transaction_details[0]['Transaction ID']
                total_amount = transaction_details[0]['Total Amount'].split()
                mobile_no = transaction_details[0]['Mobile No.']
                auth_code = transaction_details[0]['Auth Code']
                rr_number = transaction_details[0]['RR Number']
                transaction_type = transaction_details[0]['Type']
                status = transaction_details[0]['Status']
                username = transaction_details[0]['Username']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_state": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount[1],
                    "username": username
                }
                # ---------------------------------------------------------------------------------------------
                logger.debug(f"expected_portal_values : {expected_portal_values}")
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
