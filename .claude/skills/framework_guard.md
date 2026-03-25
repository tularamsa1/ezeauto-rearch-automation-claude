---
version: 1.0.0
last-updated: 2026-03-25
status: active
invoked-by: always in context (not chained — enforced on all tasks)
---

CRITICAL RULE
Never break the existing automation framework.

Only extend functionality.

FRAMEWORK PRESERVATION RULES

1. RERUN LOGIC
Preserve pytest-rerunfailures logic.
Maintain:
- bool_rerun_immediately
- bool_rerun_at_the_end
- bool_rerun_at_the_end_parallel
Do not modify Utilities/Rerun.py behavior.

2. PARALLEL EXECUTION
Preserve pytest-xdist with max 5 threads.
Keep calculateTestCasesCountForParallelExecution() unchanged.

3. MERCHANT CREATION
Do not modify merchant_creator.py or merchant_configurer.py logic.
Reuse APIs for merchant setup.

4. DATABASE OPERATIONS
Preserve dual DB architecture:

  Database/ezeauto.db (SQLite) — test framework only:
    - API request templates: DBProcessor.get_api_details("apiName", ...)
    - Resource management: app_users, portal_users, devices, appium_servers
    - NEVER use ezeauto.db for application state (txns, merchant configs, etc.)

  MySQL — all application data:
    - DBProcessor.getValueFromDB("select * from txn ...")
    - Tables: txn, upi_merchant_config, org_employee, terminal_info, org_code, etc.
    - NEVER route application DB queries to ezeauto.db

  Rule: if you need to know a txn status, merchant config, or org setting →
  query MySQL. If you need an API endpoint/request template → use ezeauto.db
  via get_api_details().

Maintain DBProcessor.py functionality.

5. THREAD RESOURCE MANAGEMENT
Preserve atomic resource allocation in ResourceAssigner.py.

6. REPORT GENERATION
Preserve existing reports:
- Excel
- Allure
- HTML
- PDF

Keep directory structure:
Reports/ExecutionDate_[DATE]/ExecutionTime_[TIME]/[ReportType]/

7. REARCH APP VALIDATION — DATE FORMAT
Use `date_time_converter.to_rearch_app_format(created_time)` for the expected date
in ReArch App Validation.
NEVER use `date_time_converter.to_app_format()` for ReArch tests — that is for the
old mpos app and produces the wrong format.

8. REARCH TXNDETAIL — NO wait_for_detail_page()
NEVER call `txn_detail_page.wait_for_detail_page()` in ReArch tests.
It fails in practice. Every `fetch_*` method (fetch_status, fetch_payment_id, etc.)
has its own internal WebDriverWait. Navigate to the detail page and call fetch_*
directly — no explicit wait needed.