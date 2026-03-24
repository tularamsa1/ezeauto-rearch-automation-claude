## ReArch Test Validations

### Allowed Validation Types (ReArch ONLY)

1. **App validation** — UI assertions via TxnHistory → TxnDetail pages
2. **API validation** — txnlist API response checks
3. **Charge slip validation** — receipt content checks

**Forbidden for ReArch:** Portal validation, DB validation.
**Markers to use:** `@pytest.mark.appVal`, `@pytest.mark.apiVal`, `@pytest.mark.chargeSlipVal`
**Markers forbidden:** `@pytest.mark.portalVal`, `@pytest.mark.dbVal`

---

### Default App Validation

When the test navigates to TxnDetail, ALWAYS assert these three fields unless
the user writes "skip default validation":

```python
# 1. Payment ID is non-empty
assert txn_detail_page.fetch_payment_id(), "Payment ID should not be empty"

# 2. Amount matches execution value
# (only if amount is displayed on detail page for this payment method)
# If not displayed, skip and log a warning instead

# 3. Date & Time is non-empty
assert txn_detail_page.fetch_date_time(), "Date & Time should not be empty"
```

These assertions go in the App Validation section AFTER any user-specified asserts.

---

### Full App Validation Pattern

```python
if ConfigReader.read_config("Validations", "app_validation") == "True":
    try:
        date_and_time = date_time_converter.to_app_format(created_time)
        expected_app_values = {
            "pmt_status":    "Payment Successful",
            "pmt_mode":      "UPI",          # or Cash, Card, etc.
            "txn_id":        txn_id,
            "settle_status": "SETTLED",
            "date":          date_and_time,
            "rrn":           str(rr_number_db),
        }

        complete_page.click_proceed_to_home()
        home_page.wait_for_home_page_load()
        home_page.click_txn_history()

        txn_history_page = ReArchTxnHistoryPage(app_driver)
        txn_history_page.wait_for_txn_list()
        txn_history_page.click_first_transaction()

        txn_detail_page = ReArchTxnDetailPage(app_driver)
        txn_detail_page.wait_for_detail_page()

        actual_app_values = {
            "pmt_status":    payment_status_ui,
            "pmt_mode":      txn_detail_page.fetch_payment_mode(),
            "txn_id":        txn_detail_page.fetch_payment_id(),
            "settle_status": txn_detail_page.fetch_status(),
            "date":          txn_detail_page.fetch_date_time(),
            "rrn":           str(txn_detail_page.fetch_rrn()),
        }
        Validator.validateAgainstAPP(
            expectedApp=expected_app_values, actualApp=actual_app_values
        )
    except Exception as e:
        Configuration.perform_app_val_exception(testcase_id, e)
```

---

### API Validation Pattern

```python
if ConfigReader.read_config("Validations", "api_validation") == "True":
    try:
        date = date_time_converter.db_datetime(created_time)
        expected_api_values = {
            "pmt_status":    "AUTHORIZED",
            "txn_amt":       float(amount),
            "pmt_mode":      "UPI",         # or Cash, Card, etc.
            "pmt_state":     "SETTLED",
            "settle_status": "SETTLED",
            "acquirer_code": "ICICI",       # adjust per payment method
            "issuer_code":   "ICICI",
            "txn_type":      "CHARGE",
            "mid":           virtual_mid,
            "tid":           virtual_tid,
            "org_code":      org_code,
            "order_id":      order_id_db,
            "rrn":           str(rrn),
            "date":          date,
        }

        api_details = DBProcessor.get_api_details(
            "txnlist",
            request_body={"username": app_username, "password": app_password},
        )
        response = APIProcessor.send_request(api_details)

        txn_data = next(
            (x for x in response["txns"] if x["txnId"] == txn_id), None
        )
        if txn_data is None:
            raise ValueError(f"txn_id '{txn_id}' not found in txnlist response")

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
        Validator.validationAgainstAPI(
            expectedAPI=expected_api_values, actualAPI=actual_api_values
        )
    except Exception as e:
        Configuration.perform_api_val_exception(testcase_id, e)
```

---

### Charge Slip Validation Pattern

**Import required:** `from Utilities import ... receipt_validator ...`
**Config key:** `ConfigReader.read_config("Validations", "charge_slip_validation")`
**Exception handler:** `Configuration.perform_charge_slip_val_exception(testcase_id, e)`

`posting_date` is sourced from the txn DB record (same query used for API validation).

**Expected fields vary by payment method:**

| Field | UPI | Card | Cash |
|---|---|---|---|
| `PAID BY:` | `"UPI"` | `"CARD"` | `"CASH"` |
| `merchant_ref_no` | `"Ref # " + order_id` | `"Ref # " + order_id` | `"Ref # " + order_id` |
| `RRN` | `str(rrn)` | `str(rrn)` | — |
| `BASE AMOUNT:` | `"Rs." + amount + ".00"` | `"Rs." + amount + ".00"` | `"Rs." + amount + ".00"` |
| `AUTH CODE` | — | `str(auth_code)` | — |
| `date` | `txn_date` | `txn_date` | `txn_date` |
| `time` | `txn_time` | `txn_time` | `txn_time` |

```python
if ConfigReader.read_config("Validations", "charge_slip_validation") == "True":
    logger.info(f"Started ChargeSlip validation for the test case : {testcase_id}")
    try:
        txn_date, txn_time = date_time_converter.to_chargeslip_format(posting_date_db=posting_date)
        expected_chargeslip_values = {
            "PAID BY:":        "UPI",                          # adjust per payment method
            "merchant_ref_no": "Ref # " + str(order_id),
            "RRN":             str(rrn),
            "BASE AMOUNT:":    "Rs." + str(amount) + ".00",
            "date":            txn_date,
            "time":            txn_time,
            # "AUTH CODE": str(auth_code),                    # card only
        }
        logger.debug(f"expected_chargeslip_values: {expected_chargeslip_values}")
        receipt_validator.perform_charge_slip_validations(
            txn_id,
            {"username": app_username, "password": app_password},
            expected_details=expected_chargeslip_values,
        )
    except Exception as e:
        Configuration.perform_charge_slip_val_exception(testcase_id, e)
    logger.info(f"Completed ChargeSlip validation for the test case : {testcase_id}")
```
