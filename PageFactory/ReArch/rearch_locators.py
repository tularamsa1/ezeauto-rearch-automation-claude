"""
rearch_locators.py
------------------
xpath_extractor skill output: UI locators extracted from pos/web/src Svelte sources
for the ReArch application (Android package: com.razorpay.pos, hybrid WebView app).

Source files analysed:
  pos/web/src/pages/login/LoginPage.svelte
  pos/web/src/pages/login/LoginForm.svelte
  pos/web/src/pages/pay/amount.svelte
  pos/web/src/pages/pay/complete.svelte
  pos/web/src/modules/payment/qr/index.svelte
  pos/web/src/modules/payment/qr/Upi.svelte
  pos/web/src/modules/payment/PaymentPage.svelte
  pos/web/src/pages/txn/list.svelte
  pos/web/src/pages/txn/detail.svelte
  pos/web/src/pages/txn/TransactionHistory.svelte
  pos/web/src/pages/menu/menu.svelte
  pos/web/src/base/rzp/numpad.svelte

Locator strategy:
  NATIVE_APP context  — AppiumBy.ID / AppiumBy.XPATH against Android native views.
                        Used before switching to WebView (e.g. system dialogs).
  WEBVIEW context     — By.CSS_SELECTOR / By.XPATH / By.ID against the HTML DOM.
                        All WebView locators are used AFTER the driver has switched
                        to the WEBVIEW context via ReArchBasePage.switch_to_webview().
"""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

REARCH_PACKAGE = "com.razorpay.pos"


# ══════════════════════════════════════════════════════════════════════════════
# NATIVE CONTEXT LOCATORS
# Used while Appium is in NATIVE_APP context (before WebView switch).
# ══════════════════════════════════════════════════════════════════════════════

class NativeLocators:
    # WebView container that hosts the entire Svelte frontend
    webview_container        = (AppiumBy.XPATH, "//android.webkit.WebView")

    # System permission dialogs
    btn_allow_permission     = (AppiumBy.ID, "com.android.packageinstaller:id/permission_allow_button")
    btn_deny_permission      = (AppiumBy.ID, "com.android.packageinstaller:id/permission_deny_button")

    # Generic Android system dialog buttons
    btn_dialog_ok            = (AppiumBy.ID, "android:id/button1")
    btn_dialog_cancel        = (AppiumBy.ID, "android:id/button2")


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# Source: pos/web/src/pages/login/LoginPage.svelte
#         pos/web/src/pages/login/LoginForm.svelte
# ══════════════════════════════════════════════════════════════════════════════

class LoginLocators:
    # Brand logo — android.widget.Image[@text='Razorpay']
    img_razorpay_logo      = (AppiumBy.XPATH, "//android.widget.Image[@text='Razorpay']")

    # Username field — android.widget.EditText[@resource-id='username']
    txt_username           = (AppiumBy.ID,    "username")
    lbl_username           = (AppiumBy.XPATH, "//android.view.View[@text='Username']")

    # Password field — android.widget.EditText[@resource-id='password']
    txt_password           = (AppiumBy.ID,    "password")
    lbl_password           = (AppiumBy.XPATH, "//android.view.View[@text='Password']")

    # Eye icon toggle — nameless Button sibling of the password EditText
    btn_toggle_password    = (AppiumBy.XPATH, "//android.view.View[.//android.widget.EditText[@resource-id='password']]//android.widget.Button")

    # Primary login CTA — android.widget.Button[@text='Login']
    btn_login              = (AppiumBy.XPATH, "//android.widget.Button[@text='Login']")

    # Settings shortcut on login screen — android.widget.Button[@text='Settings']
    btn_settings           = (AppiumBy.XPATH, "//android.widget.Button[@text='Settings']")

    # Network-error retry (not present in current XML; text may vary)
    btn_retry              = (AppiumBy.XPATH, "//android.widget.Button[@text='Try Again']")

    # Support contact footer — android.widget.TextView with support number
    lbl_support_number     = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'1800 212 212 212')]")

    # Error snackbar / toast — android.widget.TextView with error text (adjust @text when seen)
    lbl_snackbar_error     = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'error') or contains(@text,'Error') or contains(@text,'Invalid') or contains(@text,'failed')]")


