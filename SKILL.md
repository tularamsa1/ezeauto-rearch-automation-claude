# SKILL.md — ReArch NL-to-Test Skills System

## 1. What Is This File

SKILL.md is the master routing guide for the ReArch test automation skills system.

**Relationship to CLAUDE.md:**
- `CLAUDE.md` — auto-loaded by Claude Code on every session start. Holds the 6 critical rules that are always enforced and points here for all routing.
- `SKILL.md` (this file) — the skills catalog and routing guide. Read this for any generation, extraction, or validation task.

**For all generation tasks, the entry point is:** `.claude/skills/orchestrator.md`

---

## 2. Skills Routing Table

| User Intent | Signal Words / Context | Skill Chain |
|---|---|---|
| A — Generate test from NL steps | Numbered steps provided: `1. launch... 2. login...` | orchestrator → `test_generator.md` |
| B — Capture a device walk-through | "I ran", "I walked through", "on device", no steps yet | orchestrator → `device_walkthrough.md` → `test_generator.md` |
| C — New screen / page object | "new screen", XML dump shared, ADB output provided | orchestrator → `xpath_extractor.md` → `page_factory_builder.md` |
| D — Extend existing page object | "add method", "update page object", existing screen | orchestrator → `page_factory_builder.md` |
| E — System health / validate | "check registry", "validate", "is registry in sync" | `python Tools/validate_registry.py` |

**When in doubt:** Read `.claude/skills/orchestrator.md` — it classifies intent and routes to the correct skill chain, or asks a clarifying question if ambiguous.

---

## 3. Skill Inventory

| Skill File | Version | Status | Purpose | Triggered By |
|---|---|---|---|---|
| `orchestrator.md` | 1.0.0 | active | Intent router — entry point for all generation tasks | Any generation request |
| `test_generator.md` | 1.2.0 | active | Converts approved NL steps → pytest test code | orchestrator (Intent A/B) |
| `device_walkthrough.md` | 1.1.0 | active | Captures live device walk-through → approved NL steps | orchestrator (Intent B) |
| `page_factory_builder.md` | 1.0.0 | active | Builds new page objects from locator sources | orchestrator (Intent C/D) |
| `xpath_extractor.md` | 1.0.0 | active | Extracts native AppiumBy locators from uiautomator XML | orchestrator (Intent C) |
| `test_template.md` | 1.1.0 | active | Full pytest test file template (pattern library) | Referenced by test_generator.md |
| `test_preconditions.md` | 1.1.0 | active | org_settings_update patterns and key table | Referenced by test_generator.md |
| `test_validations.md` | 1.1.0 | active | App, API, and charge slip validation code patterns | Referenced by test_generator.md |
| `framework_guard.md` | 1.0.0 | active | Rules to prevent breaking the existing framework | Always in context |

**Removed skills:**
- `db_validation_generator.md` — deleted. DB validation is forbidden for ReArch tests.
- `nl_test_generator.md` — deleted. Functionality merged into `test_generator.md`.

---

## 4. Dependency Graph

```
orchestrator.md
    │
    ├─ Intent A (NL steps given)
    │       └─ test_generator.md
    │               ├─ test_template.md          (pattern library)
    │               ├─ test_preconditions.md     (pattern library)
    │               ├─ test_validations.md       (pattern library)
    │               └─ Tools/action_registry.yaml (data)
    │
    ├─ Intent B (device walk-through)
    │       └─ device_walkthrough.md
    │               └─ [returns approved NL steps to orchestrator]
    │                       └─ test_generator.md (as above)
    │
    ├─ Intent C (new screen)
    │       ├─ xpath_extractor.md
    │       └─ page_factory_builder.md
    │               └─ Tools/validate_registry.py (validation)
    │
    ├─ Intent D (extend page object)
    │       └─ page_factory_builder.md
    │               └─ Tools/validate_registry.py (validation)
    │
    └─ Intent E (system health)
            └─ python Tools/validate_registry.py

framework_guard.md — always in context, not chained
```

---

## 5. Skill Chaining Examples

