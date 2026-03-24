---
name: ReArch Test Generation Architecture
overview: End-to-end workflow for generating ReArch automation test cases from natural language. Covers native locator extraction via uiautomator, a native-only PageFactory, a semantic action mapping layer, and Claude skills for test generation.
todos:
  - id: phase1-fix-extractor
    content: "Improve rearch_xpath_extractor.py: fix duplicate class names, add screen registry, output locator_registry.yaml, add --validate flag"
    status: completed
  - id: phase1-capture-screens
    content: Define complete screen list (12 screens) in INTERACTIVE_SCREENS and run full extraction pass on device
    status: completed
  - id: phase1-remove-index-fallback
    content: "Eliminate @index XPath fallback from extractor; emit TODO comment instead; annotate existing @index locators in rearch_native_locators.py"
    status: completed
  - id: phase1-app-version-metadata
    content: "Record app versionName in locator_registry.yaml metadata at capture time via adb dumpsys"
    status: completed
  - id: phase2-native-locators
    content: Create rearch_native_locators.py with curated native-only AppiumBy locators from extraction output
    status: completed
  - id: phase2-native-base-page
    content: Create rearch_native_base_page.py without WebView context switching, keeping all interaction helpers
    status: completed
  - id: phase2-page-objects
    content: Update all ReArch page objects (login, home, qr, complete, txn_history, txn_detail) to use native locators
    status: completed
  - id: phase2-deprecate-webview-files
    content: "Add DeprecationWarning to rearch_base_page.py and rearch_locators.py on import"
    status: completed
  - id: phase2-configurable-timeout
    content: "Extract hardcoded 45s timeout to config.ini [Appium] element_wait_timeout; read as DEFAULT_TIMEOUT in rearch_native_base_page.py"
    status: completed
  - id: phase3-action-registry
    content: Create action_registry.yaml mapping natural language patterns to PageFactory methods
    status: completed
  - id: phase3-synonyms
    content: "Add synonyms block to action_registry.yaml to expand NL pattern coverage without duplicating entries"
    status: completed
  - id: phase3-preconditions
    content: "Add preconditions and priority fields to cash/UPI actions for machine-readable org settings config"
    status: completed
  - id: phase3-validate-registry
    content: "Create Tools/validate_registry.py to verify all code: snippets reference real page object methods"
    status: completed
  - id: phase4-update-xpath-skill
    content: Update xpath_extractor.md skill to reference native extraction instead of POS frontend repo
    status: completed
  - id: phase4-update-test-gen-skill
    content: "Update test_generator.md: add Step 5 verification, NL source docstring, order_id idempotency fix, references to sub-docs"
    status: completed
  - id: phase4-split-test-gen-skill
    content: "Split monolithic test_generator.md into focused sub-documents: test_template.md, test_preconditions.md, test_validations.md"
    status: completed
  - id: phase4-new-pagefactory-skill
    content: "Create page_factory_builder.md skill; add Step 5 validate_registry.py check"
    status: completed
  - id: phase4-new-nl-test-skill
    content: "NL-to-test generation consolidated into test_generator.md (nl_test_generator.md was merged and deleted)"
    status: completed
  - id: phase4-ci-workflow
    content: "Create .github/workflows/locator_health.yml: weekly registry validation + banned pattern checks + syntax checks"
    status: completed
  - id: fix-upi-test-driver
    content: "Fix test_UI_ReArch_PM_UPI_QR_POS_Success_ICICI_DIRECT_01.py: initialize_app_driver → initialize_rearch_driver; remove DB and Portal validation blocks"
    status: completed
  - id: cleanup-stray-files
    content: "Delete PageFactory/ReArch/test.py scratch file"
    status: completed
isProject: false
---

# ReArch Native Test Generation Architecture

## Current State

