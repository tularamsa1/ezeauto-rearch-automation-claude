import random
import shutil
import sys
import time
from datetime import datetime
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import remotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_077():
    """
    Sub Feature Code: UI_Common_PM_CNP_Cyber_bumpCount_CnpSettigs
    Sub Feature Description: Verification of the bump count via cnp link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    077: TC_077
    """
    expectedExpiryMessage = "Remote payment link has expired, Use a different mode or request for a new remote pay link to complete payment"
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        query = "update remotepay_setting set setting_value= '1' where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response['paymentLink']
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')
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
            # remotePayTxn.clickOnSubmitButton()

            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.waitForExpiryElement()
            expiryMessage = str(remote_pay_txn.expiryMessage())
            logger.info(f"Your expiryMessage is:  {expiryMessage}")
            logger.info(f"Your expiryMessage is:  {expectedExpiryMessage}")
            if expiryMessage == (expectedExpiryMessage):
                pass
            else:
                raise Exception("Expiry Messages are not matching.")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        query = "update remotepay_setting set setting_value=10 where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.apiVal
# @pytest.mark.dbVal
# @pytest.mark.portalVal
# @pytest.mark.appVal
# @pytest.mark.chargeSlipVal
# def test_common_100_103_078():
    """
    Sub Feature Code: UI_Common_PM_CNP_Cyber_bumpCount_CnpSettigs
    Sub Feature Description: Verification of the bump count via cnp link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    078: TC_078
    """
    expectedExpiryMessage = "Remote payment link has expired, Use a different mode or request for a new remote pay link to complete payment"
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        query = "update remotepay_setting set setting_value= '1' where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Intiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response['paymentLink']
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            externalRef = response.get('externalRefNumber')
            payment_intent_id = response.get('paymentIntentId')

            query = "select * from remotepay_setting where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bump_count = result['expire_by_time'].values[0]
            logger.debug(f"Query result, org_code : {bump_count}")
            time.sleep((((60*bump_count)/2))-2)

            query = "select * from payment_intent where id='" + payment_intent_id + "';"
            logger.debug(f"Query to fetch org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_time_before = result['expire_by_time'].values[0]
            logger.debug(f"Query result, org_code : {expiry_time_before}")

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
            # remotePayTxn.clickOnSubmitButton()

            remote_pay_txn = remotePayTxnPage(ui_driver)
            remote_pay_txn.waitForExpiryElement()
            expiryMessage = str(remote_pay_txn.expiryMessage())
            logger.info(f"Your expiryMessage is:  {expiryMessage}")
            logger.info(f"Your expiryMessage is:  {expectedExpiryMessage}")
            if expiryMessage == (expectedExpiryMessage):
                pass
            else:
                raise Exception("Expiry Messages are not matching.")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        query = "update remotepay_setting set setting_value=10 where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)



