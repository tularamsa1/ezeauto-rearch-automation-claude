#!/usr/bin/env python3
"""
rearch_xpath_extractor.py
=========================
Single-pass XPath extraction utility for the com.razorpay.pos (ReArch) app.

This tool connects to the Android device via ADB, dumps the current screen's
UI hierarchy as XML, and generates AppiumBy-compatible Python locator classes
in the exact format used by PageFactory/ReArch/rearch_native_locators.py.

Requirements:
  - adb on PATH  (run `adb devices` to verify device is connected)
  - Python 3.8+
  - PyYAML  (pip install pyyaml)

Usage — interactive (recommended for full single-pass extraction):
  python Tools/rearch_xpath_extractor.py --interactive

Usage — single screen dump:
  python Tools/rearch_xpath_extractor.py --screen LoginLocators
  python Tools/rearch_xpath_extractor.py --screen HomeAmountLocators

Usage — parse an existing XML file:
  python Tools/rearch_xpath_extractor.py --xml-file /path/to/dump.xml --screen QRPaymentLocators

Usage — re-generate from all saved XML dumps:
  python Tools/rearch_xpath_extractor.py --regenerate

Usage — validate extracted locators against a live device (requires Appium):
  python Tools/rearch_xpath_extractor.py --validate

Outputs:
  Tools/output/xml_dumps/              — raw XML per screen
  Tools/output/rearch_locators_generated.py  — ready-to-review locator file
  Tools/output/locator_registry.yaml   — machine-readable registry for Claude
"""

import subprocess
import xml.etree.ElementTree as ET
import re
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from textwrap import dedent
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# ── Config ──────────────────────────────────────────────────────────────────

PACKAGE = "com.razorpay.pos"
OUTPUT_DIR = Path(__file__).parent / "output"
XML_DUMP_DIR = OUTPUT_DIR / "xml_dumps"
GENERATED_LOCATORS_FILE = OUTPUT_DIR / "rearch_locators_generated.py"
LOCATOR_REGISTRY_FILE = OUTPUT_DIR / "locator_registry.yaml"

# Appium-class tag → locator name prefix
CLASS_PREFIXES = {
    "android.widget.EditText":    "txt",
    "android.widget.Button":      "btn",
    "android.widget.TextView":    "lbl",
    "android.widget.ImageView":   "img",
    "android.widget.Image":       "img",
    "android.widget.CheckBox":    "chk",
    "android.widget.RadioButton": "rdb",
    "android.widget.Switch":      "swt",
    "android.view.View":          "lbl",
    "android.widget.ScrollView":  "scr",
    "android.widget.ListView":    "lst",
    "android.widget.RecyclerView": "lst",
    "android.webkit.WebView":     "wv",
}

INTERACTIVE_SCREENS = [
    ("LoginLocators",          "Login screen (username/password fields + Login button visible)"),
    ("HomeAmountLocators",     "Home/Amount page (numpad + Collect Payment / UPI / Card visible)"),
    ("PaymentMethodLocators",  "Payment method selection overlay (after entering amount, UPI/Card/Cash/Cheque visible)"),
    ("OrderDetailsLocators",   "Order details overlay (Order ID + Device Serial fields visible)"),
    ("QRPaymentLocators",      "UPI QR code display screen (Scan & Pay visible)"),
    ("CashConfirmLocators",    "Cash payment confirmation screen (Confirm Payment button visible)"),
    ("PaymentSuccessLocators", "Payment result — success (Thank you / Payment Successful visible)"),
    ("PaymentFailedLocators",  "Payment result — failure (Payment Failed visible)"),
    ("TxnHistoryLocators",     "Transaction history list (list of past transactions visible)"),
    ("TxnSearchLocators",      "Transaction search screen (Payment ID / RRN / Amount search visible)"),
    ("TxnDetailLocators",      "Single transaction detail view (Status, Payment ID, RRN fields visible)"),
    ("MenuLocators",           "Menu / Dashboard page (Collect Payment, Transactions, Settings tiles)"),
]


# ── Screen registry (prevents duplicate class names) ────────────────────────

class ScreenRegistry:
    """Tracks which screens have been captured to prevent duplicates."""

    def __init__(self):
        self._captured: dict[str, dict] = {}

    def is_captured(self, screen_name: str) -> bool:
        return screen_name in self._captured

    def register(self, screen_name: str, xml_path: str, element_count: int):
        self._captured[screen_name] = {
            "xml_path": str(xml_path),
            "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "element_count": element_count,
        }

    def get_all(self) -> dict:
        return dict(self._captured)

    def suggest_alternative(self, screen_name: str) -> str:
        counter = 2
        candidate = f"{screen_name}_{counter}"
        while candidate in self._captured:
            counter += 1
            candidate = f"{screen_name}_{counter}"
        return candidate


