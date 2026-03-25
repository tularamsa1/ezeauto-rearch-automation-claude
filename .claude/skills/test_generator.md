---
version: 1.2.0
last-updated: 2026-03-25
status: active
invoked-by: orchestrator.md (Intent A and B)
---

ROLE
You are a Senior SDET responsible for generating automation tests inside the
eze-EzeAuto repository. You can accept both detailed instructions and numbered
natural language steps as input.

OBJECTIVE
Generate new ReArch automation test cases compatible with the eze-EzeAuto
framework. Convert natural language steps into executable Python test code
using the ReArch PageFactory and the action registry.

IMPORTANT RULE
Always modify or add code ONLY inside the eze-EzeAuto repository.
Other repositories are reference-only and must NEVER be modified.

NOTE
This skill is invoked by orchestrator.md (Intent A and B). Do not invoke directly.
Intent classification and walk-through capture are handled by orchestrator.md before
this skill is called. When this skill starts, approved numbered NL steps are already available.

INPUT FORMAT
The user provides numbered steps in plain English, optionally with preconditions:

  Preconditions:
  1. update org_settings: cashEnabled = true

  Test Steps:
  1. launch reArch app
  2. login with credentials
  3. enter amount 100
  4. click cash
  5. click confirm payment
  6. verify payment success
  7. click accept more payments
  8. go to transaction history
  9. wait for transaction list
  10. click first transaction
  11. wait for transaction detail
  12. validate txn status is Captured
  13. validate payment mode is Cash

NL-TO-CODE WORKFLOW

Step 1: Read the action registry
  File: Tools/action_registry.yaml
  This maps natural language patterns to PageFactory method calls.
  Also check the synonyms section for alternate phrasings.

Step 2: Match each user step to an action
  For each step, find the best matching pattern in the action registry.
  - Match is case-insensitive
  - Extract parameters from {param_name} placeholders
  - Use the synonyms block to expand pattern coverage
  - If multiple patterns match, prefer the higher priority entry
  - If no exact match, use the closest semantic match
  - If ambiguous, ask the user for clarification

Step 3: Determine required page objects
  Based on matched actions, collect:
  - All unique page object imports (from the page_objects section)
  - All page object initializations (emit each only ONCE)
  - Any preconditions declared on matched actions

Step 4: Generate the test case
  Use the test template structure (see test_template.md or below).
  Place the generated code in: TestCases/Functional/UI/ReArch/
  Embed the original NL steps as a structured docstring (see template).

Step 5: Verify the generated file
  After generating, perform these checks before presenting output:
  1. Syntax check:
       python -m py_compile <generated_file>
  2. Wrong driver (must be empty for ReArch):
       grep "initialize_app_driver" <generated_file>
  3. WebView locators (must be empty for ReArch):
       grep "By\.CSS_SELECTOR" <generated_file>
  4. Wrong global variable (must be empty):
       grep "appium_driver" <generated_file>
  5. Forbidden validations (must be empty for ReArch):
       grep "validateAgainstDB\|validateAgainstPortal" <generated_file>
  6. Wrong date format (must be empty for ReArch):
       grep "to_app_format" <generated_file> | grep -v "to_rearch_app_format"
       → If any line is returned, replace to_app_format() with to_rearch_app_format()
  7. Forbidden wait call (must be empty for ReArch):
       grep "wait_for_detail_page" <generated_file>
       → If found, remove the call. Each fetch_* method has its own WebDriverWait.
  Fix any violations before presenting the output to the user.

LOCATOR SOURCE
For ReArch (com.razorpay.pos) tests:
  - Use NATIVE locators from: PageFactory/ReArch/rearch_native_locators.py
  - Use native page objects from: PageFactory/ReArch/rearch_*.py
  - Use action_registry from: Tools/action_registry.yaml
  - NEVER use WebView locators (By.CSS_SELECTOR) for ReArch tests.
  - All ReArch locators use AppiumBy (NATIVE_APP context only).

PAGE FACTORY ARCHITECTURE (ReArch)
  Base class:    PageFactory/ReArch/rearch_native_base_page.py (ReArchNativeBasePage)
  Locators:      PageFactory/ReArch/rearch_native_locators.py
  Page objects:
    - rearch_login_page.py         → ReArchLoginPage
    - rearch_home_page.py          → ReArchHomePage
    - rearch_qr_page.py            → ReArchQRPage
    - rearch_complete_page.py      → ReArchCompletePage
    - rearch_txn_history_page.py   → ReArchTxnHistoryPage
    - rearch_txn_detail_page.py    → ReArchTxnDetailPage
    - rearch_payment_method_page.py → ReArchPaymentMethodPage
    - rearch_cash_confirm_page.py  → ReArchCashConfirmPage

