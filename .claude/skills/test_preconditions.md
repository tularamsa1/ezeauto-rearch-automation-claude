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
