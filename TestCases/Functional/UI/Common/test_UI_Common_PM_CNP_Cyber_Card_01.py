import json
import random
import time
from datetime import datetime

import pytest
import requests
from Configuration import Configuration
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
@pytest.mark.usefixtures("appium_driver","ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_001(): #Make sure to add the test case name as same as the sub feature code.

    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_001')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_001')
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            # username = "4455778875"
            # password = "q121212"
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            url = 'https://dev11.ezetap.com/api/3.0/pay/remote/initiate'
            headers = {'Content-Type': 'application/json'}
            payload = {
                # "username": "9949134775",
                # "appKey": "c7244973-694a-47e7-953a-2f3af792d7ad",
                "username": str(username),
                "password": str(password),
                "amount": amount,
                "agentMobileNumber": "1122112221",
                "customerName": "Sandeep Kumar",
                "customerMobileNumber": "0000000000",
                "customerEmail": "sandeep.r@ezetap.com",
                "paymentFlow": "REMOTEPAY",
                "externalRefNumber": order_id,
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            json_data = json.loads(response.text)
            print(json_data)
            ui_driver = GlobalVariables.portalDriver
            paymentLinkUrl = json_data['paymentLink']
            externalRef = json_data.get('externalRefNumber')
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
            if successMessage == "Your payment is successfully completed! You may close the browser now.":
                print("Test Passed"+ successMessage)
            else:
                print("Success Message is not matching")
                print(successMessage)

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
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started APP validation for the test case : test_com_100_103_001")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                driver = GlobalVariables.appDriver
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                txnHistoryPage = TransHistoryPage(driver)
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
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "CNP"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist', request_body={"username": username, "password": password})
                response = APIProcessor.send_request(api_details)
                responseInList = response["txns"]

                status_api = ''
                amount_api = ''
                payment_mode_api = ''
                for elements in responseInList:
                    if elements["txnId"] == Txn_id:
                        status_api = elements["status"]
                        amount_api = int(elements["amount"])
                        payment_mode_api = elements["paymentMode"]
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


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "CNP",
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
                expectedPortalValues = {"Payment State": "Settled", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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

        # -----------------------------------------End of Portal Validation---------------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info("Started ChargeSlip validation for the test case : test_common_100_103_001")
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

            logger.info("Completed ChargeSlip validation for the test case : test_common_100_103_001")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock("test_common_100_103_001")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver","ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_103_002(): #Make sure to add the test case name as same as the sub feature code.
    """
    UI_Common_PM_CNP_Credit_Card_Failed_Cyber
    Verification of failed remote pay credit card txn  for cybersource pg
    UI_Common_PM_CNP_Credit_Card_failed_Screen_Message_Cyber
    Verifying the message in the failed screen via CNP link
    """
    username_portal = '9660867344'
    password_portal = 'A123456'
    username_app = "4455778875"
    password_app = "q121212"
    expected_Failed_Message = "Sorry! Your payment could not be processed. Please click on the payment link sent to you on SMS or Email and attempt the payment again."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_002')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_002')
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            # username = "4455778875"
            # password = "q121212"
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            url = 'https://dev11.ezetap.com/api/3.0/pay/remote/initiate'
            headers = {'Content-Type': 'application/json'}
            payload = {
                # "username": "9949134775",
                # "appKey": "c7244973-694a-47e7-953a-2f3af792d7ad",
                "username": str(username),
                "password": str(password),
                "amount": amount,
                "agentMobileNumber": "1122112221",
                "customerName": "Sandeep Kumar",
                "customerMobileNumber": "0000000000",
                "customerEmail": "sandeep.r@ezetap.com",
                "paymentFlow": "REMOTEPAY",
                "externalRefNumber": order_id,
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            json_data = json.loads(response.text)
            print(json_data)
            ui_driver = GlobalVariables.portalDriver
            paymentLinkUrl = json_data['paymentLink']
            externalRef = json_data.get('externalRefNumber')
            ui_driver.get(paymentLinkUrl)
            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.clickOnCreditCardToExpand()
            remotePayTxn.enterNameOnTheCard("Sandeep")
            remotePayTxn.enterCreditCardNumber("4111 1111 1111 1111")
            remotePayTxn.enterCreditCardExpiryMonth("12")
            remotePayTxn.enterCreditCardExpiryYear("2050")
            remotePayTxn.enterCreditCardCvv("111")
            remotePayTxn.clickOnProceedToPay()
            time.sleep(3)

            failedMessage = str(remotePayTxn.failedScreenMessage())
            if failedMessage == "Sorry! Your payment could not be processed. Please click on the payment link sent to you on SMS or Email and attempt the payment again.":
                print("Test Passed"+ failedMessage)
            else:
                print("Failed Message is not matching")
                print(failedMessage)

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                driver = GlobalVariables.appDriver
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()

                txnHistoryPage = TransHistoryPage(driver)
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
                logger.info("Started API validation for the test case : test_com_100_103_002")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "CNP"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnlist',
                                                          request_body={"username": username, "password": password})
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


        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
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


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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

        # -----------------------------------------End of Portal Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_common_100_103_002")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.

@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver","ui_driver") #This is an optional line. Keep only whichever driver is required.
@pytest.mark.appVal
# From below use only the markers that are applicable for the test case and remove the rest.
def test_common_100_103_009(): #Make sure to add the test case name as same as the sub feature code.
    """
    UI_Common_PM_CNP_Credit_Card_After_Expiry_Cyber
    Verification of remote pay txn after link expiry.
    """
    # username_portal = '9660867344'
    # password_portal = 'A123456'
    # username_app = "4455778875"
    # password_app = "q121212"
    expectedExpiryMessage = "Sorry!You have exceeded the time available to complete the payment. Please request for a new link."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info("Execution Started for the test case : test_common_100_103_009")
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_009')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_009')
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

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
            payment_Intent_ID = response.get('paymentIntentId')
            ui_driver = GlobalVariables.portalDriver

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"

            query = "select setting_value from ezetap_demo.remotepay_setting where setting_name='remotePayExpTime' and org_code = '" + str(org_code)+"';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_Time = result['setting_value'].values[0]
            logger.debug(f"Query to fetch expiry_Time from the DB : {query}")
            logger.debug(f"Query result, expiry time : {expiry_Time}")

            expiry_Time_From_DB = int(expiry_Time)
            print(expiry_Time_From_DB)
            time.sleep(expiry_Time_From_DB * 60)
            ui_driver.get(paymentLinkUrl)

            remotePayTxn = remotePayTxnPage(ui_driver)
            remotePayTxn.waitForExpiryElement()
            expiryMessage = str(remotePayTxn.expiryMessage())
            logger.info(f"Your expiryMessage is:  {expiryMessage}")
            logger.info(f"Your expiryMessage is:  {expectedExpiryMessage}")
            if expiryMessage == (expectedExpiryMessage):
                pass
            else:
                raise Exception("Expiry Messages are not matching.")
    #
    #         # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

    finally:
        Configuration.executeFinallyBlock("test_common_100_103_009")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.




