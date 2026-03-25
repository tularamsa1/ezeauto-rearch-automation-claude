SKILL: device_walkthrough
PURPOSE
Capture a live device walk-through from the user and produce verified, registry-aligned
NL steps that can be handed off directly to test_generator.md for code generation.

USE THIS SKILL WHEN
- The user has NOT yet provided numbered NL steps
- The flow is new, unfamiliar, or involves a payment method not previously generated
- The user says "I just ran through the flow on device" or similar
- Multiple scenarios need to be captured in one session

DO NOT USE THIS SKILL WHEN
- The user already provides complete numbered NL steps → go directly to test_generator.md
- The new test is a trivial variation of an already-generated test (e.g., same Cash flow,
  different amount) → parameterise the existing test instead

─────────────────────────────────────────────────────────────────────────────────
PHASE 1 — PRE-FLIGHT
─────────────────────────────────────────────────────────────────────────────────
Ask the following questions BEFORE asking the user to narrate screens.
Present them all at once (not one-by-one) to avoid back-and-forth.

  Q1. Payment method?
      (Cash / UPI QR / Card / EMI / other)
  Q2. Scenario?
      (Success / Failure / Partial refund / Timeout / other)
  Q3. Amount?
      (fixed value, e.g. 100 — or a range, e.g. 50–500)
  Q4. Bank / acquirer / issuer?
      (e.g. HDFC acquirer, ICICI issuer — leave blank if not applicable)
  Q5. Any special setup you performed before launching the app?
      (e.g. "I enabled cash in merchant portal", "I configured UPI in settings",
       "no special setup needed")

After the user answers, summarise a PRE-FLIGHT CARD:

  Payment method : <answer>
  Scenario       : <answer>
  Amount         : <answer>
  Bank/acquirer  : <answer>
  Pre-setup done : <answer>

Confirm with the user ("Does this look right?") then move to Phase 2.

─────────────────────────────────────────────────────────────────────────────────
PHASE 2 — SCREEN-BY-SCREEN CAPTURE
─────────────────────────────────────────────────────────────────────────────────
MANDATORY — never skip this phase, even if pre-flight answers seem detailed enough.
Pre-flight answers describe intent; Phase 2 captures what actually happened on device.
Skipping Phase 2 leads to missed wait states, intermediate screens, and wrong step ordering.

Open with this exact prompt:
  "Now walk me through each screen you saw on device, one at a time — starting from
   the moment you launched the app. Describe what was visible and what you tapped."

For each screen the user describes, ask 1–2 targeted follow-up questions if anything
is ambiguous. Keep follow-ups short and precise.

PROBING QUESTION TEMPLATES (use the most relevant ones):
  - "Did a payment method overlay/bottom-sheet appear before you reached <next screen>?"
  - "After tapping Confirm, did the app show a loading/spinner state before success?"
  - "What exact fields are visible on the transaction detail screen?"
    (payment id / status / amount / date / RRN / auth code / payment mode — list all)
  - "Was there an intermediate screen between A and BDevice Screen (real Android)
           ↓
      [ADB command]
           ↓
  UIAutomator XML Dump
  (hierarchy + attributes)
           ↓
  [rearch_xpath_extractor.py]
      ↓           ↓
    ✅ Auto-generates     ✅ Builds YAML
    rearch_locators_      locator_
    generated.py          registry.yaml
           ↓
      [YOU REVIEW]
      ✅ Check each locator works
      ✅ Fix TODOs manually
      ✅ Merge into rearch_native_locators.py
           ↓
  [YOU CREATE]
  rearch_<screen>_page.py
  (business-level methods)
           ↓
  [YOU REGISTER]
  action_registry.yaml
  (NL pattern → method mapping)
           ↓
      [test_generator.md]
      Uses the registry to
      convert NL steps → Python test codeDevice Screen (real Android)
               ↓
          [ADB command]
               ↓
      UIAutomator XML Dump
      (hierarchy + attributes)
               ↓
      [rearch_xpath_extractor.py]
          ↓           ↓
        ✅ Auto-generates     ✅ Builds YAML
        rearch_locators_      locator_
        generated.py          registry.yaml
               ↓
          [YOU REVIEW]
          ✅ Check each locator works
          ✅ Fix TODOs manually
          ✅ Merge into rearch_native_locators.py
               ↓
      [YOU CREATE]
      rearch_<screen>_page.py
      (business-level methods)
               ↓
      [YOU REGISTER]
      action_registry.yaml
      (NL pattern → method mapping)
               ↓
          [test_generator.md]
          Uses the registry to
          convert NL steps → Python test codeDevice Screen (real Android)
                   ↓
              [ADB command]
                   ↓
          UIAutomator XML Dump
          (hierarchy + attributes)
                   ↓
          [rearch_xpath_extractor.py]
              ↓           ↓
            ✅ Auto-generates     ✅ Builds YAML
            rearch_locators_      locator_
            generated.py          registry.yaml
                   ↓
              [YOU REVIEW]
              ✅ Check each locator works
              ✅ Fix TODOs manually
              ✅ Merge into rearch_native_locators.py
                   ↓
          [YOU CREATE]
          rearch_<screen>_page.py
          (business-level methods)
                   ↓
          [YOU REGISTER]
          action_registry.yaml
          (NL pattern → method mapping)
                   ↓
              [test_generator.md]
              Uses the registry to
              convert NL steps → Python test code?"
  - "Did the app require you to re-enter or confirm anything at that point?"
  - "What did the success screen show — just a checkmark, or a summary with amount?"

