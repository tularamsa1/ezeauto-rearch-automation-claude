import json
import random
import string
import sys

import pytest
import requests

from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_trial():
    """
    Sub Feature Code: Trial
    Sub Feature Description:
    TC naming code description:
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        query = "select * from app_key where org_code ='" + str(org_code) + "'"
        logger.debug(f"Query to fetch app_key from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        app_key = result['app_key'].values[0]
        logger.debug(f"Query result, app_key : {app_key}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('AutoRefund', request_body={"username": portal_username,
                                                                              "password": portal_password,
                                                                              "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["autoRefundEnabled"] = "true"
        logger.debug(f"API details  : {api_details}")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions AutoRefund enabled is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
        logger.info(
            f"Logging in the MPOSX application using username : {app_username} and password : {app_password}")
        login_page = LoginPage(app_driver)
        login_page.perform_login(app_username, app_password)
        logger.info(f"Logged in to the app")
        home_page = HomePage(app_driver)
        home_page.wait_for_navigation_to_load()
        home_page.wait_for_home_page_load()
        home_page.check_home_page_logo()
        logger.info(f"Loaded home page")

        api_details = DBProcessor.get_api_details('p2p_start', request_body={
            "username": app_username,
            "appKey": app_key,
            "amount": 502,
            "externalRefNumber": 'Auto_p2p_0010',
            "pushTo": {"deviceId": "1490329804|ezetap_android"}
        })
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for P2P start API is : {response}")

        payment_page = PaymentPage(app_driver)
        app_driver.reset()
        logger.info(f"Killed the app")


        payment_page.click_on_Upi_paymentMode()
        logger.info("Selected payment mode is UPI")
        payment_page.validate_upi_bqr_payment_screen()
        logger.info("Payment QR generated and displayed successfully")
        payment_page.click_on_back_btn()
        logger.info(f"Clicked on back button")
        payment_page.click_on_transaction_cancel_yes()

    finally:
        Configuration.executeFinallyBlock(testcase_id)