@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver","ui_driver") #This is an optional line. Keep only whichever driver is required.
# From below use only the markers that are applicable for the test case and remove the rest.
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_010(): #Make sure to add the test case name as same as the sub feature code.
    """
    UI_Common_PM_CNP_Credit_Card_After_Timeout_Cyber
    Verification of a message when txn done after timeout  via CNP link
    """
    expected_Timeout_Message = "Your payment attempt failed, Sorry for the inconvenience. Please contact support@ezetap.com for further clarifications."
    try:
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

        GlobalVariables.setupCompletedSuccessfully = True  #Do not remove this line of code.
        #---------------------------------------------------------------------------------------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = True, cnpwareLog = True, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            logger.info("Execution Started for the test case : test_common_100_103_010")
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_010')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_010')
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

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
            ui_driver = GlobalVariables.portalDriver
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

            query = "select setting_value from ezetap_demo.remotepay_setting where setting_name='cnpTxnTimeoutDuration' and org_code ='" + str(org_code) + "';"
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
                raise Exception("Expiry Messages are not matching.")


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
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started APP validation for the test case : test_common_100_103_010")
                expectedAppValues = {"Payment mode": "PAY LINK", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                driver = GlobalVariables.appDriver
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
                homePage.wait_for_home_page_load()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
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
                logger.info("Started API validation for the test case : test_common_100_103_010")
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
                logger.info("Started DB validation for the test case : test_common_100_103_010")
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


        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                logger.info("Started Portal validation for the test case : test_common_100_103_010")
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "CNP",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
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

        # -----------------------------------------End of Portal Validation---------------------------------------
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_common_100_103_010")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock("test_common_100_103_010")
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.