MAPPING RULE (internal — do NOT show to user)
While the user narrates, maintain a running internal list of steps.
Map each described action to the closest action_registry.yaml pattern using the
vocabulary in Tools/action_registry.yaml (synonyms block included).
Flag any step where no registry pattern clearly matches — ask the user for more
detail on that screen before proceeding to Phase 3.

─────────────────────────────────────────────────────────────────────────────────
PHASE 3 — NL STEP REVIEW
─────────────────────────────────────────────────────────────────────────────────
Present the derived steps using registry vocabulary (not the user's raw words).
Format exactly as shown below so test_generator.md can consume it directly.

EXAMPLE OUTPUT:

  Preconditions:
  1. update org_settings: cashEnabled = true   ← include only if user mentioned pre-setup

  Test Steps:
  1. launch rearch app
  2. login with credentials
  3. wait for home page to load
  4. enter amount 45
  5. select cash from payment methods
  6. wait for cash confirm screen
  7. click confirm payment
  8. verify success screen
  9. click proceed to home
  10. click txn history
  11. click first transaction
  12. wait for txn detail page
  13. fetch payment id, status, payment mode, date time
  14. validate app values
  15. validate api values

Then ask: "Do these steps match what you observed on device? Correct any step before I generate code."

WAIT for explicit user approval ("yes", "looks good", "LGTM", or corrected steps)
before moving to Phase 4. Do NOT generate code before approval is received.

─────────────────────────────────────────────────────────────────────────────────
PHASE 4 — TEST GENERATION HAND-OFF
─────────────────────────────────────────────────────────────────────────────────
Once the user approves the NL steps in Phase 3, run the standard test_generator.md
5-step workflow using those approved steps as the INPUT.

Carry forward from Phase 1:
  - Pre-setup answers → org_settings_update preconditions (see test_preconditions.md)
  - Bank/acquirer/issuer → used in testcase_id suffix and file name
  - Validation fields confirmed in Phase 3 → app validation assertions

Verification checklist (from test_generator.md Step 5) MUST pass before presenting
the generated file to the user:
  1. python -m py_compile <generated_file>          (no syntax errors)
  2. grep "initialize_app_driver" <generated_file>  (must be empty)
  3. grep "By\.CSS_SELECTOR" <generated_file>       (must be empty)
  4. grep "appium_driver" <generated_file>           (must be empty)
  5. grep "validateAgainstDB\|validateAgainstPortal" <generated_file>  (must be empty)

─────────────────────────────────────────────────────────────────────────────────
PRECONDITION MAPPING (Phase 1 Q5 → org_settings_update key)
─────────────────────────────────────────────────────────────────────────────────
Pre-setup answer                    → Precondition key
"enabled cash"                      → cashEnabled = true
"disabled cash"                     → cashEnabled = false
"configured UPI" / "enabled UPI"    → upiEnabled = true
"disabled UPI"                      → upiEnabled = false
"enabled card"                      → cardEnabled = true
"no special setup"                  → (no precondition block needed)

See .claude/skills/test_preconditions.md for the full key table and revert template.
Always revert preconditions in the finally block.

─────────────────────────────────────────────────────────────────────────────────
MULTI-SCENARIO SESSIONS
─────────────────────────────────────────────────────────────────────────────────
If the user ran through more than one flow in the same device session:
- Complete Phases 1–3 for scenario A, get approval, generate test A.
- Then ask: "Ready to capture the next scenario?" and restart from Phase 1.
- Each scenario produces one independent test file.
- Do NOT batch multiple scenarios into a single test method.

─────────────────────────────────────────────────────────────────────────────────
VALIDATION FIELDS REFERENCE
─────────────────────────────────────────────────────────────────────────────────
Common fields visible on ReArch txn detail screen (confirm with user in Phase 2):
  payment_id    → non-empty string assertion
  status        → "Captured" / "Failed" / "Refunded"
  amount        → matches entered amount
  date_time     → non-empty string assertion
  payment_mode  → "Cash" / "UPI" / "Card" / etc.
  rrn           → (card/UPI flows only) non-empty string
  auth_code     → (card flows only) non-empty string

Only assert fields the user confirmed seeing on the detail screen.
Do NOT assert fields the user did not mention.