All four phases are **fully implemented and operational**. The pipeline converts numbered natural language steps into executable pytest + Appium test cases for the ReArch POS app (`com.razorpay.pos`) without any WebView context switching.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph extraction [Phase 1: Locator Extraction]
        A[Launch ReArch on Device] --> B[uiautomator XML Dump per Screen]
        B --> C[rearch_xpath_extractor.py]
        C --> D["locator_registry.yaml\n(with app_version metadata)"]
        D --> E[Human Review & TODO Annotation]
    end

    subgraph pagefactory [Phase 2: Native PageFactory]
        E --> F[rearch_native_locators.py]
        F --> G[Page Objects: LoginPage, HomePage, etc.]
        G --> H["rearch_native_base_page.py\n(DEFAULT_TIMEOUT from config.ini)"]
    end

    subgraph mapping [Phase 3: Action Mapping Layer]
        G --> I["action_registry.yaml\n(patterns + synonyms + priority + preconditions)"]
        I --> V[validate_registry.py]
        V -->|"CI: locator_health.yml"| CI[Weekly Health Check]
    end

    subgraph generation [Phase 4: Test Generation]
        K[Natural Language Steps] --> L["Claude + test_generator.md\n(5-step workflow)"]
        L --> I
        L --> G
        L --> M["Generated pytest Test Case\n(NL docstring embedded)"]
        M --> S["Step 5: Verify\npy_compile + grep checks"]
    end
```

---

## Phase 1: Locator Extraction

**Files:** `Tools/rearch_xpath_extractor.py`, `Tools/output/xml_dumps/`, `Tools/output/locator_registry.yaml`

### What is implemented

- **Interactive screen capture** (`--interactive`): walks through 12 defined screens, dumps uiautomator XML per screen, generates `rearch_locators_generated.py` and `locator_registry.yaml`.
- **Screen registry** prevents duplicate class names across sessions.
- **Three-tier locator priority**: resource-id (`AppiumBy.ID`) → `@text` XPath → **TODO annotation** (no `@index` fallback).
- **App version metadata**: at capture time, `adb dumpsys package com.razorpay.pos` is called to record `versionName` in the registry.
- **`--validate` mode**: connects to Appium, walks each screen interactively, tests every locator, outputs a CSV report.
- **`--regenerate` mode**: re-processes all saved XML dumps without needing a connected device.

### locator_registry.yaml format

```yaml
metadata:
  package: com.razorpay.pos
  app_version: "2.3.1"
  captured_at: "2026-03-15T10:22:00"
screens:
  HomeAmountLocators:
    source_xml: HomeAmountLocators.xml
    captured_at: "2026-03-15 10:22"
    element_count: 18
    elements:
      btn_1: { by: "AppiumBy.XPATH", value: "//android.widget.Button[@text='1']", type: "action" }
      btn_menu: { by: "TODO", value: "no resource-id or text; class=android.widget.Button index=0", type: "unknown", needs_annotation: true }
```

### @index locator policy

`@index`-based XPaths are **not generated**. When the extractor cannot find a resource-id or `@text` for an element, it emits a `# TODO: needs stable locator` comment instead. Existing `@index` locators in `rearch_native_locators.py` are annotated with `# TODO:` inline comments for human follow-up.

### Defined screens

| Screen Name              | Navigation Instruction                                          |
|--------------------------|-----------------------------------------------------------------|
| `LoginLocators`          | Login screen (username/password fields visible)                 |
| `HomeAmountLocators`     | Home page with numpad                                           |
| `PaymentMethodLocators`  | Payment method selection overlay after entering amount          |
| `OrderDetailsLocators`   | Order details overlay (Order ID / Device Serial fields)         |
| `QRPaymentLocators`      | UPI QR code display screen                                      |
| `CashConfirmLocators`    | Cash payment confirmation screen                                |
| `PaymentSuccessLocators` | Payment successful result screen                                |
| `PaymentFailedLocators`  | Payment failed result screen                                    |
| `TxnHistoryLocators`     | Transaction history list                                        |
| `TxnSearchLocators`      | Transaction search screen                                       |
| `TxnDetailLocators`      | Single transaction detail view                                  |
| `MenuLocators`           | Menu / dashboard page                                           |

---

## Phase 2: Native PageFactory

**Files:** `PageFactory/ReArch/rearch_native_locators.py`, `PageFactory/ReArch/rearch_native_base_page.py`, `PageFactory/ReArch/rearch_*.py`

### What is implemented

