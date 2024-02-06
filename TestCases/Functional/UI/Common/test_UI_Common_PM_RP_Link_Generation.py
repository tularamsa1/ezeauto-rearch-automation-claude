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
from PageFactory.sa.app_payment_page import PaymentPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, receipt_validator, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_103_324():
    """
     Sub Feature Code: UI_Common_PM_RP_Link_Generation_Success_Valid_Amount
     Sub Feature Description: Enter the valid sale amount and click on Remote pay option to create the link
     TC naming code description: 100: Payment Method, 103: RemotePay, 324: TC324
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True)
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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number(amt=amount, order_number=order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed(amount=amount, order_id=order_id)
            payment_page.click_on_remote_pay_payment_mode()
            check_customer_mobile = payment_page.check_customer_mobile_number_field_visible()
            if check_customer_mobile:
                msg1 = "customer mobile number field visible"
            else:
                msg1 = "customer mobile number field not visible"

            check_agent_mobile = payment_page.check_agent_mobile_number_field_visible()
            if check_agent_mobile:
                msg2 = "agent mobile number field visible"
            else:
                msg2 = "agent mobile number field not visible"
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
                expected_app_values = {
                    "customer_mobile_visible": "customer mobile number field visible",
                    "agent_mobile_visible": "agent mobile number field visible"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "customer_mobile_visible": msg1,
                    "agent_mobile_visible": msg2
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.appVal
def test_common_100_103_325():
    """
     Sub Feature Code: UI_Common_PM_RP_Link_Generation_Success_Mobile_Number_Mandatory
     Sub Feature Description: Mobile Number field is mandatory for the Remote pay link Generation
     TC naming code description: 100: Payment Method, 103: RemotePay, 325: TC325
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

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True)
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
            app_driver = TestSuiteSetup.initialize_app_driver(request=testcase_id)
            login_page = LoginPage(driver=app_driver)
            login_page.perform_login(username=app_username, password=app_password)
            logger.info(f"Logging in the MPOSX application using username : {app_username}")
            home_page = HomePage(driver=app_driver)
            home_page.check_home_page_logo()
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            logger.info(f"App homepage loaded successfully")
            home_page.enter_amount_and_order_number(amt=amount, order_number=order_id)
            logger.debug(f"Entered amount is : {amount}")
            logger.debug(f"Entered order_id is : {order_id}")
            payment_page = PaymentPage(driver=app_driver)
            payment_page.is_payment_page_displayed(amount=amount, order_id=order_id)
            payment_page.click_on_remote_pay_payment_mode()
            payment_page.clink_on_send_link_btn()
            error_msg_mobile_number = payment_page.fetch_mobile_number_error_msg_for_remote_pay()
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
                expected_app_values = {
                    "err_msg": "Enter a valid phone number"
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                actual_app_values = {
                    "err_msg": error_msg_mobile_number
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstAPP(expectedApp=expected_app_values, actualApp=actual_app_values)
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case : {testcase_id}")
        # -----------------------------------------End of App Validation---------------------------------------

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
def test_common_100_103_326():
    """
    Sub Feature Code: UI_Common_PM_RP_Setting_Minimum_Amount_Success_Transaction
    Sub Feature Description: Success Remote Pay transaction via HDFC when Transaction Amount equal to the Minimum amount set in Org Setting.
    TC naming code description: 100: Payment Method, 103: RemotePay, 326: TC326
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "300"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "301"

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for minimum and maximum txn amount:  {response}")

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
            amount = 300
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
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "9999999999"

            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for minimum and maximum txn amount:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_343():
    """
    Sub Feature Code: UI_Common_PM_RP_Setting_Minimum_Amount_Success_Transaction
    Sub Feature Description: Success Remote Pay transaction via axis_direct when Transaction Amount equal to the Minimum amount set in Org Setting.
    TC naming code description: 100: Payment Method, 103: RemotePay, 343: TC343
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

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code
        })
        api_details["RequestBody"]["settings"]["minTxnAmount"] = "300"
        api_details["RequestBody"]["settings"]["maxTxnAmount"] = "301"

        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Response received for minimum and maximum txn amount:  {response}")

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
            amount = 300
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
        try:
            api_details = DBProcessor.get_api_details('org_settings_update', request_body={
                "username": portal_username,
                "password": portal_password,
                "entityName": "org",
                "settingForOrgCode": org_code
            })
            api_details["RequestBody"]["settings"]["minTxnAmount"] = "1"
            api_details["RequestBody"]["settings"]["maxTxnAmount"] = "9999999999"

            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details=api_details)
            logger.debug(f"Response received for minimum and maximum txn amount:  {response}")
        except Exception as e:
            logger.exception(f"org setting updation failed due to expection : {e}")
        Configuration.executeFinallyBlock(testcase_id)



