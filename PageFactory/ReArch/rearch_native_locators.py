"""
rearch_native_locators.py
-------------------------
Native-only UI locators for the ReArch application (com.razorpay.pos).

All locators use AppiumBy (NATIVE_APP context) -- no WebView context switching
required. These are extracted from uiautomator XML dumps of the actual device
UI hierarchy using Tools/rearch_xpath_extractor.py.

Locator strategy priority:
  1. AppiumBy.ID (resource-id) -- most stable
  2. AppiumBy.XPATH with @text -- reliable for text-bearing elements
  3. AppiumBy.XPATH with @index -- fallback for elements without text/id

To regenerate or extend these locators:
  python Tools/rearch_xpath_extractor.py --interactive
  python Tools/rearch_xpath_extractor.py --regenerate
"""

from appium.webdriver.common.appiumby import AppiumBy

REARCH_PACKAGE = "com.razorpay.pos"


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM / NATIVE DIALOGS
# ══════════════════════════════════════════════════════════════════════════════

class NativeLocators:
    btn_allow_permission     = (AppiumBy.ID, "com.android.packageinstaller:id/permission_allow_button")
    btn_deny_permission      = (AppiumBy.ID, "com.android.packageinstaller:id/permission_deny_button")
    btn_dialog_ok            = (AppiumBy.ID, "android:id/button1")
    btn_dialog_cancel        = (AppiumBy.ID, "android:id/button2")


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

class LoginLocators:
    img_razorpay_logo      = (AppiumBy.XPATH, "//android.widget.Image[@text='Razorpay']")
    txt_username           = (AppiumBy.ID,    "username")
    lbl_username           = (AppiumBy.XPATH, "//android.view.View[@text='Username']")
    txt_password           = (AppiumBy.ID,    "password")
    lbl_password           = (AppiumBy.XPATH, "//android.view.View[@text='Password']")
    btn_toggle_password    = (AppiumBy.XPATH, "//android.view.View[.//android.widget.EditText[@resource-id='password']]//android.widget.Button")
    btn_login              = (AppiumBy.XPATH, "//android.widget.Button[@text='Login']")
    btn_settings           = (AppiumBy.XPATH, "//android.widget.Button[@text='Settings']")
    btn_retry              = (AppiumBy.XPATH, "//android.widget.Button[@text='Try Again']")
    lbl_support_number     = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'1800 212 212 212')]")
    lbl_snackbar_error     = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'error') or contains(@text,'Error') or contains(@text,'Invalid') or contains(@text,'failed')]")


# ══════════════════════════════════════════════════════════════════════════════
# HOME / AMOUNT PAGE (numpad + payment method buttons)
# ══════════════════════════════════════════════════════════════════════════════

class HomeAmountLocators:
    lbl_rupee_symbol       = (AppiumBy.XPATH, "//android.widget.TextView[@text='\u20b9']")
    lbl_amount_display     = (AppiumBy.XPATH, "//android.widget.TextView[@text='0']")

    # Numpad digit buttons
    btn_numpad_0           = (AppiumBy.XPATH, "//android.widget.Button[@text='0']")
    btn_numpad_1           = (AppiumBy.XPATH, "//android.widget.Button[@text='1']")
    btn_numpad_2           = (AppiumBy.XPATH, "//android.widget.Button[@text='2']")
    btn_numpad_3           = (AppiumBy.XPATH, "//android.widget.Button[@text='3']")
    btn_numpad_4           = (AppiumBy.XPATH, "//android.widget.Button[@text='4']")
    btn_numpad_5           = (AppiumBy.XPATH, "//android.widget.Button[@text='5']")
    btn_numpad_6           = (AppiumBy.XPATH, "//android.widget.Button[@text='6']")
    btn_numpad_7           = (AppiumBy.XPATH, "//android.widget.Button[@text='7']")
    btn_numpad_8           = (AppiumBy.XPATH, "//android.widget.Button[@text='8']")
    btn_numpad_9           = (AppiumBy.XPATH, "//android.widget.Button[@text='9']")
    btn_numpad_dot         = (AppiumBy.XPATH, "//android.widget.Button[@text='\u2022']")
    btn_numpad_back        = (AppiumBy.XPATH, "//android.widget.Button[@index='18']")  # TODO: needs stable locator (no text/id on backspace key)

    # Payment method buttons (visible directly on home page)
    btn_card               = (AppiumBy.XPATH, "//android.widget.Button[@text='Card']")
    btn_upi                = (AppiumBy.XPATH, "//android.widget.Button[@text='UPI']")
    btn_add_tip            = (AppiumBy.XPATH, "//android.widget.Button[@text='Add Tip']")

    # Header navigation — TODO: needs stable locators (no text/id on icon-only buttons)
    btn_menu               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator
    btn_txn_history        = (AppiumBy.XPATH, "//android.widget.Button[@index='2']")  # TODO: needs stable locator


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT METHOD SELECTION (after entering amount and tapping a method)
# ══════════════════════════════════════════════════════════════════════════════