# ══════════════════════════════════════════════════════════════════════════════
# AMOUNT / HOME PAGE
# Source: pos/web/src/pages/pay/amount.svelte
#         pos/web/src/base/rzp/numpad.svelte
# ══════════════════════════════════════════════════════════════════════════════

class AmountLocators:
    # Brand logo in header — amount.svelte line 141
    img_brand_logo         = (By.CSS_SELECTOR, "header img")

    # Numeric amount display — numpad.svelte (font-heading + text-primary)
    lbl_amount_display     = (By.XPATH, "//div[contains(@class,'font-heading') and contains(@class,'text-primary')]")

    # Numpad digit keys — numpad.svelte lines 167-179
    btn_numpad_1           = (By.XPATH, "//button[normalize-space(.)='1']")
    btn_numpad_2           = (By.XPATH, "//button[normalize-space(.)='2']")
    btn_numpad_3           = (By.XPATH, "//button[normalize-space(.)='3']")
    btn_numpad_4           = (By.XPATH, "//button[normalize-space(.)='4']")
    btn_numpad_5           = (By.XPATH, "//button[normalize-space(.)='5']")
    btn_numpad_6           = (By.XPATH, "//button[normalize-space(.)='6']")
    btn_numpad_7           = (By.XPATH, "//button[normalize-space(.)='7']")
    btn_numpad_8           = (By.XPATH, "//button[normalize-space(.)='8']")
    btn_numpad_9           = (By.XPATH, "//button[normalize-space(.)='9']")
    btn_numpad_0           = (By.XPATH, "//button[normalize-space(.)='0']")
    btn_numpad_dot         = (By.XPATH, "//button[normalize-space(.)='.']")
    # Back/delete key uses an icon SVG — last button in the numpad grid
    btn_numpad_back        = (By.XPATH, "(//div[contains(@class,'flex-wrap')]//button)[last()]")

    # Payment CTA buttons — amount.svelte lines 170-188
    btn_collect_payment    = (By.XPATH, "//button[.//span[normalize-space()='Collect Payment']]")
    btn_pay_by_card        = (By.XPATH, "//button[.//span[normalize-space()='Card']]")
    btn_pay_by_upi         = (By.XPATH, "//button[.//span[normalize-space()='UPI']]")
    btn_pay_by_bqr         = (By.XPATH, "//button[.//span[normalize-space()='Bharat QR'] or .//span[normalize-space()='BQR']]")

    # Others / union button — amount.svelte line 182
    btn_other_methods      = (By.XPATH, "//button[contains(@class,'rounded-full') and contains(@class,'bg-surface-low') and not(.//span)]")

    # Header navigation — amount.svelte lines 140-142
    btn_menu               = (By.XPATH, "(//header//button)[1]")   # leftmost  → opens Menu
    btn_txn_history        = (By.XPATH, "(//header//button)[2]")   # rightmost → opens TxnHistory

    # Add Tip CTA — amount.svelte line 155
    btn_add_tip            = (By.XPATH, "//button[.//span[normalize-space()='Add Tip']]")


# ══════════════════════════════════════════════════════════════════════════════
# QR / UPI PAYMENT SCREEN
# Source: pos/web/src/modules/payment/qr/index.svelte
#         pos/web/src/modules/payment/qr/Upi.svelte
# ══════════════════════════════════════════════════════════════════════════════

