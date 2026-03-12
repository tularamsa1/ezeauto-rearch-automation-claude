#!/usr/bin/env python3
"""
rearch_xpath_extractor.py
=========================
Single-pass XPath extraction utility for the com.razorpay.pos (ReArch) app.

This tool connects to the Android device via ADB, dumps the current screen's
UI hierarchy as XML, and generates AppiumBy-compatible Python locator classes
in the exact format used by PageFactory/ReArch/rearch_locators.py.

Requirements:
  - adb on PATH  (run `adb devices` to verify device is connected)
  - Python 3.8+

Usage — interactive (recommended for full single-pass extraction):
  python Tools/rearch_xpath_extractor.py --interactive

Usage — single screen dump:
  python Tools/rearch_xpath_extractor.py --screen LoginLocators
  python Tools/rearch_xpath_extractor.py --screen AmountLocators

Usage — parse an existing XML file (paste xml from Appium Inspector / DDMS):
  python Tools/rearch_xpath_extractor.py --xml-file /path/to/dump.xml --screen QRPaymentLocators

Outputs:
  Tools/output/xml_dumps/   — raw XML per screen
  Tools/output/rearch_locators_generated.py  — ready-to-review locator file
"""

import subprocess
import xml.etree.ElementTree as ET
import re
import os
import argparse
import sys
from pathlib import Path
from datetime import datetime
from textwrap import dedent
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────

PACKAGE = "com.razorpay.pos"
OUTPUT_DIR = Path(__file__).parent / "output"
XML_DUMP_DIR = OUTPUT_DIR / "xml_dumps"
GENERATED_LOCATORS_FILE = OUTPUT_DIR / "rearch_locators_generated.py"

# Appium-class tag → locator name prefix
CLASS_PREFIXES = {
    "android.widget.EditText":   "txt",
    "android.widget.Button":     "btn",
    "android.widget.TextView":   "lbl",
    "android.widget.ImageView":  "img",
    "android.widget.Image":      "img",
    "android.widget.CheckBox":   "chk",
    "android.widget.RadioButton":"rdb",
    "android.widget.Switch":     "swt",
    "android.view.View":         "lbl",
    "android.widget.ScrollView": "scr",
    "android.widget.ListView":   "lst",
    "android.widget.RecyclerView":"lst",
    "android.webkit.WebView":    "wv",
}

# Interactive screen definitions — add more as the app grows
INTERACTIVE_SCREENS = [
    ("LoginLocators",          "Login screen  (enter username/password fields + Login button visible)"),
    ("AmountLocators",         "Amount/Home   (numpad + Collect Payment / UPI / Card buttons visible)"),
    ("QRPaymentLocators",      "QR/UPI screen (QR code + Scan & Pay visible)"),
    ("PaymentCompleteLocators","Payment result (Thank you / Payment Successful / Failed visible)"),
    ("TxnHistoryLocators",     "Transaction history list"),
    ("TxnDetailLocators",      "Transaction detail page"),
    ("MenuLocators",           "Menu / Dashboard page"),
]


# ── ADB helpers ─────────────────────────────────────────────────────────────

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
    # Strip non-alphanum, collapse spaces, lowercase
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)
    return text[:40]  # cap length


def _best_xpath(elem: ET.Element) -> tuple[str, str]:
    """
    Return (by_strategy, locator_value) choosing the most stable selector:
      1. resource-id  → AppiumBy.ID
      2. @text        → AppiumBy.XPATH with exact text match
      3. class + index fallback  → AppiumBy.XPATH
    """
    rid = elem.attrib.get("resource-id", "").strip()
    text = elem.attrib.get("text", "").strip()
    cls = elem.attrib.get("class", "")
    index = elem.attrib.get("index", "0")

    # Prefer resource-id (most stable)
    if rid and ":" not in rid:          # skip generic "android:id/..." ids
        return "AppiumBy.ID", rid
    if rid.startswith(PACKAGE + ":id/"):
        local_id = rid.split(":id/")[1]
        return "AppiumBy.ID", local_id

    # Button/TextView/EditText with visible text — single quotes inside XPath so
    # the outer Python string delimiter can stay double-quoted without escaping
    if text and cls:
        return "AppiumBy.XPATH", f"//{cls}[@text='{text}']"

    # Fallback: class with index path
    if cls:
        return "AppiumBy.XPATH", f"//{cls}[@index='{index}']"

    return "AppiumBy.XPATH", "//*"


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
    # Deduplicate
    candidate = base
    counter = 2
    while candidate in seen:
        candidate = f"{base}_{counter}"
        counter += 1
    seen.add(candidate)
    return candidate


# ── Element filtering ────────────────────────────────────────────────────────

