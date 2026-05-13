import sys
import time
import random
import string
import pytest

from appium.webdriver.common.appiumby import AppiumBy

from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.ReArch.rearch_login_page import ReArchLoginPage
from PageFactory.ReArch.rearch_home_page import ReArchHomePage
from PageFactory.ReArch.rearch_cash_confirm_page import ReArchCashConfirmPage
from PageFactory.ReArch.rearch_complete_page import ReArchCompletePage
from Utilities import (
    APIProcessor, ConfigReader, DBProcessor, ResourceAssigner,
    Validator,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.appVal
def test_common_rearch_0061():
    """
    Sub Feature Code: UI_ReArch_PM_P2P_Cash_Queue_Success_HDFC
    Sub Feature Description:
        Launch ReArch app, apply P2P + Cash preconditions, verify P2P connected
        notification, queue two p2p_start CASH requests with different amounts,
        confirm payment 1 and validate success screen shows amount_1, then
        confirm payment 2 and validate success screen shows amount_2.

    Preconditions (not reverted):
        preAuthOption=1, autoLoginByTokenEnabled=true, cardPaymentEnabled=true,
        enableWebAppRevamp=true, p2pEnabled=true, mqttEnabled=true,
        cashPaymentEnabled=true, addlAuthReqdForCash=false,
        orderNumberInputEnabled=false, customerAuthDataCaptureEnabled=true,
        amountCutOffForCustomerAuth=10000, eSignatureForNonCardEnabled=false
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function: {testcase_id}")

        # ── Fetch Credentials ──────────────────────────────────────────────────
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"App credentials fetched: {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Portal credentials fetched: {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result["org_code"].values[0]
        logger.debug(f"org_code: {org_code}")

        # Fetch app_key for p2p APIs
        query = f"select app_key from app_key where org_code='{org_code}';"
        logger.debug(f"Query to fetch app_key: {query}")
        result = DBProcessor.getValueFromDB(query)
        app_key = result["app_key"].values[0]
        logger.debug(f"app_key: {app_key}")

        # ── PreConditions ──────────────────────────────────────────────────────
        logger.info(f"Starting Precondition setup for the test case: {testcase_id}")

        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code,
        })
        api_details["RequestBody"]["settings"]["preAuthOption"] = "1"
        api_details["RequestBody"]["settings"]["autoLoginByTokenEnabled"] = "true"
        api_details["RequestBody"]["settings"]["cardPaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["enableWebAppRevamp"] = "true"
        api_details["RequestBody"]["settings"]["p2pEnabled"] = "true"
        api_details["RequestBody"]["settings"]["mqttEnabled"] = "true"
        api_details["RequestBody"]["settings"]["cashPaymentEnabled"] = "true"
        api_details["RequestBody"]["settings"]["addlAuthReqdForCash"] = "false"
        api_details["RequestBody"]["settings"]["orderNumberInputEnabled"] = "false"
        api_details["RequestBody"]["settings"]["customerAuthDataCaptureEnabled"] = "true"
        api_details["RequestBody"]["settings"]["amountCutOffForCustomerAuth"] = "10000"
        api_details["RequestBody"]["settings"]["eSignatureForNonCardEnabled"] = "false"
        logger.debug(f"Precondition API details: {api_details}")
        response = APIProcessor.send_request(api_details=api_details)
        logger.debug(f"Precondition response: {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case: {testcase_id}")

        Configuration.configureLogCaptureVariables(
            apiLog=True, portalLog=False, cnpwareLog=False,
            middlewareLog=True, config_log=False,
        )

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function: {testcase_id}")

        # ── Test Execution ─────────────────────────────────────────────────────
        try:
            logger.info(f"Starting execution for the test case: {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function: {testcase_id}")

            # Generate two distinct amounts and ext_ref_numbers for the queue
            amount_1 = str(random.randint(100, 499))
            amount_2 = str(random.randint(500, 999))
            display_amount_1 = f"{int(amount_1):,}.00"
            display_amount_2 = f"{int(amount_2):,}.00"
            ext_ref_1 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            ext_ref_2 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            logger.debug(
                f"amount_1={amount_1}, ext_ref_1={ext_ref_1}, "
                f"amount_2={amount_2}, ext_ref_2={ext_ref_2}"
            )

            # Step 1: Launch ReArch app and login if present
            app_driver = TestSuiteSetup.initialize_rearch_driver(testcase_id)
            login_page = ReArchLoginPage(app_driver)
            login_page.perform_login_if_required(app_username, app_password)
            logger.debug("Login completed (or auto-login)")

            # Wait for initial home screen
            home_page = ReArchHomePage(app_driver)
            home_page.wait_for_initial_home_screen()
            logger.debug("Initial home screen loaded")

            # Step 3: Check P2P Connected notification in Android notification bar
            app_driver.open_notifications()
            logger.info("Opened notification bar to check P2P connectivity")
            time.sleep(2)
            try:
                p2p_element = app_driver.find_element(
                    AppiumBy.XPATH,
                    '//android.widget.TextView[@resource-id="android:id/text" '
                    'and @text="Connected"]'
                )
                logger.info(f"P2P Connected notification verified: {p2p_element.text}")
            except Exception:
                app_driver.back()
                raise Exception("P2P Connected notification not found in notification bar")
            app_driver.back()
            logger.debug("Closed notification bar")

            device_serial = GlobalVariables.str_device_id
            push_to = {"deviceId": f"{device_serial}|ezetap_android"}

            # Step 4: Hit p2p_start API #1 with CASH payment mode
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "appKey": app_key,
                "amount": int(amount_1),
                "paymentMode": "CASH",
                "externalRefNumber": ext_ref_1,
                "pushTo": push_to
            })
            resp_start_1 = APIProcessor.send_request(api_details)
            logger.debug(f"p2p_start #1 response: {resp_start_1}")
            start_success_1 = resp_start_1['success']
            assert start_success_1 is True, f"p2p_start #1 failed: {resp_start_1}"
            request_id_1 = resp_start_1['p2pRequestId']
            logger.info(f"p2p_start #1 successful, request_id_1={request_id_1}")

            # Step 5: Hit p2p_start API #2 with different amount and externalRefNumber
            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "appKey": app_key,
                "amount": int(amount_2),
                "paymentMode": "CASH",
                "externalRefNumber": ext_ref_2,
                "pushTo": push_to
            })
            resp_start_2 = APIProcessor.send_request(api_details)
            logger.debug(f"p2p_start #2 response: {resp_start_2}")
            start_success_2 = resp_start_2['success']
            assert start_success_2 is True, f"p2p_start #2 failed: {resp_start_2}"
            request_id_2 = resp_start_2['p2pRequestId']
            logger.info(f"p2p_start #2 successful, request_id_2={request_id_2}")

            # Step 6: Verify Confirm Payment button for txn 1, then confirm
            time.sleep(3)
            cash_confirm_page = ReArchCashConfirmPage(app_driver)
            complete_page = ReArchCompletePage(app_driver)

            cash_confirm_page.wait_for_cash_confirm_screen(timeout=60)
            logger.info("Confirm Payment screen displayed for txn 1")
            cash_confirm_page.click_confirm_payment()

            # Wait for success screen and capture "Payment Successful" text + amount for txn 1
            complete_page.wait_for_success_screen(timeout=60)
            app_success_msg_1 = app_driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Payment Successful"]'
            ).text
            app_amount_1 = app_driver.find_element(
                AppiumBy.XPATH,
                f'//android.widget.TextView[@text="{display_amount_1}"]'
            ).text
            logger.info(
                f"Txn 1 success screen — msg='{app_success_msg_1}', amount='{app_amount_1}'"
            )

            # Step 7: Click Accept More Payments
            complete_page.click_proceed_to_home()
            logger.debug("Clicked Accept More Payments for txn 1")

            # Step 8: Second queued P2P request auto-shows Confirm Payment screen
            cash_confirm_page.wait_for_cash_confirm_screen(timeout=90)
            logger.info("Confirm Payment screen displayed for txn 2")
            cash_confirm_page.click_confirm_payment()

            # Wait for success screen and capture "Payment Successful" text + amount for txn 2
            complete_page.wait_for_success_screen(timeout=60)
            app_success_msg_2 = app_driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Payment Successful"]'
            ).text
            app_amount_2 = app_driver.find_element(
                AppiumBy.XPATH,
                f'//android.widget.TextView[@text="{display_amount_2}"]'
            ).text
            logger.info(
                f"Txn 2 success screen — msg='{app_success_msg_2}', amount='{app_amount_2}'"
            )

            complete_page.click_proceed_to_home()
            logger.debug("Clicked Accept More Payments for txn 2")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function: {testcase_id}")
            logger.info(f"Execution is completed for the test case: {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception - " + str(e))

        # ── Validation ─────────────────────────────────────────────────────────
        logger.info(f"Starting Validation for the test case: {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function: {testcase_id}")

        # ── App Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "app_validation") == "True":
            logger.info(f"Started APP validation for the test case: {testcase_id}")
            try:
                expected_app_values = {
                    "txn_1_payment_msg": "Payment Successful",
                    "txn_1_amount":      display_amount_1,
                    "txn_2_payment_msg": "Payment Successful",
                    "txn_2_amount":      display_amount_2,
                }
                actual_app_values = {
                    "txn_1_payment_msg": app_success_msg_1,
                    "txn_1_amount":      app_amount_1,
                    "txn_2_payment_msg": app_success_msg_2,
                    "txn_2_amount":      app_amount_2,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(
                    expectedApp=expected_app_values, actualApp=actual_app_values
                )

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case: {testcase_id}")

        # ── API Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "api_validation") == "True":
            logger.info(f"Started API validation for the test case: {testcase_id}")
            try:
                # p2p_status for txn 1
                api_details_status_1 = DBProcessor.get_api_details('p2p_status', request_body={
                    "username": app_username,
                    "appKey": app_key,
                    "origP2pRequestId": request_id_1
                })
                resp_status_1 = APIProcessor.send_request(api_details_status_1)
                logger.debug(f"p2p_status #1 response: {resp_status_1}")

                # p2p_status for txn 2
                api_details_status_2 = DBProcessor.get_api_details('p2p_status', request_body={
                    "username": app_username,
                    "appKey": app_key,
                    "origP2pRequestId": request_id_2
                })
                resp_status_2 = APIProcessor.send_request(api_details_status_2)
                logger.debug(f"p2p_status #2 response: {resp_status_2}")

                expected_api_values = {
                    "p2p_start_success_1":    True,
                    "p2p_start_success_2":    True,
                    "p2p_status_success_1":   True,
                    "p2p_status_mssg_code_1": "P2P_DEVICE_TXN_DONE",
                    "p2p_status_real_code_1": "P2P_DEVICE_TXN_DONE",
                    "p2p_status_success_2":   True,
                    "p2p_status_mssg_code_2": "P2P_DEVICE_TXN_DONE",
                    "p2p_status_real_code_2": "P2P_DEVICE_TXN_DONE",
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "p2p_start_success_1":    start_success_1,
                    "p2p_start_success_2":    start_success_2,
                    "p2p_status_success_1":   resp_status_1['success'],
                    "p2p_status_mssg_code_1": resp_status_1['messageCode'],
                    "p2p_status_real_code_1": resp_status_1['realCode'],
                    "p2p_status_success_2":   resp_status_2['success'],
                    "p2p_status_mssg_code_2": resp_status_2['messageCode'],
                    "p2p_status_real_code_2": resp_status_2['realCode'],
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(
                    expectedAPI=expected_api_values, actualAPI=actual_api_values
                )

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case: {testcase_id}")

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function: {testcase_id}")
        logger.info(f"Completed Validation for the test case: {testcase_id}")

    finally:
        # NOTE: Preconditions are NOT reverted per test requirement
        Configuration.executeFinallyBlock(testcase_id)
