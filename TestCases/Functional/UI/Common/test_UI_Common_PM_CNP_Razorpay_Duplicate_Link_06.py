import random
import sys
import time
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from PageFactory.merchant_portal.portal_trans_history_page import get_transaction_details_for_portal
from PageFactory.mpos.app_home_page import HomePage
from PageFactory.mpos.app_login_page import LoginPage
from PageFactory.sa.app_trans_history_page import TransHistoryPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_404():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_One_Link_Opened_Two_Tabs_First_Txn_Netbanking_In_Progress_Second_Txn_Debit_Card
    Sub Feature Description: Try to make successful payment using Netbanking and then try to make a transaction using Debit Card by opening same link in 2 Tabs when max pay attempts is one
    TC naming code description: 100: Payment Method, 103: RemotePay, 404: TC404
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
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

        query = f"update remotepay_setting set setting_value= '1' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
            expected_progress_message = f"Transaction for the Reference Number: {order_id} and amount {amount}"+".00"+" is in progress. Wait for it to complete."
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page_1 = TestSuiteSetup.initialize_ui_browser()
                page_1.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_Rzp()
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.wait_for_success_btn()

                page_2 = TestSuiteSetup.initialize_ui_browser()
                page_2.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_2)
                progress_message = str(remote_pay_txn.in_progress_screen_message())
                logger.info(f"Your progress message is:  {progress_message}")
                logger.info(f"Your expected Message is:  {expected_progress_message}")
                assert progress_message == expected_progress_message, "Progress Message is not matching."

                page_1.bring_to_front()
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

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
            query = f"update remotepay_setting set setting_value='2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
def test_common_100_103_405():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_One_Link_Opened_Two_Browsers_First_Txn_Netbanking_In_Progress_Second_Txn_Netbanking
    Sub Feature Description: Try to make successful payment using Netbanking and then try to make a transaction using same Netbanking by opening same link in 2 browsers when max pay attempts is one
    TC naming code description: 100: Payment Method, 103: RemotePay, 405: TC405
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
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

        query = f"update remotepay_setting set setting_value= '1' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
            expected_progress_message = f"Transaction for the Reference Number: {order_id} and amount {amount}" + ".00" + " is in progress. Wait for it to complete."
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                page_1 = TestSuiteSetup.initialize_ui_browser()
                page_1.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_Rzp()
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.wait_for_success_btn()

                TestSuiteSetup.launch_browser_and_context_initialize("firefox")
                page_2 = TestSuiteSetup.initialize_ui_browser()
                page_2.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_2)
                progress_message = str(remote_pay_txn.in_progress_screen_message())
                logger.info(f"Your progress message is:  {progress_message}")
                logger.info(f"Your expected Message is:  {expected_progress_message}")
                assert progress_message == expected_progress_message, "Progress Message is not matching."

                page_1.bring_to_front()
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

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
            query = f"update remotepay_setting set setting_value='2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
