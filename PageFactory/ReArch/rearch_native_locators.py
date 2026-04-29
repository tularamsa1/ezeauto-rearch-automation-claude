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
    txt_username           = (AppiumBy.XPATH,    "//android.widget.EditText[@resource-id='username']")
    lbl_username           = (AppiumBy.XPATH, "//android.view.View[@text='Username']")
    txt_password           = (AppiumBy.XPATH,    "//android.widget.EditText[@resource-id='password']")
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
    btn_more_payment_options = (AppiumBy.XPATH, "//android.widget.Button[@text='UPI']/following-sibling::android.widget.Button[1]")
    btn_add_tip            = (AppiumBy.XPATH, "//android.widget.Button[@text='Add Tip']")

    # Promo overlay (appears on amount screen when paymentPromotionEnabled=true)
    img_promo              = (AppiumBy.XPATH, "//android.widget.Image[@text='e91cc2003e6491b7f659']")

    # Branding logo (appears when brandingInfo is set)
    img_branding_logo      = (AppiumBy.XPATH, "//android.widget.Image[@text='logo']")  # TODO: verify on first run

    # Header navigation — TODO: needs stable locators (no text/id on icon-only buttons)
    btn_menu               = (AppiumBy.XPATH, "//android.widget.Button[@index='0']")  # TODO: needs stable locator
    btn_txn_history        = (AppiumBy.XPATH, "//android.widget.Button[@index='2']")  # TODO: needs stable locator


# ══════════════════════════════════════════════════════════════════════════════
# ACCOUNT DETAILS / SETTINGS SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class AccountDetailsLocators:
    lbl_account            = (AppiumBy.XPATH, "//android.widget.TextView[@text='Account']")
    lbl_mid                = (AppiumBy.XPATH, "//android.widget.TextView[@text='MID']")
    lbl_tid                = (AppiumBy.XPATH, "//android.widget.TextView[@text='TID']")
    lbl_app_version        = (AppiumBy.XPATH, "//android.widget.TextView[@text='App Version']")
    lbl_web_app_version    = (AppiumBy.XPATH, "//android.widget.TextView[@text='Web App Version']")
    lbl_devices            = (AppiumBy.XPATH, "//android.widget.TextView[@text='Devices']")

    btn_relaunch_app       = (AppiumBy.XPATH, "//android.widget.Button[@text='Relaunch App Resolve issues by relaunching app']")
    btn_delete_cache_relaunch = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'Delete Cache')]")
    btn_yes_delete_relaunch   = (AppiumBy.XPATH, "//android.widget.Button[@text='Yes, Delete & Relaunch']")

    @staticmethod
    def lbl_text(text: str):
        """Locate any TextView by its exact text (e.g. username, org_code value)."""
        return (AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']")

    @staticmethod
    def btn_text(text: str):
        """Locate any Button by its exact text (e.g. org_code button)."""
        return (AppiumBy.XPATH, f"//android.widget.Button[contains(@text,'{text}')]")


# ══════════════════════════════════════════════════════════════════════════════
# TIP DETAILS SCREEN (after tapping Add Tip)
# ══════════════════════════════════════════════════════════════════════════════

class TipDetailsLocators:
    lbl_want_to_leave_a_tip = (AppiumBy.XPATH, "//android.view.View[contains(@text,'Want to leave a tip')]")
    btn_31_6                = (AppiumBy.XPATH, "//android.widget.Button[@text='\u20b931 6%']")
    btn_57_11               = (AppiumBy.XPATH, "//android.widget.Button[@text='\u20b957 11%']")
    txt_custom_amount       = (AppiumBy.XPATH, "//android.widget.EditText[contains(@text,'Custom Amount')]")
    lbl_payment_details     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Details']")
    lbl_tip_amount          = (AppiumBy.XPATH, "//android.widget.TextView[@text='Tip Amount']")
    lbl_to_pay              = (AppiumBy.XPATH, "//android.widget.TextView[@text='To Pay']")
    btn_done                = (AppiumBy.XPATH, "//android.widget.Button[@text='Done']")


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
    btn_emi                = (AppiumBy.XPATH, "//android.widget.Button[@text='EMI']")
    btn_my_discount_emi    = (AppiumBy.XPATH, "//android.widget.Button[@text='My Discount EMI']")
    lbl_secured_by         = (AppiumBy.XPATH, "//android.widget.TextView[@text='Secured by']")


# ══════════════════════════════════════════════════════════════════════════════
# ORDER DETAILS OVERLAY
# ══════════════════════════════════════════════════════════════════════════════

class OrderDetailsLocators:
    lbl_order_details      = (AppiumBy.XPATH, "//android.widget.TextView[@text='Order Details']")
    lbl_order_id           = (AppiumBy.XPATH, "//android.view.View[@text='Order ID']")
    txt_order_number       = (AppiumBy.ID,    "order-number-input")
    lbl_device_serial      = (AppiumBy.XPATH, "//android.view.View[@text='Device Serial']")
    txt_additional_field    = (AppiumBy.XPATH,   "//android.widget.EditText[@index='2']")
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
    btn_back               = (AppiumBy.XPATH, '//android.view.View[@resource-id="page"]/android.view.View[1]/android.view.View/android.widget.Button')
    btn_confirm_cancel     = (AppiumBy.XPATH, "//android.widget.Button[@text='Yes, Cancel']")
    lbl_cancel_dialog_title = (AppiumBy.XPATH, "//android.widget.TextView[@text='Cancel the Payment?']")
    btn_card               = (AppiumBy.XPATH, "//android.widget.Button[@text='Card']")
    btn_link               = (AppiumBy.XPATH, "//android.widget.Button[@text='Link']")
    btn_others             = (AppiumBy.XPATH, "//android.widget.Button[@text='Others']")


# ══════════════════════════════════════════════════════════════════════════════
# CASH PAYMENT CONFIRMATION
# ══════════════════════════════════════════════════════════════════════════════

class CashConfirmLocators:
    lbl_payment_amount     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Amount']")
    lbl_tap_confirm        = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'Tap confirm to record')]")
    btn_confirm_payment    = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMER AUTH / PAN ENTRY SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class CustomerAuthLocators:
    txt_pan_number         = (AppiumBy.XPATH, "//android.widget.EditText[@text='Ex: ABCDE1234A']")
    btn_confirm_payment    = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")


