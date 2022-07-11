import random
import sys
import time
from datetime import datetime
import allure
import pandas as pd
import pytest
import requests
from allure_commons.types import AttachmentType
from Configuration import TestSuiteSetup, Configuration
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from Utilities import ReportProcessor, Validator, ConfigReader, APIProcessor, DBProcessor, receipt_validator, \
    ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)



@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_102_040():
    """
    :Description: Verification of  a BQR UPG txn when Auto refund is enabled via HDFC
    :Sub Feature code: UI_Common_PM_BQR_UPG_AUTOREFUND_ENABLED_HDFC_19
    :TC naming code description: 100->Payment Method
                                102->BQR
                                019-> TC19
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

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

        logger.info("Finished performing preconditions before starting test case execution")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        app_driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            amount = random.randint(300, 500)

            query = "select * from upi_merchant_config where bank_code = 'HDFC' AND status = 'ACTIVE' AND org_code = " \
                    "'" + str(org_code) + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch pgMerchantId and vpa from upi_merchant_config : {query}")
            result = DBProcessor.getValueFromDB(query)
            pgMerchantId = result['pgMerchantId'].values[0]
            vpa = result['vpa'].values[0]
            logger.debug(f"Query result, vpa : {vpa} and pgMerchantId : {pgMerchantId}")

            request_id  = '220518115526031E' + str(random.randint(10000000, 999999999))
            vpa = 'abccccc@ybl'
            amount = random.randint(300, 399)
            rrn = random.randint(1111110, 9999999)
            ref_id = '211115084892E01' + str(rrn)
            logger.debug(f"generated random request_id is : {request_id}")
            logger.debug(f"passing vpa is : {vpa}")
            logger.debug(f"generated random amount is : {amount}")
            logger.debug(f"generated random rrn number is : {rrn}")
            logger.debug(f"generated random ref_id number is : {ref_id}")
            # time.sleep(15)
            # query = ("select * from invalid_pg_request where request_id ='" + request_id + "';")
            # print(query)
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # result = DBProcessor.getValueFromDB(query)
            # print(result)
            # txn_id = result['txn_id'].iloc[0]

            logger.debug(
                f"replacing the Txn_id with {request_id}, amount with {amount}.00, vpa with {vpa} and rrn with {rrn} in the curl_data "
                f"reference id with {ref_id}")
            api_details = DBProcessor.get_api_details('upi_success_curl',
                                                      curl_data={'ref_id': ref_id, 'Txn_id': request_id,
                                                                 'amount': str(amount) + ".00",
                                                                 'vpa': vpa, 'rrn': rrn
                                                                 })
            print(api_details['CurlData'])
            curl_data = api_details['CurlData']
            logger.debug(f"After replacing the data the updated curl_data is : {curl_data}")

            data_buffer = ''

            ssh_stdin, ssh_stdout, ssh_stderr = TestSuiteSetup.GlobalVariables.ssh.exec_command(curl_data, get_pty=True)
            for line in iter(lambda: ssh_stdout.readline(), ''):
                data_buffer += line
            logger.debug(f"OUTPUT : {data_buffer}")

            logger.debug(
                f"preparing the request payload data to trigger the /api/2.0/upimerchant/hdfc/callBackUpiMerchantRes")
            api_details = DBProcessor.get_api_details('callBackUpiMerchantRes',
                                                      request_body={'pgMerchantId': str(pgMerchantId),
                                                                    'meRes': str(data_buffer)})
            response = APIProcessor.send_request(api_details)
            print(response)

            query = ("select * from invalid_pg_request where request_id ='" + request_id + "';")
            print(query)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            q_result = DBProcessor.getValueFromDB(query)
            print(q_result)
            txn_id = q_result['txn_id'].iloc[0]

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
                          attachment_type=AttachmentType.PNG)
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            logger.error(f"Test case execution failed due to the exception : {e}")
            pytest.fail("Test case execution failed due to the exception -" + str(e))

        logger.info(f"Execution is completed for the test case : {testcase_id}")
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------

        logger.info(f"Starting validation for the test case : {testcase_id}")

        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of App Validation---------------------------------
        if (ConfigReader.read_config("Validations", "app_validation")) == "True":
            logger.info(f"Started APP validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expectedAppValues = {"Payment mode": "UPI", "Payment Txn ID": txn_id, "Payment Amt": str(amount),
                                     "Payment Status": "UPG_AUTHORIZED", "rrn": str(rrn)}
                loginPage = LoginPage(app_driver)
                logger.info(
                    f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
                loginPage.perform_login(app_username, app_password)

                homePage = HomePage(app_driver)
                homePage.wait_for_navigation_to_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()
                homePage.click_on_history()
                transactionsHistoryPage = TransHistoryPage(app_driver)
                transactionsHistoryPage.click_on_transaction_by_txn_id(txn_id)
                app_payment_status_original = transactionsHistoryPage.fetch_txn_status_text()
                logger.debug(
                    f"Fetching Transaction status of original txn from transaction history of MPOS app: Txn status = {app_payment_status_original}")
                app_payment_mode_original = transactionsHistoryPage.fetch_txn_type_text()
                logger.debug(
                    f"Fetching Transaction payment mode of original txn from transaction history of MPOS app: Txn "
                    f"Mode = {app_payment_mode_original}")
                app_txn_id_original = transactionsHistoryPage.fetch_txn_id_text()
                logger.debug(
                    f"Fetching Transaction id of original txn from transaction history of MPOS app: Txn Id = {app_txn_id_original}")
                app_payment_amt_original = transactionsHistoryPage.fetch_txn_amount_text().split()[1]
                logger.debug(
                    f"Fetching Transaction amount of orginal txn from transaction history of MPOS app: Txn Amt = {app_payment_amt_original}")
                app_rrn_original = transactionsHistoryPage.fetch_RRN_text()
                logger.debug(f"Fetching rrn from txn history for the txn : {txn_id}, {app_rrn_original}")

                actualAppValues = {"Payment Status": app_payment_status_original.split(':')[1],
                                   "Payment mode": app_payment_mode_original,
                                   "Payment Txn ID": app_txn_id_original,
                                   "Payment Amt": str(app_payment_amt_original),
                                   "rrn": str(app_rrn_original)}

                logger.debug(f"actualAppValues: {actualAppValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expectedAppValues, actualApp=actualAppValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("App Validation failed due to exception - " + str(e))
                logger.exception(f"App Validation failed due to exception - {e}")
                msg = msg + "App Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_app_val_result = "Fail"

            logger.info(f"Completed APP validation for the test case : {testcase_id}")

        # -----------------------------------------End of App Validation---------------------------------------

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expectedAPIValues = {"Payment Status": "UPG_AUTHORIZED",
                                     "Amount": amount,
                                     "Payment State": "UPG_AUTHORIZED",
                                     "Payment Mode": "UPI",
                                     "rrn": str(rrn)}

                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username, "password": app_password,
                                                                        "txnId": txn_id})
                print("API DETAILS for original_txn_id:", api_details)
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for transaction details api is : {response}")
                print(response)

                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]

                actualAPIValues = {"Payment Status": status_api,
                                   "Amount": amount_api,
                                   "Payment State": state_api,
                                   "Payment Mode": payment_mode_api,
                                   "rrn": str(rrn_api)}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception : {e} ")
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = 'Fail'

            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expectedDBValues = {"Payment Status": "UPG_AUTHORIZED",
                                    "Payment State": "UPG_AUTHORIZED",
                                    "UPI_Txn_Status": "UPG_AUTHORIZED",
                                    "Payment mode": "UPI",
                                    "Payment amount": amount}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]

                actualDBValues = {"Payment Status": status_db,
                                  "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db,
                                  "UPI_Txn_Status": upi_status_db}

                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                logger.exception(f"DB Validation failed due to exception :  {e}")
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started PORTAL validation for the test case : {testcase_id}")
            try:
                expectedPortalValues = {"Payment Type": "UPI",
                                        "Payment State": "Upg Authorized",
                                        "Amount": "Rs." + str(amount) + ".00"}
                logger.debug(f"expectedPortalValues : {expectedPortalValues}")

                portal_driver = GlobalVariables.portalDriver
                login_page_portal = PortalLoginPage(portal_driver)

                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)

                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.search_merchant_name(org_code)
                logger.debug(f"searching for the org_code : {org_code}")

                home_page_portal.click_switch_button(org_code)
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()
                portal_trans_history_page = PortalTransHistoryPage(portal_driver)

                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_txn_type = portal_values_dict['Type']
                portal_state = portal_values_dict['Status']
                portal_amt = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                logger.debug(f"Fetching Transaction state from portal : {portal_state} ")
                logger.debug(f"Fetching Transaction type from portal : {portal_txn_type} ")
                logger.debug(f"Fetching Transaction amount from portal : {portal_amt} ")
                logger.debug(f"Fetching Username from portal : {portal_username} ")

                actualPortalValues = {"Payment Type": portal_txn_type,
                                      "Payment State": portal_state,
                                      "Amount": portal_amt}

                logger.debug(f"actualPortalValues : {actualPortalValues}")
                Validator.validateAgainstPortal(expectedPortal=expectedPortalValues, actualPortal=actualPortalValues)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------
    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
            # -------------------------------Revert Preconditions done(setup)--------------------------------------------

            logger.info("Reverted back all the settings that were done as preconditions")