class PaymentMethodLocators:
    lbl_payment_amount     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Amount']")
    btn_upi                = (AppiumBy.XPATH, "//android.widget.Button[@text='UPI']")
    btn_card               = (AppiumBy.XPATH, "//android.widget.Button[@text='Card']")
    btn_payment_link       = (AppiumBy.XPATH, "//android.widget.Button[@text='Payment link']")
    btn_pre_auth           = (AppiumBy.XPATH, "//android.widget.Button[@text='Pre Auth']")
    btn_bharat_qr          = (AppiumBy.XPATH, "//android.widget.Button[@text='Bharat QR']")
    btn_cash               = (AppiumBy.XPATH, "//android.widget.Button[@text='Cash']")
    btn_cheque             = (AppiumBy.XPATH, "//android.widget.Button[@text='Cheque']")
    btn_demand_draft       = (AppiumBy.XPATH, "//android.widget.Button[@text='Demand Draft']")
    lbl_secured_by         = (AppiumBy.XPATH, "//android.widget.TextView[@text='Secured by']")


# ══════════════════════════════════════════════════════════════════════════════
# ORDER DETAILS OVERLAY
# ══════════════════════════════════════════════════════════════════════════════

class OrderDetailsLocators:
    lbl_order_details      = (AppiumBy.XPATH, "//android.widget.TextView[@text='Order Details']")
    lbl_order_id           = (AppiumBy.XPATH, "//android.view.View[@text='Order ID']")
    txt_order_number       = (AppiumBy.ID,    "order-number-input")
    lbl_device_serial      = (AppiumBy.XPATH, "//android.view.View[@text='Device Serial']")
    txt_additional_field    = (AppiumBy.ID,    "additional-field-input")
    btn_cancel             = (AppiumBy.XPATH, "//android.widget.Button[@text='Cancel']")
    btn_proceed            = (AppiumBy.XPATH, "//android.widget.Button[@text='Proceed']")
    btn_close_overlay      = (AppiumBy.XPATH, "//android.widget.Button[@text='Close overlay']")


# ══════════════════════════════════════════════════════════════════════════════
# QR / UPI PAYMENT SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class QRPaymentLocators:
    lbl_scan_and_pay       = (AppiumBy.XPATH, "//android.widget.TextView[@text='Scan & Pay']")
    lbl_payment_amount     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Amount']")
    lbl_amount_value       = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'\u20b9')]")
    btn_back               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator
    btn_confirm_cancel     = (AppiumBy.XPATH, "//android.widget.Button[@text='Yes, Cancel']")
    lbl_cancel_dialog_title = (AppiumBy.XPATH, "//android.widget.TextView[@text='Cancel the Payment?']")


# ══════════════════════════════════════════════════════════════════════════════
# CASH PAYMENT CONFIRMATION
# ══════════════════════════════════════════════════════════════════════════════

class CashConfirmLocators:
    lbl_payment_amount     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Amount']")
    lbl_tap_confirm        = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'Tap confirm to record')]")
    btn_confirm_payment    = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT SUCCESS SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class PaymentSuccessLocators:
    lbl_txn_page           = (AppiumBy.ID,    "txn-page")
    lbl_txn_page_gradient  = (AppiumBy.ID,    "txn-page-gradient")
    lbl_thank_you          = (AppiumBy.XPATH, "//android.widget.TextView[@text='Thank you!']")
    lbl_payment_successful = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Successful']")
    lbl_amount_received    = (AppiumBy.XPATH, "//android.widget.TextView[@text='Amount received']")
    lbl_amount_value       = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'\u20b9')]")
    btn_view_details       = (AppiumBy.XPATH, "//android.widget.Button[@text='View Details']")
    btn_print_receipt      = (AppiumBy.XPATH, "//android.widget.Button[@text='Print Receipt']")
    btn_send_ereceipt      = (AppiumBy.XPATH, "//android.widget.Button[@text='Send E-Receipt']")
    btn_accept_more_payments = (AppiumBy.XPATH, "//android.widget.Button[@text='Accept more payments']")


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT FAILED SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class PaymentFailedLocators:
    lbl_txn_page           = (AppiumBy.ID,    "txn-page")
    lbl_payment_failed     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Failed']")
    lbl_error_detail       = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'failed') or contains(@text,'error')]")
    btn_retry              = (AppiumBy.XPATH, "//android.widget.Button[@text='Retry']")
    btn_go_back            = (AppiumBy.XPATH, "//android.widget.Button[@text='Go Back']")
    btn_back_to_home       = (AppiumBy.XPATH, "//android.widget.Button[@text='Back to Home']")


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION HISTORY LIST
# ══════════════════════════════════════════════════════════════════════════════

