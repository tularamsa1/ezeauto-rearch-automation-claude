import json
import random
import time
from datetime import datetime, timedelta
import shutil
import sys

import pytz
from termcolor import colored

import pytest
import requests
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
def test_common_100_103_001():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Success_Cyber
    Sub Feature Description: Verification of a Remote Pay successful credit card txn
    TC naming code description:
    100: Payment Method
    103: RemotePay
    001: TC_001
    """
    ##Need to verfiy with team
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_gateway='CYBERSOURCE')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

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
            if response['success'] == False:
                raise Exception ("Api could not initate a cnp txn.")
            else:
                ##verify whether link is generated or not
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                portal_driver = TestSuiteSetup.initialize_portal_driver()
                portal_driver.get(paymentLinkUrl)
                remotePayTxn = remotePayTxnPage(portal_driver)
                remotePayTxn.clickOnCreditCardToExpand()
                remotePayTxn.enterNameOnTheCard("Sandeep")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
                remotePayTxn.enterCreditCardExpiryMonth("12")
                remotePayTxn.enterCreditCardExpiryYear("2050")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()
                remotePayTxn.clickOnSubmitButton()
                successMessage = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {successMessage}")
                logger.info(f"Your expiryMessage is:  {expectedMessage}")
                if successMessage == expectedMessage:
                    pass
                else:
                    raise Exception("Success Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id = result['id'].values[0]
            logger.debug(f"Query result, txn_txn_id : {txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            txn_issuer_code = result['issuer_code'].values[0]
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")

            query = "select * from cnp_txn where txn_id='"+txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            cnp_txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            cnp_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")
            cnp_payment_flow = result['payment_flow'].values[0]

            query = "select * from cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            cnpware_txn_txn_type = result['txn_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            cnpware_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
            cnpware_payment_flow = result['payment_flow'].values[0]

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
                                     "rrn":cnp_txn_rrn,
                                     "order_id":order_id,
                                     "msg":"PAYMENT SUCCESSFUL",
                                     "customer_name":txn_customer_name,
                                     "settle_status":txn_settle_status,
                                     "auth_code":txn_auth_code,
                                     "date": date_and_time
                                     }

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                logger.debug("Login completed in the app.")
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                logger.debug("Waiting completed for txn history page.")
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(app_driver)

                #add prefix as app in variable names.
                txnHistoryPage.click_on_transaction_by_txn_id(txn_id)
                payment_status = txnHistoryPage.fetch_txn_status_text()
                logger.info(f"Fetching status from txn history for the txn : {txn_id}, {payment_status}")
                payment_mode = txnHistoryPage.fetch_txn_type_text()
                logger.info(f"Fetching payment mode from txn history for the txn : {txn_id}, {payment_mode}")
                app_txn_id = txnHistoryPage.fetch_txn_id_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {txn_id}, {app_txn_id}")
                app_amount = txnHistoryPage.fetch_txn_amount_text()
                logger.info(f"Fetching txn amount from txn history for the txn : {txn_id}, {app_amount}")
                payment_rrn = txnHistoryPage.fetch_RRN_text()
                logger.info(f"Fetching txn rrn from txn history for the txn : {txn_id}, {payment_rrn}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(f"Fetching txn status message from txn history for the txn : {txn_id}, {payment_status_msg}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {txn_id}, {payment_settlement_status}")
                payment_auth_code = txnHistoryPage.fetch_auth_code_text()
                logger.info(f"Fetching txn auth code from txn history for the txn : {txn_id}, {payment_auth_code}")
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {txn_id}, {app_date_and_time}")

                actualAppValues = {"pmt_mode": payment_mode,
                                   "pmt_status": payment_status.split(':')[1],
                                   "txn_amt": app_amount.split(' ')[1], #santo's implementation needs to be added
                                   "txn_id": app_txn_id,"rrn":payment_rrn,
                                   "order_id":payment_orderId,
                                   "msg":payment_status_msg,
                                   "customer_name":payment_customer_name,
                                   "settle_status":payment_settlement_status,
                                   "auth_code":payment_auth_code,
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
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "AUTHORIZED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state":"SETTLED",
                                     "acquirer_code":"HDFC",
                                     "settle_status":"SETTLED",
                                     "rrn":cnp_txn_rrn,
                                     "issuer_code":"HDFC",
                                     "txn_type":"REMOTE_PAY",
                                     "org_code":org_code,
                                     "date": date}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username, "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                #Remove jo nahi chaiye
                payment_mode_api = ''
                for elements in responseInList:
                    if elements["txnId"] == txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"]) #Not a correct way of doing it.
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        rrNumber_api = elements["rrNumber"]
                        issuerCode_api = elements["issuerCode"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]

                actualAPIValues = {"pmt_status": status_api,
                                   "txn_amt": amount_api,
                                   "pmt_mode": "CNP",
                                   "pmt_state":cnp_txn_state,
                                   "acquirer_code":acquirer_code__api,
                                   "settle_status":settlementStatus_api,
                                   "rrn":rrNumber_api,
                                   "issuer_code":issuerCode_api,
                                   "txn_type":txnType_api,
                                   "org_code":orgCode_api,
                                   "date": date_time_converter.from_api_to_datetime_format(date_api)
                                   }
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                #Add other tables for validation as well.
                expectedDBValues = {"pmt_status": "AUTHORIZED",
                                    "pmt_state": "SETTLED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status":"SETTLED",
                                    "pmt_gateway":"CYBERSOURCE",
                                    "auth_code":txn_auth_code,
                                    "cnp_pmt_gateway":"CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow":"REMOTEPAY",
                                    "pmt_intent_status": "COMPLETED"
                                    }

                logger.debug(f"expectedDBValues: {expectedDBValues}")
                query = "select * from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                #Handle in the posting datetime method.
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0]) #Amount should not be converted to int
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
                                    "settle_status":settle_status_db,
                                    "pmt_gateway":payment_gateway_db,
                                    "auth_code":cnp_txn_auth_code,
                                    "cnp_pmt_gateway": cnp_payment_gateway,
                                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                                    "pmt_flow":cnp_payment_flow,
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
                expectedPortalValues = {"pmt_state": "Settled", "pmt_type": "CNP",
                                        "txn_amt": "Rs." + str(amount) + ".00", "username": app_username}
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
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date)
                logger.info(f"date and time is: {txn_date},{txn_time}")
                #Python naming convention
                expectedValues = {'CARD TYPE': 'VISA',
                                    'merchant_ref_no': 'Ref # ' + str(order_id),
                                    'RRN': str(cnp_txn_rrn),
                                    'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                    'date': txn_date, #Date and time small letter mein de rahe hai lekin UI mein captila mein hai.
                                    'time': txn_time,
                                    "AUTH CODE":txn_auth_code}
                receipt_validator.perform_charge_slip_validations(txn_id, {"username":app_username,"password":app_password}, expectedValues)
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
def test_common_100_103_002(): #Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_Failed_Cyber
    Sub Feature Description: Verification of failed remote pay credit card txn  for cybersource pg
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_failed_Screen_Message_Cyber
    Sub Feature Description: Verifying the message in the failed screen via CNP link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    002: TC_002
    """
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    try:
        # -------------------------------Reset Settings to default(started)--------------------------------------------
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

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                response = APIProcessor.send_request(api_details)
                paymentLinkUrl = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')
                ui_driver = TestSuiteSetup.initialize_portal_driver()
                ui_driver.get(paymentLinkUrl)
                remote_pay_txn = remotePayTxnPage(ui_driver)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
                remote_pay_txn.enterCreditCardExpiryMonth("12")
                remote_pay_txn.enterCreditCardExpiryYear("2050")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()

            time.sleep(5)
            remote_pay_txn.wait_for_failed_message()
            failed_message = str(remote_pay_txn.failedScreenMessage())
            logger.info(f"Your failed Message is:  {failed_message}")

            if failed_message == expected_failed_message:
                pass
            else:
                logger.info(f"expected failed message is: {failed_message}")
                logger.info(f"actual failed message is: {expected_failed_message}")
                raise Exception(f"failed Messages are not matching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")

            query = "select * from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            cnp_txn_state = result['state'].values[0]
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")

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
                date_and_time = date_time_converter.to_app_format(posting_date)
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount),
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
                # loginPage = LoginPage(driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
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
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {Txn_id}, {app_date_and_time}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(f"Fetching txn customer name from txn history for the txn : {Txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(f"Fetching txn settlement status from txn history for the txn : {Txn_id}, {payment_settlement_status}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {Txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {Txn_id}, {payment_status_msg}")

                actualAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
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
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_com_100_103_002")
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "FAILED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state":"FAILED",
                                     "acquirer_code":"HDFC",
                                     "settle_status":"FAILED",
                                     "issuer_code":"HDFC",
                                     "txn_type":"REMOTE_PAY",
                                     "org_code":org_code,
                                     "date": date
                                     }
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": app_username, "password": app_password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]
                status_api = ''
                amount_api = ''
                #Remove jo nahi chaiye
                payment_mode_api = ''
                for elements in responseInList:
                    if elements["txnId"] == Txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"]) #Not a correct way of doing it.
                        acquirer_code__api = elements["acquirerCode"]
                        settlementStatus_api = elements["settlementStatus"]
                        issuerCode_api = elements["issuerCode"]
                        txnType_api = elements["txnType"]
                        orgCode_api = elements["orgCode"]
                        date_api = elements["postingDate"]
                #
                actualAPIValues = {
                    "pmt_status": status_api,
                    "txn_amt": amount_api,
                    "pmt_mode": "CNP",
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
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "settle_status": "FAILED",
                                    "pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "cnpware_pmt_flow": "REMOTEPAY",
                                    "pmt_intent_status": "ACTIVE"
                                    }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select * from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                #Handle in the posting datetime method.
                pmt_status_db = result["status"].iloc[0]
                pmt_mode_db = result["payment_mode"].iloc[0]
                txn_amt_db = int(result["amount"].iloc[0]) #Amount should not be converted to int
                settle_status_db = result["settlement_status"].iloc[0]
                pmt_state_db = result["state"].iloc[0]
                payment_gateway_db = result["payment_gateway"].iloc[0]

                query = "select * from payment_intent where id='" + payment_intent_id + "'"
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                payment_intent_status = result["status"].iloc[0]

                query = "select * from cnpware_txn where txn_id='" + Txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query, "cnpware")
                cnpware_txn_txn_type = result['txn_type'].values[0]
                logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
                cnpware_txn_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
                cnpware_txn_state = result['state'].values[0]
                logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
                cnpware_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")
                cnpware_payment_flow = result['payment_flow'].values[0]

                actualDBValues = {"pmt_status": pmt_status_db,
                                    "pmt_state": pmt_state_db,
                                    "pmt_mode": pmt_mode_db,
                                    "txn_amt": txn_amt_db,
                                    "settle_status":settle_status_db,
                                    "pmt_gateway":payment_gateway_db,
                                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                                    "cnpware_pmt_gateway": cnpware_payment_gateway,
                                    "cnpware_pmt_flow":cnpware_payment_flow,
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
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed",
                                        "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")

                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                # time.sleep(2)
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
            # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_103_009():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_After_Expiry_Cyber
    Sub Feature Description: Verification of remote pay txn after link expiry.
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_failed_Screen_Message_Cyber
    Sub Feature Description: Verifying the message in the failed screen via CNP link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    009: TC_009
    """
    # expectedExpiryMessage = "Sorry!You have exceeded the time available to complete the payment. Please request for a new link."
    expectedExpiryMessage = "Remote payment link has expired, Use a different mode or request for a new remote pay link to complete payment"
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

        portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_009')
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

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False, config_log=False)

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
            logger.info(response)
            paymentLinkUrl = response.get('paymentLink')
            logger.debug(f"Payment link url is : {paymentLinkUrl}")
            payment_Intent_ID = response.get('paymentIntentId')
            externalRef = response.get('externalRefNumber')
            portal_driver = TestSuiteSetup.initialize_portal_driver()

            query = "select setting_value from ezetap_demo.remotepay_setting where setting_name='remotePayExpTime' and org_code = '" + str(org_code)+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_Time = result['setting_value'].values[0]
            logger.debug(f"Query to fetch expiry_Time from the DB : {query}")
            logger.debug(f"Query result, expiry time : {expiry_Time}")

            expiry_Time_From_DB = int(expiry_Time)
            print(expiry_Time_From_DB)
            # time.sleep(100)
            time.sleep(expiry_Time_From_DB * 60)
            portal_driver.get(paymentLinkUrl)

            remotePayTxn = remotePayTxnPage(portal_driver)
            remotePayTxn.waitForExpiryElement()
    #         # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")

    finally:
        Configuration.executeFinallyBlock(testcase_id)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_010():
    """
    Sub Feature Code: UI_Common_PM_CNP_Credit_Card_After_Expiry_Cyber
    Sub Feature Description: Verification of remote pay txn after link expiry.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    010: TC_010
    """
    expected_Timeout_Message = "Sorry! Your payment could not be processed. Any amount if debited will be reversed. Please click on the payment link sent by the merchant to you via SMS."
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

        portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_010')
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
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False, config_log=False)

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
            portal_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            portal_driver.get(paymentLinkUrl)
            remotePayTxn = remotePayTxnPage(portal_driver)
            remotePayTxn.clickOnCreditCardToExpand()
            remotePayTxn.enterNameOnTheCard("Sandeep")
            remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
            remotePayTxn.enterCreditCardExpiryMonth("12")
            remotePayTxn.enterCreditCardExpiryYear("2050")
            remotePayTxn.enterCreditCardCvv("111")
            remotePayTxn.clickOnProceedToPay()

            query = "select * from remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code = '" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch max Attempts from the DB : {query}")
            try:
                result = DBProcessor.getValueFromDB(query)
                print("result: ", result)
                print("type of result: ", type(result))
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

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            txn_state = result['state'].values[0]
            logger.debug(f"Query result, db txn_state from db : {txn_state}")

            query1 = "select rr_number,org_code from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, rrn : {rrn}")
            logger.debug(f"Query result, org code is : {org_code}")

    #         # ------------------------------------------------------------------------------------------------
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
                date_and_time = date_time_converter.to_app_format(posting_date)
                logger.info(f"Started APP validation for the test case : {testcase_id}")
                expectedAppValues = {"pmt_mode": "PAY LINK",
                                     "pmt_status": "FAILED",
                                     "txn_amt": str(amount),
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
                homePage.check_home_page_logo()
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
                app_date_and_time = txnHistoryPage.fetch_date_time_text()
                logger.info(f"Fetching date from txn history for the txn : {Txn_id}, {app_date_and_time}")
                payment_customer_name = txnHistoryPage.fetch_customer_name_text()
                logger.info(
                    f"Fetching txn customer name from txn history for the txn : {Txn_id}, {payment_customer_name}")
                payment_settlement_status = txnHistoryPage.fetch_settlement_status_text()
                logger.info(
                    f"Fetching txn settlement status from txn history for the txn : {Txn_id}, {payment_settlement_status}")
                payment_orderId = txnHistoryPage.fetch_order_id_text()
                logger.info(f"Fetching txn orderId from txn history for the txn : {Txn_id}, {payment_orderId}")
                payment_status_msg = txnHistoryPage.fetch_txn_payment_msg_text()
                logger.info(
                    f"Fetching txn status message from txn history for the txn : {Txn_id}, {payment_status_msg}")

                actualAppValues = {"pmt_mode": "PAY LINK",
                                    "pmt_status": "FAILED",
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
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {
                                    "pmt_status": "FAILED",
                                    "txn_amt": amount,
                                    "pmt_mode": "CNP",
                                    "cnp_pmt_card_brand": "VISA",
                                    "cnp_pmt_card_type": "CREDIT",
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
                payment_Card_Brand = response["paymentCardBrand"]
                payment_Card_Type = response["paymentCardType"]
                acquirer_code__api = response["acquirerCode"]
                settlementStatus_api = response["settlementStatus"]
                issuerCode_api = response["issuerCode"]
                txnType_api = response["txnType"]
                date_api = response["postingDate"]
                orgCode_api = response["orgCode"]

                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_Card_Brand} ")
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_Card_Type} ")

                actualAPIValues = {
                                    "pmt_status": status_api,
                                    "txn_amt": amount_api,
                                    "pmt_mode": payment_mode_api,
                                    "cnp_pmt_card_brand": payment_Card_Brand,
                                    "cnp_pmt_card_type": payment_Card_Type,
                                    "pmt_state": txn_state,
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
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expectedDBValues = {"pmt_status": "FAILED",
                                    "pmt_state": "FAILED",
                                    "pmt_mode": "CNP",
                                    "txn_amt": amount,
                                    "acquirer_code": "HDFC",
                                    "org_code": org_code,
                                    "pmt_gateway": "CYBERSOURCE",
                                    "txn_type": "REMOTE_PAY",
                                    "settle_status": "FAILED",
                                    "rrn": rrn,
                                    "cnp_txn_id": Txn_id,
                                    "cnp_pmt_flow": "REMOTEPAY",
                                    "cnp_pmt_option": "CNP_CC",
                                    "cnp_pmt_status": "PAYMENT_FAILED",
                                    "cnp_pmt_state": "FAILED",
                                    "cnp_pmt_card_brand": "VISA",
                                    "cnp_pmt_card_type": "CREDIT"}

                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref,acquirer_code,issuer_code,org_code,payment_card_brand,payment_card_type," \
                        "payment_gateway,txn_type,settlement_status from txn where id='" + Txn_id + "'"

                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                acquirer_code = result["acquirer_code"].iloc[0]
                org_code = result["org_code"].iloc[0]
                payment_gateway = result["payment_gateway"].iloc[0]
                txn_type = result["txn_type"].iloc[0]
                settlement_status = result["settlement_status"].iloc[0]

                query1 = "select rr_number,txn_id,payment_flow,payment_option," \
                         "payment_option_value1,payment_status,state,payment_card_brand,payment_card_type from cnp_txn where txn_id='" + Txn_id + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query1}")
                result = DBProcessor.getValueFromDB(query1)
                rrn_cnp_txn = result['rr_number'].values[0]
                txn_id_cnp_txn = result['txn_id'].values[0]
                payment_flow_cnp_txn = result['payment_flow'].values[0]
                payment_option_cnp_txn = result['payment_option'].values[0]
                payment_status_cnp_txn = result['payment_status'].values[0]
                state_cnp_txn = result['state'].values[0]
                payment_card_brand_cnp_txn = result['payment_card_brand'].values[0]
                payment_card_type_cnp_txn = result['payment_card_type'].values[0]

                logger.debug(f"Query result, Txn_id : {Txn_id}")
                logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id_cnp_txn}")
                logger.debug(f"Query result, rrn : {rrn_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, payment_flow : {payment_flow_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, payment_option : {payment_option_cnp_txn}")
                # logger.debug(f"Query result from cnp_txn, payment_option_value1 : {payment_option_value1_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, payment_status : {payment_status_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, state : {state_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, payment_card_brand : {payment_card_brand_cnp_txn}")
                logger.debug(f"Query result from cnp_txn, payment_card_type : {payment_card_type_cnp_txn}")

                actualDBValues = {"pmt_status": status_db,
                                  "pmt_state": state_db,
                                  "pmt_mode": payment_mode_db,
                                  "txn_amt": amount_db,
                                  "acquirer_code": acquirer_code,
                                  "org_code": org_code,
                                  "pmt_gateway": payment_gateway,
                                  "txn_type": txn_type,
                                  "settle_status": settlement_status,
                                  "rrn": rrn,
                                  "cnp_txn_id": Txn_id,
                                  "cnp_pmt_flow": payment_flow_cnp_txn,
                                  "cnp_pmt_option": payment_option_cnp_txn,
                                  "cnp_pmt_status": payment_status_cnp_txn,
                                  "cnp_pmt_state": state_cnp_txn,
                                  "cnp_pmt_card_brand": payment_card_brand_cnp_txn,
                                  "cnp_pmt_card_type": payment_card_type_cnp_txn}

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
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")
                homePagePortal.click_switch_button(str(org_code))
                homePagePortal.perform_merchant_switched_verfication()
                homePagePortal.click_transaction_search_menu()
                portalTransHistoryPage = PortalTransHistoryPage(portal_driver)
                portalValuesDict = portalTransHistoryPage.get_transaction_details_for_portal(Txn_id)
                portalType = portalValuesDict['Type']
                portalStatus = portalValuesDict['Status']
                portalAmount = portalValuesDict['Total Amount']
                portalUsername = portalValuesDict['Username']

                actualPortalValues = {"Payment State": str(portalStatus), "Payment Type": portalType,
                                      "Amount": portalAmount, "Username": portalUsername}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
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
def test_common_100_103_012():
    """
    Sub Feature Code: UI_Common_PM_CNP_Refund_Card_txn
    Sub Feature Description: Verification of a refund for card txn using remote pay.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    012: TC_012
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE', portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

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
            logger.info(f"Response from api is: {response}")
            paymentLinkUrl = response.get('paymentLink')
            portal_driver = TestSuiteSetup.initialize_portal_driver()
            portal_driver.get(paymentLinkUrl)
            remote_pay_txn = remotePayTxnPage(portal_driver)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4000 0000 0000 0002")
            remote_pay_txn.enterCreditCardExpiryMonth("12")
            remote_pay_txn.enterCreditCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()
            remote_pay_txn.clickOnSubmitButton()

            remote_pay_txn.wait_for_success_message()
            successMessage = str(remote_pay_txn.succcessScreenMessage())
            logger.info(f"Your expected success message is:  {successMessage}")
            logger.info(f"Your expiryMessage is:  {expectedMessage}")
            if successMessage == expectedMessage:
                pass
            else:
                raise Exception("Success Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            txn_customer_name = result['customer_name'].values[0]
            logger.debug(f"Query result, txn_customer_name : {txn_customer_name}")
            txn_settle_status = result['settlement_status'].values[0]
            logger.debug(f"Query result, txn_settle_status : {txn_settle_status}")
            txn_auth_code = result['auth_code'].values[0]
            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            posting_date = result['posting_date'].values[0]
            logger.debug(f"Query result, db date from db : {posting_date}")
            created_time = result['created_time'].values[0]
            logger.debug(f"fetched created_time from txn table is : {created_time}")
            auth_code = result['auth_code'].values[0]
            logger.debug(f"fetched auth_code from txn table is : {auth_code}")
            customer_name = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            rrn = result['rr_number'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched txn_type from txn table is : {txn_type}")
            org_code_txn = result['org_code'].values[0]
            logger.debug(f"fetched org_code_txn from txn table is : {org_code_txn}")
            original_txn_type = result['txn_type'].values[0]
            bank_code_1 = result['bank_code'].values[0]

            query = "select * from cnpware_txn where txn_id='" + original_txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query, "cnpware")
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            logger.debug(f"original_acquirer_code_cnpware from cnpware_txn table : {original_acquirer_code_cnpware}")
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"original_payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")



            query = "select * from cnp_txn where txn_id='"+original_txn_id+"';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn_cnp_txn = result['rr_number'].values[0]
            logger.debug(f"Query result, original_rrn_cnp_txn : {original_rrn_cnp_txn}")
            state_cnp_txn_original = result['state'].values[0]
            logger.debug(f"Query result, state_cnp_txn_original : {state_cnp_txn_original}")


            #Refund
            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={"username": app_username, "password":app_password, "amount": amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")

            query = "select * from txn where orig_txn_id = '" + str(original_txn_id) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund = result['id'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            amount_after_refund = result['amount'].values[0]
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            paymentMode_after_refund = result['payment_mode'].values[0]
            logger.debug(f"paymentMode from txn table after refund: {paymentMode_after_refund}")
            state_after_refund = result['state'].values[0]
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            status_after_refund = result['status'].values[0]
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            logger.debug(f"acquirer_code from txn table after refund: {acquirer_code_after_refund}")
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")
            created_datetime_after_refund = result['created_time'].values[0]
            logger.debug(f"posting_date from txn table after refund: {created_datetime_after_refund}")
            refund_created_time = result['created_time'].values[0]
            logger.debug(f"fetched refund_created_time from txn table is : {refund_created_time}")
            customer_name_2 = result['customer_name'].values[0]
            logger.debug(f"fetched customer_name from txn table is : {customer_name}")
            payer_name_2 = result['payer_name'].values[0]
            logger.debug(f"fetched payer_name from txn table is : {payer_name}")
            refund_rrn = result['rr_number'].iloc[0]
            logger.debug(f"fetched refund_rrn from txn table is : {refund_rrn}")
            refund_txn_type = result['txn_type'].values[0]
            logger.debug(f"fetched refund_txn_type from txn table is : {refund_txn_type}")
            order_id_after_refund = result['external_ref'].values[0]
            logger.debug(f"Order Id after refund : {refund_txn_type}")
            bank_code_after_refund = result['bank_code'].values[0]
            logger.debug(f"bank_code_after_refund is : {bank_code_after_refund}")

            query = "select * from cnpware_txn where txn_id='" + txn_id_after_refund + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query,"cnpware")
            txn_id_after_refund_cnpware = result['txn_id'].values[0]
            amount_after_refund = result['amount'].values[0]
            paymentMode_after_refund = result['payment_mode'].values[0]
            state_after_refund = result['state'].values[0]
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            payment_flow_after_refund = result['payment_flow'].values[0]
            txn_type_after_refund = result['txn_type'].values[0]
            logger.debug(f"txn id from cnpware_txn table : {txn_id_after_refund_cnpware}")
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            logger.debug(f"paymentMode from cnpware_txn table : {paymentMode_after_refund}")
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            logger.debug(f"acquirer_code from cnpware_txn table : {acquirer_code_after_refund}")
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")

            query = "select * from cnp_txn where txn_id='" + txn_id_after_refund + "';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn_cnp_txn = result['rr_number'].values[0]
            acquirer_code_cnp_txn = result['acquirer_code'].values[0]
            state_cnp_txn = result['state'].values[0]
            payment_flow_cnp_txn = result['payment_flow'].values[0]
            txn_type_cnp_txn = result['txn_type'].values[0]
            payment_mode_cnp_txn = result['payment_mode'].values[0]
            payment_gateway_cnp_txn = result['payment_gateway'].values[0]
            org_code_cnp_txn = result['org_code'].values[0]
            logger.debug(f"fetched rrn from txn table is : {rrn}")
            logger.debug(f"Query result, rrn_cnp_txn : {rrn_cnp_txn}")
            logger.debug(f"Query result, acquirer_code_cnp_txn : {acquirer_code_cnp_txn}")
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            logger.debug(f"Query result, payment_flow_cnp_txn : {payment_flow_cnp_txn}")
            logger.debug(f"Query result, txn_type_cnp_txn : {txn_type_cnp_txn}")
            logger.debug(f"Query result, payment_mode_cnp_txn : {payment_mode_cnp_txn}")
            logger.debug(f"Query result, payment_gateway_cnp_txn : {payment_gateway_cnp_txn}")
            logger.debug(f"Query result, org_code_cnp_txn : {org_code_cnp_txn}")

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
                expectedAppValues = {
                                     "pmt_status_1": "STATUS:AUTHORIZED_REFUNDED",
                                     "pmt_mode_1": "PAY LINK",
                                     "txn_id_1": original_txn_id,
                                     "txn_amt_1": str(amount),
                                     "rrn_1": str(original_rrn_cnp_txn),
                                     "order_id_1": order_id,
                                     "msg_1": "PAYMENT VOIDED/REFUNDED",
                                     "customer_name_1": txn_customer_name,
                                     "settle_status_1": txn_settle_status,
                                     "date_1": date_and_time,

                                    "pmt_status_2": "STATUS:REFUNDED",
                                    "pmt_mode_2": "PAY LINK",
                                    "txn_id_2": txn_id_after_refund,
                                    "txn_amt_2": str(amount),
                                    "rrn_2": str(rrn_cnp_txn),
                                    "order_id_2": order_id,
                                     "msg_2": "PAYMENT VOIDED/REFUNDED",
                                     "customer_name_2": txn_customer_name,
                                     "settle_status_2": txn_settle_status,
                                     "date_2": date_and_time
                                     }
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                home_page = HomePage(app_driver)
                home_page.wait_for_navigation_to_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
                transactions_history_page = TransHistoryPage(app_driver)
                transactions_history_page.click_on_transaction_by_txn_id(txn_id_after_refund)

                app_rrn_refunded = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_after_refund}, {app_rrn_refunded}")
                app_date_and_time_refunded = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {txn_id_after_refund}, {app_date_and_time_refunded}")
                app_payment_status_refunded = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status_refunded}")
                # app_auth_code_refunded = transactions_history_page.fetch_auth_code_text()
                # logger.info(
                #     f"Fetching AUTH CODE from txn history for the txn : {txn_id_after_refund}, {app_auth_code_refunded}")
                app_payment_mode_refunded = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode_refunded}")
                app_txn_id_refunded = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id_refunded}")
                app_payment_amt_refunded = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt_refunded}")
                app_settlement_status_refunded = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: settlement status Id = {app_settlement_status_refunded}")
                payment_msg_refunded = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: msg Id = {payment_msg_refunded}")
                app_order_id_refunded = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id_refunded}")

                transactions_history_page.click_back_Btn_transaction_details()
                transactions_history_page.click_on_transaction_by_txn_id(original_txn_id)
                app_date_and_time = transactions_history_page.fetch_date_time_text()
                logger.info(
                    f"Fetching date from txn history for the txn : {original_txn_id}, {app_date_and_time}")
                app_rrn_original = transactions_history_page.fetch_RRN_text()
                logger.debug(f"Fetching txn_id from txn history for the txn : {original_txn_id}, {app_rrn_original}")
                app_auth_code_original = transactions_history_page.fetch_auth_code_text()
                logger.info(
                    f"Fetching AUTH CODE from txn history for the txn : {original_txn_id}, {app_auth_code_original}")
                app_payment_status_original = transactions_history_page.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactions_history_page.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactions_history_page.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactions_history_page.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_settlement_status_original = transactions_history_page.fetch_settlement_status_text()
                logger.debug(
                    f"Fetching settlement status of original txn from transaction history of MPOS app: Txn Id = {app_settlement_status_original}")
                payment_msg_original = transactions_history_page.fetch_txn_payment_msg_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_order_id = transactions_history_page.fetch_order_id_text()
                logger.debug(
                    f"Fetching order id from app transaction history: order Id = {app_order_id}")
                actualAppValues = {

                                    "pmt_status_1": app_payment_status_original,
                                    "pmt_mode_1": app_payment_mode_original,
                                    "txn_amt_1": str(app_payment_amt_original),
                                    "txn_id_1": original_txn_id,
                                    "rrn_1": str(original_rrn_cnp_txn),
                                   "order_id_1": order_id,
                                   "msg_1": payment_msg_original,
                                   "customer_name_1": txn_customer_name,
                                   "settle_status_1": txn_settle_status,
                                   "date_1": date_and_time,

                                   "pmt_status_2": app_payment_status_refunded,
                                   "pmt_mode_2": app_payment_mode_refunded,
                                   "txn_id_2": app_txn_id_refunded,
                                   "txn_amt_2": str(app_payment_amt_refunded),
                                   "rrn_2": str(app_rrn_refunded),
                                   "order_id_2":app_order_id_refunded,
                                   "msg_2": payment_msg_refunded,
                                   "customer_name_2": txn_customer_name,
                                   "settle_status_2": app_settlement_status_refunded,
                                   "date_2": app_date_and_time_refunded

                                   }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
                logger.info(f"Completed API validation for the test case : {testcase_id}")
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
                logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started API validation for the test case : {testcase_id}")
                date = date_time_converter.db_datetime(created_time)
                refund_date = date_time_converter.db_datetime(refund_created_time)
                expected_api_values = {
                                       "pmt_status_1": "AUTHORIZED_REFUNDED",
                                       "pmt_status_2": "REFUNDED",
                                       "pmt_state_1": "REFUNDED",
                                       "pmt_state_2": "REFUNDED",
                                       "pmt_mode_1": "CNP",
                                       "pmt_mode_2": "CNP",
                                       "settle_status_1": "SETTLED",
                                       "settle_status_2": "SETTLED",
                                       "txn_amt_1": str(amount),
                                       "txn_amt_2": str(amount),
                                       "customer_name_1": customer_name,
                                       "customer_name_2": customer_name_2,
                                       "payer_name_1": payer_name,
                                       "payer_name_2": payer_name_2,
                                       "order_id_1": order_id,
                                       "order_id_2": order_id,
                                       "rrn_1": str(original_rrn_cnp_txn),
                                       "rrn_2": str(rrn_cnp_txn),
                                       "acquirer_code_1": "HDFC",
                                       "issuer_code_1": "HDFC",
                                       "txn_type_1": txn_type,
                                       "org_code_1": org_code_txn,
                                       "acquirer_code_2": "HDFC",
                                       "txn_type_2": refund_txn_type,
                                       "org_code_2": org_code_txn,
                                       "auth_code_1": auth_code,
                                       "date_1": date,
                                       "date_2": refund_date,
                                       }
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == original_txn_id][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_original = response["status"]
                amount_api_original = int(response["amount"])
                payment_mode_api_original = response["paymentMode"]
                rrn_api_original = response["rrNumber"]
                state_api_original = response["states"][0]
                settlement_status_api_original = response["settlementStatus"]
                issuer_code_api_original = response["issuerCode"]
                acquirer_code_api_original = response["acquirerCode"]
                org_code_api_original = response["orgCode"]
                mid_api_original = response["mid"]
                tid_api_original = response["tid"]
                txn_type_api_original = response["txnType"]
                auth_code_api_original = response["authCode"]
                date_api_original = response["createdTime"]
                order_id_api_original = response["orderNumber"]

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username,
                                                                        "password": app_password})
                logger.debug(f"API DETAILS for txn : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction list api is : {response}")
                response = [x for x in response["txns"] if x["txnId"] == txn_id_after_refund][0]
                logger.debug(f"Response after filtering data of current txn is : {response}")
                status_api_refunded = response["status"]
                amount_api_refunded = int(response["amount"])
                payment_mode_api_refunded = response["paymentMode"]
                rrn_api_refunded = response["rrNumber"]
                state_api_refunded = response["states"][0]
                settlement_status_api_refunded = response["settlementStatus"]
                # issuer_code_api_refunded = response["issuerCode"]
                acquirer_code_api_refunded = response["acquirerCode"]
                org_code_api_refunded = response["orgCode"]
                # mid_api_refunded = response["mid"]
                # tid_api_refunded = response["tid"]
                txn_type_api_refunded = response["txnType"]
                # auth_code_api_refunded = response["authCode"]
                date_api_refunded = response["createdTime"]
                order_id_api_refunded = response["orderNumber"]
                actual_api_values = {
                    "pmt_status_1": status_api_original,
                    "pmt_status_2": status_api_refunded,
                    "pmt_state_1": state_api_original,
                    "pmt_state_2": state_api_refunded,
                    "pmt_mode_1": payment_mode_api_original,
                    "pmt_mode_2": payment_mode_api_refunded,
                    "settle_status_1": settlement_status_api_original,
                    "settle_status_2": settlement_status_api_refunded,
                    "txn_amt_1": str(amount_api_original),
                    "txn_amt_2": str(amount_api_refunded),
                    "customer_name_1": customer_name,
                    "customer_name_2": customer_name,
                    "payer_name_1": payer_name,
                    "payer_name_2": payer_name,
                    "order_id_1": order_id_api_original,
                    "order_id_2": order_id_api_refunded,
                    "rrn_1": str(rrn_api_original),
                    "rrn_2": str(rrn_api_refunded),
                    "acquirer_code_1": acquirer_code_api_original,
                    "issuer_code_1": issuer_code_api_original,
                    "txn_type_1": txn_type_api_original,
                    "org_code_1": org_code_api_original,
                    "acquirer_code_2": acquirer_code_api_refunded,
                    "txn_type_2": txn_type_api_refunded,
                    "org_code_2": org_code_api_refunded,
                    "auth_code_1": auth_code_api_original,
                    "date_1": date_time_converter.from_api_to_datetime_format(date_api_original),
                    "date_2": date_time_converter.from_api_to_datetime_format(date_api_refunded),

                    }
                logger.debug(f"actualAPIValues: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expected_db_values = {
                    "pmt_status_1": "REFUNDED",
                    "pmt_status_2": "REFUNDED",
                    "pmt_state_2": "REFUNDED",
                    "pmt_state_1": "REFUNDED",
                    "pmt_mode_1": "CNP",
                    "pmt_mode_2": "CNP",
                    "txn_amt_1": amount,
                    "txn_amt_2": amount,
                    "order_id_1": order_id,
                    "order_id_2": order_id,
                    "cnp_txn_status_1": "SETTLED",
                    "cnp_txn_status_2": "REFUNDED",
                    "settle_status_1": "SETTLED",
                    "settle_status_2": "SETTLED",
                    "acquirer_code_1": "HDFC",
                    "acquirer_code_2": "HDFC",
                    "pmt_gateway_1": "CYBERSOURCE",
                    "pmt_gateway_2": "CYBERSOURCE",
                    "cnpware_txn_type_1": "REMOTE_PAY",
                    "cnpware_txn_type_2": "REFUND",
                    "cnpware_pmt_flow_1": "REMOTEPAY",
                    "cnpware_pmt_flow_2": "None",
                }
                logger.debug(f"expectedDBValues: {expected_db_values}")

                query = "select * from txn where id = '" + str(txn_id_after_refund) + "';"
                logger.debug(f"Query to fetch Txn_id from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                original_txn_id_db = result['id'].values[0]
                amount_txn_db = result['amount'].values[0]
                paymentMode_db = result['payment_mode'].values[0]
                state_db = result['state'].values[0]
                status_db = result['status'].values[0]
                acquirer_code_db = result['acquirer_code'].values[0]
                payment_gateway_db = result['payment_gateway'].values[0]
                settlement_status_db = result['settlement_status'].values[0]
                # bank_code_1 = result['bank_code'].values[0]
                txn_type_db = result['txn_type'].values[0]
                Org_Code_db = result['org_code'].values[0]
                logger.debug(f"txn id from txn table : {original_txn_id_db}")
                logger.debug(f"amount from txn table : {amount_txn_db}")
                logger.debug(f"paymentMode from txn table : {paymentMode_db}")
                logger.debug(f"state from txn table : {state_db}")
                logger.debug(f"status from txn table : {status_db}")
                logger.debug(f"acquirer_code from txn table : {acquirer_code_db}")
                logger.debug(f"payment_gateway from txn table : {payment_gateway_db}")
                logger.debug(f"settlement_status from txn table : {settlement_status_db}")
                logger.debug(f"txn type from txn table : {txn_type_db}")
                logger.debug(f"Org code from txn table : {Org_Code_db}")

                actual_db_values = {"pmt_status_1": status_db,
                                    "pmt_status_2": status_after_refund,
                                    "pmt_state_1": state_db,
                                    "pmt_state_2": state_after_refund,
                                    "pmt_mode_1": paymentMode_db,
                                    "pmt_mode_2": payment_mode_cnp_txn,
                                    "txn_amt_1": amount_txn_db,
                                    "txn_amt_2": amount_after_refund,
                                    "order_id_1": order_id,
                                    "order_id_2": order_id_after_refund,
                                    "cnp_txn_status_1": state_cnp_txn_original,
                                    "cnp_txn_status_2": state_cnp_txn,
                                    "settle_status_1": settlement_status_db,
                                    "settle_status_2": settlement_status_after_refund,
                                    "acquirer_code_1": acquirer_code_db,
                                    "acquirer_code_2": original_acquirer_code_cnpware,
                                    "pmt_gateway_1": payment_gateway_db,
                                    "pmt_gateway_2": payment_gateway_after_refund,
                                    "cnpware_txn_type_1": original_txn_type,
                                    "cnpware_txn_type_2": txn_type_after_refund,
                                    "cnpware_pmt_flow_1": original_payment_flow_cnpware,
                                    "cnpware_pmt_flow_2": str(payment_flow_after_refund),

                                    }
                logger.debug(f"actualDBValues : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------Start of chargeslip Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(created_datetime_after_refund)
                expected_chargeslip_values = {"payment_option":"REFUND",
                                              'merchant_ref_no': 'Ref # ' + str(order_id),
                                              'RRN': str(rrn_cnp_txn),
                                              'BASE AMOUNT:': "Rs." + str(amount) + ".00",
                                              'date': txn_date, 'time': txn_time,
                                              'AUTH CODE': ""}

                logger.debug(
                    f"expected_chargeslip_values : {expected_chargeslip_values} for the testcase_id {testcase_id}")

                receipt_validator.perform_charge_slip_validations(txn_id_after_refund,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_chargeslip_values)


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