def test_common_100_103_406():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_One_Failed_Attempts_Two_Same_Link
    Sub Feature Description: Try to make two failed attempts to the same link with Failed state when max pay attempts is one
    TC naming code description: 100: Payment Method, 103: RemotePay, 406: TC406
    """
    expected_message = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
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

        query = f"update remotepay_setting set setting_value= '1' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_Rzp()
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.click_failure_pmt_btn()
                max_attempt_message = str(remote_pay_txn.maxAttemptsMessage())
                logger.info(f"Your expected max_attempt message is:  {max_attempt_message}")
                logger.info(f"Your expected message is:  {expected_message}")
                assert max_attempt_message == expected_message, "Message is not matching."

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
            query = f"update remotepay_setting set setting_value='2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_103_407():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_Two_Link_Opened_Two_Browsers_First_Txn_Credit_Card_Failed_Second_Txn_Debit_Card_Success
    Sub Feature Description:Try to make Failed payment using Credit card and then try to make a success transaction using Debit Card by opening same link in 2 browser when max pay attempts is two
    TC naming code description: 100: Payment Method, 103: RemotePay, 407: TC407
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
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

        query = f"update remotepay_setting set setting_value= '2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
                page_1 = TestSuiteSetup.initialize_ui_browser()
                page_1.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()
                failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"Your failed message is:  {failed_message}")
                logger.info(f"Your expected Message is:  {expected_failed_message}")
                assert failed_message == expected_failed_message, "Failed Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

                TestSuiteSetup.launch_browser_and_context_initialize("firefox")
                page_2 = TestSuiteSetup.initialize_ui_browser()
                page_2.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_2)
                remote_pay_txn.clickOnDebitCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id_2 = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch txn details from the txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for failed txn: {settle_status}")
                pmt_status = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for failed txn: {pmt_status}")
                payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for failed txn: {payment_mode}")
                pmt_state = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for failed txn: {pmt_state}")
                amount_txn = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for failed txn: {amount_txn}")
                order_id_txn = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for failed txn: {order_id_txn}")
                payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for failed txn: {payment_gateway}")

                query = f"select * from txn where id='{txn_id_2}'"
                logger.debug(f"Query to fetch txn details from the txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status_2 = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for success txn: {settle_status_2}")
                pmt_status_2 = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for success txn: {pmt_status_2}")
                payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for success txn: {payment_mode_2}")
                pmt_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for success txn: {pmt_state_2}")
                amount_txn_2 = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for success txn: {amount_txn_2}")
                order_id_txn_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for success txn: {order_id_txn_2}")
                payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for success txn: {payment_gateway_2}")

                query = f"select * from cnp_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for failed txn: {cnp_txn_payment_option}")
                cnp_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for failed txn: {cnp_txn_payment_flow}")
                cnp_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for failed txn: {cnp_txn_payment_status}")
                cnp_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for failed txn: {cnp_txn_type}")
                cnp_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for failed txn: {cnp_txn_payment_mode}")
                cnp_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for failed txn: {cnp_txn_payment_state}")
                cnp_txn_payment_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Fetching payment_card_type from cnp_txn table for failed txn: {cnp_txn_payment_card_type}")
                cnp_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table for failed txn: {cnp_txn_payment_gateway}")

                query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option_2 = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for success txn: {cnp_txn_payment_option_2}")
                cnp_txn_payment_flow_2 = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for success txn: {cnp_txn_payment_flow_2}")
                cnp_txn_payment_status_2 = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for success txn: {cnp_txn_payment_status_2}")
                cnp_txn_type_2 = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for success txn: {cnp_txn_type_2}")
                cnp_txn_payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for success txn: {cnp_txn_payment_mode_2}")
                cnp_txn_payment_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for success txn: {cnp_txn_payment_state_2}")
                cnp_txn_payment_card_type_2 = result['payment_card_type'].values[0]
                logger.debug(f"Fetching payment_card_type from cnp_txn table for success txn: {cnp_txn_payment_card_type_2}")
                cnp_txn_payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table for success txn: {cnp_txn_payment_gateway_2}")

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
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_FAILED",
                    "cnp_pmt_state": "FAILED",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "pmt_gateway_2": "RAZORPAY",

                    "cnp_pmt_option_2": "CNP_DC",
                    "cnp_pmt_flow_2": "REMOTEPAY",
                    "cnp_pmt_status_2": "PAYMENT_COMPLETED",
                    "cnp_pmt_state_2": "SETTLED",
                    "cnp_pmt_card_type_2": "DEBIT",
                    "cnp_txn_type_2": "REMOTE_PAY",
                    "cnp_pmt_mode_2": "CNP",
                    "cnp_pmt_gateway_2": "RAZORPAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "pmt_gateway": payment_gateway,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "pmt_gateway_2": payment_gateway_2,

                    "cnp_pmt_option_2": cnp_txn_payment_option_2,
                    "cnp_pmt_flow_2": cnp_txn_payment_flow_2,
                    "cnp_pmt_status_2": cnp_txn_payment_status_2,
                    "cnp_pmt_state_2": cnp_txn_payment_state_2,
                    "cnp_pmt_card_type_2": cnp_txn_payment_card_type_2,
                    "cnp_txn_type_2": cnp_txn_type_2,
                    "cnp_pmt_mode_2": cnp_txn_payment_mode_2,
                    "cnp_pmt_gateway_2": cnp_txn_payment_gateway_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_103_408():
    """
    Sub Feature Code: UI_Common_PM_CNP_Remotepay_Razorpay_Max_Pay_Attempts_Two_Link_Opened_Two_Browsers_First_Txn_Credit_Card_Failed_Second_Txn_Netbanking_Success
    Sub Feature Description: Try to make Failed payment using Credit card and then try to make a success transaction using Netbanking by opening same link in 2 browser when max pay attempts is two
    TC naming code description: 100: Payment Method, 103: RemotePay, 408: TC408
    """
    expected_success_message = "Your payment is successfully completed! You may close the browser now."
    expected_failed_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
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

        query = f"update remotepay_setting set setting_value= '2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
                page_1 = TestSuiteSetup.initialize_ui_browser()
                page_1.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.clickOnCreditCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                remote_pay_txn.enterCreditCardExpiryMonth("3")
                remote_pay_txn.enterCreditCardExpiryYear("2048")
                remote_pay_txn.enterCreditCardCvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.click_failure_pmt_btn()
                failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"Your failed message is:  {failed_message}")
                logger.info(f"Your expected Message is:  {expected_failed_message}")
                assert failed_message == expected_failed_message, "Failed Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id}")

                TestSuiteSetup.launch_browser_and_context_initialize("firefox")
                page_2 = TestSuiteSetup.initialize_ui_browser()
                page_2.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_2)
                remote_pay_txn.remote_pay_netbanking()
                remote_pay_txn.remote_pay_click_and_expand_netbanking()
                remote_pay_txn.remote_pay_select_netbanking_Rzp()
                remote_pay_txn.remote_pay_proceed_netbanking()
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

                query = f"select * from txn where org_code='{org_code}' and external_ref='{order_id}' order by created_time " \
                        f"desc limit 1 "
                logger.debug(f"Query to fetch txn details from the txn table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                txn_id_2 = result['id'].values[0]
                logger.debug(f"Fetching txn_id from the txn table : {txn_id_2}")

                query = f"select * from txn where id='{txn_id}'"
                logger.debug(f"Query to fetch txn details from the txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for failed txn: {settle_status}")
                pmt_status = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for failed txn: {pmt_status}")
                payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for failed txn: {payment_mode}")
                pmt_state = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for failed txn: {pmt_state}")
                amount_txn = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for failed txn: {amount_txn}")
                order_id_txn = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for failed txn: {order_id_txn}")
                payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for failed txn: {payment_gateway}")

                query = f"select * from txn where id='{txn_id_2}'"
                logger.debug(f"Query to fetch txn details from the txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result from txn table :{result}")
                settle_status_2 = result['settlement_status'].values[0]
                logger.debug(f"Fetching settlement_status from the txn table for success txn: {settle_status_2}")
                pmt_status_2 = result['status'].values[0]
                logger.debug(f"Fetching status from the txn table for success txn: {pmt_status_2}")
                payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from the txn table for success txn: {payment_mode_2}")
                pmt_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from the txn table for success txn: {pmt_state_2}")
                amount_txn_2 = result['amount'].values[0]
                logger.debug(f"Fetching amount from the txn table for success txn: {amount_txn_2}")
                order_id_txn_2 = result['external_ref'].values[0]
                logger.debug(f"Fetching order_id from the txn table for success txn: {order_id_txn_2}")
                payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from the txn table for success txn: {payment_gateway_2}")

                query = f"select * from cnp_txn where txn_id = '{txn_id}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for failed txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for failed txn: {cnp_txn_payment_option}")
                cnp_txn_payment_flow = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for failed txn: {cnp_txn_payment_flow}")
                cnp_txn_payment_status = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for failed txn: {cnp_txn_payment_status}")
                cnp_txn_type = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for failed txn: {cnp_txn_type}")
                cnp_txn_payment_mode = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for failed txn: {cnp_txn_payment_mode}")
                cnp_txn_payment_state = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for failed txn: {cnp_txn_payment_state}")
                cnp_txn_payment_card_type = result['payment_card_type'].values[0]
                logger.debug(f"Fetching payment_card_type from cnp_txn table for failed txn: {cnp_txn_payment_card_type}")
                cnp_txn_payment_gateway = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table for failed txn: {cnp_txn_payment_gateway}")

                query = f"select * from cnp_txn where txn_id = '{txn_id_2}'"
                logger.debug(f"Query to fetch data from the cnp_txn table for success txn: {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Fetching result for cnp_txn table : {result} ")
                cnp_txn_payment_option_2 = result['payment_option'].values[0]
                logger.debug(f"Fetching payment_option from cnp_txn table for success txn: {cnp_txn_payment_option_2}")
                cnp_txn_payment_flow_2 = result['payment_flow'].values[0]
                logger.debug(f"Fetching payment_flow from cnp_txn table for success txn: {cnp_txn_payment_flow_2}")
                cnp_txn_payment_status_2 = result['payment_status'].values[0]
                logger.debug(f"Fetching payment_status from cnp_txn table for success txn: {cnp_txn_payment_status_2}")
                cnp_txn_type_2 = result['txn_type'].values[0]
                logger.debug(f"Fetching txn_type from cnp_txn table for success txn: {cnp_txn_type_2}")
                cnp_txn_payment_mode_2 = result['payment_mode'].values[0]
                logger.debug(f"Fetching payment_mode from cnp_txn table for success txn: {cnp_txn_payment_mode_2}")
                cnp_txn_payment_state_2 = result['state'].values[0]
                logger.debug(f"Fetching state from cnp_txn table for success txn: {cnp_txn_payment_state_2}")
                cnp_txn_payment_gateway_2 = result['payment_gateway'].values[0]
                logger.debug(f"Fetching payment_gateway from cnp_txn table for success txn: {cnp_txn_payment_gateway_2}")

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
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "pmt_status": "FAILED",
                    "pmt_state": "FAILED",
                    "pmt_mode": "CNP",
                    "txn_amt": float(amount),
                    "order_id": order_id,
                    "settle_status": "FAILED",
                    "pmt_gateway": "RAZORPAY",

                    "cnp_pmt_option": "CNP_CC",
                    "cnp_pmt_flow": "REMOTEPAY",
                    "cnp_pmt_status": "PAYMENT_FAILED",
                    "cnp_pmt_state": "FAILED",
                    "cnp_pmt_card_type": "CREDIT",
                    "cnp_txn_type": "REMOTE_PAY",
                    "cnp_pmt_mode": "CNP",
                    "cnp_pmt_gateway": "RAZORPAY",

                    "pmt_status_2": "AUTHORIZED",
                    "pmt_state_2": "SETTLED",
                    "pmt_mode_2": "CNP",
                    "txn_amt_2": float(amount),
                    "order_id_2": order_id,
                    "settle_status_2": "SETTLED",
                    "pmt_gateway_2": "RAZORPAY",

                    "cnp_pmt_option_2": "CNP_NB",
                    "cnp_pmt_flow_2": "REMOTEPAY",
                    "cnp_pmt_status_2": "PAYMENT_COMPLETED",
                    "cnp_pmt_state_2": "SETTLED",
                    "cnp_txn_type_2": "REMOTE_PAY",
                    "cnp_pmt_mode_2": "CNP",
                    "cnp_pmt_gateway_2": "RAZORPAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "pmt_status": pmt_status,
                    "pmt_state": pmt_state,
                    "pmt_mode": payment_mode,
                    "txn_amt": amount_txn,
                    "order_id": order_id_txn,
                    "settle_status": settle_status,
                    "pmt_gateway": payment_gateway,

                    "cnp_pmt_option": cnp_txn_payment_option,
                    "cnp_pmt_flow": cnp_txn_payment_flow,
                    "cnp_pmt_status": cnp_txn_payment_status,
                    "cnp_pmt_state": cnp_txn_payment_state,
                    "cnp_pmt_card_type": cnp_txn_payment_card_type,
                    "cnp_txn_type": cnp_txn_type,
                    "cnp_pmt_mode": cnp_txn_payment_mode,
                    "cnp_pmt_gateway": cnp_txn_payment_gateway,

                    "pmt_status_2": pmt_status_2,
                    "pmt_state_2": pmt_state_2,
                    "pmt_mode_2": payment_mode_2,
                    "txn_amt_2": amount_txn_2,
                    "order_id_2": order_id_txn_2,
                    "settle_status_2": settle_status_2,
                    "pmt_gateway_2": payment_gateway_2,

                    "cnp_pmt_option_2": cnp_txn_payment_option_2,
                    "cnp_pmt_flow_2": cnp_txn_payment_flow_2,
                    "cnp_pmt_status_2": cnp_txn_payment_status_2,
                    "cnp_pmt_state_2": cnp_txn_payment_state_2,
                    "cnp_txn_type_2": cnp_txn_type_2,
                    "cnp_pmt_mode_2": cnp_txn_payment_mode_2,
                    "cnp_pmt_gateway_2": cnp_txn_payment_gateway_2
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        try:
            query = f"update remotepay_setting set setting_value='2' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
            logger.debug(f"Query to update remotepay_setting table: {query}")
            result = DBProcessor.setValueToDB(query=query)
            logger.debug(f"query result : {result}")

            refresh_db()
            logger.debug(f"Refreshing the db after reverting back the remotepay settings")

        except Exception as e:
            logger.exception(f"Query updation failed due to exception : {e}")
        Configuration.executeFinallyBlock(testcase_id)