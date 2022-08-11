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
    001: TC_01
    """
    ##Need to verfiy with team
    expectedMessage = "Your payment is successfully completed! You may close the browser now."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
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
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
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
                # successMessage = str(remotePayTxn.succcessScreenMessage())
                # logger.info(f"Your expected success message is:  {successMessage}")
                # logger.info(f"Your expiryMessage is:  {expectedMessage}")
                # if successMessage == expectedMessage:
                #     pass
                # else:
                #     # can we give like this in the execution block??
                #     # check whether if finally is executed or not?
                #     raise Exception("Success Message is not matching.")

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
            txn_auth_code = result['auth_code'].values[0]
            txn_issuer_code = result['issuer_code'].values[0]
            txn_bank_name = result['bank_name'].values[0]
            txn_acquirer_code = result['acquirer_code'].values[0]
            txn_settlement_status = result['settlement_status'].values[0]
            txn_payment_mode = result['payment_mode'].values[0]
            txn_amount = result['amount'].values[0]
            posting_date = result['posting_date'].values[0]

            #Add these below each fetch query.




            logger.debug(f"Query result, txn_auth_code : {txn_auth_code}")
            logger.debug(f"Query result, txn_issuer_code : {txn_issuer_code}")
            logger.debug(f"Query result, txn_bank_name : {txn_bank_name}")
            logger.debug(f"Query result, txn_acquirer_code : {txn_acquirer_code}")
            logger.debug(f"Query result, txn_settlement_status : {txn_settlement_status}")
            logger.debug(f"Query result, txn_payment_mode : {txn_payment_mode}")
            logger.debug(f"Query result, txn_amount : {txn_amount}")
            logger.debug(f"Query result, db date from db : {posting_date}")


            query = "select * from cnp_txn where txn_id='"+txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_txn_rrn = result['rr_number'].values[0]
            cnp_txn_state = result['state'].values[0]
            cnp_txn_acquirer_code = result['acquirer_code'].values[0]
            cnp_txn_card_type = result['payment_card_type'].values[0]
            cnp_txn_external_ref = result['external_ref'].values[0]
            cnp_txn_auth_code = result['auth_code'].values[0]
            cnp_payment_gateway = result['payment_gateway'].values[0]
            cnp_payment_flow = result['payment_flow'].values[0]

            logger.debug(f"Query result, cnp_txn_rrn : {cnp_txn_rrn}")
            logger.debug(f"Query result, cnp_txn_state : {cnp_txn_state}")
            logger.debug(f"Query result, cnp_txn_acquirer_code : {cnp_txn_acquirer_code}")
            logger.debug(f"Query result, cnp_txn_card_type : {cnp_txn_card_type}")
            logger.debug(f"Query result, cnp_txn_external_ref : {cnp_txn_external_ref}")
            logger.debug(f"Query result, cnp_txn_auth_code : {cnp_txn_auth_code}")
            logger.debug(f"Query result, cnp_payment_gateway : {cnp_payment_gateway}")

            query = "select * from cnpware_demo.cnpware_txn where txn_id='" + txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnpware_txn_txn_type = result['txn_type'].values[0]
            cnpware_txn_rrn_number = result['rr_number'].values[0]
            cnpware_txn_acquirer_code = result['acquirer_code'].values[0]
            cnpware_txn_card_type = result['payment_card_type'].values[0]
            cnpware_txn_external_ref = result['external_ref'].values[0]
            cnpware_txn_auth_code = result['auth_code'].values[0]
            cnpware_txn_state = result['state'].values[0]
            cnpware_txn_amount = result['amount'].values[0]
            cnpware_payment_gateway = result['payment_gateway'].values[0]
            cnpware_payment_flow = result['payment_flow'].values[0]

            logger.debug(f"Query result, cnpware_txn_txn_type : {cnpware_txn_txn_type}")
            logger.debug(f"Query result, cnpware_txn_rrn_number : {cnpware_txn_rrn_number}")
            logger.debug(f"Query result, cnpware_txn_acquirer_code : {cnpware_txn_acquirer_code}")
            logger.debug(f"Query result, cnpware_txn_card_type : {cnpware_txn_card_type}")
            logger.debug(f"Query result, cnpware_txn_external_ref : {cnpware_txn_external_ref}")
            logger.debug(f"Query result, cnpware_txn_auth_code : {cnpware_txn_auth_code}")
            logger.debug(f"Query result, cnpware_txn_state : {cnpware_txn_state}")
            logger.debug(f"Query result, cnpware_txn_amount : {cnpware_txn_amount}")
            logger.debug(f"Query result, cnpware_payment_gateway : {cnpware_payment_gateway}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))       # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(posting_date)
                #follow python naming convention.
                expectedAppValues = {"pmt_mode": "PAY LINK", "pmt_status": "AUTHORIZED",
                                     "txn_amt": str(amount),"txn_id": txn_id,
                                     "rrn":cnp_txn_rrn,
                                     "order_id":order_id,"msg":"PAYMENT SUCCESSFUL",
                                     "customer_name":txn_customer_name,
                                     "settle_status":txn_settle_status,
                                     "auth_code":txn_auth_code,
                                     "date": date_and_time}

                logger.debug(f"expectedAppValues: {expectedAppValues}")
                #Add loggers to each steps.
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(app_username, app_password)
                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
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
                #add app screenshot method
                ReportProcessor.capture_ss_when_app_val_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                #Add date variable as date and time
                date = date_time_converter.db_datetime(posting_date)
                expectedAPIValues = {"pmt_status": "AUTHORIZED",
                                     "txn_amt": amount,
                                     "pmt_mode": "CNP",
                                     "pmt_state":cnp_txn_state,
                                     "acquirer_code":cnp_txn_acquirer_code,
                                     "settle_status":txn_settle_status,
                                     "rrn":cnp_txn_rrn,
                                     "issuer_code":txn_issuer_code,
                                     "txn_type":cnpware_txn_txn_type,
                                     "org_code":org_code,
                                     "date": date}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                #Use txn details
                #
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

                actualAPIValues = {"pmt_status": status_api, "txn_amt": amount_api,
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
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
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
                                    "payment_mode":"PAY LINK",
                                    "auth_code":txn_auth_code,
                                    "cnp_pmt_gateway":"CYBERSOURCE",
                                    "cnpware_pmt_gateway": "CYBERSOURCE",
                                    "pmt_flow":cnpware_payment_flow,
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
                                    "settle_status":settle_status_db,
                                    "pmt_gateway":payment_gateway_db,
                                    "payment_mode":payment_mode,
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
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'
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
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
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
                ReportProcessor.capture_ss_when_portal_val_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                #Modified below varaibale and value.
                GlobalVariables.str_chargeslip_val_result = "Fail"
            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
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
    # expected_Failed_Message = "Sorry! Your payment could not be processed. Please click on the payment link sent to you on SMS or Email and attempt the payment again."
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here

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

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
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

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            # logger.info(api_details)
            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response.get('paymentLink')
            payment_Intent_ID = response.get('paymentIntentId')
            externalRef = response.get('externalRefNumber')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            # ui_driver = GlobalVariables.portalDriver
            ui_driver.get(paymentLinkUrl)
            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.clickOnCreditCardToExpand()
            remote_pay_txn.enterNameOnTheCard("Sandeep")
            remote_pay_txn.enterCreditCardNumber("4111 1111 1111 1111")
            remote_pay_txn.enterCreditCardExpiryMonth("12")
            remote_pay_txn.enterCreditCardExpiryYear("2050")
            remote_pay_txn.enterCreditCardCvv("111")
            remote_pay_txn.clickOnProceedToPay()

            # remote_pay_txn.wait_for_failed_message()
            # failed_message = str(remote_pay_txn.failedScreenMessage())
            # logger.info(f"Your failed Message is:  {failed_message}")

            # if failed_message == expected_failed_message:
            #     pass
            # else:
            #     logger.info(f"expected failed message is: {failed_message}")
            #     logger.info(f"actual failed message is: {expected_failed_message}")
            #     raise Exception(f"failed Messages are not mactching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()  # If In the execution or try block app driver is not initialized then we can remove this line
            ReportProcessor.capture_ss_when_portal_val_exe_failed()  # If In the execution or try block portal driver is not initialized then we can remove this line
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------

                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
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
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                logger.debug(f"actualAppValues: {actualAppValues}")

                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_com_100_103_002")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "CNP"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": app_username, "password": app_password})
                response = APIProcessor.send_request(api_details)
                list = response["txns"]
                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for li in list:
                    if li["txnId"] == Txn_id:
                        status_api = li["status"]
                        amount_api = int(li["amount"])
                        payment_mode_api = li["paymentMode"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "CNP",
                                    "Payment amount": amount}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount}
                                  # "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                # portal_username = '9660867344'
                # portal_password = 'A123456'
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")

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
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -------------------------------------------End of Validation---------------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")


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
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            logger.info(response)
            paymentLinkUrl = response.get('paymentLink')
            logger.debug(f"Payment link url is : {paymentLinkUrl}")
            payment_Intent_ID = response.get('paymentIntentId')
            externalRef = response.get('externalRefNumber')
            ui_driver = TestSuiteSetup.initialize_portal_driver()

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
            ui_driver.get(paymentLinkUrl)

            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.waitForExpiryElement()
            # expiryMessage = str(remotePayTxn.expiryMessage())
            # logger.info(f"Your expiryMessage is:  {expiryMessage}")
            # logger.info(f"Your expiryMessage is:  {expectedExpiryMessage}")
            # if expiryMessage == (expectedExpiryMessage):
            #     pass
            # else:
            #     raise Exception("Expiry Messages are not matching.")
    #         # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()  # If In the execution or try block app driver is not initialized then we can remove this line
            ReportProcessor.capture_ss_when_portal_val_exe_failed()

            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

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
    # expected_Timeout_Message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    expected_Timeout_Message = "Sorry! Your payment could not be processed. Any amount if debited will be reversed. Please click on the payment link sent by the merchant to you via SMS."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        logger.info("Execution Started for the test case : test_common_100_103_010")
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

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))


            query = "select org_code from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            # ui_driver = GlobalVariables.portalDriver
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            ui_driver.get(paymentLinkUrl)
            remotePayTxn = remotePayTxnPage(ui_driver)
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
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_exe_failed()
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------

                logger.info(f"Started APP validation for the test case : {testcase_id}")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
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
                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id}
                logger.debug(f"actualAppValues: {actualAppValues}")
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result="Fail"
            logger.info(f"Completed APP validation for the test case : {testcase_id}")


        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started API validation for the test case : {testcase_id}")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "CNP", "Payment Card Brand": "VISA","Payment Card Type": "CREDIT"}
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
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api, "Payment Card Brand": payment_Card_Brand,"Payment Card Type": payment_Card_Type}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "CNP",
                                    "Payment amount": amount, "external_ref": order_id, "acquirer_code": "HDFC",
                                    "issuer_code": "HDFC", "org_code": org_code,
                                    "payment_gateway": "CYBERSOURCE", "txn_type": "REMOTE_PAY",
                                    "settlement_status": "FAILED", "state": "FAILED", "RRNumber": rrn
                    , "CNP Txn Id": Txn_id, "Payment Flow": "REMOTEPAY", "Payment Option": "CNP_CC",
                                    "CNP Payment Status": "PAYMENT_FAILED",
                                    "State": "FAILED", "Payment Card Brand": "VISA",
                                    "payment_card_type": "CREDIT"}

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
                external_ref = result["external_ref"].iloc[0]
                acquirer_code = result["acquirer_code"].iloc[0]
                issuer_code = result["issuer_code"].iloc[0]
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
                # payment_option_value1_cnp_txn = result['payment_option_value1'].values[0]
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

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount_db,
                                  "external_ref": external_ref,
                                  "acquirer_code": acquirer_code, "issuer_code": issuer_code, "org_code": org_code,
                                  "payment_gateway": payment_gateway, "txn_type": txn_type,
                                  "settlement_status": settlement_status, "state": state_db, "RRNumber": rrn,
                                  "CNP Txn Id": Txn_id, "Payment Flow": payment_flow_cnp_txn,
                                  "Payment Option": payment_option_cnp_txn,
                                  "CNP Payment Status": payment_status_cnp_txn,
                                  "State": state_cnp_txn, "Payment Card Brand": payment_card_brand_cnp_txn,
                                  "payment_card_type": payment_card_type_cnp_txn}

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'
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
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'
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
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)
        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from api is: {response}")
            paymentLinkUrl = response.get('paymentLink')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            ui_driver.get(paymentLinkUrl)
            remotePayTxn = remotePayTxnPage(ui_driver)
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
                raise Exception("Expiry Message is not matching.")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id = result['id'].values[0]
            amount_txn = result['amount'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id}")
            logger.debug(f"amount from txn table : {amount_txn}")

            #Refund
            api_details = DBProcessor.get_api_details('RemotePayRefund', request_body={"username": app_username, "password":app_password, "amount": amount,
                                                                    "originalTransactionId": str(original_txn_id)})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for transaction details api is : {response}")
            txn_id_after_refund = response.get('txnId')
            # original_txn_id_after_refund = response.get('origTxnId')
            logger.debug(f"Query result, txn_id_after_refund : {txn_id_after_refund}")
            # logger.debug(f"Query result, original_txn_id_after_refund : {original_txn_id_after_refund}")

            query = "select * from txn where orig_txn_id = '" + str(original_txn_id) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn details from the DB after refund: {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund = result['id'].values[0]
            amount_after_refund = result['amount'].values[0]
            paymentMode_after_refund = result['payment_mode'].values[0]
            state_after_refund = result['state'].values[0]
            status_after_refund = result['status'].values[0]
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"txn id from txn table after refund : {txn_id_after_refund}")
            logger.debug(f"amount from txn table after refund: {amount_after_refund}")
            logger.debug(f"paymentMode from txn table after refund: {paymentMode_after_refund}")
            logger.debug(f"state from txn table after refund: {state_after_refund}")
            logger.debug(f"status from txn table after refund: {status_after_refund}")
            logger.debug(f"acquirer_code from txn table after refund: {acquirer_code_after_refund}")
            logger.debug(f"payment_gateway from txn table after refund: {payment_gateway_after_refund}")
            logger.debug(f"settlement_status from txn table after refund: {settlement_status_after_refund}")

            query = "select * from cnpware_demo.cnpware_txn where txn_id='" + txn_id_after_refund + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id_after_refund_cnpware = result['txn_id'].values[0]
            amount_after_refund = result['amount'].values[0]
            paymentMode_after_refund = result['payment_mode'].values[0]
            state_after_refund = result['state'].values[0]
            # status = result['status'].values[0]
            acquirer_code_after_refund = result['acquirer_code'].values[0]
            payment_gateway_after_refund = result['payment_gateway'].values[0]
            # settlement_status = result['settlement_status'].values[0]
            payment_flow_after_refund = result['payment_flow'].values[0]
            logger.debug(f"txn id from cnpware_txn table : {txn_id_after_refund_cnpware}")
            logger.debug(f"amount from cnpware_txn table : {amount_after_refund}")
            logger.debug(f"paymentMode from cnpware_txn table : {paymentMode_after_refund}")
            logger.debug(f"state from cnpware_txn table : {state_after_refund}")
            # logger.debug(f"status from cnpware_txn table : {status}")
            logger.debug(f"acquirer_code from cnpware_txn table : {acquirer_code_after_refund}")
            logger.debug(f"payment_gateway from cnpware_txn table : {payment_gateway_after_refund}")
            # logger.debug(f"settlement_status from cnpware_txn table : {settlement_status}")
            logger.debug(f"payment_flow from cnpware_txn table : {payment_flow_after_refund}")

            query = "select rr_number, acquirer_code,state,payment_flow,txn_type,payment_mode,payment_gateway,org_code from cnp_txn where txn_id='" + txn_id_after_refund + "';"
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
            logger.debug(f"Query result, rrn_cnp_txn : {rrn_cnp_txn}")
            logger.debug(f"Query result, acquirer_code_cnp_txn : {acquirer_code_cnp_txn}")
            logger.debug(f"Query result, state_cnp_txn : {state_cnp_txn}")
            logger.debug(f"Query result, payment_flow_cnp_txn : {payment_flow_cnp_txn}")
            logger.debug(f"Query result, txn_type_cnp_txn : {txn_type_cnp_txn}")
            logger.debug(f"Query result, payment_mode_cnp_txn : {payment_mode_cnp_txn}")
            logger.debug(f"Query result, payment_gateway_cnp_txn : {payment_gateway_cnp_txn}")
            logger.debug(f"Query result, org_code_cnp_txn : {org_code_cnp_txn}")

            #Original Txn Details after refund
            query = "select * from txn where id = '" + str(original_txn_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id_after_refund = result['id'].values[0]
            original_amount_txn_after_refund = result['amount'].values[0]
            original_paymentMode_after_refund = result['payment_mode'].values[0]
            original_state_after_refund = result['state'].values[0]
            original_status_after_refund = result['status'].values[0]
            original_acquirer_code_after_refund = result['acquirer_code'].values[0]
            original_payment_gateway_after_refund = result['payment_gateway'].values[0]
            original_settlement_status_after_refund = result['settlement_status'].values[0]
            logger.debug(f"txn id from txn table : {original_txn_id_after_refund}")
            logger.debug(f"amount from txn table : {original_amount_txn_after_refund}")
            logger.debug(f"paymentMode from txn table : {original_paymentMode_after_refund}")
            logger.debug(f"state from txn table : {original_state_after_refund}")
            logger.debug(f"status from txn table : {original_status_after_refund}")
            logger.debug(f"acquirer_code from txn table : {original_acquirer_code_after_refund}")
            logger.debug(f"payment_gateway from txn table : {original_payment_gateway_after_refund}")
            logger.debug(f"settlement_status from txn table : {original_settlement_status_after_refund}")

            query = "select * from cnpware_demo.cnpware_txn where txn_id='"+original_txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_txn_id_cnpware = result['txn_id'].values[0]
            original_amount_cnpware = result['amount'].values[0]
            original_paymentMode_cnpware = result['payment_mode'].values[0]
            original_state_cnpware = result['state'].values[0]
            # status = result['status'].values[0]
            original_acquirer_code_cnpware = result['acquirer_code'].values[0]
            original_payment_gateway_cnpware = result['payment_gateway'].values[0]
            # settlement_status = result['settlement_status'].values[0]
            original_payment_flow_cnpware = result['payment_flow'].values[0]
            logger.debug(f"txn id from cnpware_txn table : {original_txn_id_cnpware}")
            logger.debug(f"amount from cnpware_txn table : {original_amount_cnpware}")
            logger.debug(f"paymentMode from cnpware_txn table : {original_paymentMode_cnpware}")
            logger.debug(f"state from cnpware_txn table : {original_state_cnpware}")
            # logger.debug(f"status from cnpware_txn table : {status}")
            logger.debug(f"acquirer_code from cnpware_txn table : {original_acquirer_code_cnpware}")
            logger.debug(f"payment_gateway from cnpware_txn table : {original_payment_gateway_cnpware}")
            # logger.debug(f"settlement_status from cnpware_txn table : {settlement_status}")
            logger.debug(f"payment_flow from cnpware_txn table : {original_payment_flow_cnpware}")

            query = "select rr_number, acquirer_code,state,payment_flow,txn_type,payment_mode,payment_gateway,org_code from cnp_txn where txn_id='"+original_txn_id+"';"
            logger.debug(f"Query to fetch rrn number from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            original_rrn_cnp_txn = result['rr_number'].values[0]
            original_acquirer_code_cnp_txn = result['acquirer_code'].values[0]
            original_state_cnp_txn = result['state'].values[0]
            original_payment_flow_cnp_txn = result['payment_flow'].values[0]
            original_txn_type_cnp_txn = result['txn_type'].values[0]
            original_payment_mode_cnp_txn = result['payment_mode'].values[0]
            original_payment_gateway_cnp_txn = result['payment_gateway'].values[0]
            original_org_code_cnp_txn = result['org_code'].values[0]
            logger.debug(f"Query result, rrn_cnp_txn : {original_rrn_cnp_txn}")
            logger.debug(f"Query result, acquirer_code_cnp_txn : {original_acquirer_code_cnp_txn}")
            logger.debug(f"Query result, state_cnp_txn : {original_state_cnp_txn}")
            logger.debug(f"Query result, payment_flow_cnp_txn : {original_payment_flow_cnp_txn}")
            logger.debug(f"Query result, txn_type_cnp_txn : {original_txn_type_cnp_txn}")
            logger.debug(f"Query result, payment_mode_cnp_txn : {original_payment_mode_cnp_txn}")
            logger.debug(f"Query result, payment_gateway_cnp_txn : {original_payment_gateway_cnp_txn}")
            logger.debug(f"Query result, org_code_cnp_txn : {original_org_code_cnp_txn}")


            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            ReportProcessor.get_TC_Exe_Time()
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            expectedAppValues = {"Payment Status": "STATUS:REFUNDED", "Payment mode": "PAY LINK",
                                 "Payment Txn ID": txn_id_after_refund, "Payment Amt": str(amount),"rrn": str(rrn_cnp_txn),
                                 "OrderId":"Order Id # '"+order_id+"'",
                                 "Payment Status Original": "STATUS:AUTHORIZED_REFUNDED",
                                 "Payment mode Original": "PAY LINK", "Payment Txn ID Original": original_txn_id,
                                 "Payment Amt Original": str(amount), "rrn Original": str(original_rrn_cnp_txn)}

            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            loginPage = LoginPage(app_driver)
            loginPage.perform_login(app_username, app_password)
            homePage = HomePage(app_driver)
            homePage.wait_for_navigation_to_load()
            homePage.wait_for_home_page_load()
            homePage.check_home_page_logo()
            homePage.click_on_history()
            transactionsHistoryPage = TransHistoryPage(app_driver)
            transactionsHistoryPage.click_on_transaction_by_order_id(order_id)
            app_rrn = transactionsHistoryPage.fetch_RRN_text()
            logger.debug(f"Fetching txn_id from txn history for the txn : {txn_id_after_refund}, {app_rrn}")
            app_payment_status = transactionsHistoryPage.fetch_txn_status_text()
            logger.debug(f"Fetching Transaction status from transaction history of MPOS app: Txn status = {app_payment_status}")
            app_payment_mode = transactionsHistoryPage.fetch_txn_type_text()
            logger.debug(f"Fetching Transaction payment mode from transaction history of MPOS app: Txn Mode = {app_payment_mode}")
            app_txn_id = transactionsHistoryPage.fetch_txn_id_text()
            logger.debug(f"Fetching Transaction id from transaction history of MPOS app: Txn Id = {app_txn_id}")
            app_payment_amt = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
            logger.debug(f"Fetching Transaction amount from transaction history of MPOS app: Txn Amt = {app_payment_amt}")
            transactionsHistoryPage.click_back_Btn_transaction_details()
            transactionsHistoryPage.click_on_second_transaction_by_order_id(order_id)
            app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
            logger.debug(f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
            app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
            logger.debug(f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "f"Mode = {app_payment_mode_original}")
            app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
            logger.debug(f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
            app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
            logger.debug(f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
            actualAppValues = {"Payment Status": app_payment_status, "Payment mode": app_payment_mode,
                               "Payment Txn ID": app_txn_id, "Payment Amt": str(app_payment_amt),"rrn": str(rrn_cnp_txn),
                                 "OrderId":"Order Id # '"+order_id+"'",
                               "Payment Status Original": app_payment_status_original,
                               "Payment mode Original": app_payment_mode_original,
                               "Payment Txn ID Original": original_txn_id,
                               "Payment Amt Original": str(app_payment_amt_original), "rrn": str(app_rrn),
                               "rrn Original": str(original_rrn_cnp_txn)}
            # ---------------------------------------------------------------------------------------------
            Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started API validation for the test case : {testcase_id}")
                expectedAPIValues = {"Payment Status": "REFUNDED", "Amount": amount_txn, "Payment Mode": "CNP","State":"REFUNDED",
                                     "Acquirer Code":acquirer_code_after_refund, "Settlement Status":settlement_status_after_refund, "RRN Number":rrn_cnp_txn,
                                     "Txn Type":txn_type_cnp_txn, "Org Code": original_org_code_cnp_txn}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": txn_id_after_refund})
                response = APIProcessor.send_request(api_details)
                logger.info(f"Fetching response from txn details api : {response} ")
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                payment_Card_Brand = response["paymentCardBrand"]
                payment_Card_Type = response["paymentCardType"]
                state_api = response["states"]
                acquirer_code_api = response["acquirerCode"]
                settlement_status_api = response["settlementStatus"]
                rrNumber_api = response["rrNumber"]
                txntype_api = response["txnType"]
                org_code_api = response["orgCode"]
                # converting lsit to string
                stateInStringformat = ' '.join(map(str, state_api))
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction payment Card Brand from transaction api : {payment_Card_Brand} ")
                logger.debug(f"Fetching Transaction payment Card Type from transaction api : {payment_Card_Type} ")
                logger.debug(f"Fetching Transaction payment state from transaction api : {stateInStringformat} ")
                logger.debug(f"Fetching Transaction acquirer from transaction api : {acquirer_code_api} ")
                logger.debug(f"Fetching Transaction payment settlement status from transaction api : {settlement_status_api} ")
                logger.debug(f"Fetching Transaction payment rrn number from transaction api : {rrNumber_api} ")
                logger.debug(f"Fetching Transaction payment txn type from transaction api : {txntype_api} ")
                logger.debug(f"Fetching Transaction org code from transaction api : {org_code_api} ")
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,"State":stateInStringformat,
                                   "Acquirer Code": acquirer_code_api,
                                   "Settlement Status": settlement_status_api, "RRN Number": rrNumber_api,
                                   "Txn Type": txntype_api, "Org Code": org_code_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info(f"Started DB validation for the test case : {testcase_id}")
                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": app_username,
                                                                                      "password": app_password,
                                                                                      "txnId": txn_id_after_refund})
                response = APIProcessor.send_request(api_details)
                logger.info(f"Fetching response from txn details api : {response} ")
                acquirer_code_api = response["acquirerCode"]
                settlement_status_api = response["settlementStatus"]
                rrn_number_api = response["rrNumber"]
                txn_type_api = response["txnType"]
                org_code_api = response["orgCode"]

                expectedDBValues = {"Payment Status": "REFUNDED", "Payment State": "REFUNDED", "Payment mode": "CNP",
                                    "Payment amount": original_amount_cnpware, "Acquirer Code":acquirer_code_api, "RRN Number":rrn_number_api,
                                    "Settlement Status":settlement_status_api,"Txn Type":txn_type_api,"Org Code":org_code_api}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

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
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db, "Payment mode": paymentMode_db,
                                    "Payment amount": amount_txn_db, "Acquirer Code":acquirer_code_db, "RRN Number":rrn_cnp_txn,
                                    "Settlement Status":settlement_status_db,"Txn Type":txn_type_db,"Org Code":Org_Code_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'
            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)