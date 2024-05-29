import random
import sys
from datetime import datetime
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.portal_remotepay_page import RemotePayTxnPage
from Utilities import  DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities.merchant_configurer import refresh_db

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_425():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Edge_Cases_Only_One_Success_Others_Failed_For_Three_Attempts
    Sub Feature Description: Verify only one txn will go on success and other two will be failed (for 3 attemps)
    TC naming code description: 100: Payment Method, 103: RemotePay, 425: TC425
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

        query = f"update remotepay_setting set setting_value= '3' where org_code='{org_code}' and setting_name='maximumPayAttemptsAllowed';"
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
                remote_pay_txn.clickOnDebitCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.wait_for_success_btn()

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
                remote_pay_txn.wait_for_success_btn()

                page_3 = TestSuiteSetup.initialize_ui_browser()
                page_3.goto(payment_link_url)
                remote_pay_txn = RemotePayTxnPage(page_3)
                remote_pay_txn.clickOnDebitCardToExpand()
                remote_pay_txn.enterNameOnTheCard("Sandeep")
                remote_pay_txn.enter_debit_card_number("4111 1111 1111 1111")
                remote_pay_txn.enterDebitCardExpiryMonth("12")
                remote_pay_txn.enterDebitCardExpiryYear("2050")
                remote_pay_txn.enter_debit_card_cvv("111")
                remote_pay_txn.clickOnProceedToPay()
                remote_pay_txn.wait_for_success_btn()

                page_1.bring_to_front()
                remote_pay_txn = RemotePayTxnPage(page_1)
                remote_pay_txn.click_success_pmt_btn()
                success_message = str(remote_pay_txn.succcessScreenMessage())
                logger.info(f"Your expected success message is:  {success_message}")
                logger.info(f"Your expected Message is:  {expected_success_message}")
                assert success_message == expected_success_message, "Success Message is not matching."

                page_2.bring_to_front()
                remote_pay_txn = RemotePayTxnPage(page_2)
                remote_pay_txn.click_success_pmt_btn()
                failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"Your expected success message is:  {failed_message}")
                logger.info(f"Your expected Message is:  {expected_failed_message}")
                assert success_message == expected_success_message, "Failed Message is not matching."

                page_3.bring_to_front()
                remote_pay_txn = RemotePayTxnPage(page_3)
                remote_pay_txn.click_success_pmt_btn()
                failed_message = str(remote_pay_txn.failedScreenMessage())
                logger.info(f"Your expected success message is:  {failed_message}")
                logger.info(f"Your expected Message is:  {expected_failed_message}")
                assert success_message == expected_success_message, "Failed Message is not matching."

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
