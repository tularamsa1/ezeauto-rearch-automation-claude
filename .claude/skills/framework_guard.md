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
- SQLite
- MySQL
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