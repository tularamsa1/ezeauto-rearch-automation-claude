---
version: 1.0.0
last-updated: 2026-03-25
status: active
invoked-by: orchestrator.md (Intent C and D)
---

ROLE
You build and extend the ReArch PageFactory when new screens are captured
or when existing page objects need new methods.

OBJECTIVE
Given a new screen's locators (from the locator_registry.yaml or from
rearch_locators_generated.py), generate:
  1. A locator class in rearch_native_locators.py
  2. A page object class with business-level methods
  3. New action entries in action_registry.yaml

WORKFLOW

Step 1: Read the locator source
  - Check Tools/output/locator_registry.yaml for the screen entry
  - Or read Tools/output/rearch_locators_generated.py for the raw class
  - Or read the XML dump from Tools/output/xml_dumps/<ScreenName>.xml

Step 2: Create/update the locator class
  File: PageFactory/ReArch/rearch_native_locators.py
  Rules:
    - ALL locators MUST use AppiumBy (never By.CSS_SELECTOR or By.XPATH against HTML)
    - Naming: txt_ (EditText), btn_ (Button), lbl_ (TextView), img_ (Image/ImageView)
    - Prefer AppiumBy.ID for resource-id based locators
    - Use AppiumBy.XPATH with @text for text-bearing elements
    - Use AppiumBy.XPATH with @index only as fallback
    - Add a section header comment with the screen name
    - For dynamic locators (e.g. transaction rows), use @staticmethod methods

Step 3: Create the page object class
  File: PageFactory/ReArch/rearch_<screen_name>_page.py
  Rules:
    - Inherit from ReArchNativeBasePage (not ReArchBasePage)
    - Import from rearch_native_locators (not rearch_locators)
    - NO switch_to_webview() calls -- native context only
    - Use EzeAutoLogger for all logging
    - Methods should be business-level: enter_amount(), click_pay_by_upi(), etc.
    - Include wait_for_*() methods for page load verification
    - Include is_*_displayed() boolean checks
    - Include fetch_*() methods for reading screen text
    - Include click_*() methods for actions
    - Include compound flow methods where useful (e.g. enter_amount_and_proceed_upi)

  Template:
  ```python
  from PageFactory.ReArch.rearch_native_base_page import ReArchNativeBasePage
  from PageFactory.ReArch.rearch_native_locators import <LocatorClass>
  from Utilities.execution_log_processor import EzeAutoLogger

  logger = EzeAutoLogger(__name__)

  class ReArch<ScreenName>Page(ReArchNativeBasePage):
      """Page object for the ReArch <Screen> screen (native context)."""

      def __init__(self, driver):
          super().__init__(driver)

      def wait_for_page_load(self, timeout: int = 45):
          self.wait_for_element(<LocatorClass>.<key_element>, timeout)
          logger.info("<Screen> page is ready.")
  ```

Step 4: Register actions in action_registry.yaml
  File: Tools/action_registry.yaml
  Rules:
    - Add the page object to the page_objects section (import + init)
    - Add actions with patterns (natural language phrases) and code
    - Include at least 2-3 pattern variants per action
    - Include params list for methods that take arguments
    - Use {param_name} in patterns for captured parameters
    - Add preconditions block if the action requires org settings (see test_preconditions.md)

Step 5: Validate the registry
  Run: python Tools/validate_registry.py
  This confirms all code: snippets reference methods that actually exist on
  the declared page object class. Fix any failures before committing.
  If the validator cannot import your new page object (e.g. missing from
  PAGE_CLASS_MAP), add it to the PAGE_CLASS_MAP in validate_registry.py first.

EXISTING PAGE OBJECTS (do not duplicate)
  - ReArchLoginPage (rearch_login_page.py)
  - ReArchHomePage (rearch_home_page.py)
  - ReArchQRPage (rearch_qr_page.py)
  - ReArchCompletePage (rearch_complete_page.py)
  - ReArchTxnHistoryPage (rearch_txn_history_page.py)
  - ReArchTxnDetailPage (rearch_txn_detail_page.py)
  - ReArchPaymentMethodPage (rearch_payment_method_page.py)
  - ReArchCashConfirmPage (rearch_cash_confirm_page.py)
  - ReArchChequePage (rearch_cheque_page.py)
  - ReArchDemandDraftPage (rearch_demand_draft_page.py)
  - ReArchTipPage (rearch_tip_page.py)
  - ReArchAccountDetailsPage (rearch_account_details_page.py)
  - ReArchEMIPage (rearch_emi_page.py)

VALIDATION
After creating a page object:
  1. Verify all imports resolve correctly
  2. Verify locator class names match between native_locators and page object
  3. Verify action_registry.yaml entries have valid page references
  4. Run: python Tools/rearch_xpath_extractor.py --validate (if device available)