class QRPaymentLocators:
    # "Scan & Pay" label — Upi.svelte line 25
    lbl_scan_and_pay       = (By.XPATH, "//*[normalize-space(.)='Scan & Pay']")

    # Amount shown above the QR code (Amount component inside header)
    lbl_amount             = (By.XPATH, "//header//*[contains(@class,'text-primary')]")

    # QR code canvas / image rendered by the Qr base component
    img_qr_code            = (By.CSS_SELECTOR, "canvas, img[alt*='QR']")

    # Expiry countdown timer — index.svelte Timer badge
    lbl_timer              = (By.XPATH, "//*[contains(@class,'timer') or contains(@class,'Timer')]")

    # Brand / scheme logos at the bottom — Upi.svelte lines 37-42
    img_upi_logo           = (By.CSS_SELECTOR, "img[alt='UPI']")
    img_bhim_logo          = (By.CSS_SELECTOR, "img[alt='BHIM']")
    img_razorpay_logo      = (By.CSS_SELECTOR, "img[alt='Razorpay']")

    # Cancel payment confirmation dialog — PaymentPage.svelte cancel snippet
    btn_confirm_cancel     = (By.XPATH, "//button[normalize-space(.)='Yes, Cancel']")

    # "Cancel the Payment?" dialog heading
    lbl_cancel_dialog_title = (By.XPATH, "//h1[normalize-space(.)='Cancel the Payment?']")


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT COMPLETE / RESULT SCREEN
# Source: pos/web/src/pages/pay/complete.svelte
# ══════════════════════════════════════════════════════════════════════════════

class PaymentCompleteLocators:
    # Top-level page container — complete.svelte line 418  (id="txn-page")
    page_txn               = (By.CSS_SELECTOR, "#txn-page")

    # Success state elements
    lbl_thank_you          = (By.XPATH, "//h1[contains(normalize-space(.), 'Thank you')]")
    lbl_payment_successful = (By.XPATH, "//h2[normalize-space(.)='Payment Successful']")
    lbl_payment_settled    = (By.XPATH, "//h1[normalize-space(.)='Payment Settled!']")

    # Failure state elements
    lbl_payment_failed     = (By.XPATH, "//h1[normalize-space(.)='Payment Failed']")
    lbl_error_detail       = (By.XPATH, "//div[contains(@class,'text-on-surface-high') and not(descendant::h1)]")

    # Amount section labels — complete.svelte
    lbl_amount_label       = (By.XPATH, "//*[normalize-space(.)='Amount Received' or normalize-space(.)='Payment Amount' or normalize-space(.)='Settlement Amount']")

    # Action buttons — complete.svelte
    btn_view_details       = (By.XPATH, "//button[normalize-space(.)='View Details']")
    btn_print_receipt      = (By.XPATH, "//button[.//span[normalize-space()='Print Receipt']]")
    btn_send_e_receipt     = (By.XPATH, "//button[.//span[normalize-space()='Send E-Receipt']]")
    btn_retry              = (By.XPATH, "//button[.//span[normalize-space()='Retry']]")
    btn_e_signature        = (By.XPATH, "//button[normalize-space(.)='E-Signature']")

    # Progress / done buttons (auto-close timer) — complete.svelte line 566
    btn_accept_more_payments = (By.XPATH, "//button[normalize-space(.)='Accept more payments']")
    btn_back_to_home         = (By.XPATH, "//button[normalize-space(.)='Back to Home']")
    btn_go_back              = (By.XPATH, "//button[normalize-space(.)='Go Back']")

    # Print copy sheet options (inside dialog)
    btn_print_merchant_copy  = (By.XPATH, "//button[normalize-space(.)='Print Merchant Copy']")
    btn_print_customer_copy  = (By.XPATH, "//button[normalize-space(.)='Print Customer Copy']")

    # Transaction details dialog content — complete.svelte txnDetails snippet
    lbl_detail_date_time   = (By.XPATH, "//span[normalize-space(.)='Date & Time']/following-sibling::span[1]")
    lbl_detail_status      = (By.XPATH, "//span[normalize-space(.)='Status']/following-sibling::span[1]")
    lbl_detail_payment_id  = (By.XPATH, "//span[normalize-space(.)='Payment ID']/following-sibling::span[1]")
    lbl_detail_auth_code   = (By.XPATH, "//span[normalize-space(.)='Auth Code']/following-sibling::span[1]")
    lbl_detail_rrn         = (By.XPATH, "//span[normalize-space(.)='RRN']/following-sibling::span[1]")

    # Status icons
    img_success_icon       = (By.CSS_SELECTOR, "img[src*='txn-success']")
    img_failed_icon        = (By.CSS_SELECTOR, "img[src*='txn-fail']")


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION HISTORY PAGE
# Source: pos/web/src/pages/txn/list.svelte
#         pos/web/src/pages/txn/TransactionHistory.svelte
# ══════════════════════════════════════════════════════════════════════════════