_registry = ScreenRegistry()


# ── ADB helpers ─────────────────────────────────────────────────────────────

def get_app_version(device_id: str) -> str:
    """Return the installed versionName of PACKAGE from adb dumpsys."""
    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "shell", "dumpsys", "package", PACKAGE],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if "versionName=" in line:
                return line.strip().split("versionName=")[1].strip()
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return "unknown"


def get_connected_devices() -> list[str]:
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if line and "\tdevice" in line:
            devices.append(line.split("\t")[0])
    return devices


def dump_screen_xml(device_id: str, local_path: Path) -> bool:
    """Use adb + uiautomator to dump current screen XML."""
    remote = "/sdcard/ui_dump.xml"
    try:
        subprocess.run(
            ["adb", "-s", device_id, "shell", "uiautomator", "dump", remote],
            check=True, capture_output=True
        )
        subprocess.run(
            ["adb", "-s", device_id, "pull", remote, str(local_path)],
            check=True, capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] adb dump failed: {e.stderr.decode()}")
        return False


# ── XPath / locator generation ───────────────────────────────────────────────

def _clean_name(text: str) -> str:
    """Turn element text into a valid Python identifier fragment."""
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)
    return text[:40]


def _best_xpath(elem: ET.Element) -> "tuple[Optional[str], str]":
    """
    Return (by_strategy, locator_value) choosing the most stable selector:
      1. resource-id  → AppiumBy.ID
      2. @text        → AppiumBy.XPATH with exact text match
      3. No stable locator → (None, human-readable TODO description)

    @index is intentionally NOT used as a fallback because index-based
    locators break silently when the UI reorders elements.  Elements with no
    resource-id and no text are flagged as TODO for human annotation.
    """
    rid = elem.attrib.get("resource-id", "").strip()
    text = elem.attrib.get("text", "").strip()
    cls = elem.attrib.get("class", "")
    index = elem.attrib.get("index", "0")

    if rid and ":" not in rid:
        return "AppiumBy.ID", rid
    if rid.startswith(PACKAGE + ":id/"):
        local_id = rid.split(":id/")[1]
        return "AppiumBy.ID", local_id

    if text and cls:
        return "AppiumBy.XPATH", f"//{cls}[@text='{text}']"

    # No stable locator available — require human annotation
    return None, f"no resource-id or text; class={cls} index={index}"


def _locator_name(elem: ET.Element, seen: set[str]) -> str:
    """Auto-generate a unique locator name from element class + text/id."""
    cls = elem.attrib.get("class", "android.view.View")
    short_cls = cls.split(".")[-1]

    prefix = CLASS_PREFIXES.get(cls, "el")
    text = elem.attrib.get("text", "").strip()
    rid = elem.attrib.get("resource-id", "").strip()

    if rid and ":" not in rid:
        label = _clean_name(rid)
    elif rid.startswith(PACKAGE + ":id/"):
        label = _clean_name(rid.split(":id/")[1])
    elif text:
        label = _clean_name(text)
    else:
        label = _clean_name(short_cls)

    base = f"{prefix}_{label}" if label else f"{prefix}_{short_cls.lower()}"
    candidate = base
    counter = 2
    while candidate in seen:
        candidate = f"{base}_{counter}"
        counter += 1
    seen.add(candidate)
    return candidate


# ── Element filtering ────────────────────────────────────────────────────────

_SKIP_CLASSES = {
    "android.webkit.WebView",
    "android.widget.FrameLayout",
    "android.widget.LinearLayout",
    "android.widget.RelativeLayout",
    "android.widget.ScrollView",
    "android.view.ViewGroup",
}

def _is_interesting(elem: ET.Element) -> bool:
    """
    Keep elements that are actually useful as locators:
      - Interactable (clickable / focusable) leaf elements
      - OR text-bearing label elements
      - Skip invisible, layout containers, and WebView wrappers
    """
    cls = elem.attrib.get("class", "")
    text = elem.attrib.get("text", "").strip()
    rid = elem.attrib.get("resource-id", "").strip()
    clickable = elem.attrib.get("clickable", "false") == "true"
    focusable = elem.attrib.get("focusable", "false") == "true"
    displayed = elem.attrib.get("displayed", "true") == "true"
    enabled = elem.attrib.get("enabled", "true") == "true"

    if not displayed or not enabled:
        return False

    if cls in _SKIP_CLASSES:
        return False

    if clickable or focusable:
        return True

    if text and cls in (
        "android.widget.TextView",
        "android.widget.Image",
        "android.view.View",
    ):
        return True

    if rid and rid != "" and "android:id" not in rid:
        return True

    return False


