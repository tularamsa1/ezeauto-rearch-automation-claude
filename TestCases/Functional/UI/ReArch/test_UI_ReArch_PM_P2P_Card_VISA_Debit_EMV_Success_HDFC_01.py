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
from PageFactory.ReArch.rearch_card_type_page import ReArchCardTypePage
from PageFactory.ReArch.rearch_complete_page import ReArchCompletePage
from PageFactory.ReArch.rearch_txn_history_page import ReArchTxnHistoryPage
from PageFactory.ReArch.rearch_txn_detail_page import ReArchTxnDetailPage
from Utilities import (
    APIProcessor, ConfigReader, DBProcessor, ResourceAssigner,
    Validator, date_time_converter, receipt_validator,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_rearch_0058():
    """
    Sub Feature Code: UI_ReArch_PM_P2P_Card_VISA_Debit_EMV_Success_HDFC
    Sub Feature Description:
        Launch ReArch app, apply P2P + Card preconditions, verify P2P connected
        notification in Android notification bar, hit p2p_start API with CARD
        payment mode, select Visa Debit (EMV) on device, HDFC simulator
        auto-authorizes the transaction, navigate to Payment History and validate
        via App, API, and Charge Slip.

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

        # Fetch app_key for p2p_start API
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
            display_amount = f"{int(amount):,}.00"
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

            # Step 4: Hit p2p_start API with CARD payment mode
            device_serial = GlobalVariables.str_device_id
            push_to = {"deviceId": f"{device_serial}|ezetap_android"}

            api_details = DBProcessor.get_api_details('p2p_start', request_body={
                "username": app_username,
                "password": app_password,
                "appKey": app_key,
                "amount": int(amount),
                "paymentMode": "CARD",
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

            # Step 5: After P2P push, device shows card type selection screen
            # Select Visa Debit (EMV) — HDFC simulator auto-authorizes
            time.sleep(3)

            card_type_page = ReArchCardTypePage(app_driver)
            card_type_page.wait_for_card_type_screen(timeout=60)
            logger.info("Card type selection screen displayed after P2P push")

            card_type_page.click_visa_debit_emv()
            logger.debug("Selected Visa Debit (EMV)")

            # Step 6: Wait for success screen (HDFC simulator auto-processes)
            complete_page = ReArchCompletePage(app_driver)
            complete_page.wait_for_success_screen(timeout=120)
            logger.info("Payment Successful screen confirmed")

            # Allow backend to complete processing
            time.sleep(2)

            # Get txn_id from p2p_status API
            api_details_status = DBProcessor.get_api_details('p2p_status', request_body={
                "username": app_username,
                "appKey": app_key,
                "origP2pRequestId": request_id
            })
            resp_status = APIProcessor.send_request(api_details_status)
            logger.debug(f"p2p_status API response: {resp_status}")
            status_after_pmt_success = resp_status['success']
            status_after_pmt_mssgcode = resp_status['messageCode']
            status_after_pmt_mssg = resp_status['message']
            status_after_pmt_realcode = resp_status['realCode']
            status_after_pmt_username = resp_status['username']
            txn_id = resp_status['txnId']
            logger.info(f"Transaction completed, txn_id={txn_id}")

            # Get txn details from DB
            query = (
                f"select id, created_time, posting_date, rr_number, auth_code "
                f"from txn where id='{txn_id}';"
            )
            logger.debug(f"Query to fetch txn details: {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time = result["created_time"].values[0]
            posting_date = result["posting_date"].values[0]
            rrn = str(result["rr_number"].values[0])
            auth_code = str(result["auth_code"].values[0])
            logger.debug(
                f"txn_id={txn_id}, created_time={created_time}, "
                f"posting_date={posting_date}, rrn={rrn}, auth_code={auth_code}"
            )

            # After payment, device redirects to collect payment screen
            complete_page.click_proceed_to_home()
            logger.debug("Clicked proceed to home from payment success screen")

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
                date_and_time = date_time_converter.to_rearch_app_format(created_time)
                expected_app_values = {
                    "txn_status": "Payment Authorized",
                    "txn_id":     txn_id,
                    "date":       date_and_time,
                    "amount":     display_amount,
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                # Navigate to Payment History from collect payment (initial home) screen
                home_page.wait_for_initial_home_screen()
                home_page.click_payments_history()

                txn_history_page = ReArchTxnHistoryPage(app_driver)
                txn_history_page.wait_for_txn_list()
                txn_history_page.click_on_transaction_by_txn_id(txn_id=txn_id)

                txn_detail_page = ReArchTxnDetailPage(app_driver)

                app_txn_id     = txn_detail_page.fetch_payment_id()
                app_txn_status = txn_detail_page.fetch_status(display_amount)
                app_date_time  = txn_detail_page.fetch_date_time()
                app_amount     = txn_detail_page.fetch_amount(display_amount)
                logger.info(
                    f"App txn_id={app_txn_id}, date_time={app_date_time}, "
                    f"status={app_txn_status}, amount={app_amount}"
                )

                actual_app_values = {
                    "txn_status": app_txn_status,
                    "txn_id":     app_txn_id,
                    "date":       app_date_time,
                    "amount":     app_amount,
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(
                    expectedApp=expected_app_values, actualApp=actual_app_values
                )

                assert app_txn_id, "Payment ID should not be empty"
                assert app_date_time, "Date & Time should not be empty"

            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"Completed APP validation for the test case: {testcase_id}")

        # ── API Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "api_validation") == "True":
            logger.info(f"Started API validation for the test case: {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    # Transaction validation via txnlist
                    "pmt_status":    "AUTHORIZED",
                    "txn_amt":       float(amount),
                    "pmt_mode":      "CARD",
                    "txn_type":      "CHARGE",
                    "acquirer_code": "HDFC",
                    "issuer_code":   "HDFC",
                    "org_code":      org_code,
                    "rrn":           rrn,
                    "date":          date,
                    # Card-specific fields (required for all Card tests)
                    "pmt_card_brand": "VISA",
                    "pmt_card_type":  "DEBIT",
                    "card_txn_type":  "EMV",
                    # P2P status validation
                    "p2p_start_success":    True,
                    "p2p_status_success":   True,
                    "p2p_status_mssg_code": "P2P_DEVICE_TXN_DONE",
                    "p2p_status_real_code": "P2P_DEVICE_TXN_DONE",
                    "p2p_status_mssg":      "Transaction done on device, Please look at Txn status.",
                    "p2p_status_username":  app_username,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(
                    "txnlist",
                    request_body={"username": app_username, "password": app_password},
                )
                response = APIProcessor.send_request(api_details)
                logger.debug("txnlist API response received")

                txn_data = next(
                    (x for x in response["txns"] if x["txnId"] == txn_id), None
                )
                if txn_data is None:
                    raise ValueError(f"txn_id '{txn_id}' not found in txnlist API response")
                logger.debug(f"Filtered txn entry from txnlist: {txn_data}")

                actual_api_values = {
                    "pmt_status":    txn_data["status"],
                    "txn_amt":       float(txn_data["amount"]),
                    "pmt_mode":      txn_data["paymentMode"],
                    "txn_type":      txn_data["txnType"],
                    "acquirer_code": txn_data["acquirerCode"],
                    "issuer_code":   txn_data["issuerCode"],
                    "org_code":      txn_data["orgCode"],
                    "rrn":           str(txn_data["rrNumber"]),
                    "date":          date_time_converter.from_api_to_datetime_format(
                                         txn_data["createdTime"]
                                     ),
                    # Card-specific fields (required for all Card tests)
                    "pmt_card_brand": txn_data["paymentCardBrand"],
                    "pmt_card_type":  txn_data["paymentCardType"],
                    "card_txn_type":  txn_data["cardTxnTypeDesc"],
                    # P2P status validation
                    "p2p_start_success":    start_success,
                    "p2p_status_success":   status_after_pmt_success,
                    "p2p_status_mssg_code": status_after_pmt_mssgcode,
                    "p2p_status_real_code": status_after_pmt_realcode,
                    "p2p_status_mssg":      status_after_pmt_mssg,
                    "p2p_status_username":  status_after_pmt_username,
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(
                    expectedAPI=expected_api_values, actualAPI=actual_api_values
                )

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case: {testcase_id}")

        # ── Charge Slip Validation ────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "charge_slip_validation") == "True":
            logger.info(f"Started ChargeSlip validation for the test case: {testcase_id}")
            try:
                txn_date, txn_time = date_time_converter.to_chargeslip_format(
                    posting_date_db=posting_date
                )
                expected_charge_slip_values = {
                    "RRN":          rrn,
                    "AUTH CODE":    auth_code,
                    "BASE AMOUNT:": f"Rs.{int(amount):,}.00",
                    "date":         txn_date,
                    "time":         txn_time,
                }
                logger.debug(f"expected_charge_slip_values: {expected_charge_slip_values}")
                receipt_validator.perform_charge_slip_validations(
                    txn_id=txn_id,
                    credentials={"username": app_username, "password": app_password},
                    expected_details=expected_charge_slip_values,
                )

            except Exception as e:
                Configuration.perform_charge_slip_val_exception(testcase_id, e)
            logger.info(f"Completed ChargeSlip validation for the test case: {testcase_id}")

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function: {testcase_id}")
        logger.info(f"Completed Validation for the test case: {testcase_id}")

    finally:
        # NOTE: Preconditions are NOT reverted per test requirement
        Configuration.executeFinallyBlock(testcase_id)
