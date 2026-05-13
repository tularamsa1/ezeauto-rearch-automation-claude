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
from Utilities import (
    APIProcessor, ConfigReader, DBProcessor, ResourceAssigner,
    Validator,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_rearch_0059():
    """
    Sub Feature Code: UI_ReArch_PM_P2P_Cash_Cancel_HDFC
    Sub Feature Description:
        Launch ReArch app, apply P2P + Cash preconditions, verify P2P connected
        notification in Android notification bar, hit p2p_start API with CASH
        payment mode, verify Confirm Payment button is visible on device, hit
        p2p_cancel API and validate 'Payment Cancelled' text appears on device.

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

        # Fetch app_key for p2p_start / p2p_cancel APIs
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

            amount = str(random.randint(100, 999))
            ext_ref_number = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            logger.debug(f"amount={amount}, ext_ref_number={ext_ref_number}")

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

            # Step 4: Hit p2p_start API with CASH payment mode
            device_serial = GlobalVariables.str_device_id
            push_to = {"deviceId": f"{device_serial}|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "appKey": app_key,
                "amount": int(amount),
                "paymentMode": "CASH",
                "externalRefNumber": ext_ref_number,
                "pushTo": push_to
            })
            logger.debug(f"p2p_start API details: {api_details}")
            resp_start = APIProcessor.send_request(api_details)
            logger.debug(f"p2p_start API response: {resp_start}")

            start_success = resp_start['success']
            assert start_success is True, f"p2p_start API failed: {resp_start}"
            request_id = resp_start['p2pRequestId']
            logger.info(f"p2p_start successful, request_id={request_id}")

            # Step 5: Verify Confirm Payment button is visible on device
            time.sleep(3)

            cash_confirm_page = ReArchCashConfirmPage(app_driver)
            cash_confirm_page.wait_for_cash_confirm_screen(timeout=60)
            logger.info("Confirm Payment button is visible on device after P2P push")

            # Step 6: Hit p2p_cancel API
            api_details_cancel = DBProcessor.get_api_details('p2p_cancel', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            logger.debug(f"p2p_cancel API details: {api_details_cancel}")
            resp_cancel = APIProcessor.send_request(api_details_cancel)
            logger.debug(f"p2p_cancel API response: {resp_cancel}")

            cancel_success = resp_cancel['success']
            assert cancel_success is True, f"p2p_cancel API failed: {resp_cancel}"
            logger.info(f"p2p_cancel successful, success={cancel_success}")

            # Validate 'Payment Cancelled' text is visible on device
            time.sleep(2)
            payment_cancelled_element = app_driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="Payment Cancelled"]'
            )
            assert payment_cancelled_element.is_displayed(), \
                "'Payment Cancelled' text not visible on device after p2p_cancel"
            logger.info("'Payment Cancelled' text verified on device")

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

        # ── API Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "api_validation") == "True":
            logger.info(f"Started API validation for the test case: {testcase_id}")
            try:
                expected_api_values = {
                    "p2p_start_success":      True,
                    "p2p_cancel_success":     True,
                    "p2p_status_mssg_code":   "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "p2p_status_real_code":   "P2P_STATUS_IN_CANCELED_FROM_EXTERNAL_SYSTEM",
                    "p2p_status_mssg":        "PushToPay Notification has been Canceled from Billing/External System.",
                    "p2p_status_username":    app_username,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                # p2p_status after cancel to confirm final state
                api_details_status = DBProcessor.get_api_details('p2p_status', request_body={
                    "username": app_username,
                    "appKey": app_key,
                    "origP2pRequestId": request_id
                })
                resp_status = APIProcessor.send_request(api_details_status)
                logger.debug(f"p2p_status after cancel response: {resp_status}")

                actual_api_values = {
                    "p2p_start_success":    start_success,
                    "p2p_cancel_success":   cancel_success,
                    "p2p_status_mssg_code": resp_status['messageCode'],
                    "p2p_status_real_code": resp_status['realCode'],
                    "p2p_status_mssg":      resp_status['message'],
                    "p2p_status_username":  resp_status['username'],
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