def _collect_elements(root: ET.Element) -> list[ET.Element]:
    """Walk entire tree and collect all interesting elements."""
    results = []
    for elem in root.iter():
        if _is_interesting(elem):
            results.append(elem)
    return results


# ── Locator class renderer ───────────────────────────────────────────────────

def render_locator_class(screen_name: str, elements: list[ET.Element]) -> str:
    """Render a Python locator class string from a list of XML elements."""
    seen_names: set[str] = set()
    lines = [
        f"class {screen_name}:",
        f'    """Auto-generated from uiautomator dump — review and adjust as needed."""',
    ]

    for elem in elements:
        cls = elem.attrib.get("class", "")
        text = elem.attrib.get("text", "").strip()
        rid = elem.attrib.get("resource-id", "").strip()

        name = _locator_name(elem, seen_names)
        by, value = _best_xpath(elem)

        if by is None:
            # No stable locator — emit TODO comment, skip the assignment
            lines.append(f'    # TODO: {name} — needs stable locator ({value})')
            continue

        comment_parts = []
        if cls:
            comment_parts.append(cls.split(".")[-1])
        if text:
            comment_parts.append(f'"{text}"')
        elif rid:
            comment_parts.append(f"[{rid}]")
        comment = "  # " + " · ".join(comment_parts) if comment_parts else ""

        lines.append(f'    {name:<30} = ({by}, "{value}"){comment}')

    return "\n".join(lines)


def build_registry_entry(screen_name: str, elements: list[ET.Element], xml_path: str) -> dict:
    """Build a YAML-serializable dict for one screen's locators."""
    seen_names: set[str] = set()
    entry = {
        "source_xml": str(Path(xml_path).name),
        "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "element_count": len(elements),
        "elements": {},
    }
    for elem in elements:
        cls = elem.attrib.get("class", "")
        text = elem.attrib.get("text", "").strip()
        clickable = elem.attrib.get("clickable", "false") == "true"

        name = _locator_name(elem, seen_names)
        by, value = _best_xpath(elem)

        if by is None:
            # No stable locator — record as TODO in the registry
            entry["elements"][name] = {
                "by": "TODO",
                "value": value,
                "type": "unknown",
                "android_class": cls,
                "needs_annotation": True,
            }
            continue

        el_type = "label"
        if clickable or "Button" in cls:
            el_type = "action"
        elif "EditText" in cls:
            el_type = "input"
        elif "Image" in cls:
            el_type = "image"

        entry["elements"][name] = {
            "by": by,
            "value": value,
            "type": el_type,
            "android_class": cls,
        }
        if text:
            entry["elements"][name]["text"] = text

    return entry


# ── File output ──────────────────────────────────────────────────────────────

FILE_HEADER = dedent("""\
    \"\"\"
    rearch_locators_generated.py
    ----------------------------
    AUTO-GENERATED by Tools/rearch_xpath_extractor.py
    Generated : {timestamp}
    Source    : uiautomator XML dumps (NATIVE_APP context)
    Package   : com.razorpay.pos

    !! REVIEW BEFORE USE !!
    - Rename / remove duplicates
    - Confirm each locator by running a quick find_element test
    - Merge reviewed entries into PageFactory/ReArch/rearch_native_locators.py
    \"\"\"

    from appium.webdriver.common.appiumby import AppiumBy

    REARCH_PACKAGE = "com.razorpay.pos"

""")