class TxnHistoryLocators:
    lbl_payments           = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payments']")
    btn_my_dashboard       = (AppiumBy.XPATH, "//android.widget.Button[@text='My Dashboard']")
    btn_filter_date        = (AppiumBy.XPATH, "//android.widget.Button[@text='Date']")
    btn_filter_method      = (AppiumBy.XPATH, "//android.widget.Button[@text='Method']")
    btn_filter_status      = (AppiumBy.XPATH, "//android.widget.Button[@text='Status']")
    btn_back               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator
    btn_search             = (AppiumBy.XPATH, "//android.widget.Button[@index='2']")  # TODO: needs stable locator
    btn_more_options       = (AppiumBy.XPATH, "//android.widget.Button[@index='3']")  # TODO: needs stable locator

    # Transaction row buttons contain the full text: "transaction logo UPI 4:07 PM ₹389 Settled"
    # Use contains(@text, ...) to match partial content
    @staticmethod
    def txn_row_by_method_and_amount(method: str, amount: str):
        return (AppiumBy.XPATH,
                f"//android.widget.Button[contains(@text,'{method}') and contains(@text,'{amount}')]")

    @staticmethod
    def txn_row_by_status(status: str):
        return (AppiumBy.XPATH,
                f"//android.widget.Button[contains(@text,'{status}')]")


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION SEARCH
# ══════════════════════════════════════════════════════════════════════════════

class TxnSearchLocators:
    lbl_search             = (AppiumBy.XPATH, "//android.widget.TextView[@text='Search']")
    btn_payment_id         = (AppiumBy.XPATH, "//android.widget.Button[@text='Payment ID']")
    btn_rrn_number         = (AppiumBy.XPATH, "//android.widget.Button[@text='RRN Number']")
    btn_amount             = (AppiumBy.XPATH, "//android.widget.Button[@text='Amount']")
    btn_auth_code          = (AppiumBy.XPATH, "//android.widget.Button[@text='Auth Code']")
    txt_search_input       = (AppiumBy.XPATH, "//android.widget.EditText[@index='3']")  # TODO: needs stable locator
    btn_back               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION DETAIL PAGE
# ══════════════════════════════════════════════════════════════════════════════

class TxnDetailLocators:
    lbl_page               = (AppiumBy.ID,    "page")
    btn_back               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator

    # Key-value fields displayed as adjacent TextViews
    lbl_status_label       = (AppiumBy.XPATH, "//android.widget.TextView[@text='Status']")
    lbl_payment_id_label   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment ID']")
    lbl_rrn_label          = (AppiumBy.XPATH, "//android.widget.TextView[@text='RRN']")
    lbl_auth_code_label    = (AppiumBy.XPATH, "//android.widget.TextView[@text='Auth Code']")
    lbl_date_time_label    = (AppiumBy.XPATH, "//android.widget.TextView[@text='Date & Time']")
    lbl_payment_mode_label = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Mode']")
    lbl_customer_name_label = (AppiumBy.XPATH, "//android.widget.TextView[@text='Customer Name']")

    # Action buttons
    btn_refund             = (AppiumBy.XPATH, "//android.widget.Button[@text='Refund']")
    btn_print_chargeslip   = (AppiumBy.XPATH, "//android.widget.Button[@text='Print Chargeslip']")
    btn_send_receipt       = (AppiumBy.XPATH, "//android.widget.Button[@text='Send E-Receipt']")

    @staticmethod
    def field_value_after(label_text: str):
        """Get the value TextView that follows a label TextView."""
        return (AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{label_text}']/following-sibling::android.widget.TextView[1]")


# ══════════════════════════════════════════════════════════════════════════════
# MENU / DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════

class MenuLocators:
    btn_collect_payment    = (AppiumBy.XPATH, "//android.widget.Button[@text='Collect Payment']")
    btn_transactions       = (AppiumBy.XPATH, "//android.widget.Button[@text='Transactions']")
    btn_settings           = (AppiumBy.XPATH, "//android.widget.Button[@text='Settings']")
    btn_help               = (AppiumBy.XPATH, "//android.widget.Button[@text='Help']")
    btn_khaata             = (AppiumBy.XPATH, "//android.widget.Button[@text='Khaata']")