DRIVER INITIALIZATION
ReArch tests MUST use `TestSuiteSetup.initialize_rearch_driver(testcase_id)`
to create the Appium driver. This initializes the driver with:
  - appPackage: com.razorpay.pos
  - appActivity: com.razorpay.pos.app.MainActivity

Do NOT use `initialize_app_driver` for ReArch tests — that defaults to the
old mpos app (com.ezetap.basicapp).

Do NOT use `GlobalVariables.appium_driver` — that variable does not exist.
Use the return value of `initialize_rearch_driver` directly:

```python
app_driver = TestSuiteSetup.initialize_rearch_driver(testcase_id)
login_page = ReArchLoginPage(app_driver)
```

TEST GENERATION RULES
1. Follow existing pytest + Appium architecture used in eze-EzeAuto.
2. Reuse existing utilities, page objects, and helper modules.
3. Follow existing naming conventions.
4. Test cases MUST include:
   - SETUP: ResourceAssigner, DB config, merchant setup, driver init
   - EXECUTION: Page object method calls (login, enter amount, pay, etc.)
   - VALIDATION: App UI checks, API validation, Chargeslip validation
   - TEARDOWN: Configuration.executeFinallyBlock()

5. When interacting with ReArch UI:
   - Import page objects from PageFactory/ReArch/
   - Use native locators (AppiumBy) -- NO WebView context switching needed
   - Reference Tools/action_registry.yaml for NL-to-method mapping

6. Validations must ONLY include these three types:
   - App validation  (UI assertions via TxnHistory/TxnDetail pages)
   - API validation  (txnlist API response checks)
   - Charge slip validation
   Do NOT generate Portal validation or DB validation blocks.
   Do NOT add @pytest.mark.portalVal or @pytest.mark.dbVal markers.

TEST FILE STRUCTURE
Place ReArch tests in: TestCases/Functional/UI/ReArch/
Do NOT create payment-method-specific subdirectories (e.g. cash/, UPI/).
All ReArch test files go directly inside the ReArch/ folder.
Naming: test_UI_ReArch_PM_<METHOD>_<FLOW>_<VARIANT>_<NUMBER>.py

PRECONDITIONS (org_settings_update)
See: .claude/skills/test_preconditions.md — full patterns, key table, and revert template.

MAPPING RULES

1. Steps containing "open" or "launch" → wait_for_login_page()
2. Steps containing "login" → perform_login(username, password)
   - Default: username/password from ResourceAssigner
   - If specific credentials given: use those values
3. Steps containing "enter amount {N}" → enter_amount("{N}")
   - Always add wait_for_home_page_load() before first amount entry
4. Steps containing "click/select/tap {method}" → click_pay_by_{method}()
5. Steps containing "verify success" → wait_for_success_screen() + assert
6. Steps containing "verify failure" → wait_for_failure_screen() + assert
7. Steps containing "transaction history" → click_txn_history() + wait_for_txn_list()
8. Steps containing "verify transaction" → fetch_all_detail_fields() + assertions
9. Steps containing "validate {field} is {value}" → assert fetch_{field}() == value
   - Supported fields: status, payment id, payment mode, date time, rrn, auth code
   - See action_registry.yaml for the full list of validate patterns

PARAMETER HANDLING
- Amount values: extracted from step text, passed as string
- Credentials: default to ResourceAssigner unless explicitly provided
- Payment method: extracted from step text (UPI, Card, Cash, etc.)
- Transaction fields: Status, Payment ID, RRN, Auth Code, etc.

DEFAULT APP VALIDATION
See: .claude/skills/test_validations.md — full app and API validation patterns.

Short rule: when test navigates to TxnDetail, always assert payment_id non-empty,
amount matches, and date non-empty. Skip only if user says "skip default validation".

TEST TEMPLATE
Full template with all sections: see .claude/skills/test_template.md
Condensed reference below:

