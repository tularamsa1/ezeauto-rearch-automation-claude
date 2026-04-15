---
version: 1.1.0
last-updated: 2026-03-25
status: active
invoked-by: test_generator.md (pattern library — not chained directly)
---

## ReArch Test Preconditions

### org_settings_update Pattern

To enable or disable a merchant-level setting before a test, use the
`org_settings_update` endpoint. This is the ONLY supported way to configure
merchant-level preconditions in ReArch tests.

**Setup code (in SETUP section):**
```python
api_details = DBProcessor.get_api_details('org_settings_update', request_body={
    "username": portal_username,
    "password": portal_password,
    "entityName": "org",
    "settingForOrgCode": org_code,
})
api_details["RequestBody"]["settings"]["settingKeyHere"] = "true"
logger.debug(f"Precondition API details: {api_details}")
response = APIProcessor.send_request(api_details=api_details)
logger.debug(f"Precondition response: {response}")
```

**Revert code (in finally block, before executeFinallyBlock):**
```python
finally:
    try:
        api_details = DBProcessor.get_api_details('org_settings_update', request_body={
            "username": portal_username,
            "password": portal_password,
            "entityName": "org",
            "settingForOrgCode": org_code,
        })
        api_details["RequestBody"]["settings"]["settingKeyHere"] = "false"
        APIProcessor.send_request(api_details=api_details)
    except Exception as e:
        logger.exception(f"Precondition revert failed: {e}")
    Configuration.executeFinallyBlock(testcase_id)
```

### Settings Refresh After Auto-Login

When a test uses `autoLoginByTokenEnabled = true` (auto-login) AND applies new
org_settings preconditions, the app won't pick up the changed settings because
auto-login bypasses the fresh login flow that triggers a settings re-fetch.

**Fix:** After landing on the Collect Payment page, navigate to Payment History,
wait until the Dashboard is visible, then go back. This forces the app to
re-fetch org settings.

**When to add this block:** Whenever the test has org_settings preconditions
AND the login step uses `perform_login_if_required()` (auto-login path).

**Code (insert after `click_collect_payment()` + `wait_for_home_page_load()`,
before entering any amount):**
```python
# Refresh settings: navigate to Payment History, wait for Dashboard, then back
# (auto-login bypasses fresh login, so preconditions aren't picked up without this)
home_page.click_txn_history()
txn_history_page = ReArchTxnHistoryPage(app_driver)
txn_history_page.wait_for_txn_list()
assert home_page.is_element_visible(TxnHistoryLocators.btn_my_dashboard, time=10), \
    "My Dashboard button should be visible on Payment History"
logger.debug("Payment History loaded with Dashboard visible — settings refreshed")
home_page.go_back()
logger.debug("Navigated back from Payment History")
```

**Required imports (add if not already present):**
```python
from PageFactory.ReArch.rearch_txn_history_page import ReArchTxnHistoryPage
from PageFactory.ReArch.rearch_native_locators import TxnHistoryLocators
```

### Reading Preconditions from action_registry.yaml

The `action_registry.yaml` declares preconditions on relevant actions:

```yaml
- patterns: ["click cash", "select cash"]
  page: ReArchHomePage
  method: click_pay_by_cash
  preconditions:
    org_settings:
      cashEnabled: "true"
    revert_on_finally:
      cashEnabled: "false"
```

When generating a test, collect all unique `preconditions.org_settings` from
matched actions and emit one `org_settings_update` call per unique key in SETUP.
Collect all `revert_on_finally` entries and emit revert calls in the finally block.

### Common Setting Keys

| Feature           | Key                                   | Enable  | Disable |
|-------------------|---------------------------------------|---------|---------|
| Cash payment      | `cashEnabled`                         | `"true"` | `"false"` |
| Remote pay        | `remotePaymentEnabled`                | `"true"` | `"false"` |
| EMI               | `emiEnabled`                          | `"true"` | `"false"` |
| Instant EMI       | `instantEmiEnabled`                   | `"true"` | `"false"` |
| Customer auth     | `customerAuthDataCaptureEnabled`      | `"true"` | `"false"` |
| Time-based restriction | `timeBasedTxnRestrictionEnabled` | `"true"` | `"false"` |
