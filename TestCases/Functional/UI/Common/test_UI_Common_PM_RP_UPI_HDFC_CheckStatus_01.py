import json
import random
import time
from datetime import datetime

import pyautogui
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
def test_common_100_103_003(): #Make sure to add the test case name as same as the sub feature code.
    username_portal = '9660867344'
    password_portal = 'A123456'
    username_app = "4455778875"
    password_app = "q121212"
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
            app_cred = ResourceAssigner.getAppUserCredentials('test_common_100_103_003')
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials('test_common_100_103_003')
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
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": username_app, "password": password_app})
            response = APIProcessor.send_request(api_details)
            ui_driver = GlobalVariables.portalDriver
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            ui_driver.get(paymentLinkUrl)
            remotePayUpiTxn = remotePayTxnPage(ui_driver)
            remotePayUpiTxn.clikOnRemotePayUPI()
            remotePayUpiTxn.clikOnRemotePayLaunchUPI()
            time.sleep(4)
            pyautogui.press('enter')
            remotePayUpiTxn.clikOnRemotePayCancelUPI()
            remotePayUpiTxn.clikOnRemotePayProceed()

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
                logger.info("Started APP validation for the test case : test_com_100_103_003")
                expectedAppValues = {"Payment mode": "UPI", "Status": "AUTHORIZED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                driver = GlobalVariables.appDriver
                loginPage = LoginPage(driver)
                loginPage.perform_login(username, password)
                homePage = HomePage(driver)
                homePage.wait_for_navigation_to_load()
                homePage.check_home_page_logo()
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
                logger.info("Started API validation for the test case : test_com_100_103_003")
                expectedAPIValues = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": username_app,
                                                                                      "password": password_app,
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
                logger.info("Started DB validation for the test case : test_com_100_103_003")
                expectedDBValues = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI",
                                    "Payment amount": amount, }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result1 = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db1 = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db1 = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount, }
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
                logger.info("Started Portal validation for the test case : test_com_100_103_003")
                expectedPortalValues = {"Payment State": "Settled", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
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
            logger.info("Started ChargeSlip validation for the test case : test_common_100_103_003")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expectedValues = {'PAID BY:':'UPI', 'merchant_ref_no': 'Ref # '+str(order_id)}
                receipt_validator.perform_charge_slip_validations(Txn_id, {"username":username,"password":password}, expectedValues)

            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.bool_chargeslip_val_result = False

            logger.info("Completed ChargeSlip validation for the test case : test_common_100_103_003")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock("test_common_100_103_003")
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
def test_common_100_103_006(): #Make sure to add the test case name as same as the sub feature code.
    """
    UI_Common_PM_RP_UPI_Failed_Via_CheckStatus_HDFC
    Verification of a Remote Pay failed UPI txn via HDFC using check status
    """
    username_portal = '9660867344'
    password_portal = 'A123456'
    username_app = "4455778875"
    password_app = "q121212"
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
            logger.info("Test Case Execution Started for the test case : test_com_100_103_006")
            amount = 111
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": username_app, "password": password_app})
            response = APIProcessor.send_request(api_details)
            ui_driver = GlobalVariables.portalDriver
            paymentLinkUrl = response['paymentLink']
            externalRef = response.get('externalRefNumber')
            ui_driver.get(paymentLinkUrl)
            remotePayUpiTxn = remotePayTxnPage(ui_driver)
            remotePayUpiTxn.clickOnRemotePayUPI()
            remotePayUpiTxn.clickOnRemotePayLaunchUPI()
            time.sleep(4)
            kb = Controller()
            kb.press(Key.esc)
            kb.release(Key.esc)
            remotePayUpiTxn.clickOnRemotePayCancelUPI()
            remotePayUpiTxn.clickOnRemotePayProceed()

            query = "select * from txn where org_code = 'SANDEEPTEST_6979' AND external_ref = '" + str(order_id) + "';"
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
                logger.info("Started APP validation for the test case : test_com_100_103_006")
                expectedAppValues = {"Payment mode": "UPI", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                driver = GlobalVariables.appDriver
                loginPage = LoginPage(driver)
                loginPage.perform_login(username_app, password_app)
                homePage = HomePage(driver)
                homePage.wait_for_navigationTo_load()
                homePage.check_home_page_logo()
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
                logger.info("Started API validation for the test case : test_com_100_103_006")
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails', request_body={"username": username_app,
                                                                                      "password": password_app,
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
                logger.info("Started DB validation for the test case : test_com_100_103_006")
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI",
                                    "Payment amount": amount, 'Transaction Type': 'REMOTE_PAY_UPI_INTENT'}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select txn_type from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result1 = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result1}")
                txnType_db1 = result1["txn_type"].iloc[0]

                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db, "Payment amount": amount_db,
                                  "Transaction Type": txnType_db1}
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
                logger.info("Started Portal validation for the test case : test_com_100_103_006")
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
                                        "Amount": "Rs." + str(amount) + ".00", "Username": username_app}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                loginPagePortal = PortalLoginPage(portal_driver)
                logger.debug(
                    f"Logging in to the portal with the username : {username_portal} and password : {password_portal}")

                loginPagePortal.perform_login_to_portal(username_portal, password_portal)
                homePagePortal = PortalHomePage(portal_driver)
                homePagePortal.search_merchant_name('SANDEEPTEST_6979')
                logger.debug(f"searching for the org_code : SANDEEPTEST_6979")
                # time.sleep(2)
                homePagePortal.perform_merchant_verfication()
                homePagePortal.click_transaction_search_menu()
                # logger.info("Clearing the text")
                # homePagePortal.perform_clear_txt()
                # logger.info("text cleared")
                # homePagePortal.perform_txn_count_search(3)
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

        # -----------------------------------------End of Portal Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:

        Configuration.executeFinallyBlock(test_common_100_103_006)
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