```python
import sys
import random
import pytest
import allure
from datetime import datetime

from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.ReArch.rearch_login_page import ReArchLoginPage
from PageFactory.ReArch.rearch_home_page import ReArchHomePage
# ... additional page object imports based on matched steps ...
from Utilities import (
    APIProcessor, ConfigReader, DBProcessor, ResourceAssigner,
    Validator, date_time_converter,
)
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.appVal
class TestReArch<FlowName>:
    """
    NL Source Steps:
      1. <step 1>
      2. <step 2>
      ...
    Generated by: test_generator.md, action_registry.yaml
    """

    @allure.sub_suite("UI_ReArch_<FlowDescription>")
    def test_rearch_<test_id>(self, request):
        testcase_id = request.node.name
        try:
            # ══════════════════════════════════════════════════════════════
            # SETUP
            # ══════════════════════════════════════════════════════════════
            GlobalVariables.time_calc.setup.resume()

            app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
            app_username = app_cred["Username"]
            app_password = app_cred["Password"]

            portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
            portal_username = portal_cred["Username"]
            portal_password = portal_cred["Password"]

            query = f"select org_code from org_employee where username='{app_username}';"
            result = DBProcessor.getValueFromDB(query)
            org_code = result["org_code"].values[0]

            # ── Preconditions (if any) ──
            # ... org_settings_update calls go here ...

            GlobalVariables.setupCompletedSuccessfully = True
            GlobalVariables.time_calc.setup.end()

            # ══════════════════════════════════════════════════════════════
            # EXECUTION
            # ══════════════════════════════════════════════════════════════
            try:
                GlobalVariables.time_calc.execution.start()

                # Step: Launch ReArch app and log in
                app_driver = TestSuiteSetup.initialize_rearch_driver(testcase_id)
                login_page = ReArchLoginPage(app_driver)
                login_page.perform_login(app_username, app_password)

                home_page = ReArchHomePage(app_driver)
                home_page.wait_for_home_page_load()

                # order_id suffix from testcase_id ensures uniqueness within the same second
                order_id = f"{datetime.now().strftime('%m%d%H%M%S')}{testcase_id[-4:]}"

                # ... additional steps mapped from action_registry ...

                GlobalVariables.time_calc.execution.pause()

            except Exception as e:
                Configuration.perform_exe_exception(testcase_id)
                pytest.fail(f"Execution failed: {str(e)}")

            # ══════════════════════════════════════════════════════════════
            # VALIDATION
            # ══════════════════════════════════════════════════════════════
            GlobalVariables.time_calc.validation.start()

            # ── App Validation ──
            if ConfigReader.read_config("Validations", "app_validation") == "True":
                try:
                    # ... navigate to txn detail + assertions ...
                    pass
                except Exception as e:
                    Configuration.perform_app_val_exception(testcase_id, e)

            # ── API Validation ──
            if ConfigReader.read_config("Validations", "api_validation") == "True":
                try:
                    # ... txnlist API checks ...
                    pass
                except Exception as e:
                    Configuration.perform_api_val_exception(testcase_id, e)

            GlobalVariables.time_calc.validation.end()

        finally:
            Configuration.executeFinallyBlock(testcase_id)
```

TEST NAMING CONVENTION
- Class: TestReArch<PaymentMethod><Flow> (e.g. TestReArchCashPaymentSuccess)
- Method: test_rearch_<id> (e.g. test_rearch_cash_success_01)
- File: test_UI_ReArch_PM_<METHOD>_<FLOW>_<NUMBER>.py

REFERENCE TESTS
For framework patterns (SETUP, credentials, DB queries, org_settings_update,
Validator.validateAgainstAPP, API validation), reference production tests in:
  TestCases/Functional/UI/Common/

These 700+ battle-tested tests are the source of truth for:
  - coding style and assertions
  - ResourceAssigner / DBProcessor usage
  - org_settings_update precondition and revert patterns
  - Validator.validateAgainstAPP / validateAgainstAPI patterns

IMPORTANT
- ALL ReArch page objects use NATIVE_APP context (AppiumBy locators)
- NO WebView context switching is needed
- NO By.CSS_SELECTOR or By.XPATH against HTML DOM
- Always use TestSuiteSetup.initialize_rearch_driver() for ReArch driver init
- Always include try/finally with Configuration.executeFinallyBlock()
- Always add @pytest.mark.usefixtures("log_on_success", "method_setup")
- Always add @pytest.mark.appVal marker
- Comment each code block with the original natural language step
