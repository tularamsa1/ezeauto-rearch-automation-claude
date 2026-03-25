---
version: 1.0.0
last-updated: 2026-03-25
status: active
invoked-by: orchestrator.md (Intent C)
---

ROLE
You extract native UI locators from the ReArch Android app using uiautomator XML dumps.

SOURCE
Native locators are extracted from the device UI hierarchy using:
  Tools/rearch_xpath_extractor.py

DO NOT extract locators from the POS frontend repository (pos/web/src).
Those produce WebView/HTML locators (By.CSS_SELECTOR, By.XPATH against DOM)
which do NOT work in NATIVE_APP context.

EXTRACTION TOOL
The extractor uses ADB + uiautomator to dump the screen XML, then generates
AppiumBy-compatible locator classes.

Commands:
  # Interactive full extraction (all screens):
  python Tools/rearch_xpath_extractor.py --interactive

  # Single screen from live device:
  python Tools/rearch_xpath_extractor.py --screen login --class-name LoginLocators

  # Parse existing XML dump:
  python Tools/rearch_xpath_extractor.py --xml-file Tools/output/xml_dumps/Login_ReArch.xml --screen login --class-name LoginLocators

  # Regenerate from all saved XML dumps:
  python Tools/rearch_xpath_extractor.py --regenerate

  # Validate locators against live device (requires Appium):
  python Tools/rearch_xpath_extractor.py --validate

OUTPUTS
  Tools/output/rearch_locators_generated.py  — Python locator classes (review before use)
  Tools/output/locator_registry.yaml         — Machine-readable registry for Claude
  Tools/output/xml_dumps/                    — Raw XML per screen

LOCATOR RULES
1. ALL locators for ReArch MUST use AppiumBy (NATIVE_APP context).
2. NEVER generate By.CSS_SELECTOR or By.XPATH against HTML DOM elements.
3. Prefer AppiumBy.ID (resource-id) for stability.
4. Use AppiumBy.XPATH with @text for text-bearing elements.
5. Use AppiumBy.XPATH with @index only as a last resort.
6. Follow naming conventions: txt_ (inputs), btn_ (buttons), lbl_ (labels), img_ (images).

INTEGRATION
After extraction and review, curated locators go into:
  PageFactory/ReArch/rearch_native_locators.py

The locator_registry.yaml is consumed by the nl_test_generator skill
to map natural language steps to PageFactory methods.