def _init_output_file():
    """Create the generated locators file with header if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not GENERATED_LOCATORS_FILE.exists():
        with open(GENERATED_LOCATORS_FILE, "w") as f:
            f.write(FILE_HEADER.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")))


def write_to_output(class_code: str, screen_name: str):
    _init_output_file()

    existing = GENERATED_LOCATORS_FILE.read_text(encoding="utf-8")
    if f"class {screen_name}:" in existing:
        print(f"  [SKIP] {screen_name} already exists in output file — use a different class name.")
        return

    with open(GENERATED_LOCATORS_FILE, "a") as f:
        f.write("\n\n# " + "═" * 76 + "\n")
        f.write(f"# {screen_name}\n")
        f.write("# " + "═" * 76 + "\n\n")
        f.write(class_code)
        f.write("\n")

    print(f"  -> Appended {screen_name} to {GENERATED_LOCATORS_FILE}")


def write_registry(all_screens: dict, app_version: str = "unknown"):
    """Write the locator_registry.yaml file with app version metadata."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    registry_data = {
        "metadata": {
            "package": PACKAGE,
            "app_version": app_version,
            "captured_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "screens": all_screens,
    }
    if HAS_YAML:
        with open(LOCATOR_REGISTRY_FILE, "w") as f:
            yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"  -> Updated {LOCATOR_REGISTRY_FILE}")
    else:
        json_path = LOCATOR_REGISTRY_FILE.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        print(f"  -> Updated {json_path} (install pyyaml for .yaml output)")


def save_xml_dump(xml_text: str, screen_name: str) -> Path:
    XML_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    path = XML_DUMP_DIR / f"{screen_name}.xml"
    path.write_text(xml_text, encoding="utf-8")
    return path


# ── Core pipeline ────────────────────────────────────────────────────────────

_all_registry_entries: dict = {}