### Example A — Generate test from NL steps
```
User: "1. launch rearch app  2. login  3. enter amount 200  4. pay by card..."
→ orchestrator detects numbered steps → Intent A
→ reads test_generator.md
→ reads Tools/action_registry.yaml
→ matches each step to registry actions
→ generates test file in TestCases/Functional/UI/ReArch/
→ runs Step-5 verification (py_compile + grep checks)
```

### Example B — Device walk-through
```
User: "I just ran a UPI success flow on device"
→ orchestrator detects "ran / device / flow" → Intent B
→ reads device_walkthrough.md
→ Phase 1: pre-flight questions (method, scenario, amount, bank, setup)
→ Phase 2: screen-by-screen capture
→ Phase 3: produces approved NL steps
→ returns steps to orchestrator
→ orchestrator hands off to test_generator.md (Intent A path)
```

### Example C — New screen
```
User: "New card PIN entry screen appeared — here's the XML dump"
→ orchestrator detects "new screen / XML" → Intent C
→ reads xpath_extractor.md → extracts AppiumBy locators
→ reads page_factory_builder.md → builds ReArchCardPinPage
→ runs python Tools/validate_registry.py to confirm
```

### Example D — Extend existing page object
```
User: "Add a method to click the refund button on the TxnDetail page"
→ orchestrator detects "add method / existing page" → Intent D
→ reads page_factory_builder.md (skip xpath_extractor)
→ adds method, updates action_registry.yaml
→ runs python Tools/validate_registry.py
```

### Example E — System health check
```
User: "Is the registry in sync with page objects?"
→ orchestrator detects "validate / registry / health" → Intent E
→ runs: python Tools/validate_registry.py
→ reports: N passed | 0 failed | 0 skipped
```

---

## 6. How to Add a New Skill

1. Create `.claude/skills/<skill_name>.md`
2. Add the version header block at the top:
   ```
   ---
   version: 1.0.0
   last-updated: YYYY-MM-DD
   status: active
   ---
   ```
3. Add an entry to the **Skill Inventory** table in this file (SKILL.md)
4. Add a routing row to the **Skills Routing Table** if the skill handles a new intent
5. Add the skill node to the **Dependency Graph**
6. Update `orchestrator.md` with the new intent classification logic

**Mandatory skill file sections:**
- `ROLE` — one-line description of what the skill does
- `OBJECTIVE` — what it produces
- `WORKFLOW` — numbered steps
- `RULES` — constraints and guardrails
- `Changelog` — version history

---

## 7. Common Mistakes

| Mistake | Correct Approach |
|---|---|
| Using `initialize_app_driver()` for ReArch | Always use `initialize_rearch_driver(testcase_id)` |
| Using `By.CSS_SELECTOR` in ReArch tests | AppiumBy (NATIVE_APP context) only — no WebView locators |
| Using `external_ref='{order_id}'` in txn DB lookup | Use `org_code + payment_mode ORDER BY created_time DESC LIMIT 1` |
| Adding charge slip validation to failure tests | Charge slip only for success/authorized flows — no RRN exists on failure |
| Calling `wait_for_detail_page()` on TxnDetail | Never call it — each `fetch_*` method has its own internal WebDriverWait |
| Using `to_app_format()` for ReArch date | Use `date_time_converter.to_rearch_app_format(created_time)` |
| Adding Portal or DB validation blocks | Only App + API + Charge slip validation in ReArch tests |
| Placing tests in payment-method subdirectories | All ReArch tests go directly in `TestCases/Functional/UI/ReArch/` |
| Adding new page object without updating PAGE_CLASS_MAP | Always add to `Tools/validate_registry.py` PAGE_CLASS_MAP first |

---

## 8. Data Layer Reference

| File | Purpose |
|---|---|
| `Tools/action_registry.yaml` | NL patterns → PageFactory method mapping + preconditions |
| `Tools/validate_registry.py` | Validates all `code:` snippets reference real page object methods |
| `Database/ezeauto.db` | SQLite — framework only: API templates, devices, users |
| MySQL (remote) | Application data: txn, org_code, org_employee, terminal_info, etc. |
| `PageFactory/ReArch/` | All ReArch page objects and locators |
| `TestCases/Functional/UI/ReArch/` | Generated test files |
| `TestCases/Functional/UI/Common/` | 700+ reference tests — source of truth for coding style |
