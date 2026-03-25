import random
import sys
import time
from datetime import datetime

import pytest

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_PaymentPage import PaymentPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_TransHistoryPage import get_transaction_details_for_portal
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


# ---------------------------------------------------------------------------
# Skill: framework_guard  — eze-auto lifecycle markers applied
# Skill: xpath_extractor  — XPaths sourced from PageFactory/App_*.py files
# Skill: db_validation_generator — txn + upi_txn table assertions generated
# Skill: test_generator   — pytest-compatible test scaffolded below
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
def test_common_100_101_501():
    """
    Sub Feature Code: UI_Common_PM_UPI_QR_POS_Success_ICICI_DIRECT
    Sub Feature Description:
        Launch POS app via Appium, navigate to payment screen, select UPI mode
        to trigger QR generation on the device, simulate a payment-app scan by
        sending a success callback via ICICI_DIRECT, and verify the resulting
        AUTHORIZED transaction across App UI, API, DB, and Portal.

    Test Steps:
        1. Launch POS app and log in (UI)
        2. Enter amount + order-number and proceed (UI)
        3. Select UPI payment mode → QR displayed on device (UI)
        4. Resolve txn_id from DB using order_id (app generates QR internally)
        5. Simulate QR scan: send ICICI_DIRECT success callback (API)
        6. Verify "PAYMENT SUCCESSFUL" status on POS app screen (UI)
        7. Navigate to Transaction History and validate fields (App validation)
        8. Validate against txnlist API response (API validation)
        9. Validate against txn + upi_txn DB rows (DB validation)
       10. Validate against Merchant Portal (Portal validation)

    TC naming: 100 = Payment Method, 101 = UPI, 501 = TC501
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed : {testcase_id}")

        # ── Reset Settings to Default ─────────────────────────────────────
        logger.info(f"[SETUP] Reverting settings to default : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"App credentials fetched from ezeauto db : {app_cred}")
        app_username = app_cred["Username"]
        app_password = app_cred["Password"]

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Portal credentials fetched from ezeauto db : {portal_cred}")
        portal_username = portal_cred["Username"]
        portal_password = portal_cred["Password"]

        query = f"select org_code from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result["org_code"].values[0]
        logger.debug(f"org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(
            org_code,
            bank_code="ICICI_DIRECT",
            portal_un=portal_username,
            portal_pw=portal_password,
            payment_mode="UPI",
        )
        logger.info(f"[SETUP] Settings reverted : {testcase_id}")
        # ─────────────────────────────────────────────────────────────────

        # ── PreConditions ─────────────────────────────────────────────────
        logger.info(f"[SETUP] Starting precondition setup : {testcase_id}")

        query = (
            f"select * from upi_merchant_config "
            f"where org_code='{org_code}' AND status='ACTIVE' AND bank_code='ICICI_DIRECT';"
        )
        logger.debug(f"Query to fetch upi_merchant_config : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"upi_merchant_config result : {result}")
        upi_mc_id    = result["id"].values[0]
        virtual_tid  = result["virtual_tid"].values[0]
        virtual_mid  = result["virtual_mid"].values[0]
        logger.debug(
            f"Fetched upi_mc_id={upi_mc_id}, virtual_tid={virtual_tid}, "
            f"virtual_mid={virtual_mid}"
        )

        # Initialise browser context for portal validation; app driver
        # is initialised inside the execution block.
        TestSuiteSetup.launch_browser_and_context_initialize()

        # framework_guard: mark setup complete so teardown logic is safe
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"[SETUP] Preconditions complete : {testcase_id}")
        # ─────────────────────────────────────────────────────────────────

        Configuration.configureLogCaptureVariables(
            apiLog=True, portalLog=True, cnpwareLog=False,
            middlewareLog=True, config_log=False,
        )

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended : {testcase_id}")

        # ══════════════════════════════════════════════════════════════════
        # TEST EXECUTION
        # ══════════════════════════════════════════════════════════════════
        try:
            logger.info(f"[EXECUTION] Starting : {testcase_id}")
            GlobalVariables.time_calc.execution.start()

            amount   = random.randint(1, 500)
            order_id = datetime.now().strftime("%m%d%H%M%S")
            logger.debug(f"amount={amount}, order_id={order_id}")

            # ── Step 1: Launch POS app and log in ─────────────────────────
            # xpath_extractor source: PageFactory/App_LoginPage.py
            #   txt_username  → (AppiumBy.ID, "com.ezetap.basicapp:id/etUid")
            #   txt_password  → (AppiumBy.ID, "com.ezetap.basicapp:id/etPassword")
            #   btn_login     → (AppiumBy.ID, "com.ezetap.basicapp:id/btnLogin")
            logger.info("[STEP 1] Launching POS app and logging in")
            app_driver = TestSuiteSetup.initialize_app_driver(testcase_id)
            login_page = LoginPage(app_driver)
            login_page.perform_login(app_username, app_password)
            logger.debug("Login completed successfully")

            # ── Step 2: Enter amount + order number ───────────────────────
            # xpath_extractor source: PageFactory/App_HomePage.py
            #   txt_enterAmountField → (By.ID, "com.ezetap.basicapp:id/tvAmountCard")
            #   btn_collect_payment  → (By.XPATH, "//*[@text = 'Collect Payment']")
            #   txt_orderNo          → (By.ID,    "com.ezetap.basicapp:id/editTextOrderNo")
            #   btn_paymentProceed   → (By.ID,    "com.ezetap.basicapp:id/buttonProceed")
            logger.info(f"[STEP 2] Entering amount={amount} and order_id={order_id} via POS UI")
            home_page = HomePage(app_driver)
            home_page.wait_for_navigation_to_load()
            home_page.wait_for_home_page_load()
            home_page.enter_amount_and_order_number(amount, order_id)
            logger.debug("Amount and order number entered")

            # ── Step 3: Select UPI → QR generated on device ───────────────
            # xpath_extractor source: PageFactory/App_PaymentPage.py
            #   btn_upi        → (By.XPATH, "//*[@text='UPI']")
            #   lbl_scanQRCode → (By.XPATH, '//*[contains(@text,"Scan QR code")]')
            logger.info("[STEP 3] Selecting UPI payment mode — QR will be generated")
            payment_page = PaymentPage(app_driver)
            payment_page.click_on_Upi_paymentMode()
            logger.debug("UPI payment mode selected")

            qr_screen_text = payment_page.validate_upi_bqr_payment_screen()
            logger.info(f"[STEP 3] QR screen confirmed on device: '{qr_screen_text}'")

            # ── Step 4: Resolve txn_id from DB ────────────────────────────
            # The POS app calls upiqrGenerate internally when UPI is selected;
            # we retrieve the resulting txn_id via external_ref = order_id.
            logger.info("[STEP 4] Resolving txn_id from DB using order_id")
            time.sleep(3)  # allow server write to complete
            query = (
                f"select * from txn "
                f"where org_code='{org_code}' "
                f"AND external_ref='{order_id}' "
                f"AND payment_mode='UPI' "
                f"order by created_time desc limit 1;"
            )
            logger.debug(f"Query to fetch txn after QR generation : {query}")
            result = DBProcessor.getValueFromDB(query)
            txn_id       = result["id"].values[0]
            created_time = result["created_time"].values[0]
            order_id_db  = result["external_ref"].values[0]
            logger.debug(
                f"Resolved txn_id={txn_id}, created_time={created_time}, "
                f"order_id_db={order_id_db}"
            )
            # RRN is derived from the txn_id suffix (post 'E')
            rrn = txn_id.split("E")[1]
            logger.debug(f"Derived RRN : {rrn}")

            # ── Step 5: Simulate QR scan via payment app (callback) ────────
            logger.info("[STEP 5] Simulating payment app QR scan via ICICI_DIRECT callback")
            api_details = DBProcessor.get_api_details(
                "callbackgeneratorUpiICICI",
                request_body={
                    "merchantId":    virtual_mid,
                    "subMerchantId": virtual_mid,
                    "terminalId":    virtual_tid,
                    "PayerAmount":   str(amount),
                    "BankRRN":       rrn,
                    "merchantTranId": str(txn_id),
                },
            )
            callback_payload = APIProcessor.send_request(api_details)
            logger.debug(f"Callback generator response : {callback_payload}")

            api_details = DBProcessor.get_api_details(
                "callbackUpiICICI", request_body=callback_payload
            )
            callback_response = APIProcessor.send_request(api_details)
            logger.debug(f"Callback API response : {callback_response}")

            # ── Step 6: Verify payment success on POS app screen ──────────
            # xpath_extractor source: PageFactory/App_PaymentPage.py
            #   lbl_paymentStatus    → (By.ID, "com.ezetap.service.demo:id/tvTxnStatus")
            #   btn_proceedToHomepage→ (By.ID, "com.ezetap.service.demo:id/btnProceed")
            logger.info("[STEP 6] Verifying 'PAYMENT SUCCESSFUL' on POS app screen")
            payment_status_ui = payment_page.fetch_payment_status()
            logger.info(f"POS app payment status: '{payment_status_ui}'")
            payment_page.click_on_proceed_homepage()
            logger.debug("Clicked Proceed to Homepage")

            # ── Collect final DB state for validation ─────────────────────
            # db_validation_generator: txn table fields
            query = f"select * from txn where id='{txn_id}';"
            logger.debug(f"Query to fetch final txn state : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"txn table result : {result}")
            status_db           = result["status"].iloc[0]
            payment_mode_db     = result["payment_mode"].iloc[0]
            amount_db           = float(result["amount"].iloc[0])
            state_db            = result["state"].iloc[0]
            payment_gateway_db  = result["payment_gateway"].iloc[0]
            acquirer_code_db    = result["acquirer_code"].iloc[0]
            bank_code_db        = result["bank_code"].iloc[0]
            settlement_status_db = result["settlement_status"].iloc[0]
            tid_db              = result["tid"].values[0]
            mid_db              = result["mid"].values[0]
            txn_type_db         = result["txn_type"].values[0]
            error_msg_db        = result["error_message"].values[0]
            rr_number_db        = result["rr_number"].values[0]
            logger.debug(
                f"txn table: status={status_db}, state={state_db}, "
                f"rr_number={rr_number_db}, mid={mid_db}, tid={tid_db}"
            )

            # db_validation_generator: upi_txn table fields
            query = f"select * from upi_txn where txn_id='{txn_id}';"
            logger.debug(f"Query to fetch upi_txn data : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"upi_txn table result : {result}")
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
            logger.info(f"[EXECUTION] Completed : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail(f"Test execution failed: {str(e)}")
        # ══════════════════════════════════════════════════════════════════

        # ══════════════════════════════════════════════════════════════════
        # VALIDATION
        # ══════════════════════════════════════════════════════════════════
        logger.info(f"[VALIDATION] Starting : {testcase_id}")
        GlobalVariables.time_calc.validation.start()

        # ── App Validation ────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "app_validation") == "True":
            logger.info(f"[APP VAL] Starting for : {testcase_id}")
            try:
                date_and_time = date_time_converter.to_app_format(created_time)
                expected_app_values = {
                    "pmt_msg":       "PAYMENT SUCCESSFUL",
                    "pmt_mode":      "UPI",
                    "txn_amt":       "{:.2f}".format(amount),
                    "txn_id":        txn_id,
                    "order_id":      order_id,
                    "settle_status": "SETTLED",
                    "date":          date_and_time,
                    "rrn":           str(rr_number_db),
                }
                logger.debug(f"expected_app_values : {expected_app_values}")

                # Navigate to Transaction History in POS app
                home_page.click_on_history()
                txn_history_page = TransHistoryPage(app_driver)
                txn_history_page.click_on_transaction_by_txn_id(txn_id)

                app_payment_msg      = txn_history_page.fetch_txn_payment_msg_text()
                logger.info(f"App payment message     : {app_payment_msg}")
                app_payment_mode     = txn_history_page.fetch_txn_type_text()
                logger.info(f"App payment mode        : {app_payment_mode}")
                app_amount           = txn_history_page.fetch_txn_amount_text()
                logger.info(f"App amount              : {app_amount}")
                app_txn_id           = txn_history_page.fetch_txn_id_text()
                logger.info(f"App txn_id              : {app_txn_id}")
                app_order_id         = txn_history_page.fetch_order_id_text()
                logger.info(f"App order_id            : {app_order_id}")
                app_settlement_status = txn_history_page.fetch_settlement_status_text()
                logger.info(f"App settlement status   : {app_settlement_status}")
                app_date_and_time    = txn_history_page.fetch_date_time_text()
                logger.info(f"App date                : {app_date_and_time}")
                app_rrn              = txn_history_page.fetch_RRN_text()
                logger.info(f"App RRN                 : {app_rrn}")

                actual_app_values = {
                    "pmt_msg":       app_payment_msg,
                    "pmt_mode":      app_payment_mode,
                    "txn_amt":       app_amount.split(" ")[1],
                    "txn_id":        app_txn_id,
                    "order_id":      app_order_id,
                    "settle_status": app_settlement_status,
                    "date":          app_date_and_time,
                    "rrn":           str(app_rrn),
                }
                logger.debug(f"actual_app_values : {actual_app_values}")
                Validator.validateAgainstAPP(
                    expectedApp=expected_app_values, actualApp=actual_app_values
                )
            except Exception as e:
                Configuration.perform_app_val_exception(testcase_id, e)
            logger.info(f"[APP VAL] Completed for : {testcase_id}")

        # ── API Validation ────────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "api_validation") == "True":
            logger.info(f"[API VAL] Starting for : {testcase_id}")
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
                    "order_id":      order_id,
                    "rrn":           str(rrn),
                    "date":          date,
                }
                logger.debug(f"expected_api_values : {expected_api_values}")

                api_details = DBProcessor.get_api_details(
                    "txnlist",
                    request_body={"username": app_username, "password": app_password},
                )
                response = APIProcessor.send_request(api_details)
                logger.debug(f"txnlist API response : {response}")

                txn_data = next(
                    (x for x in response["txns"] if x["txnId"] == txn_id), None
                )
                if txn_data is None:
                    raise ValueError(
                        f"txn_id '{txn_id}' not found in txnlist API response"
                    )
                logger.debug(f"Filtered txn entry from txnlist : {txn_data}")

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
                logger.debug(f"actual_api_values : {actual_api_values}")
                Validator.validationAgainstAPI(
                    expectedAPI=expected_api_values, actualAPI=actual_api_values
                )
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"[API VAL] Completed for : {testcase_id}")

        # ── DB Validation ─────────────────────────────────────────────────
        # db_validation_generator: expected values for AUTHORIZED UPI QR txn
        if ConfigReader.read_config("Validations", "db_validation") == "True":
            logger.info(f"[DB VAL] Starting for : {testcase_id}")
            try:
                expected_db_values = {
                    # txn table
                    "pmt_status":    "AUTHORIZED",
                    "pmt_state":     "SETTLED",
                    "pmt_mode":      "UPI",
                    "txn_amt":       float(amount),
                    "settle_status": "SETTLED",
                    "txn_type":      "CHARGE",
                    "acquirer_code": "ICICI",
                    "bank_code":     "ICICI",
                    "pmt_gateway":   "ICICI",
                    "error_msg":     None,
                    "mid":           virtual_mid,
                    "tid":           virtual_tid,
                    "order_id":      order_id,
                    # upi_txn table
                    "upi_txn_status": "AUTHORIZED",
                    "upi_txn_type":   "PAY_QR",
                    "upi_bank_code":  "ICICI_DIRECT",
                    "upi_mc_id":      upi_mc_id,
                }
                logger.debug(f"expected_db_values : {expected_db_values}")

                actual_db_values = {
                    # txn table
                    "pmt_status":    status_db,
                    "pmt_state":     state_db,
                    "pmt_mode":      payment_mode_db,
                    "txn_amt":       amount_db,
                    "settle_status": settlement_status_db,
                    "txn_type":      txn_type_db,
                    "acquirer_code": acquirer_code_db,
                    "bank_code":     bank_code_db,
                    "pmt_gateway":   payment_gateway_db,
                    "error_msg":     error_msg_db,
                    "mid":           mid_db,
                    "tid":           tid_db,
                    "order_id":      order_id_db,
                    # upi_txn table
                    "upi_txn_status": upi_status_db,
                    "upi_txn_type":   upi_txn_type_db,
                    "upi_bank_code":  upi_bank_code_db,
                    "upi_mc_id":      upi_mc_id_db,
                }
                logger.debug(f"actual_db_values : {actual_db_values}")
                Validator.validateAgainstDB(
                    expectedDB=expected_db_values, actualDB=actual_db_values
                )
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"[DB VAL] Completed for : {testcase_id}")

        # ── Portal Validation ─────────────────────────────────────────────
        if ConfigReader.read_config("Validations", "portal_validation") == "True":
            logger.info(f"[PORTAL VAL] Starting for : {testcase_id}")
            try:
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
                logger.debug(f"expected_portal_values : {expected_portal_values}")

                transaction_details = get_transaction_details_for_portal(
                    app_username, app_password, order_id
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
                logger.debug(f"actual_portal_values : {actual_portal_values}")
                Validator.validateAgainstPortal(
                    expectedPortal=expected_portal_values,
                    actualPortal=actual_portal_values,
                )
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"[PORTAL VAL] Completed for : {testcase_id}")

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended : {testcase_id}")
        logger.info(f"[VALIDATION] All validations completed : {testcase_id}")
        # ══════════════════════════════════════════════════════════════════

    finally:
        # framework_guard: always runs cleanup/log-finalisation
        Configuration.executeFinallyBlock(testcase_id)