def process_xml_file(xml_path: Path, screen_name: str):
    """Parse XML file -> extract elements -> render locator class -> write output."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"  [ERROR] Failed to parse XML: {e}")
        return

    root = tree.getroot()
    elements = _collect_elements(root)

    if not elements:
        print(f"  [WARN] No interesting elements found in {xml_path.name}")
        return

    if _registry.is_captured(screen_name):
        alt = _registry.suggest_alternative(screen_name)
        print(f"  [WARN] '{screen_name}' already captured. Suggest using '{alt}' instead.")
        user_choice = input(f"  Use '{alt}'? [Y/n]: ").strip().lower()
        if user_choice != "n":
            screen_name = alt

    print(f"  Found {len(elements)} elements -> generating {screen_name}")
    class_code = render_locator_class(screen_name, elements)
    write_to_output(class_code, screen_name)

    registry_entry = build_registry_entry(screen_name, elements, str(xml_path))
    _all_registry_entries[screen_name] = registry_entry
    _registry.register(screen_name, str(xml_path), len(elements))

    print("\n" + "-" * 60)
    print(class_code[:1500] + (" ..." if len(class_code) > 1500 else ""))
    print("-" * 60 + "\n")


def dump_and_process(device_id: str, screen_name: str):
    """Dump current screen from device -> process XML -> generate locators."""
    XML_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = XML_DUMP_DIR / f"{screen_name}.xml"

    print(f"\n  Dumping screen XML from device {device_id} ...")
    success = dump_screen_xml(device_id, xml_path)
    if not success:
        print("  [SKIP] XML dump failed -- skipping this screen.")
        return

    print(f"  XML saved -> {xml_path}")
    process_xml_file(xml_path, screen_name)


# ── CLI: Interactive ─────────────────────────────────────────────────────────

def cmd_interactive():
    """Walk through all defined screens interactively."""
    devices = get_connected_devices()
    if not devices:
        print("[ERROR] No ADB devices found. Connect device and retry.")
        sys.exit(1)

    device_id = devices[0]
    if len(devices) > 1:
        print("Multiple devices found:")
        for i, d in enumerate(devices):
            print(f"  [{i}] {d}")
        choice = int(input("Select device index [0]: ") or "0")
        device_id = devices[choice]

    app_version = get_app_version(device_id)
    print(f"\nUsing device: {device_id}")
    print(f"App version : {PACKAGE} {app_version}")
    print("=" * 60)
    print("INTERACTIVE XPath Extraction -- single pass through all screens")
    print("=" * 60)

    if GENERATED_LOCATORS_FILE.exists():
        backup = GENERATED_LOCATORS_FILE.with_suffix(".py.bak")
        GENERATED_LOCATORS_FILE.rename(backup)
        print(f"  Backed up previous output -> {backup.name}")

    for suggested_name, instruction in INTERACTIVE_SCREENS:
        print(f"\n{'-'*60}")
        print(f"  SCREEN : {suggested_name}")
        print(f"  ACTION : Navigate the app to -> {instruction}")
        print(f"{'-'*60}")
        user = input("  Press [Enter] to capture, [s] to skip, [q] to quit: ").strip().lower()

        if user == "q":
            print("\nExtraction stopped by user.")
            break
        if user == "s":
            print(f"  Skipped {suggested_name}")
            continue

        class_name = input(
            f"  Class name [{suggested_name}]: "
        ).strip()
        if not class_name:
            class_name = suggested_name

        dump_and_process(device_id, class_name)

    if _all_registry_entries:
        write_registry(_all_registry_entries, app_version=app_version)

    print("\n" + "=" * 60)
    print(f"DONE -- Review output files:")
    print(f"  Locators : {GENERATED_LOCATORS_FILE}")
    print(f"  Registry : {LOCATOR_REGISTRY_FILE}")
    print(f"  Screens captured: {len(_all_registry_entries)}")
    print(f"  App version: {app_version}")
    print("=" * 60)


# ── CLI: Single screen ───────────────────────────────────────────────────────

def cmd_single_screen(screen_name: str, xml_file: Optional[str], class_name: Optional[str]):
    """Dump or parse a single screen."""
    final_class_name = class_name if class_name else screen_name
    if xml_file:
        xml_path = Path(xml_file)
        if not xml_path.exists():
            print(f"[ERROR] File not found: {xml_file}")
            sys.exit(1)
        process_xml_file(xml_path, final_class_name)
    else:
        devices = get_connected_devices()
        if not devices:
            print("[ERROR] No ADB devices found.")
            sys.exit(1)
        dump_and_process(devices[0], final_class_name)

    if _all_registry_entries:
        write_registry(_all_registry_entries)


# ── CLI: Regenerate from saved XMLs ──────────────────────────────────────────

def cmd_regenerate():
    """Re-process all saved XML dumps to regenerate output files."""
    if not XML_DUMP_DIR.exists():
        print("[ERROR] No XML dumps found. Run --interactive first.")
        sys.exit(1)

    xml_files = sorted(XML_DUMP_DIR.glob("*.xml"))
    if not xml_files:
        print("[ERROR] No XML files found in", XML_DUMP_DIR)
        sys.exit(1)

    if GENERATED_LOCATORS_FILE.exists():
        backup = GENERATED_LOCATORS_FILE.with_suffix(".py.bak")
        GENERATED_LOCATORS_FILE.rename(backup)
        print(f"  Backed up previous output -> {backup.name}")

    print(f"Regenerating from {len(xml_files)} XML dump(s)...")
    for xml_path in xml_files:
        screen_name = xml_path.stem
        print(f"\n  Processing: {xml_path.name} -> {screen_name}")
        process_xml_file(xml_path, screen_name)

    if _all_registry_entries:
        write_registry(_all_registry_entries)

    print(f"\nDONE -- Regenerated {len(_all_registry_entries)} screen(s).")


# ── CLI: Validate locators ───────────────────────────────────────────────────

def cmd_validate():
    """
    Validate extracted locators against the current device screen.
    Requires Appium to be running and the app to be open.
    """
    if not LOCATOR_REGISTRY_FILE.exists():
        json_fallback = LOCATOR_REGISTRY_FILE.with_suffix(".json")
        if json_fallback.exists():
            with open(json_fallback) as f:
                registry_data = json.load(f)
        else:
            print("[ERROR] No locator registry found. Run --interactive or --regenerate first.")
            sys.exit(1)
    else:
        if not HAS_YAML:
            print("[ERROR] PyYAML is required for --validate with .yaml registry. Install: pip install pyyaml")
            sys.exit(1)
        with open(LOCATOR_REGISTRY_FILE) as f:
            registry_data = yaml.safe_load(f)

    try:
        from appium import webdriver as appium_webdriver
        from appium.webdriver.common.appiumby import AppiumBy as _AB
    except ImportError:
        appium_webdriver = None
        _AB = None
        print("[ERROR] Appium-Python-Client is required. Install: pip install Appium-Python-Client")
        sys.exit(1)

    screens = registry_data.get("screens", {})
    if not screens:
        print("[ERROR] Registry has no screens.")
        sys.exit(1)

    print("=" * 60)
    print("LOCATOR VALIDATION")
    print("=" * 60)
    print(f"Screens to validate: {len(screens)}")
    print("\nThis requires the app to be open on the correct screen.")
    print("For each screen, navigate to the right page, then press Enter.\n")

    by_map = {"AppiumBy.ID": _AB.ID, "AppiumBy.XPATH": _AB.XPATH}

    devices = get_connected_devices()
    if not devices:
        print("[ERROR] No ADB devices found.")
        sys.exit(1)

    print(f"Using device: {devices[0]}")
    print("Connecting to Appium at http://127.0.0.1:4723 ...")

    caps = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:udid": devices[0],
        "appium:noReset": True,
        "appium:autoLaunch": False,
    }

    try:
        driver = appium_webdriver.Remote("http://127.0.0.1:4723", caps)
    except Exception as e:
        print(f"[ERROR] Could not connect to Appium: {e}")
        print("Make sure Appium server is running on port 4723.")
        sys.exit(1)

    total_pass = 0
    total_fail = 0
    total_skip = 0
    report_lines = []

    try:
        for screen_name, screen_data in screens.items():
            print(f"\n{'-'*60}")
            print(f"  SCREEN: {screen_name}")
            user = input("  Navigate to this screen, then press [Enter], [s] to skip, [q] to quit: ").strip().lower()
            if user == "q":
                break
            if user == "s":
                total_skip += len(screen_data.get("elements", {}))
                continue

            elements = screen_data.get("elements", {})
            screen_pass = 0
            screen_fail = 0

            for loc_name, loc_data in elements.items():
                by_str = loc_data["by"]
                value = loc_data["value"]
                by = by_map.get(by_str)
                if by is None:
                    print(f"    [SKIP] {loc_name}: unknown strategy '{by_str}'")
                    total_skip += 1
                    continue

                try:
                    driver.find_element(by, value)
                    status = "PASS"
                    screen_pass += 1
                    total_pass += 1
                except Exception:
                    status = "FAIL"
                    screen_fail += 1
                    total_fail += 1

                print(f"    [{status}] {loc_name:<30} ({by_str}, \"{value}\")")
                report_lines.append(f"{screen_name},{loc_name},{status},{by_str},{value}")

            print(f"  Summary: {screen_pass} passed, {screen_fail} failed out of {len(elements)}")
    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print(f"VALIDATION COMPLETE")
    print(f"  PASS: {total_pass}  |  FAIL: {total_fail}  |  SKIP: {total_skip}")
    print("=" * 60)

    report_path = OUTPUT_DIR / "validation_report.csv"
    with open(report_path, "w") as f:
        f.write("screen,locator,status,strategy,value\n")
        for line in report_lines:
            f.write(line + "\n")
    print(f"  Report saved: {report_path}")


# ── CLI: List screens ────────────────────────────────────────────────────────

def cmd_list_screens():
    print("\nDefined screens for interactive extraction:\n")
    for name, desc in INTERACTIVE_SCREENS:
        print(f"  {name:<30}  {desc}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ReArch XPath extractor -- generate AppiumBy locators from uiautomator XML dumps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Examples:
              # Full single-pass interactive run:
              python Tools/rearch_xpath_extractor.py --interactive

              # Dump live screen with custom class name:
              python Tools/rearch_xpath_extractor.py --screen login --class-name LoginLocators

              # Parse an existing XML file:
              python Tools/rearch_xpath_extractor.py --screen amount --class-name HomeAmountLocators --xml-file ~/dump.xml

              # Re-generate from all saved XML dumps:
              python Tools/rearch_xpath_extractor.py --regenerate

              # Validate locators against live device (requires Appium):
              python Tools/rearch_xpath_extractor.py --validate

              # List all defined screen names:
              python Tools/rearch_xpath_extractor.py --list
        """),
    )
    parser.add_argument("--interactive", action="store_true",
                        help="Interactive mode: walk through all screens one by one")
    parser.add_argument("--screen", metavar="SCREEN_KEY",
                        help="Screen key used to name the XML dump file")
    parser.add_argument("--class-name", metavar="CLASS_NAME",
                        help="Python class name for the output (overrides --screen)")
    parser.add_argument("--xml-file", metavar="PATH",
                        help="Parse this XML file instead of capturing from device")
    parser.add_argument("--regenerate", action="store_true",
                        help="Re-process all saved XML dumps to regenerate output files")
    parser.add_argument("--validate", action="store_true",
                        help="Validate extracted locators against a live device (requires Appium)")
    parser.add_argument("--list", action="store_true",
                        help="List all defined screen names and exit")
    parser.add_argument("--device", metavar="DEVICE_ID",
                        help="Specify ADB device ID (default: first connected)")

    args = parser.parse_args()

    if args.list:
        cmd_list_screens()
    elif args.interactive:
        cmd_interactive()
    elif args.regenerate:
        cmd_regenerate()
    elif args.validate:
        cmd_validate()
    elif args.screen:
        cmd_single_screen(args.screen, args.xml_file, args.class_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
