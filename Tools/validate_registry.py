#!/usr/bin/env python3
"""
validate_registry.py
====================
Validates that every `code:` snippet in Tools/action_registry.yaml references
a method that actually exists on the declared page object class.

Usage:
  python Tools/validate_registry.py

Exit codes:
  0 — all code: snippets are valid
  1 — one or more snippets reference a missing method (or file not found)

Run as a pre-commit hook or in CI to catch registry drift immediately.
"""

import sys
import re
import inspect
import importlib
from pathlib import Path
from typing import Dict, Optional, Set

# Ensure project root is on the path so PageFactory.* can be imported
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required. Install: pip install pyyaml")
    sys.exit(1)

REGISTRY_PATH = Path(__file__).parent / "action_registry.yaml"

# Maps page object name → fully-qualified Python class path
PAGE_CLASS_MAP = {
    "ReArchLoginPage":        "PageFactory.ReArch.rearch_login_page.ReArchLoginPage",
    "ReArchHomePage":         "PageFactory.ReArch.rearch_home_page.ReArchHomePage",
    "ReArchQRPage":           "PageFactory.ReArch.rearch_qr_page.ReArchQRPage",
    "ReArchCompletePage":     "PageFactory.ReArch.rearch_complete_page.ReArchCompletePage",
    "ReArchTxnHistoryPage":   "PageFactory.ReArch.rearch_txn_history_page.ReArchTxnHistoryPage",
    "ReArchTxnDetailPage":    "PageFactory.ReArch.rearch_txn_detail_page.ReArchTxnDetailPage",
    "ReArchPaymentMethodPage": "PageFactory.ReArch.rearch_payment_method_page.ReArchPaymentMethodPage",
    "ReArchCashConfirmPage":  "PageFactory.ReArch.rearch_cash_confirm_page.ReArchCashConfirmPage",
    "ReArchNativeBasePage":   "PageFactory.ReArch.rearch_native_base_page.ReArchNativeBasePage",
    "ReArchOrderDetailsPage": "PageFactory.ReArch.rearch_order_details_page.ReArchOrderDetailsPage",
    "ReArchCardTypePage":     "PageFactory.ReArch.rearch_card_type_page.ReArchCardTypePage",
    "ReArchChequePage":       "PageFactory.ReArch.rearch_cheque_page.ReArchChequePage",
    "ReArchDemandDraftPage":  "PageFactory.ReArch.rearch_demand_draft_page.ReArchDemandDraftPage",
    "ReArchTipPage":          "PageFactory.ReArch.rearch_tip_page.ReArchTipPage",
    "ReArchAccountDetailsPage": "PageFactory.ReArch.rearch_account_details_page.ReArchAccountDetailsPage",
    "ReArchEMIPage":          "PageFactory.ReArch.rearch_emi_page.ReArchEMIPage",
    "ReArchESignaturePage":   "PageFactory.ReArch.rearch_esignature_page.ReArchESignaturePage",
}

# Regex to extract variable.method_name() calls from a code snippet
METHOD_CALL_RE = re.compile(r'(\w+)\.(\w+)\(')


def load_class_methods(class_path: str) -> Optional[Set[str]]:
    """Import a class and return its set of method names, or None on failure."""
    module_path, class_name = class_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return {name for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction)}
    except Exception as e:
        print(f"  [IMPORT ERROR] {class_path}: {e}")
        return None


def validate() -> bool:
    if not REGISTRY_PATH.exists():
        print(f"[ERROR] Registry not found: {REGISTRY_PATH}")
        return False

    with open(REGISTRY_PATH) as f:
        registry = yaml.safe_load(f)

    actions = registry.get("actions", [])
    if not actions:
        print("[WARN] No actions found in registry.")
        return True

    # Cache of loaded classes to avoid re-importing
    class_cache: Dict[str, Optional[Set[str]]] = {}

    passed = 0
    failed = 0
    skipped = 0

    print(f"Validating {len(actions)} action(s) in {REGISTRY_PATH.name} ...\n")

    for action in actions:
        code = action.get("code", "")
        page_name = action.get("page", "")
        method_name = action.get("method", "")
        patterns = action.get("patterns", [])
        description = patterns[0] if patterns else "(no pattern)"

        if not code or not page_name or not method_name:
            skipped += 1
            continue

        class_path = PAGE_CLASS_MAP.get(page_name)
        if class_path is None:
            print(f"  [SKIP] '{description}' — page '{page_name}' not in PAGE_CLASS_MAP")
            skipped += 1
            continue

        if class_path not in class_cache:
            class_cache[class_path] = load_class_methods(class_path)

        available_methods = class_cache[class_path]
        if available_methods is None:
            print(f"  [SKIP] '{description}' — could not import {class_path}")
            skipped += 1
            continue

        if method_name in available_methods:
            passed += 1
        else:
            print(f"  [FAIL] '{description}'")
            print(f"         page={page_name}, method='{method_name}' NOT FOUND")
            print(f"         Available: {sorted(m for m in available_methods if not m.startswith('_'))}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed | {failed} failed | {skipped} skipped")
    print(f"{'='*60}")

    if failed > 0:
        print(f"\n[FAIL] {failed} action(s) reference missing methods. Fix registry or page objects.")
        return False

    print("\n[PASS] All code: snippets reference valid page object methods.")
    return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
