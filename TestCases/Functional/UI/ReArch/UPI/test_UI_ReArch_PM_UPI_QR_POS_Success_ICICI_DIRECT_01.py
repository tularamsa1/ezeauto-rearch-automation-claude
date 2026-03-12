import random
import sys
import time
from datetime import datetime

import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.ReArch.rearch_login_page import ReArchLoginPage
from PageFactory.ReArch.rearch_home_page import ReArchHomePage
from PageFactory.ReArch.rearch_qr_page import ReArchQRPage
from PageFactory.ReArch.rearch_complete_page import ReArchCompletePage
from PageFactory.ReArch.rearch_txn_history_page import ReArchTxnHistoryPage
from PageFactory.ReArch.rearch_txn_detail_page import ReArchTxnDetailPage
from Utilities import (
    APIProcessor,
    ConfigReader,
    DBProcessor,
    ResourceAssigner,
    Validator,
    date_time_converter,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Skills applied:
#   framework_guard      — eze-auto lifecycle markers (setup / execution /
#                          validation / finally) strictly followed.
#   xpath_extractor      — locators sourced from PageFactory/ReArch/*.py which
#                          were extracted from the pos Svelte frontend.
#   db_validation_generator — txn + upi_txn table assertions generated from
#                             known ICICI_DIRECT success DB schema.
#   test_generator       — pytest-compatible test scaffolded below.
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_rearch_100_101_001():
    """
    Sub Feature Code: UI_ReArch_PM_UPI_QR_POS_Success_ICICI_DIRECT
    Sub Feature Description:
        Launch the ReArch POS app (com.razorpay.pos) via Appium, navigate to
        the amount screen inside the WebView, initiate a UPI QR payment, simulate
        a customer scan by sending an ICICI_DIRECT success callback via API, and
        verify the resulting AUTHORIZED transaction across App UI, API, DB, and
        Portal.

    Test Steps:
        1.  Revert org payment settings to default.
        2.  Fetch ICICI_DIRECT UPI merchant config from DB (upi_mc_id, vTID, vMID).
        3.  Initialise browser context for Portal validation.
        4.  Mark setup complete; configure log capture.
        5.  Launch ReArch app via Appium and log in (UI).
        6.  Enter payment amount on home/amount screen (UI).
        7.  Select UPI payment mode → QR displayed on device (UI).
        8.  Validate QR screen ('Scan & Pay' label + QR image visible).
        9.  Resolve txn_id from DB using org_code (QR generated internally by app).
        10. Send ICICI_DIRECT success callback via API (simulate payer scan).
        11. Verify 'Payment Successful' result screen on app (UI).
        12. Capture final DB state (txn + upi_txn tables).
        13. App validation  — transaction detail fields via TxnHistory → TxnDetail.
        14. API validation  — txnlist API response.
        15. DB validation   — txn + upi_txn table assertions.
        16. Portal validation — Merchant Portal transaction record.

    TC naming: rearch=ReArch project, 100=PaymentMethod, 101=UPI, 001=TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup timer resumed: {testcase_id}")

        # ══════════════════════════════════════════════════════════════════════
        # SETUP
        # ══════════════════════════════════════════════════════════════════════
        logger.info(f"[SETUP] Starting setup for: {testcase_id}")

        # ── Fetch credentials ──────────────────────────────────────────────────
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]
        logger.debug(f"App credentials fetched: username={app_username}")

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]
        logger.debug("Portal credentials fetched.")

        # ── Resolve org_code ──────────────────────────────────────────────────
        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code: {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result["org_code"].values[0]
        logger.debug(f"org_code resolved: {org_code}")

        # ── Revert payment settings to default ────────────────────────────────
        testsuite_teardown.revert_payment_settings_default(
            org_code,
            bank_code="ICICI_DIRECT",
            portal_un=portal_username,
            portal_pw=portal_password,
            payment_mode="UPI",
        )
        logger.info("[SETUP] Payment settings reverted to default.")

        # ── Fetch ICICI_DIRECT UPI merchant config ────────────────────────────
        query = (
            f"select * from upi_merchant_config "
            f"where org_code='{org_code}' AND status='ACTIVE' AND bank_code='ICICI_DIRECT';"
        )
        logger.debug(f"Query for upi_merchant_config: {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id   = result["id"].values[0]
        virtual_tid = result["virtual_tid"].values[0]
        virtual_mid = result["virtual_mid"].values[0]
        logger.debug(
            f"UPI merchant config: upi_mc_id={upi_mc_id}, "
            f"virtual_tid={virtual_tid}, virtual_mid={virtual_mid}"
        )

        # ── Initialise portal browser context ─────────────────────────────────
        TestSuiteSetup.launch_browser_and_context_initialize()

        # framework_guard: mark setup as complete before any execution code
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"[SETUP] Setup complete: {testcase_id}")
        # ──────────────────────────────────────────────────────────────────────

        Configuration.configureLogCaptureVariables(
            apiLog=True, portalLog=True, cnpwareLog=False,
            middlewareLog=True, config_log=False,
        )
        GlobalVariables.time_calc.setup.end()
        logger.debug("Setup timer ended.")

        # ══════════════════════════════════════════════════════════════════════
        # TEST EXECUTION
        # ══════════════════════════════════════════════════════════════════════
        try:
            logger.info(f"[EXECUTION] Starting: {testcase_id}")
            GlobalVariables.time_calc.execution.start()

            amount   = random.randint(1, 500)
            order_id = datetime.now().strftime("%m%d%H%M%S")
            logger.debug(f"amount={amount}, order_id={order_id}")

            # ── Step 5: Launch ReArch app and log in ──────────────────────────
            # xpath_extractor: locators from PageFactory/ReArch/rearch_login_page.py
            #   txt_username → By.CSS_SELECTOR "#username"
            #   txt_password → By.CSS_SELECTOR "#password"
            #   btn_login    → By.XPATH "//button[normalize-space(.)='Login']"
            logger.info("[STEP 5] Launching ReArch app and logging in.")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = ReArchLoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            logger.debug("ReArch login submitted.")

            # ── Step 6: Enter payment amount ──────────────────────────────────
            # xpath_extractor: locators from PageFactory/ReArch/rearch_home_page.py
            #   btn_numpad_* → By.XPATH "//button[normalize-space(.)='N']"
            #   btn_pay_by_upi → By.XPATH "//button[.//span[normalize-space()='UPI']]"
            logger.info(f"[STEP 6] Entering amount={amount} on ReArch home screen.")
            home_page = ReArchHomePage(app_driver)
            home_page.wait_for_home_page_load()
            home_page.enter_amount(amount)
            logger.debug("Amount entered on numpad.")

            # ── Step 7: Select UPI → QR generated on device ───────────────────
            # xpath_extractor: locators from PageFactory/ReArch/rearch_qr_page.py
            #   lbl_scan_and_pay → By.XPATH "//*[normalize-space(.)='Scan & Pay']"
            #   img_qr_code      → By.CSS_SELECTOR "canvas, img[alt*='QR']"
            logger.info("[STEP 7] Selecting UPI payment mode.")
            home_page.click_pay_by_upi()
            logger.debug("UPI payment mode selected.")

            # ── Step 8: Validate QR screen ────────────────────────────────────
            qr_page = ReArchQRPage(app_driver)
            qr_screen_text = qr_page.validate_qr_screen()
            logger.info(f"[STEP 8] QR screen confirmed: '{qr_screen_text}'")

            # ── Step 9: Resolve txn_id from DB ────────────────────────────────
            # The ReArch app calls the UPI QR generate API internally when UPI
            # is selected.  We poll the txn table using org_code + payment_mode
            # to get the latest transaction.
            logger.info("[STEP 9] Resolving txn_id from DB.")
            time.sleep(3)  # allow server write to settle
            query = (
                f"select * from txn "
                f"where org_code='{org_code}' AND payment_mode='UPI' "
                f"order by created_time desc limit 1;"
            )
            logger.debug(f"DB query for txn: {query}")
            result       = DBProcessor.getValueFromDB(query)
            txn_id       = result["id"].values[0]
            created_time = result["created_time"].values[0]
            order_id_db  = result["external_ref"].values[0]
            logger.debug(f"Resolved txn_id={txn_id}, created_time={created_time}")

            # RRN is derived from the numeric suffix of txn_id (after 'E')
            rrn = txn_id.split("E")[1]
            logger.debug(f"Derived RRN: {rrn}")

            # ── Step 10: Send ICICI_DIRECT success callback ───────────────────
            logger.info("[STEP 10] Sending ICICI_DIRECT success callback via API.")
            api_details = DBProcessor.get_api_details(
                "callbackgeneratorUpiICICI",
                request_body={
                    "merchantId":     virtual_mid,
                    "subMerchantId":  virtual_mid,
                    "terminalId":     virtual_tid,
                    "PayerAmount":    str(amount),
                    "BankRRN":        rrn,
                    "merchantTranId": str(txn_id),
                },
            )
            callback_payload  = APIProcessor.send_request(api_details)
            logger.debug(f"Callback generator response: {callback_payload}")

            api_details       = DBProcessor.get_api_details(
                "callbackUpiICICI", request_body=callback_payload
            )
            callback_response = APIProcessor.send_request(api_details)
            logger.debug(f"Callback API response: {callback_response}")

            # ── Step 11: Verify payment result on ReArch app ──────────────────
            # xpath_extractor: locators from PageFactory/ReArch/rearch_complete_page.py
            #   page_txn                → By.CSS_SELECTOR "#txn-page"
            #   lbl_payment_successful  → By.XPATH "//h2[normalize-space(.)='Payment Successful']"
            logger.info("[STEP 11] Waiting for Payment Successful screen on ReArch app.")
            complete_page = ReArchCompletePage(app_driver)
            complete_page.wait_for_success_screen(timeout=90)
            payment_status_ui = complete_page.fetch_payment_status_text()
            logger.info(f"ReArch app payment status: '{payment_status_ui}'")

            # ── Step 12: Capture final DB state ───────────────────────────────
            # db_validation_generator: txn table fields
            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Final txn DB query: {query}")
            result = DBProcessor.getValueFromDB(query)

            status_db            = result["status"].iloc[0]
            payment_mode_db      = result["payment_mode"].iloc[0]
            amount_db            = float(result["amount"].iloc[0])
            state_db             = result["state"].iloc[0]
            payment_gateway_db   = result["payment_gateway"].iloc[0]
            acquirer_code_db     = result["acquirer_code"].iloc[0]
            bank_code_db         = result["bank_code"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            tid_db               = result["tid"].values[0]
            mid_db               = result["mid"].values[0]
            txn_type_db          = result["txn_type"].values[0]
            error_msg_db         = result["error_message"].values[0]
            rr_number_db         = result["rr_number"].values[0]
            logger.debug(
                f"txn table: status={status_db}, state={state_db}, "
                f"rr_number={rr_number_db}"
            )

            # db_validation_generator: upi_txn table fields
            query = f"select * from upi_txn where txn_id='{txn_id}';"
            logger.debug(f"upi_txn DB query: {query}")
            result = DBProcessor.getValueFromDB(query)

            upi_status_db    = result["status"].iloc[0]
            upi_txn_type_db  = result["txn_type"].iloc[0]
            upi_bank_code_db = result["bank_code"].iloc[0]
            upi_mc_id_db     = result["upi_mc_id"].iloc[0]
            logger.debug(
                f"upi_txn table: status={upi_status_db}, "
                f"txn_type={upi_txn_type_db}, bank_code={upi_bank_code_db}"
            )

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.info(f"[EXECUTION] Completed: {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail(f"Execution failed: {str(e)}")
        # ══════════════════════════════════════════════════════════════════════

        # ══════════════════════════════════════════════════════════════════════
        # VALIDATION
        # ══════════════════════════════════════════════════════════════════════
        logger.info(f"[VALIDATION] Starting: {testcase_id}")
        GlobalVariables.time_calc.validation.start()

        # ── App Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "app_validation") == "True":
            logger.info(f"[APP VAL] Starting for: {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_status":    "Payment Successful",
                    "pmt_mode":      "UPI",
                    "txn_id":        txn_id,
                    "settle_status": "SETTLED",
                    "date":          date_and_time,
                    "rrn":           str(rr_number_db),
                }
                logger.debug(f"expected_app_values: {expected_app_values}")

                # Navigate to TxnHistory then open the specific transaction
                complete_page.click_proceed_to_home()
                home_page.wait_for_home_page_load()
                home_page.click_txn_history()

                txn_history_page = ReArchTxnHistoryPage(app_driver)
                txn_history_page.wait_for_page_load()
                txn_history_page.click_txn_by_index(0)

                txn_detail_page = ReArchTxnDetailPage(app_driver)
                txn_detail_page.wait_for_detail_page()

                app_payment_id   = txn_detail_page.fetch_payment_id()
                app_status       = txn_detail_page.fetch_status()
                app_rrn          = txn_detail_page.fetch_rrn()
                app_date_time    = txn_detail_page.fetch_date_time()
                app_payment_mode = txn_detail_page.fetch_payment_mode()

                logger.info(f"App txn_id: {app_payment_id}")
                logger.info(f"App status: {app_status}")
                logger.info(f"App RRN: {app_rrn}")
                logger.info(f"App date: {app_date_time}")
                logger.info(f"App payment mode: {app_payment_mode}")

                actual_app_values = {
                    "pmt_status":    payment_status_ui,
                    "pmt_mode":      app_payment_mode,
                    "txn_id":        app_payment_id,
                    "settle_status": app_status,
                    "date":          app_date_time,
                    "rrn":           str(app_rrn),
                }
                logger.debug(f"actual_app_values: {actual_app_values}")
                Validator.validateAgainstAPP(
                    expectedApp=expected_app_values, actualApp=actual_app_values
                )
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"[APP VAL] Completed for: {testcase_id}")

        # ── API Validation ────────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "api_validation") == "True":
            logger.info(f"[API VAL] Starting for: {testcase_id}")
            try:
                date = date_time_converter.db_datetime(created_time)
                expected_api_values = {
                    "pmt_status":    "AUTHORIZED",
                    "txn_amt":       float(amount),
                    "pmt_mode":      "UPI",
                    "pmt_state":     "SETTLED",
                    "settle_status": "SETTLED",
                    "acquirer_code": "ICICI",
                    "issuer_code":   "ICICI",
                    "txn_type":      "CHARGE",
                    "mid":           virtual_mid,
                    "tid":           virtual_tid,
                    "org_code":      org_code,
                    "order_id":      order_id_db,
                    "rrn":           str(rrn),
                    "date":          date,
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                api_details = DBProcessor.get_api_details(
                    "txnlist",
                    request_body={"username": app_username, "password": app_password},
                )
                response = APIProcessor.send_request(api_details)
                logger.debug(f"txnlist API response received.")

                txn_data = next(
                    (x for x in response["txns"] if x["txnId"] == txn_id), None
                )
                if txn_data is None:
                    raise ValueError(
                        f"txn_id '{txn_id}' not found in txnlist API response"
                    )

                actual_api_values = {
                    "pmt_status":    txn_data["status"],
                    "txn_amt":       float(txn_data["amount"]),
                    "pmt_mode":      txn_data["paymentMode"],
                    "pmt_state":     txn_data["states"][0],
                    "settle_status": txn_data["settlementStatus"],
                    "acquirer_code": txn_data["acquirerCode"],
                    "issuer_code":   txn_data["issuerCode"],
                    "txn_type":      txn_data["txnType"],
                    "mid":           txn_data["mid"],
                    "tid":           txn_data["tid"],
                    "org_code":      txn_data["orgCode"],
                    "order_id":      txn_data["orderNumber"],
                    "rrn":           str(txn_data["rrNumber"]),
                    "date":          date_time_converter.from_api_to_datetime_format(
                                         txn_data["createdTime"]
                                     ),
                }
                logger.debug(f"actual_api_values: {actual_api_values}")
                Validator.validationAgainstAPI(
                    expectedAPI=expected_api_values, actualAPI=actual_api_values
                )
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"[API VAL] Completed for: {testcase_id}")

        # ── DB Validation ─────────────────────────────────────────────────────
        # db_validation_generator: expected values for an ICICI_DIRECT AUTHORIZED UPI QR txn
        if ConfigReader.read_config("Validations", "db_validation") == "True":
            logger.info(f"[DB VAL] Starting for: {testcase_id}")
            try:
                expected_db_values = {
                    # txn table
                    "pmt_status":     "AUTHORIZED",
                    "pmt_state":      "SETTLED",
                    "pmt_mode":       "UPI",
                    "txn_amt":        float(amount),
                    "settle_status":  "SETTLED",
                    "txn_type":       "CHARGE",
                    "acquirer_code":  "ICICI",
                    "bank_code":      "ICICI",
                    "pmt_gateway":    "ICICI",
                    "error_msg":      None,
                    "mid":            virtual_mid,
                    "tid":            virtual_tid,
                    "order_id":       order_id_db,
                    # upi_txn table
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type":   "PAY_QR",
                    "upi_bank_code":  "ICICI_DIRECT",
                    "upi_mc_id":      upi_mc_id,
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    # txn table
                    "pmt_status":     status_db,
                    "pmt_state":      state_db,
                    "pmt_mode":       payment_mode_db,
                    "txn_amt":        amount_db,
                    "settle_status":  settlement_status_db,
                    "txn_type":       txn_type_db,
                    "acquirer_code":  acquirer_code_db,
                    "bank_code":      bank_code_db,
                    "pmt_gateway":    payment_gateway_db,
                    "error_msg":      error_msg_db,
                    "mid":            mid_db,
                    "tid":            tid_db,
                    "order_id":       order_id_db,
                    # upi_txn table
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type":   upi_txn_type_db,
                    "upi_bank_code":  upi_bank_code_db,
                    "upi_mc_id":      upi_mc_id_db,
                }
                logger.debug(f"actual_db_values: {actual_db_values}")
                Validator.validateAgainstDB(
                    expectedDB=expected_db_values, actualDB=actual_db_values
                )
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"[DB VAL] Completed for: {testcase_id}")

        # ── Portal Validation ─────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "portal_validation") == "True":
            logger.info(f"[PORTAL VAL] Starting for: {testcase_id}")
            try:
                from PageFactory.Portal_TransHistoryPage import (
                    get_transaction_details_for_portal,
                )
                date_and_time_portal = date_time_converter.to_portal_format(created_time)
                expected_portal_values = {
                    "date_time": date_and_time_portal,
                    "pmt_state": "AUTHORIZED",
                    "pmt_type":  "UPI",
                    "txn_amt":   f"{str(amount)}.00",
                    "username":  app_username,
                    "txn_id":    txn_id,
                    "rrn":       str(rrn),
                }
                logger.debug(f"expected_portal_values: {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(
                    app_username, app_password, order_id_db
                )
                txn_detail = transaction_details[0]
                actual_portal_values = {
                    "date_time": txn_detail["Date & Time"],
                    "pmt_state": str(txn_detail["Status"]),
                    "pmt_type":  txn_detail["Type"],
                    "txn_amt":   txn_detail["Total Amount"].split()[1],
                    "username":  txn_detail["Username"],
                    "txn_id":    txn_detail["Transaction ID"],
                    "rrn":       txn_detail["RR Number"],
                }
                logger.debug(f"actual_portal_values: {actual_portal_values}")
                Validator.validateAgainstPortal(
                    expectedPortal=expected_portal_values,
                    actualPortal=actual_portal_values,
                )
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"[PORTAL VAL] Completed for: {testcase_id}")

        GlobalVariables.time_calc.validation.end()
        logger.debug("Validation timer ended.")
        logger.info(f"[VALIDATION] All validations completed: {testcase_id}")
        # ══════════════════════════════════════════════════════════════════════

    finally:
        # framework_guard: always run cleanup / log finalisation
        Configuration.executeFinallyBlock(testcase_id)
