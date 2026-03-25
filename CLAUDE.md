
# CLAUDE.md

**eze-EzeAuto** is a pytest + Appium framework for testing the Razorpay ReArch POS app (`com.razorpay.pos`) on Android.

## Quick Reference

For all task routing — test generation, device walkthroughs, new screens, registry validation — read **`SKILL.md`** first. It contains the full skills catalog and routing table.

## Critical Rules (always enforced)

These six rules apply to every ReArch test and must never be violated:

1. **Driver**: Use `TestSuiteSetup.initialize_rearch_driver(testcase_id)` — NEVER `initialize_app_driver()` (that targets the old mpos app)

2. **Locators**: Use `AppiumBy` (NATIVE_APP context) only — NEVER `By.CSS_SELECTOR` or WebView locators

3. **Validations**: Generate only App validation + API validation + Charge slip validation — NEVER Portal validation or DB validation. Do NOT add `@pytest.mark.portalVal` or `@pytest.mark.dbVal`.

4. **File placement**: All ReArch tests go in `TestCases/Functional/UI/ReArch/` — no payment-method subdirectories

5. **Naming**: `test_UI_ReArch_PM_<METHOD>_<FLOW>_<VARIANT>_<NUMBER>.py`

6. **Database**: `Database/ezeauto.db` (SQLite) is for test framework only — API templates, resource management. MySQL is for all application data — transactions, merchant config, org settings. Never mix them.

## Reference Tests

The **700+ production tests** in `TestCases/Functional/UI/Common/` are the source of truth for coding style, `ResourceAssigner` / `DBProcessor` usage, `org_settings_update` patterns, and `Validator` calls. Match their structure exactly.

## Reference Repositories (read-only)

`eze-common`, `eze-server`, `eze-middleware`, `pos` — backend context only. NEVER modify. NEVER use as test code templates.
