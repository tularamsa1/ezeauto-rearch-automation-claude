import json
import random
import shutil
import sys
import time
from datetime import datetime

import pytest
from termcolor import colored

from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
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
    """
    expectedSuccessMessage = "Your payment is successfully completed! You may close the browser now."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']
        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
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
            print(colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": username, "password": password})
            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response['paymentLink']
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            externalRef = response.get('externalRefNumber')
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(paymentLinkUrl)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.clickOnDebitCardToExpand()
            logger.info("Enter Debit card details")
            remotePayTxn.enterNameOnTheCard("Sandeep")
            remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
            remotePayTxn.enterDebitCardExpiryMonth("12")
            remotePayTxn.enterDebitCardExpiryYear("2050")
            remotePayTxn.enterCreditCardCvv("111")
            remotePayTxn.clickOnProceedToPay()
            remotePayTxn.clickOnSubmitButton()
            successMessage = str(remotePayTxn.succcessScreenMessage())
            logger.info(f"Your success Message is:  {successMessage}")
            if successMessage == expectedSuccessMessage:
                pass
            else:
                logger.info(successMessage != expectedSuccessMessage)
                raise Exception("Success Messages are not mactching")
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            query = "select org_code,rr_number,txn_id,payment_gateway,payment_mode,payment_flow,payment_option," \
                    "payment_option_value1,payment_status,state,payment_card_brand,payment_card_type," \
                    "acquirer_code,issuer_code from cnp_txn where txn_id='" + Txn_id + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            txn_id = result['txn_id'].values[0]
            payment_gateway = result['payment_gateway'].values[0]
            payment_mode = result['payment_mode'].values[0]
            payment_flow = result['payment_flow'].values[0]
            payment_option = result['payment_option'].values[0]
            payment_option_value1 = result['payment_option_value1'].values[0]
            payment_status = result['payment_status'].values[0]
            state = result['state'].values[0]
            payment_card_brand = result['payment_card_brand'].values[0]
            payment_card_type = result['payment_card_type'].values[0]
            acquirer_code = result['acquirer_code'].values[0]
            issuer_code = result['issuer_code'].values[0]
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result from cnp_txn, Txn_id : {txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")
            logger.debug(f"Query result from cnp_txn, payment_gateway : {payment_gateway}")
            logger.debug(f"Query result from cnp_txn, payment_mode : {payment_mode}")
            logger.debug(f"Query result from cnp_txn, payment_flow : {payment_flow}")
            logger.debug(f"Query result from cnp_txn, payment_option : {payment_option}")
            logger.debug(f"Query result from cnp_txn, payment_option_value1 : {payment_option_value1}")
            logger.debug(f"Query result from cnp_txn, payment_status : {payment_status}")
            logger.debug(f"Query result from cnp_txn, state : {state}")
            logger.debug(f"Query result from cnp_txn, payment_card_brand : {payment_card_brand}")
            logger.debug(f"Query result from cnp_txn, payment_card_type : {payment_card_type}")
            logger.debug(f"Query result from cnp_txn, acquirer_code : {acquirer_code}")
            logger.debug(f"Query result from cnp_txn, issuer_code : {issuer_code}")
            logger.debug(f"Query result from cnp_txn, org_code : {org_code}")
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
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            ReportProcessor.get_TC_Exe_Time()
            pytest.fail("Test case execution failed due to the exception -" + str(e))
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
                logger.info("Started APP validation for the test case : test_common_100_103_007")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                # driver = GlobalVariables.appDriver
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(username, password)
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

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_common_100_103_007")
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "CNP","rrNumber":rrn}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": username,
                                                                                      "password": password,
                                                                                      "txnId": Txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                rrNumber = response["rrNumber"]
                org_code_db = response["orgCode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                logger.debug(f"Fetching Transaction rrNumber from transaction api : {rrNumber} ")
                logger.debug(f"Fetching Transaction org_code mode from transaction api : {org_code} ")
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,"rrNumber": rrn}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started DB validation for the test case : test_common_100_103_007")
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "CNP",
                                    "Payment amount": amount, "external_ref": order_id, "acquirer_code": "HDFC",
                                    "issuer_code": "HDFC", "org_code": org_code,
                                    "payment_gateway": "CYBERSOURCE", "txn_type": "REMOTE_PAY",
                                    "settlement_status": "SETTLED", "state": "SETTLED"}
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

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "external_ref": external_ref,
                                  "acquirer_code": acquirer_code,
                                  "issuer_code": issuer_code, "org_code": org_code,
                                  "payment_gateway": payment_gateway, "txn_type": txn_type,
                                  "settlement_status": settlement_status, "state": state_db
                                  }

                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started Portal validation for the test case : test_common_100_103_007")
                expectedPortalValues = {"Payment State": "Settled", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
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
                                      "Amount": portalAmount, "Username": username}
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - "+str(e))
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

        # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_common_100_103_007")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'CARD TYPE': 'VISA', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                  'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(Txn_id, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_common_100_103_007")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            #-------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_008():
    """
    UI_Common_PM_CNP_Debit_Card_Failed_Cyber
    Verification debit card failed txn for cybersource pg
    """
    # ExpectedfailedMessage = "Sorry! Your payment could not be processed. Please click on the payment link sent to you on SMS or Email and attempt the payment again."
    ExpectedfailedMessage = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        logger.info("Execution Started for the test case : test_common_100_103_008")
        app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_008')
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_008')
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)
        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            print(
                colored("Execution Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": username, "password": password})
            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(paymentLinkUrl)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.clickOnDebitCardToExpand()
            logger.info("Enter Debit card details")
            remotePayTxn.enterNameOnTheCard("Sandeep")
            remotePayTxn.enterCreditCardNumber("4111 1111 1111 1111")
            remotePayTxn.enterDebitCardExpiryMonth("12")
            remotePayTxn.enterDebitCardExpiryYear("2050")
            remotePayTxn.enterCreditCardCvv("111")
            remotePayTxn.clickOnProceedToPay()
            # remotePayTxn.clickOnSubmitButton()

            actualFailedMessage = str(remotePayTxn.failedScreenMessage())
            logger.info(f"After txn message is:  : {actualFailedMessage}")
            if ExpectedfailedMessage == actualFailedMessage:
                pass
            else:
                print("Failed Message is not matching")

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            query = "select rr_number from cnp_txn where txn_id='"+Txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")

            # ------------------------------------------------------------------------------------------------
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
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1

            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))
        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started APP validation for the test case : test_common_100_103_008")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(app_driver)
                # homePage.wait_for_home_page_load()
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
                GlobalVariables.str_app_val_result = "Fail"

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_common_100_103_008")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "CNP"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": username,
                                                                                      "password": password,
                                                                                      "txnId": Txn_id})
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = response["amount"]
                payment_mode_api = response["paymentMode"]
                logger.debug(f"Fetching Transaction status from transaction api : {status_api} ")
                logger.debug(f"Fetching Transaction amount from transaction api : {amount_api} ")
                logger.debug(f"Fetching Transaction payment mode from transaction api : {payment_mode_api} ")
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started DB validation for the test case : test_common_100_103_008")
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


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started Portal validation for the test case : test_common_100_103_008")
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                loginPagePortal.perform_login_to_portal(portal_username, portal_password)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
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
        # -----------------------------------------End of Portal Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        logger.info(f"Completed Validation for the test case : {testcase_id}")
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        Configuration.executeFinallyBlock(testcase_id)
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")
        #----------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_011():
    """
    UI_Common_PM_CNP_Debit_Card_After_Timeout_Cyber
    Verification of  debit card txn after timeout via CNP link
    """
    # expected_Timeout_Message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    expected_Timeout_Message = "Sorry! Your payment could not be processed. Any amount if debited will be reversed. Please click on the payment link sent by the merchant to you via SMS."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)
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

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": username, "password": password})

            response = APIProcessor.send_request(api_details)
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(paymentLinkUrl)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.clickOnDebitCardToExpand()
            logger.info("Enter Debit card details")
            remotePayTxn.enterNameOnTheCard("Sandeep")
            remotePayTxn.enterCreditCardNumber("4000 0000 0000 0002")
            remotePayTxn.enterDebitCardExpiryMonth("12")
            remotePayTxn.enterDebitCardExpiryYear("2050")
            remotePayTxn.enterCreditCardCvv("111")
            remotePayTxn.clickOnProceedToPay()
            query = "select setting_value from ezetap_demo.remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code ='"+org_code+"';"
            logger.debug(f"Query to fetch setting_value from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnpTxnTimeoutDuration = result['setting_value'].values[0]
            logger.debug(f"Query result, timeout Duration : {cnpTxnTimeoutDuration}")

            timeout_Duration_From_DB = int(cnpTxnTimeoutDuration)
            time.sleep(3+(timeout_Duration_From_DB * 60))
            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.clickOnSubmitButton()
            remotePayTxn.waitForTimeoutElement()
            timeout_Message = str(remotePayTxn.timeoutScreenMessage())
            logger.info(f"Your timeout Message is:  {timeout_Message}")
            logger.info(f"Your expected timeout Message is:  {expected_Timeout_Message}")
            if timeout_Message == (expected_Timeout_Message):
                pass
            else:
                raise Exception(timeout_Message!=expected_Timeout_Message)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            query = "select rr_number from cnp_txn where txn_id='"+Txn_id+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")
            logger.debug(f"Query result, rrn : {rrn}")

    #         # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in except block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in execpt block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            ReportProcessor.capture_ss_when_app_val_exe_failed()
            ReportProcessor.capture_ss_when_portal_val_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in except block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))

            logger.exception(f"Execution is completed for the test case : {testcase_id}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started APP validation for the test case : test_common_100_103_011")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
                loginPage = LoginPage(app_driver)
                loginPage.perform_login(username, password)
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

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started API validation for the test case : test_common_100_103_011")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "CNP", "Payment Card Brand": "VISA","Payment Card Type": "CREDIT"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": username,
                                                                                      "password": password,
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


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started DB validation for the test case : test_common_100_103_011")
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


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started Portal validation for the test case : test_common_100_103_011")
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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
                homePagePortal.perform_merchant_verfication()
                homePagePortal.click_transaction_search_menu()
                # logger.info("Clearing the text")
                # homePagePortal.perform_clear_txt()
                # logger.info("text cleared")
                # homePagePortal.perform_txn_count_search(3)
                # homePagePortal.perform_txn_search()
                # homePagePortal.perform_txn_search()
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
        logger.info(f"Starting execution of finally block for the test case : {testcase_id}")
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case pre condition setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------
        logger.info("Reverting back all the settings that were done as preconditions")
        # Write the code here to revert the settings that were done as precondition
        logger.info("Reverted back all the settings that were done as preconditions")
        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))

        logger.info(f"Completed execution of finally block for the test case : {testcase_id}")
        logger.info(f"Completed test case execution, validation and finally block for the test case : {testcase_id}")
