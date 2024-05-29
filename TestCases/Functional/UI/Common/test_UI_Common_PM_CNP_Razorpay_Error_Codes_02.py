import random
import sys
import time
import pytest
from datetime import datetime
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_365():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Click_Link_After_RemotePay_Expiry_Time
    Sub Feature Description: Verify the error message by opening link after RemotePay expiry time
    TC naming code description: 100: Payment Method, 103: RemotePay, 365: TC365
    """
    expected_message = "Remote payment link has expired, Use a different mode or request for a new remote pay link to complete payment"
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select setting_value from remotepay_setting where org_code='{org_code}' and setting_name='remotePayExpTime'"
        logger.debug(f"Query to fetch data from the remotepay_setting table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from remotepay_setting table :{result}")
        remote_pay_expiry_time = int(result['setting_value'].values[0])
        logger.debug(f"Fetching remote_pay_expiry_time from the remotepay_setting table : {remote_pay_expiry_time}")

        query = f"update remotepay_setting set setting_value= '3' where org_code='{org_code}' and setting_name='remotePayExpTime';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after updating the remotepay setting")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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

            time.sleep((3 * 60) + 1)
            logger.debug(f"Waiting till link got expired")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)

                expired_message = str(remote_pay_txn.expiryMessage())
                logger.info(f"Your expected success message is:  {expired_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                if expired_message == expected_message:
                    pass
                else:
                    raise Exception("Expired Message is not matching.")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='{remote_pay_expiry_time}' where org_code='{org_code}' and setting_name='remotePayExpTime';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_366():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Attempt_Successful_Transaction_After_RemotePay_Expiry_Time
    Sub Feature Description: Verify the error message by attempting successful transaction after RemotePay expiry time
    TC naming code description: 100: Payment Method, 103: RemotePay, 366: TC366
    """
    expected_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select setting_value from remotepay_setting where org_code='{org_code}' and setting_name='remotePayExpTime'"
        logger.debug(f"Query to fetch data from the remotepay_setting table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Fetching result from remotepay_setting table :{result}")
        remote_pay_expiry_time = int(result['setting_value'].values[0])
        logger.debug(f"Fetching remote_pay_expiry_time from the remotepay_setting table : {remote_pay_expiry_time}")

        query = f"update remotepay_setting set setting_value= '3' where org_code='{org_code}' and setting_name='remotePayExpTime';"
        logger.debug(f"Query to update remotepay_setting table: {query}")
        result = DBProcessor.setValueToDB(query=query)
        logger.debug(f"query result : {result}")

        refresh_db()
        logger.debug(f"Refreshing the db after updating the remotepay setting")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                time.sleep((3 * 60) + 1)
                logger.debug(f"Waiting till link got expired")
                remote_pay_txn.click_success_pmt_btn()

                timeout_failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"Your expected success message is:  {timeout_failed_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                if timeout_failed_message == expected_message:
                    pass
                else:
                    raise Exception("Time out failed message is not matching.")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='{remote_pay_expiry_time}' where org_code='{org_code}' and setting_name='remotePayExpTime';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_367():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Attempt_Txn_With_Same_Ref_id_After_Success_Txn_Within_Duplicate_Check_Interval
    Sub Feature Description: Verify the error message by attempting  transaction with same ref id after success txn within duplicate check interval
    TC naming code description: 100: Payment Method, 103: RemotePay, 367: TC367
    """
    expected_message = "Your payment is successfully completed! You may close the browser now."
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()

                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_message}")
                assert success_message == expected_message, "Success Message is not matching."

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")

            status = response.get('success')
            logger.debug(f"From response fetch status : {status}")
            error_code = response.get('errorCode')
            logger.debug(f"From response fetch errorCode : {error_code}")
            error_message = response.get('errorMessage')
            logger.debug(f"From response fetch errorMessage : {error_message}")
            real_code = response.get('realCode')
            logger.debug(f"From response fetch realCode : {real_code}")

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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "status": False,
                    "err_msg": "You have already made a similar payment for the same Ref# " + str(
                        order_id) + " and amount " + str(
                        amount) + ".00. Please check the status of the payment(s) made before you proceed.",
                    "err_code": "EZETAP_0000033",
                    "real_code": "PAYMENT_TXN_PRCSSD_FOR_REF_AMNT"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "status": status,
                    "err_msg": error_message,
                    "err_code": error_code,
                    "real_code": real_code
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_368():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Attempt_Txn_With_Same_Ref_id_After_First_Txn_In_Progress_Within_Duplicate_Check_Interval
    Sub Feature Description: Verify the error message by attempting second transaction with same ref id after first txn in progress within duplicate check interval
    TC naming code description: 100: Payment Method, 103: RemotePay, 368: TC368
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

        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.wait_for_success_btn()

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")

            status = response.get('success')
            logger.debug(f"From response fetch status : {status}")
            message = response.get('message')
            logger.debug(f"From response fetch message : {message}")
            error_code = response.get('errorCode')
            logger.debug(f"From response fetch errorCode : {error_code}")
            error_message = response.get('errorMessage')
            logger.debug(f"From response fetch errorMessage : {error_message}")
            real_code = response.get('realCode')
            logger.debug(f"From response fetch realCode : {real_code}")

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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "status": False,
                    "msg": "Payment in progress for same Ref# " + str(order_id) + " and amount " + str(
                        amount) + ".00. Please wait few minutes and check the status of the payment(s) again before you proceed.",
                    "err_msg": "Payment in progress for same Ref# " + str(order_id) + " and amount " + str(
                        amount) + ".00. Please wait few minutes and check the status of the payment(s) again before you proceed.",
                    "err_code": "EZETAP_4000008",
                    "real_code": "PAYMENT_IN_PROGRESS"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "status": status,
                    "msg": message,
                    "err_msg": error_message,
                    "err_code": error_code,
                    "real_code": real_code
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_369():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Generate_New_Link_With_Same_Ref_id_After_Max_Attempts_Failed_Within_Duplicate_Check_Interval
    Sub Feature Description: Verify the new link generation with same ref id after max attempts failed within duplicate check interval
    TC naming code description: 100: Payment Method, 103: RemotePay, 369: TC_369
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
        query = f"select org_code from org_employee where username='{str(app_username)}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")
        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='RAZORPAY')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=True, middlewareLog=False,
                                                   config_log=False)
        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
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
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()
                msg_1 = remote_pay_txn.fetch_warning_msg_txt()

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()
                msg_2 = remote_pay_txn.fetch_warning_msg_txt()

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()
                msg_3 = remote_pay_txn.fetch_warning_msg_txt()

            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received from Remotepay_Initiate api:  {response}")
            status = response.get('success')
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
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "status": True,
                    "msg_first_link": "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications.",
                    "msg_second_link": "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications.",
                    "msg_third_link": "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
                }
                logger.debug(f"expected_api_values: {expected_api_values}")
                actual_api_values = {
                    "status": status,
                    "msg_first_link": msg_1,
                    "msg_second_link": msg_2,
                    "msg_third_link": msg_3
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
