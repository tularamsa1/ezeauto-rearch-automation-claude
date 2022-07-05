import random
import sys
import time
from datetime import datetime

import pytest

from Configuration import Configuration
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_sa_100_101_001():
    """
    Sub Feature Code: UI_SA_PM_UPI_Success_Via_SA_CheckStatus_HDFC
    Sub Feature Description: Verification of a successful upi txn via HDFC using SA check status
    100: Payment Method
    101: UPI
    001: TC01
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']  # rename var with app_username
        app_password = app_cred['Password']  # rename var with app_password
        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        app_driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(
                f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            home_page = HomePage(app_driver)
            home_page.wait_for_navigationTo_load()
            home_page.wait_for_home_page_load()
            home_page.check_home_page_logo()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(app_driver)
            payment_page.is_payment_page_displayed(amount, order_id)
            payment_page.click_on_Upi_paymentMode()

            logger.info("Selected payment mode is UPI")

            payment_page.click_on_back_btn()
            payment_page.click_on_transaction_cancel_yes()
            logger.debug("Clicking on proceed to home page button on the Payment successful screen on the MPOS")
            payment_page.click_on_proceed_homepage()

            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            rrn = result['rr_number'].values[0]
            txn_id = result['id'].values[0]
            status = result['status'].values[0]
            logger.debug(
                f"Fetching Txn_id and status from the payment successful screen : Txn_id : {txn_id}, status : {status}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
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
                expected_app_values = {"Payment mode": "UPI", "Status": "AUTHORIZED", "Amount": str(amount),
                                       "Txn_id": txn_id, "rrn": str(rrn)}
                logger.debug(f"expectedAppValues: {expected_app_values}")
                home_page.wait_for_navigationTo_load()
                home_page.wait_for_home_page_load()
                home_page.check_home_page_logo()
                home_page.click_on_history()
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
                app_rrn = txn_history_page.fetch_RRN_text()
                logger.info(
                    f"Fetching txn_id from txn history for the txn : {txn_id}, {app_rrn}")  # behavior is diff on both emulator and device (Number/NUMBER)

                actual_app_values = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                     "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id, "rrn": str(app_rrn)}
                logger.debug(f"actualAppValues: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
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
                expected_api_values = {"Payment Status": "AUTHORIZED", "Amount": amount, "Payment Mode": "UPI",
                                       "Payment State": "SETTLED", "rrn": str(rrn)}
                logger.debug(f"expectedAPIValues: {expected_api_values}")
                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": app_username,
                                                                        "password": app_password,
                                                                        "txnId": txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)
                status_api = response["status"]
                amount_api = int(response["amount"])  # actual=345.00, expected should be in the same format
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                #
                actual_api_values = {"Payment Status": status_api, "Amount": amount_api,
                                     "Payment Mode": payment_mode_api,
                                     "Payment State": state_api, "rrn": str(rrn_api)}
                logger.debug(f"actualAPIValues: {actual_api_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
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
                # --------------------------------------------------------------------------------------------
                expected_db_values = {"Payment Status": "AUTHORIZED", "Payment State": "SETTLED", "Payment mode": "UPI",
                                      "Payment amount": amount, "UPI_Txn_Status": "AUTHORIZED"}
                logger.debug(f"expectedDBValues: {expected_db_values}")
                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])  # actual=345.0000, expected should be in the same format
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actual_db_values = {"Payment Status": status_db, "Payment State": state_db,
                                    "Payment mode": payment_mode_db,
                                    "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actual_db_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
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
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {"Payment State": "Settled", "Payment Type": "UPI",
                                          "Amount": "Rs." + str(amount) + ".00", "Username": app_username}
                logger.debug(f"expectedPortalValues : {expected_portal_values}")
                #
                portal_driver = GlobalVariables.portalDriver
                login_page_portal = PortalLoginPage(portal_driver)
                # portal_username = '9660867344'
                # portal_password = 'A123456'
                logger.debug(
                    f"Logging in to the portal with the username : {portal_username} and password : {portal_password}")
                login_page_portal.perform_login_to_portal(portal_username, portal_password)
                home_page_portal = PortalHomePage(portal_driver)
                home_page_portal.wait_for_home_page_load()
                home_page_portal.search_merchant_name(str(org_code))
                logger.debug(f"searching for the org_code : {str(org_code)}")
                home_page_portal.click_switch_button(str(org_code))
                home_page_portal.perform_merchant_switched_verfication()
                home_page_portal.click_transaction_search_menu()

                portal_trans_history_page = PortalTransHistoryPage(portal_driver)
                portal_values_dict = portal_trans_history_page.get_transaction_details_for_portal(txn_id)
                portal_type = portal_values_dict['Type']
                portal_status = portal_values_dict['Status']
                portal_amount = portal_values_dict['Total Amount']
                portal_username = portal_values_dict['Username']

                actual_portal_values = {"Payment State": str(portal_status), "Payment Type": portal_type,
                                        "Amount": portal_amount, "Username": portal_username}
                logger.debug(f"actualPortalValues : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Portal Validation failed due to exception - " + str(e))
                logger.exception(f"Portal Validation failed due to exception : {e}")
                msg = msg + "Portal Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_portal_val_result = 'Fail'

            logger.info(f"Completed PORTAL validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        # -----------------------------------------Start of ChargeSlip Validation---------------------------------
        if (ConfigReader.read_config("Validations", "charge_slip_validation")) == "True":
            logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
            try:
                date = datetime.today().strftime('%Y-%m-%d')
                expected_values = {'PAID BY:': 'UPI', 'merchant_ref_no': 'Ref # ' + str(order_id), 'RRN': str(rrn),
                                   'BASE AMOUNT:': "Rs." + str(amount) + ".00", 'date': date}
                receipt_validator.perform_charge_slip_validations(txn_id,
                                                                  {"username": app_username, "password": app_password},
                                                                  expected_values)
            except Exception as e:
                ReportProcessor.capture_ss_when_exe_failed()
                print("Charge Slip Validation failed due to exception - " + str(e))
                logger.exception(f"Charge Slip Validation failed due to exception : {e}")
                msg = msg + "Charge Slip Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_chargeslip_val_result = "Fail"

            logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")

        # -----------------------------------------End of ChargeSlip Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        Configuration.executeFinallyBlock(testcase_id)
        if not GlobalVariables.setupCompletedSuccessfully:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)
        logger.info(f"Test case execution and validation completed for the test caseID: {testcase_id}")


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a failed UPI txn via HDFC using SA check status
def test_sa_100_101_002():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: UI_SA_PM_UPI_Failed_Via_SA_CheckStatus_HDFC
    Sub Feature Description: Verification of a failed UPI txn via HDFC using SA check status
    100: Payment Method
    101: UPI
    001: TC02
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        app_driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
            logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
            username = app_cred['Username']
            password = app_cred['Password']
            portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
            logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
            portal_username = portal_cred['Username']
            portal_password = portal_cred['Password']

            query = "select org_code from org_employee where username='" + str(username) + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_code = result['org_code'].values[0]
            logger.debug(f"Query result, org_code : {org_code}")

            loginPage = LoginPage(app_driver)
            # username = '5784758454'
            # password = 'A123456'
            logger.info(f"Logging in the MPOSX application using username : {username} and password : {password}")
            loginPage.perform_login(username, password)
            amount = random.randint(100, 200)
            order_id = datetime.now().strftime('%m%d%H%M%S')

            homePage = HomePage(app_driver)
            homePage.wait_for_navigationTo_load()
            homePage.wait_for_home_page_load()
            homePage.check_home_page_logo()
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(app_driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")
            # time.sleep(10)
            paymentPage.click_on_back_btn()
            paymentPage.click_on_transaction_cancel_yes()

            # query = "select * from upi_txn where org_code = 'UPIHDFCBANKHDFCPG' order by created_time desc limit 1;"
            query = "select * from txn where org_code = '" + str(org_code) + "' AND external_ref = '" + str(
                order_id) + "';"
            logger.debug(f"Query to fetch Txn_id, rrn from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            rrn = result['rr_number'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}, rrn : {rrn}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
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
                expectedAppValues = {"Payment mode": "UPI", "Status": "FAILED", "Amount": str(amount),
                                     "Txn_id": Txn_id, "rrn": str(rrn)}
                logger.debug(f"expectedAppValues: {expectedAppValues}")
                logger.info("reseting the com.ezetap.basicapp")
                app_driver.reset()
                loginPage.perform_login(username, password)
                homePage.wait_for_navigationTo_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()

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
                app_rrn = txnHistoryPage.fetch_RRN_text()
                logger.info(f"Fetching txn_id from txn history for the txn : {Txn_id}, {app_rrn}")

                actualAppValues = {"Payment mode": payment_mode, "Status": payment_status.split(':')[1],
                                   "Amount": app_amount.split(' ')[1], "Txn_id": app_txn_id, "rrn": str(app_rrn)}
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
                expectedAPIValues = {"Payment Status": "FAILED", "Amount": amount, "Payment Mode": "UPI",
                                     "Payment State": "FAILED", "rrn": str(rrn)}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": Txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)

                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]
                rrn_api = response["rrNumber"]
                #
                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment State": state_api, "rrn": str(rrn_api)}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
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
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "FAILED", "Payment State": "FAILED", "Payment mode": "UPI",
                                    "Payment amount": amount,
                                    "UPI_Txn_Status": "FAILED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Failed", "Payment Type": "UPI",
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
                logger.debug(f"actualPortalValues : {actualPortalValues}")
                # ---------------------------------------------------------------------------------------------
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
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)


@pytest.mark.usefixtures("log_on_success", "method_setup")  # Mandatory line.
@pytest.mark.usefixtures("appium_driver", "ui_driver")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
# Performing a upi txn after expiry for HDFC using SA check status
def test_sa_100_101_003():  # Make sure to add the test case name as same as the sub feature code.
    """
    Sub Feature Code: UI_Common_PM_UPI_CheckStatus_After Expiry_HDFC
    Sub Feature Description: Verification of a upi txn after expiry for HDFC using SA check status
    100: Payment Method
    101: UPI
    001: TC03
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        logger.info(f"Starting execution for the test case : {testcase_id}")
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info("Performing preconditions before starting test case execution")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        username = app_cred['Username']
        password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                "password": portal_password,
                                                                                "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 1
        logger.debug(f"API details  : {api_details} ")
        print("***********API DETAILS **********:", api_details)
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")
        logger.info("Finished performing preconditions before starting test case execution")

        # url = "https://dev11.ezetap.com//api/2.0/setting/update/ "
        #
        # payload = json.dumps({
        #     "username": "9660867345",
        #     "password": "A123456",
        #     "entityName": "org",
        #     "settings": {
        #         "upiQRExpiryTime": 1
        #     },
        #     "settingForOrgCode": "UPIHDFCBANKHDFCPG"
        # })
        # headers = {
        #     'Content-Type': 'application/json'
        # }
        #
        # response = requests.request("POST", url, headers=headers, data=payload)
        #
        # print(response.text)

        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        driver = GlobalVariables.appDriver
        msg = ""
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            loginPage = LoginPage(driver)
            # username = '5784758454'
            # password = 'A123456'
            logger.info(f"Logging in the MPOSX application using username : {username} and password : {password}")
            loginPage.perform_login(username, password)
            amount = random.randint(51, 100)
            if amount == 55:
                amount = 56
            order_id = datetime.now().strftime('%m%d%H%M%S')
            homePage = HomePage(driver)
            homePage.wait_for_navigationTo_load()
            homePage.wait_for_home_page_load()
            homePage.check_home_page_logo()
            homePage.enter_amount_and_order_number(amount, order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            paymentPage = PaymentPage(driver)
            paymentPage.is_payment_page_displayed(amount, order_id)
            paymentPage.click_on_Upi_paymentMode()
            logger.info("Selected payment mode is UPI")

            logger.info("reseting the com.ezetap.basicapp")
            driver.reset()
            logger.info("waiting for the time till qr get expired...")
            time.sleep(60)

            loginPage.perform_login(username, password)
            homePage.wait_for_home_page_load()
            logger.info(
                f"After reseting the app logging in again in the MPOSX application using username : {username} and password : {password}")
            homePage.enter_amount_and_order_number(amount, order_id)
            paymentPage = PaymentPage(driver)
            homePage.perform_check_status()
            paymentPage.click_on_proceed_homepage()
            homePage.click_on_back_btn_enter_amt_page()

            # paymentPage.click_on_proceed_homepage()
            # paymentPage.click_on_back_btn()

            query = "select id from txn where org_code='" + org_code + "' and external_ref='" + order_id + "' order by created_time desc limit 1"
            logger.debug(f"Query to fetch Txn_id from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            Txn_id = result['id'].values[0]
            logger.debug(f"Query result, Txn_id : {Txn_id}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            ReportProcessor.capture_ss_when_exe_failed()
            GlobalVariables.bool_ss_app_val = 'Failed'
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
                expectedAppValues = {"Payment mode": "UPI", "Status": "EXPIRED", "Amount": str(amount),
                                     "Txn_id": Txn_id}
                # driver.reset()
                homePage.wait_for_navigationTo_load()
                homePage.wait_for_home_page_load()
                homePage.check_home_page_logo()
                homePage.click_on_history()
                txnHistoryPage = TransHistoryPage(driver)
                # txnHistoryPage.click_first_amount_field()
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
                expectedAPIValues = {"Payment Status": "EXPIRED", "Amount": amount, "Payment Mode": "UPI",
                                     "Payment State": "EXPIRED"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                api_details = DBProcessor.get_api_details('txnDetails',
                                                          request_body={"username": username, "password": password,
                                                                        "txnId": Txn_id})
                print("API DETAILS:", api_details)
                response = APIProcessor.send_request(api_details)

                status_api = response["status"]
                amount_api = int(response["amount"])
                payment_mode_api = response["paymentMode"]
                state_api = response["states"][0]

                actualAPIValues = {"Payment Status": status_api, "Amount": amount_api, "Payment Mode": payment_mode_api,
                                   "Payment State": state_api}
                logger.debug(f"actualAPIValues: {actualAPIValues}")
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
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"Payment Status": "EXPIRED", "Payment State": "EXPIRED", "Payment mode": "UPI",
                                    "Payment amount": amount,
                                    "UPI_Txn_Status": "EXPIRED"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select state,status,amount,payment_mode,external_ref from txn where id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                status_db = result["status"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                amount_db = int(result["amount"].iloc[0])
                state_db = result["state"].iloc[0]

                query = "select status from upi_txn where txn_id='" + Txn_id + "'"
                logger.debug(f"Query to fetch data from upi_txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                upi_status_db = result["status"].iloc[0]
                actualDBValues = {"Payment Status": status_db, "Payment State": state_db,
                                  "Payment mode": payment_mode_db,
                                  "Payment amount": amount_db, "UPI_Txn_Status": upi_status_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expectedPortalValues = {"Payment State": "Expired", "Payment Type": "UPI",
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
                logger.debug(f"actualPortalValues : {actualPortalValues}")
                # ---------------------------------------------------------------------------------------------
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
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
            logger.error("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)

            # -------------------------------Revert Preconditions done(setup)--------------------------------------------

            logger.info(f"Reverting all the settings that were done as preconditions for test case : {testcase_id}")
            api_details = DBProcessor.get_api_details('QRExpiryTime', request_body={"username": portal_username,
                                                                                    "password": portal_password,
                                                                                    "settingForOrgCode": org_code})
            api_details["RequestBody"]["settings"]["upiQRExpiryTime"] = 6
            logger.debug(f"API details  : {api_details} ")
            print("***********API DETAILS **********:", api_details)
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for setting preconditions is : {response}")
            logger.info("Reverted back all the settings that were done as preconditions")
            # ----------------------------------------------------------------------------------------------------------

            # url = "https://dev11.ezetap.com//api/2.0/setting/update/ "
            #
            # payload = json.dumps({
            #     "username": "9660867345",
            #     "password": "A123456",
            #     "entityName": "org",
            #     "settings": {
            #         "upiQRExpiryTime": 6
            #     },
            #     "settingForOrgCode": "UPIHDFCBANKHDFCPG"
            # })
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            #
            # response = requests.request("POST", url, headers=headers, data=payload)
            #
            # print(response.text)