class TxnHistoryLocators:
    # Transaction list items — list.svelte PlainButton rows
    lst_txn_items          = (By.XPATH, "//button[.//*[@alt='transaction logo'] or .//div[contains(@class,'flex-col') and .//span[contains(@class,'font-medium')]]]")

    # Sub-element selectors (used RELATIVE to a specific txn item element)
    lbl_txn_method         = (By.XPATH, ".//span[contains(@class,'font-medium')]")
    lbl_txn_time           = (By.XPATH, ".//span[contains(@class,'text-on-surface-high') and contains(@class,'text-sm')]")
    lbl_txn_amount         = (By.XPATH, ".//span[contains(@class,'font-semibold')]")
    lbl_txn_status         = (By.XPATH, ".//span[contains(@class,'mt-') and contains(@class,'text-on-surface-high')]")

    # Date group header rows — list.svelte line 127
    lbl_date_header        = (By.XPATH, "//header[contains(@class,'font-semibold') and contains(@class,'border-bottom-thin')]")

    # Search button in TransactionHistory header
    btn_search             = (By.XPATH, "//button[.//*[local-name()='svg'] and contains(@aria-label, 'search')]")

    # Empty state message
    lbl_empty_state        = (By.XPATH, "//*[contains(@class,'mt-10') and contains(@class,'m-auto')]")

    # Pagination loader
    lbl_loader             = (By.XPATH, "//*[contains(@class,'loader') or contains(@class,'Loader') or contains(@class,'shimmer')]")


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION DETAIL PAGE
# Source: pos/web/src/pages/txn/detail.svelte
# ══════════════════════════════════════════════════════════════════════════════

class TxnDetailLocators:
    # Page header title (from Page base component)
    lbl_page_title         = (By.XPATH, "//h1")

    # Key-value detail rows — detail.svelte
    lbl_status_value       = (By.XPATH, "//span[normalize-space(.)='Status']/following-sibling::span[1]")
    lbl_payment_id_value   = (By.XPATH, "//span[normalize-space(.)='Payment ID']/following-sibling::span[1]")
    lbl_auth_code_value    = (By.XPATH, "//span[normalize-space(.)='Auth Code']/following-sibling::span[1]")
    lbl_rrn_value          = (By.XPATH, "//span[normalize-space(.)='RRN']/following-sibling::span[1]")
    lbl_date_time_value    = (By.XPATH, "//span[normalize-space(.)='Date & Time']/following-sibling::span[1]")
    lbl_payment_mode_value = (By.XPATH, "//span[normalize-space(.)='Payment Mode']/following-sibling::span[1]")
    lbl_customer_name      = (By.XPATH, "//span[normalize-space(.)='Customer Name']/following-sibling::span[1]")

    # Action buttons — detail.svelte
    btn_refund             = (By.XPATH, "//button[normalize-space(.)='Refund']")
    btn_print_chargeslip   = (By.XPATH, "//button[.//span[normalize-space()='Print Chargeslip']]")
    btn_send_receipt       = (By.XPATH, "//button[.//span[normalize-space()='Send E-Receipt']]")


# ══════════════════════════════════════════════════════════════════════════════
# MENU / DASHBOARD PAGE
# Source: pos/web/src/pages/menu/menu.svelte
# ══════════════════════════════════════════════════════════════════════════════

class MenuLocators:
    # Primary action tiles — menu.svelte
    btn_collect_payment    = (By.XPATH, "//button[.//span[normalize-space()='Collect Payment'] or normalize-space(.)='Collect Payment']")
    btn_transactions       = (By.XPATH, "//button[.//span[normalize-space()='Transactions'] or normalize-space(.)='Transactions']")
    btn_settings           = (By.XPATH, "//button[.//span[normalize-space()='Settings'] or normalize-space(.)='Settings']")
    btn_help               = (By.XPATH, "//button[.//span[normalize-space()='Help'] or normalize-space(.)='Help']")
    btn_khaata             = (By.XPATH, "//button[.//span[normalize-space()='Khaata'] or normalize-space(.)='Khaata']")

    # Brand logo
    img_brand_logo         = (By.CSS_SELECTOR, "img.m-auto, header img")
