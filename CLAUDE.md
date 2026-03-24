# CLAUDE.md

This file provides guidance to Claude Code when working in the eze-EzeAuto repository.

## What This Repository Is

**eze-EzeAuto** is a pytest + Appium automation framework for testing Razorpay POS applications on Android devices. The primary focus is the **ReArch** app (`com.razorpay.pos`).

## Quick Reference

When the user provides **numbered natural language test steps**, always:
1. Read `.claude/skills/test_generator.md` — the unified skill for NL-to-code conversion
2. Read `Tools/action_registry.yaml` — the dictionary mapping NL patterns to PageFactory methods
3. Generate the test case following the skill's template and rules

## Repository Structure

```
eze-EzeAuto/
├── .claude/skills/             # Claude skills (auto-loaded context)
│   ├── test_generator.md       # PRIMARY: NL steps → pytest test generation
│   ├── page_factory_builder.md # Build new page objects from screen dumps
│   ├── xpath_extractor.md      # Extract native locators from uiautomator dumps
│   ├── framework_guard.md      # Rules to avoid breaking existing framework
│   └── db_validation_generator.md  # DB validation logic generation
├── PageFactory/ReArch/         # ReArch page objects (native Appium)
│   ├── rearch_native_locators.py   # All AppiumBy locators
│   ├── rearch_native_base_page.py  # Base class for all ReArch pages
│   ├── rearch_login_page.py
│   ├── rearch_home_page.py
│   ├── rearch_payment_method_page.py
│   ├── rearch_cash_confirm_page.py
│   ├── rearch_qr_page.py
│   ├── rearch_complete_page.py
│   ├── rearch_txn_history_page.py
│   └── rearch_txn_detail_page.py
├── Tools/
│   ├── action_registry.yaml    # NL pattern → method mapping
│   └── rearch_xpath_extractor.py
├── TestCases/Functional/UI/
│   ├── ReArch/                 # ReArch test cases go here
│   └── Common/                 # 700+ existing tests (reference for patterns)
├── Configuration/
│   ├── TestSuiteSetup.py       # Driver initialization (initialize_rearch_driver)
│   └── Configuration.py        # executeFinallyBlock, exception handlers
├── DataProvider/
│   └── GlobalVariables.py      # Global state (appDriver, etc.)
└── Utilities/
    ├── ResourceAssigner.py     # Device/credential assignment
    ├── DBProcessor.py          # Database operations
    ├── APIProcessor.py         # API request handling
    ├── Validator.py            # validateAgainstAPP, validateAgainstAPI
    └── ConfigReader.py         # Config file reader
```

## Critical Rules for ReArch Tests

### Driver Initialization
- **USE**: `TestSuiteSetup.initialize_rearch_driver(testcase_id)` — returns the Appium driver for `com.razorpay.pos`
- **DO NOT USE**: `TestSuiteSetup.initialize_app_driver()` — that defaults to the old mpos app (`com.ezetap.basicapp`)
- **DO NOT USE**: `GlobalVariables.appium_driver` — that variable does not exist. The actual variable is `GlobalVariables.appDriver`, but prefer using the return value from `initialize_rearch_driver` directly

### Locators
- All ReArch locators use **AppiumBy** (NATIVE_APP context only)
- Locators live in `PageFactory/ReArch/rearch_native_locators.py`
- **NEVER** use WebView locators (`By.CSS_SELECTOR`) for ReArch tests

### Test File Placement
- Place ReArch tests in: `TestCases/Functional/UI/ReArch/`
- Naming: `test_UI_ReArch_PM_<METHOD>_<FLOW>_<VARIANT>_<NUMBER>.py`

### Validations
- Only generate: App validation, API validation, Charge slip validation
- **DO NOT** generate Portal validation or DB validation blocks

## Generating Tests from Natural Language

When you receive numbered steps like:
```
1. launch reArch app
2. login with credentials
3. enter amount 45
4. select cash from payment methods
...
```

Follow this workflow:
1. **Read** `.claude/skills/test_generator.md` for the complete generation rules
2. **Read** `Tools/action_registry.yaml` to match each NL step to a PageFactory method
3. **Match** each step case-insensitively against registry patterns
4. **Generate** the test file using the template from `test_generator.md`

The skill contains the full test template, mapping rules, precondition patterns (org_settings_update), default validation rules, and naming conventions.

## Reference Tests (primary source of truth)

When generating new test cases, reference the **700+ production tests** in:
```
TestCases/Functional/UI/Common/
```

These are the source of truth for:
- **SETUP patterns**: `ResourceAssigner.getAppUserCredentials`, `getPortalUserCredentials`, DB queries for `org_code`
- **Preconditions**: `org_settings_update` request + revert-in-finally pattern
- **Validation patterns**: `Validator.validateAgainstAPP`, `Validator.validateAgainstAPI`
- **Exception handling**: `Configuration.perform_exe_exception`, `perform_app_val_exception`, `perform_api_val_exception`
- **Coding style**: allure annotations, pytest markers, logging, variable naming
- **Teardown**: `Configuration.executeFinallyBlock(testcase_id)`

Always match the structure and style of these existing tests when generating new ones.

## Reference Repositories (read-only, backend context only)

These external repos provide backend context (DB tables, API contracts) but must **NEVER** be modified. Do NOT use them as templates for writing test code:
- `eze-common`
- `eze-server`
- `eze-middleware`
- `pos` (the ReArch app source — use only for understanding app behavior)