- **`rearch_native_locators.py`**: all AppiumBy locators, grouped by screen class. No `By.CSS_SELECTOR`. Existing `@index` locators annotated with `# TODO:`.
- **`rearch_native_base_page.py`**: base page with `wait_for_element`, `perform_click`, `fetch_text`, scroll/swipe helpers. Stays in `NATIVE_APP` context permanently. Reads `DEFAULT_TIMEOUT` from `config.ini [Appium]`.
- **Page objects** (login, home, qr, complete, txn_history, txn_detail, payment_method, cash_confirm): all inherit from `ReArchNativeBasePage`, import from `rearch_native_locators`.
- **Old WebView files deprecated**: `rearch_base_page.py` and `rearch_locators.py` emit `DeprecationWarning` on import; they must not be used in new tests.

### Configurable timeout

```ini
# Configuration/config.ini
[Appium]
element_wait_timeout = 45
```

```python
# rearch_native_base_page.py
DEFAULT_TIMEOUT = int(ConfigReader.read_config("Appium", "element_wait_timeout"))

def wait_for_element(self, locator, time: int = DEFAULT_TIMEOUT):
    ...
```

### File reference

| File | Purpose |
|------|---------|
| `rearch_native_locators.py` | All AppiumBy locators, grouped by screen |
| `rearch_native_base_page.py` | Base class: waits, clicks, scrolls, app lifecycle |
| `rearch_login_page.py` | Login screen interactions |
| `rearch_home_page.py` | Amount entry, payment method selection |
| `rearch_qr_page.py` | UPI QR screen validation |
| `rearch_complete_page.py` | Payment result screen |
| `rearch_txn_history_page.py` | Transaction history list |
| `rearch_txn_detail_page.py` | Transaction detail view |
| `rearch_payment_method_page.py` | Payment method overlay |
| `rearch_cash_confirm_page.py` | Cash confirmation screen |
| `rearch_base_page.py` | **DEPRECATED** — WebView base page |
| `rearch_locators.py` | **DEPRECATED** — WebView/HTML locators |

---

## Phase 3: Action Mapping Layer

**Files:** `Tools/action_registry.yaml`, `Tools/validate_registry.py`

### What is implemented

`action_registry.yaml` is the semantic bridge between natural language steps and PageFactory method calls. It contains:

- **`page_objects`** section: centralised import + init snippets per page class (emitted once per test).
- **`synonyms`** block: extends NL pattern coverage without duplicating entries.
- **`actions`** list: each entry has `patterns`, `page`, `method`, `code`, and optionally `priority` and `preconditions`.

### Key structural additions

```yaml
synonyms:
  enter:  [input, type, key in, set, fill, put, add, specify]
  click:  [tap, press, select, choose, hit]
  verify: [validate, check, assert, confirm, ensure]
  amount: [price, value, sum, figure, total]

actions:
  - patterns: ["click cash", "select cash", "pay by cash"]
    page: ReArchHomePage
    method: click_pay_by_cash
    code: "home_page.click_pay_by_cash()"
    priority: 1
    preconditions:
      org_settings:
        cashEnabled: "true"
      revert_on_finally:
        cashEnabled: "false"
```

When multiple patterns match the same NL step, the entry with the highest `priority` value wins. The `preconditions` block is read by the test generator to auto-emit `org_settings_update` calls in SETUP and revert calls in `finally`.

### Registry validation

`Tools/validate_registry.py` statically validates every `code:` snippet:
1. Parses the `method` field from each action.
2. Imports the declared page object class.
3. Uses `inspect.getmembers()` to verify the method exists.
4. Exits with code 1 if any method is missing — catches registry drift immediately.

```bash
python Tools/validate_registry.py
```

---

## Phase 4: Test Generation Skills

**Files:** `.claude/skills/test_generator.md`, `test_template.md`, `test_preconditions.md`, `test_validations.md`, `page_factory_builder.md`

### What is implemented

`test_generator.md` is the entry point skill with a **5-step workflow**:

1. **Read** `Tools/action_registry.yaml` (patterns + synonyms).
2. **Match** each NL step (case-insensitive; use synonyms to expand coverage; use priority to resolve conflicts).
3. **Collect** unique page objects (imports/inits emitted once each).
4. **Generate** the test file using `test_template.md`; embed NL steps as structured docstring.
5. **Verify** before presenting:
   - `python -m py_compile <file>` — syntax OK
   - `grep "initialize_app_driver"` — must be empty
   - `grep "By\.CSS_SELECTOR"` — must be empty
   - `grep "appium_driver"` — must be empty
   - `grep "validateAgainstDB\|validateAgainstPortal"` — must be empty for ReArch tests

