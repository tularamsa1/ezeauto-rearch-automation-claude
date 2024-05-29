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

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_370():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Txn_In_Progress_Link_Opened_In_Second_Tab_Unable_Generate_New_Link_Same_Ref_Id
    Sub Feature Description: Verify when Opening the same link in different browsers / same browser shouldn't display in progress msg. but it should display payment in progress mesage when we generate new link with the same refId
    TC naming code description: 100: Payment Method, 103: RemotePay, 370: TC370
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

                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(payment_link_url)

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
            logger.debug(f"From response fetch realCode : {error_message}")

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
def test_common_100_103_371():
    """
    Sub Feature Code: UI_Common_PM_CNP_Razorpay_Error_Codes_Failed_Attempts_Till_Max_Pay_Attempts
    Sub Feature Description: Verify the error message for Failure Attempts till Max Pay Attempts
    TC naming code description:
    100: Payment Method
    103: RemotePay
    371: TC371
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

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='HDFC',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password,
                                                               payment_gateway='RAZORPAY')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from remotepay_setting where org_code= '{org_code}' and setting_name='maximumPayAttemptsAllowed';"
        logger.debug(f"Query to fetch remotepay_setting : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result,  : {result}")
        if len(result) > 0:
            query = f"update remotepay_setting set setting_value='3' where org_code= '{org_code}' and setting_name='maximumPayAttemptsAllowed';"
            logger.debug(f"Query to update maxPayAttemptsAllowed to 3  : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result, to update maxPayAttemptsAllowed to 3  : {result}")
        else:
            query = f"INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, entity, " \
                    f"entity_id, setting_name, setting_value, lock_id, component, inheritable, org_code) V" \
                    f"ALUES ('{org_code}',now(),'{org_code}',now(),'org','10786','maximumPayAttemptsAllowed','3',2," \
                    f"'SERVER',_binary '','{org_code}'); "
            logger.debug(f"Query to insert remotepay_setting maxPayAttemptsAllowed to 3  : {query}")
            result = DBProcessor.setValueToDB(query)
            logger.debug(f"Query result, to insert remotepay_setting maxPayAttemptsAllowed to 3 : {result}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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
                                                      request_body={"amount": amount,
                                                                    "externalRefNumber": order_id,
                                                                    "username": app_username,
                                                                    "password": app_password})

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response from cnp intiate api is: {response}")

            if not response['success']:
                raise Exception("Api could not initate a cnp txn.")
            else:
                payment_link_url = response.get('paymentLink')
                payment_intent_id = response.get('paymentIntentId')

                for index in range(3):
                    page = TestSuiteSetup.initialize_ui_browser()
                    page.goto(payment_link_url)
                    remote_pay_txn = RemotePayTxnPage(page)
                    remote_pay_txn.clickOnCreditCardToExpand()
                    remote_pay_txn.enterNameOnTheCard("Sandeep")
                    remote_pay_txn.enterCreditCardNumber("5267 3181 8797 5449")
                    remote_pay_txn.enterCreditCardExpiryMonth("12")
                    remote_pay_txn.enterCreditCardExpiryYear("2050")
                    remote_pay_txn.enterCreditCardCvv("111")
                    remote_pay_txn.clickOnProceedToPay()
                    remote_pay_txn.click_failure_pmt_btn()
                    time.sleep(5)

                    if index == 2:
                        expected_message = "Maximum number of attempts for this url exceeded. Please request for a new remote pay url."
                        actual_message = str(remote_pay_txn.failureScreenMessageMaxAttempt())
                    else:
                        expected_message = "Your payment attempt failed, Sorry for the inconvenience. Please contact pos-support@razorpay.com for further clarifications."
                        actual_message = str(remote_pay_txn.failureScreenMessage())
                    logger.info(f"Your actual failure message is:  {actual_message}")
                    logger.info(f"Your expected failure Message is:  {expected_message}")
                    assert actual_message == expected_message, "Failure Message is not matching."

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)