_SKIP_CLASSES = {
    "android.webkit.WebView",       # WebView container — not a leaf interactable
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

    # Skip pure container/layout classes
    if cls in _SKIP_CLASSES:
        return False

    # Always include interactable elements
    if clickable or focusable:
        return True

    # Include elements with meaningful text (labels, titles)
    if text and cls in (
        "android.widget.TextView",
        "android.widget.Image",
        "android.view.View",
    ):
        return True

    # Include elements with a scoped resource-id
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

        # Build a short inline comment for context
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
    - Merge reviewed entries into PageFactory/ReArch/rearch_locators.py
    \"\"\"

    from appium.webdriver.common.appiumby import AppiumBy

    REARCH_PACKAGE = "com.razorpay.pos"

""")


def write_to_output(class_code: str, screen_name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not GENERATED_LOCATORS_FILE.exists():
        with open(GENERATED_LOCATORS_FILE, "w") as f:
            f.write(FILE_HEADER.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")))

    with open(GENERATED_LOCATORS_FILE, "a") as f:
        f.write("\n\n# " + "═" * 76 + "\n")
        f.write(f"# {screen_name}\n")
        f.write("# " + "═" * 76 + "\n\n")
        f.write(class_code)
        f.write("\n")

    print(f"  → Appended {screen_name} to {GENERATED_LOCATORS_FILE}")


def save_xml_dump(xml_text: str, screen_name: str) -> Path:
    XML_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    path = XML_DUMP_DIR / f"{screen_name}.xml"
    path.write_text(xml_text, encoding="utf-8")
    return path


# ── Core pipeline ────────────────────────────────────────────────────────────

def process_xml_file(xml_path: Path, screen_name: str):
    """Parse XML file → extract elements → render locator class → write output."""
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

    print(f"  Found {len(elements)} elements → generating {screen_name}")
    class_code = render_locator_class(screen_name, elements)
    write_to_output(class_code, screen_name)

    # Print preview
    print("\n" + "─" * 60)
    print(class_code[:1500] + (" ..." if len(class_code) > 1500 else ""))
    print("─" * 60 + "\n")


def dump_and_process(device_id: str, screen_name: str):
    """Dump current screen from device → process XML → generate locators."""
    XML_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = XML_DUMP_DIR / f"{screen_name}.xml"

    print(f"\n  Dumping screen XML from device {device_id} ...")
    success = dump_screen_xml(device_id, xml_path)
    if not success:
        print("  [SKIP] XML dump failed — skipping this screen.")
        return

    print(f"  XML saved → {xml_path}")
    process_xml_file(xml_path, screen_name)


# ── CLI entry points ─────────────────────────────────────────────────────────

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

    print(f"\nUsing device: {device_id}")
    print("=" * 60)
    print("INTERACTIVE XPath Extraction — single pass through all screens")
    print("=" * 60)

    # Clear previous output for a fresh run
    if GENERATED_LOCATORS_FILE.exists():
        backup = GENERATED_LOCATORS_FILE.with_suffix(".py.bak")
        GENERATED_LOCATORS_FILE.rename(backup)
        print(f"  Backed up previous output → {backup.name}")

    for suggested_name, instruction in INTERACTIVE_SCREENS:
        print(f"\n{'─'*60}")
        print(f"  SCREEN : {suggested_name}")
        print(f"  ACTION : Navigate the app to → {instruction}")
        print(f"{'─'*60}")
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

    print("\n" + "=" * 60)
    print(f"DONE — Review output file:")
    print(f"  {GENERATED_LOCATORS_FILE}")
    print("=" * 60)


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


def cmd_list_screens():
    print("\nDefined screens for interactive extraction:\n")
    for name, desc in INTERACTIVE_SCREENS:
        print(f"  {name:<30}  {desc}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ReArch XPath extractor — generate AppiumBy locators from uiautomator XML dumps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Examples:
              # Full single-pass interactive run (prompted for class name at each screen):
              python Tools/rearch_xpath_extractor.py --interactive

              # Dump live screen, use custom class name:
              python Tools/rearch_xpath_extractor.py --screen login --class-name ReArchLoginLocators

              # Parse an existing XML file with your own class name:
              python Tools/rearch_xpath_extractor.py --screen amount --class-name HomePageLocators --xml-file ~/dump.xml

              # List all defined screen names:
              python Tools/rearch_xpath_extractor.py --list
        """),
    )
    parser.add_argument("--interactive", action="store_true",
                        help="Interactive mode: walk through all screens one by one")
    parser.add_argument("--screen", metavar="SCREEN_KEY",
                        help="Screen key used to name the XML dump file (e.g. login, amount)")
    parser.add_argument("--class-name", metavar="CLASS_NAME",
                        help="Python class name to use in the output (overrides --screen). "
                             "E.g. ReArchLoginLocators")
    parser.add_argument("--xml-file", metavar="PATH",
                        help="Parse this XML file instead of capturing from device")
    parser.add_argument("--list", action="store_true",
                        help="List all defined screen names and exit")
    parser.add_argument("--device", metavar="DEVICE_ID",
                        help="Specify ADB device ID (default: first connected)")

    args = parser.parse_args()

    if args.list:
        cmd_list_screens()
    elif args.interactive:
        cmd_interactive()
    elif args.screen:
        cmd_single_screen(args.screen, args.xml_file, args.class_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