# ══════════════════════════════════════════════════════════════════════════════
# CHEQUE PAYMENT FORM
# ══════════════════════════════════════════════════════════════════════════════

class ChequePaymentLocators:
    txt_enter_cheque_number = (AppiumBy.XPATH, "//android.widget.EditText[@text='Enter Cheque Number']")
    btn_select_bank         = (AppiumBy.XPATH, "//android.widget.Button[@text='Select Bank']")
    btn_ddmmyyyy            = (AppiumBy.XPATH, "//android.widget.Button[@text='dd/mm/yyyy']")
    txt_enter_ifsc_code     = (AppiumBy.XPATH, "//android.widget.EditText[@text='Enter IFSC Code']")  # TODO: verify placeholder text on first run
    btn_confirm_payment     = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")
    btn_apply               = (AppiumBy.XPATH, "//android.widget.Button[@text='Apply']")  # TODO: verify on first run — shared by bank dropdown and date picker

    # Error messages (displayed when submitting empty/invalid cheque form)
    lbl_error_cheque_number = (AppiumBy.XPATH, "//android.widget.TextView[@text='Cheque number should be 6 digits']")
    lbl_error_select_bank   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please select a bank']")
    lbl_error_cheque_date   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please select Cheque Date']")
    lbl_error_invalid_ifsc  = (AppiumBy.XPATH, "//android.widget.TextView[@text='Invalid Bank IFSC Code']")

    @staticmethod
    def bank_btn(bank_name: str):
        """Locate a bank button by its display name (e.g. 'Abn Amro Bank')."""
        return (AppiumBy.XPATH, f"//android.widget.Button[@text='{bank_name}']")


# ══════════════════════════════════════════════════════════════════════════════
# DEMAND DRAFT PAYMENT FORM
# ══════════════════════════════════════════════════════════════════════════════

class DemandDraftLocators:
    txt_enter_dd_number     = (AppiumBy.XPATH, "//android.widget.EditText[@text='Enter DD Number']")
    btn_select_bank         = (AppiumBy.XPATH, "//android.widget.Button[@text='Select Bank']")
    txt_enter_branch_name   = (AppiumBy.XPATH, "//android.widget.EditText[@text='Enter Branch Name']")  # TODO: verify placeholder text on first run
    btn_ddmmyyyy            = (AppiumBy.XPATH, "//android.widget.Button[@text='dd/mm/yyyy']")
    btn_confirm_payment     = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")
    btn_apply               = (AppiumBy.XPATH, "//android.widget.Button[@text='Apply']")  # TODO: verify on first run

    # Error messages (displayed when submitting empty/invalid DD form)
    lbl_error_dd_number     = (AppiumBy.XPATH, "//android.widget.TextView[@text='DD number should be 6 digits']")
    lbl_error_select_bank   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please select a bank']")
    lbl_error_branch_name   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please provide Branch Name']")
    lbl_error_dd_date       = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please enter DD Date']")

    @staticmethod
    def bank_btn(bank_name: str):
        """Locate a bank button by its display name (e.g. 'Pallavan Gramma Bank')."""
        return (AppiumBy.XPATH, f"//android.widget.Button[@text='{bank_name}']")


