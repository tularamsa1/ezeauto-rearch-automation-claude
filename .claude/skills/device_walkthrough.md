---
version: 1.1.0
last-updated: 2026-03-25
status: active
invoked-by: orchestrator.md (Intent B)
---

SKILL: device_walkthrough
PURPOSE
Capture a live device walk-through from the user and produce verified, registry-aligned
NL steps that can be handed back to orchestrator.md for handoff to test_generator.md.

USE THIS SKILL WHEN
- The user has NOT yet provided numbered NL steps
- The flow is new, unfamiliar, or involves a payment method not previously generated
- The user says "I just ran through the flow on device" or similar
- Multiple scenarios need to be captured in one session

DO NOT USE THIS SKILL WHEN
- The user already provides complete numbered NL steps → orchestrator routes to test_generator.md directly
- The new test is a trivial variation of an already-generated test (e.g., same Cash flow,
  different amount) → parameterise the existing test instead

─────────────────────────────────────────────────────────────────────────────
PHASE 1 — PRE-FLIGHT
─────────────────────────────────────────────────────────────────────────────
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

─────────────────────────────────────────────────────────────────────────────
PHASE 2 — SCREEN-BY-SCREEN CAPTURE
─────────────────────────────────────────────────────────────────────────────
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
  - "Was there an intermediate screen between A and B?"
  - "Did the app require you to re-enter or confirm anything at that point?"
  - "What did the success screen show — just a checkmark, or a summary with amount?"

MAPPING RULE (internal — do NOT show to user)
While the user narrates, maintain a running internal list of steps.
Map each described action to the closest action_registry.yaml pattern using the
vocabulary in Tools/action_registry.yaml (synonyms block included).
Flag any step where no registry pattern clearly matches — ask the user for more
detail on that screen before proceeding to Phase 3.

─────────────────────────────────────────────────────────────────────────────
PHASE 3 — NL STEP REVIEW
─────────────────────────────────────────────────────────────────────────────
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

─────────────────────────────────────────────────────────────────────────────
PHASE 4 — HAND-OFF TO ORCHESTRATOR
─────────────────────────────────────────────────────────────────────────────
Once the user approves the NL steps in Phase 3, return the approved steps to
orchestrator.md. Do NOT run test_generator.md directly from here — orchestrator
owns the handoff.

Return to orchestrator with:
  - The approved numbered NL steps (Phase 3 output)
  - Pre-flight context (from Phase 1):
      payment_method  → file name suffix (e.g. _PM_Card_)
      scenario        → flow name (Success / Failure / etc.)
      bank_acquirer   → variant suffix (e.g. _HDFC_01)
      pre_setup       → org_settings precondition key (see PRECONDITION MAPPING below)

Orchestrator will then proceed as Intent A → read test_generator.md with the
approved steps as INPUT. The Step-5 verification gate is owned by orchestrator.

─────────────────────────────────────────────────────────────────────────────
PRECONDITION MAPPING (Phase 1 Q5 → org_settings_update key)
─────────────────────────────────────────────────────────────────────────────
Pre-setup answer                    → Precondition key
"enabled cash"                      → cashEnabled = true
"disabled cash"                     → cashEnabled = false
"configured UPI" / "enabled UPI"    → upiEnabled = true
"disabled UPI"                      → upiEnabled = false
"enabled card"                      → cardEnabled = true
"no special setup"                  → (no precondition block needed)

See .claude/skills/test_preconditions.md for the full key table and revert template.
Always revert preconditions in the finally block.

─────────────────────────────────────────────────────────────────────────────
MULTI-SCENARIO SESSIONS
─────────────────────────────────────────────────────────────────────────────
If the user ran through more than one flow in the same device session:
- Complete Phases 1–3 for scenario A, get approval, hand off to orchestrator for test A.
- Then ask: "Ready to capture the next scenario?" and restart from Phase 1.
- Each scenario produces one independent test file.
- Do NOT batch multiple scenarios into a single test method.

─────────────────────────────────────────────────────────────────────────────
VALIDATION FIELDS REFERENCE
─────────────────────────────────────────────────────────────────────────────
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