### Sub-documents

| File | Content |
|------|---------|
| `test_generator.md` | Entry point: role, 5-step workflow, locator rules, driver rules |
| `test_template.md` | Complete Python test file template with all sections |
| `test_preconditions.md` | `org_settings_update` pattern, setting key table, revert template |
| `test_validations.md` | App validation pattern, API validation pattern, forbidden types |
| `page_factory_builder.md` | 5-step workflow to build new page objects + Step 5 registry validation |

### Test generation rules (enforced)

| Rule | Detail |
|------|--------|
| Driver | Always `TestSuiteSetup.initialize_rearch_driver(testcase_id)` |
| Locators | Native `AppiumBy` only — no `By.CSS_SELECTOR` |
| Validations | App + API + Charge slip only — no DB, no Portal |
| Markers | `@pytest.mark.appVal`, `@pytest.mark.apiVal`, `@pytest.mark.chargeSlipVal` — no `dbVal`, `portalVal` |
| `order_id` | `f"{datetime.now().strftime('%m%d%H%M%S')}{testcase_id[-4:]}"` for uniqueness |
| NL docstring | Embed original steps as `NL Source Steps:` class docstring |
| File location | `TestCases/Functional/UI/ReArch/` (no payment-method subdirectories) |

---

## CI Health Check

**File:** `.github/workflows/locator_health.yml`

Runs every Monday at 09:00 UTC (and on manual dispatch). Single job (`validate-registry`) with these steps:

1. **Registry validation** — `python Tools/validate_registry.py`
2. **Banned pattern scan** — greps all ReArch tests for `initialize_app_driver`, `By.CSS_SELECTOR`, `appium_driver`, `validateAgainstDB`, `validateAgainstPortal`
3. **Syntax check** — `python -m py_compile` on every `TestCases/Functional/UI/ReArch/*.py`
4. **@index locator warning** — warns if any `@index=` remains in `rearch_native_locators.py`

---

## End-to-End Workflow Example

**Input to Claude:**

```
1. launch reArch app
2. login with credentials
3. enter amount 45
4. select cash from payment methods
5. confirm cash payment
6. verify payment success
7. go to transaction history
8. click first transaction
9. wait for transaction detail
10. validate txn status is Captured
11. validate payment mode is Cash
```

**Claude workflow:**
1. Reads `action_registry.yaml` — matches each step to a method.
2. Detects `cashEnabled` precondition from the cash actions.
3. Collects unique page objects: `ReArchLoginPage`, `ReArchHomePage`, `ReArchPaymentMethodPage`, `ReArchCashConfirmPage`, `ReArchCompletePage`, `ReArchTxnHistoryPage`, `ReArchTxnDetailPage`.
4. Generates `TestCases/Functional/UI/ReArch/test_UI_ReArch_PM_Cash_POS_Success_01.py` using `test_template.md`.
5. Runs syntax check + banned pattern grep before presenting.

**Key generated structure:**

```python
class TestReArchCashPaymentSuccess:
    """
    NL Source Steps:
      1. launch reArch app
      2. login with credentials
      ...
    Generated by: test_generator.md, action_registry.yaml
    """

    def test_rearch_cash_success_01(self, request):
        try:
            # SETUP: credentials, org_code, cashEnabled precondition
            # EXECUTION: initialize_rearch_driver → login → amount → cash → confirm → verify
            # VALIDATION: App (TxnDetail) + API (txnlist)
        finally:
            # Revert cashEnabled → executeFinallyBlock
```

---

## Deprecation & Migration Status

| Old File | Status | Replacement |
|----------|--------|-------------|
| `rearch_locators.py` | Deprecated (DeprecationWarning on import) | `rearch_native_locators.py` |
| `rearch_base_page.py` | Deprecated (DeprecationWarning on import) | `rearch_native_base_page.py` |
| `nl_test_generator.md` | Deleted — merged into `test_generator.md` | `test_generator.md` |
| `PageFactory/ReArch/test.py` | Deleted (was a scratch file) | — |

The existing UPI test (`test_UI_ReArch_PM_UPI_QR_POS_Success_ICICI_DIRECT_01.py`) has been migrated: driver call fixed to `initialize_rearch_driver`, DB validation and Portal validation blocks removed.