# ══════════════════════════════════════════════════════════════════════════════
# EMI PLAN SELECTION / BREAKUP SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class EMILocators:
    lbl_choose_emi_plans   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Choose EMI Plans']")
    btn_bank               = (AppiumBy.XPATH, "//android.widget.Button[@text='Bank']")
    btn_credit_card        = (AppiumBy.XPATH, "//android.widget.Button[@text='Credit Card']")
    btn_debit_card         = (AppiumBy.XPATH, "//android.widget.Button[@text='Debit Card']")
    btn_hdfc_bank_credit   = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'HDFC Bank Credit Card')]")
    btn_hdfc_bank_debit    = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'HDFC Bank Debit Card')]")
    btn_sbi_bank_credit    = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'SBI Bank Credit Card')]")
    btn_bob_bank_credit    = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'BOB Bank Credit Card')]")
    btn_icici_bank_credit  = (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'ICICI Bank Credit Card')]")
    btn_view_breakup       = (AppiumBy.XPATH, "//android.widget.Button[@text='View Breakup']")
    btn_proceed            = (AppiumBy.XPATH, "//android.widget.Button[@text='Proceed']")
    lbl_emi_breakup_sheet  = (AppiumBy.ID, "emi-breakup-bottomsheet")

    # Breakup detail labels (Credit Card uses "Order Total", Debit Card uses "Item Price")
    lbl_summary            = (AppiumBy.XPATH, "//android.widget.TextView[@text='Summary']")
    lbl_order_total        = (AppiumBy.XPATH, "//android.widget.TextView[@text='Order Total']")
    lbl_item_price         = (AppiumBy.XPATH, "//android.widget.TextView[@text='Item Price']")
    lbl_interest_charged   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Interest charged by Bank']")
    lbl_total_amount       = (AppiumBy.XPATH, "//android.widget.TextView[@text='Total Amount']")

    # Breakup detail values (following-sibling of the label)
    val_order_total        = (AppiumBy.XPATH, "//android.widget.TextView[@text='Order Total']/following-sibling::android.widget.TextView[1]")
    val_item_price         = (AppiumBy.XPATH, "//android.widget.TextView[@text='Item Price']/following-sibling::android.widget.TextView[1]")
    val_mydiscount         = (AppiumBy.XPATH, "//android.widget.TextView[@text='MyDiscount']/following-sibling::android.widget.TextView[1]")
    val_instant_discount   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Instant Discount']/following-sibling::android.widget.TextView[1]")
    val_interest_charged   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Interest charged by Bank']/following-sibling::android.widget.TextView[1]")
    val_additional_cashback = (AppiumBy.XPATH, "//android.widget.TextView[@text='Additional Cashback']/following-sibling::android.widget.TextView[1]")
    val_net_effective_price = (AppiumBy.XPATH, "//android.widget.TextView[@text='Net Effective Price']/following-sibling::android.widget.TextView[1]")
    val_total_amount       = (AppiumBy.XPATH, "//android.widget.TextView[@text='Total Amount']/following-sibling::android.widget.TextView[1]")

    # 3-month EMI plan radio buttons (amount=5959)
    rdb_3m_plan            = (AppiumBy.XPATH, "//android.widget.RadioButton[contains(@text,'3m') and contains(@text,'6,068.58')]")
    rdb_3m_no_cost_plan    = (AppiumBy.XPATH, "//android.widget.RadioButton[contains(@text,'3m') and contains(@text,'No Cost EMI')]")

    # 3-month EMI plan radio button (amount=6000, BOB)
    rdb_bob_3m_plan        = (AppiumBy.XPATH, "//android.widget.RadioButton[@text='\u20b92,040.13 \u00d7 3m \u20b96,120.39 Interest of \u20b9120.39 @ 12% p.a.']")

    # 3-month EMI plan radio button (amount=8000, BOB)
    rdb_bob_3m_plan_8000   = (AppiumBy.XPATH, "//android.widget.RadioButton[contains(@text,'2,550.17') and contains(@text,'3m')]")

    # Pay in Full radio button (amount=8000, BOB, ₹500 discount → ₹7,500)
    rdb_pay_in_full_7500   = (AppiumBy.XPATH, "//android.widget.RadioButton[@text='Pay in Full \u20b97,500 \u20b9500 Discount']")

    # Generic first 3-month EMI plan radio button (matches first visible × 3m plan)
    rdb_3m_plan_first      = (AppiumBy.XPATH, "(//*[@class='android.widget.RadioButton'])[1]")

    @staticmethod
    def lbl_text(text: str):
        """Locate any TextView by exact text (for verifying amounts like '₹5,959')."""
        return (AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']")

    @staticmethod
    def bank_btn(bank_name: str):
        """Locate a bank EMI button by bank name."""
        return (AppiumBy.XPATH, f"//android.widget.Button[contains(@text,'{bank_name}')]")


# ══════════════════════════════════════════════════════════════════════════════
# CARD TYPE SELECTION SCREEN (DUMMY / test simulator)
# ══════════════════════════════════════════════════════════════════════════════

class CardTypeSelectionLocators:
    lbl_select_test_card   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Select Test Card']")
    lbl_payment_amount     = (AppiumBy.XPATH, "//android.widget.TextView[@text='Payment Amount']")
    btn_back               = (AppiumBy.XPATH, '//android.view.View[@resource-id="page"]/android.view.View[1]/android.view.View/android.widget.Button')

    @staticmethod
    def card_type_btn(card_name: str):
        """Locate a card type button by its display name prefix (e.g. 'Visa Debit (EMV)')."""
        return (AppiumBy.XPATH, f"//android.widget.Button[starts-with(@text,'{card_name}')]")


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
    btn_search             = (AppiumBy.XPATH, "//android.widget.Button[@index='3']")
    btn_more_options       = (AppiumBy.XPATH, "//android.widget.Button[@index='3']")  # TODO: needs stable locator
    btn_apply_filter       = (AppiumBy.XPATH, "//android.widget.Button[@text='Apply']")
    btn_today              = (AppiumBy.XPATH, "(//*[@class='android.widget.Button'])[16]")  # TODO: index-based — verify on first run
    btn_clear_all          = (AppiumBy.XPATH, "//android.widget.Button[@text='Clear all']")

    @staticmethod
    def filter_option_btn(text: str):
        """Locate a filter option button by its text (e.g., 'Cash', 'Settled')."""
        return (AppiumBy.XPATH, f"//android.widget.Button[@text='{text}']")

    @staticmethod
    def filter_chip_text(text: str):
        """Locate any element with the given text (for verifying active filter chips)."""
        return (AppiumBy.XPATH, f"//*[@text='{text}']")

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
    txn_row = (AppiumBy.XPATH,
               "(//*[@class='android.widget.Button'][2])[2]")  # TODO: index-based locator — needs stable resource-id or @text


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
    btn_void_amount        = (AppiumBy.XPATH, "//android.widget.Button[@text='Void Amount']")  # TODO: verify text on first run
    btn_release_pre_auth   = (AppiumBy.XPATH, "//android.widget.Button[@text='Release Pre-Auth']")  # TODO: verify text on first run
    btn_confirm_pre_auth   = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Pre-Auth']")  # TODO: verify text on first run
    btn_print_chargeslip   = (AppiumBy.XPATH, "//android.widget.Button[@text='Print Chargeslip']")
    btn_send_receipt       = (AppiumBy.XPATH, "//android.widget.Button[@text='Send E-Receipt']")

    @staticmethod
    def field_value_after(label_text: str, sibling_index: int = 1):
        """Get the value TextView that follows a label TextView."""
        return (AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{label_text}']/following-sibling::android.widget.TextView[{sibling_index}]")

    @staticmethod
    def field_value_by_amount(amount: str):
        """Get the status value that is an immediate sibling of the given amount."""
        return (AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{amount}']/following-sibling::android.widget.TextView[1]")

    @staticmethod
    def lbl_amount(amount: str):
        """Locate the amount TextView on the detail page by its displayed text."""
        return (AppiumBy.XPATH, f"//android.widget.TextView[@text='{amount}']")


# ══════════════════════════════════════════════════════════════════════════════
# RELEASE PRE-AUTH FLOW
# ══════════════════════════════════════════════════════════════════════════════

class ReleasePreAuthLocators:
    """Locators for the Release Pre-Auth confirmation flow."""
    btn_yes_release      = (AppiumBy.XPATH, "//android.widget.Button[@text='Yes, Release']")  # TODO: verify text on first run
    btn_done             = (AppiumBy.XPATH, "//android.widget.Button[@text='Done']")  # TODO: verify on first run


# ══════════════════════════════════════════════════════════════════════════════
# CONFIRM PRE-AUTH FLOW
# ══════════════════════════════════════════════════════════════════════════════

class ConfirmPreAuthLocators:
    """Locators for the Confirm Pre-Auth confirmation flow."""
    btn_confirm_pre_auth = (AppiumBy.XPATH, "//android.widget.Button[@index='22']")  # TODO: verify text on first run
    btn_done             = (AppiumBy.XPATH, "//android.widget.Button[@text='Done']")  # TODO: verify on first run


# ══════════════════════════════════════════════════════════════════════════════
# E-SIGNATURE FLOW
# ══════════════════════════════════════════════════════════════════════════════

class ESignatureLocators:
    """Locators for the eSignature capture screen (appears when eSignatureForNonCardEnabled=true)."""
    lbl_please_sign_here = (AppiumBy.XPATH, "//android.widget.TextView[@text='Please sign here']")
    chk_agree_signature  = (AppiumBy.XPATH, "//android.view.View[@text='I agree to securely save my signature for verifying this transaction.']")  # TODO: verify on first run — may be TextView or CheckBox
    btn_proceed          = (AppiumBy.XPATH, "//android.widget.Button[@text='Proceed']")  # TODO: verify text on first run
    btn_confirm_payment  = (AppiumBy.XPATH, "//android.widget.Button[@text='Confirm Payment']")  # TODO: verify text on first run


# ══════════════════════════════════════════════════════════════════════════════
# VOID TRANSACTION FLOW (Enter Password → Void Confirmation → Done)
# ══════════════════════════════════════════════════════════════════════════════

class VoidLocators:
    """Locators for the Void transaction flow screens."""
    # Enter Password screen
    lbl_enter_password   = (AppiumBy.XPATH, "//android.widget.TextView[@text='Enter Password']")  # TODO: verify text on first run
    txt_password         = (AppiumBy.CLASS_NAME, "android.widget.EditText")
    btn_continue         = (AppiumBy.XPATH, "//android.widget.Button[@text='Continue']")  # TODO: verify on first run
    # Void confirmation
    btn_void_payment     = (AppiumBy.XPATH, "//android.widget.Button[@text='Void Payment']")  # TODO: verify on first run
    # Post-void completion
    btn_done             = (AppiumBy.XPATH, "//android.widget.Button[@text='Done']")  # TODO: verify on first run


# ══════════════════════════════════════════════════════════════════════════════
# MENU / DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════

class HomeScreen:
    btn_collect_payment    = (AppiumBy.XPATH, "//android.widget.Button[@text='Collect Payment']")
    btn_payments_history   = (AppiumBy.XPATH, "//android.widget.Button[@text='Payments History']")
    btn_transactions       = (AppiumBy.XPATH, "//android.widget.Button[@text='Transactions']")
    btn_settings           = (AppiumBy.XPATH, "//android.widget.Button[@text='Settings']")
    btn_help               = (AppiumBy.XPATH, "//android.widget.Button[@text='Help']")
    btn_khaata             = (AppiumBy.XPATH, "//android.widget.Button[@text='Khaata']")
    btn_other_apps         = (AppiumBy.XPATH, "//android.widget.Button[@text='Other Apps']")


# ══════════════════════════════════════════════════════════════════════════════
# OTHER APPS PAGE
# ══════════════════════════════════════════════════════════════════════════════

class OtherAppsLocators:
    btn_calculator         = (AppiumBy.XPATH, "//android.widget.Button[@text='Calculator Calculator']")


# ══════════════════════════════════════════════════════════════════════════════
# CALCULATOR PAGE
# ══════════════════════════════════════════════════════════════════════════════

class CalculatorLocators:
    btn_7                  = (AppiumBy.XPATH, "//android.widget.Button[@text='7']")


# ══════════════════════════════════════════════════════════════════════════════
# HELP CENTER PAGE
# ══════════════════════════════════════════════════════════════════════════════

class HelpCenterLocators:
    lbl_support_numbers    = (AppiumBy.XPATH, "//android.widget.TextView[@text='1800 212 212 212 / 1800 313 313 313']")


# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING / SELECT ENVIRONMENT (post-install first launch)
# ══════════════════════════════════════════════════════════════════════════════

class OnboardingLocators:
    lbl_select_environment = (AppiumBy.XPATH, "//android.widget.TextView[@text='Select Environment']")  # TODO: verify text on first run
    chk_dont_show_again    = (AppiumBy.XPATH, '//android.view.View[@text="I don\'t want to see this again"]')  # TODO: verify locator — may be View or Button
    btn_next               = (AppiumBy.XPATH, "//android.widget.Button[@text='Next']")
    btn_start              = (AppiumBy.XPATH, "//android.widget.Button[@text='Start']")
