import re
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage
from PageFactory.mpos.app_home_page import HomePage
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class PaymentPage(BasePage):
    btn_cash = (By.XPATH, '//android.widget.TextView[@text = "Cash"]')
    btn_Details = (By.ID, 'com.ezetap.service.demo:id/btnDetails')
    btn_dismissDetails = (By.ID, 'com.ezetap.service.demo:id/btnDismiss')
    btn_confirmPayment = (By.ID, 'com.ezetap.service.demo:id/btnConfirm')
    lbl_customerEmail = (By.XPATH, "//android.widget.TextView[contains(text(),'.com')]")
    lbl_mobileNumber = (By.XPATH, "//android.widget.TextView[contains(text(),'9845698456')]")
    btn_upi = (By.XPATH, "//*[@text='UPI']")
    btn_bqr = (By.XPATH, "//*[@text='Bharat QR']")
    btn_card = (By.XPATH, "//*[@text='Card']")
    # btn_credit_debit_card = (By.ID, "com.ezetap.service.demo:id/imgCardIcon")
    btn_credit_debit_card = (By.XPATH, "//*[@text='Card']")
    btn_back = (By.ID, "com.ezetap.service.demo:id/ibtnBack")
    btn_back_enter_amt_window = (By.ID, "com.ezetap.basicapp:id/imgBack")
    txa_daAlertMessage = (By.ID, 'com.ezetap.service.demo:id/tvAlert')
    txa_promoMessage = (By.ID, 'com.ezetap.service.demo:id/tvAvailableOffer')
    lbl_paymentStatus = (By.ID, 'com.ezetap.service.demo:id/tvTxnStatus')
    btn_proceedToHomepage = (By.ID, "com.ezetap.service.demo:id/btnProceed")
    btn_viewDetails = (By.ID, "com.ezetap.service.demo:id/btnViewDetails")
    txa_transactionId = (By.XPATH, '//*[@text="Transaction Id"]/following-sibling::android.widget.TextView[2]')
    txa_status = (By.XPATH, '//*[@text="Status"]/following-sibling::android.widget.TextView[2]')
    txa_orderId = (By.XPATH, '//*[@text="Order Id"]/following-sibling::android.widget.TextView[2]')
    btn_closeTransactionDetails = (By.ID, 'com.ezetap.service.demo:id/btnDismiss')
    lbl_scanQRCode = (By.XPATH, '//*[contains(@text,"Scan QR code")]')
    lbl_paymentMode = (By.ID, "com.ezetap.service.demo:id/tvPaymentType")
    lbl_paymentAmt = (By.ID, "com.ezetap.service.demo:id/tvTxnAmount")
    lbl_payWith = (By.ID, 'com.ezetap.service.demo:id/tvPayWithTop')
    lbl_checkstatusTitle = (By.ID, 'com.ezetap.service.demo:id/tvCheckStatusTitle')
    lbl_checkstatus = (By.ID, "com.ezetap.service.demo:id/btn_check_status")
    lbl_skip = (By.ID, "com.ezetap.service.demo:id/btnSkip")
    btn_cancelTransactionYes = (By.XPATH, '//*[contains(@text,"Yes")]')
    btn_cancel_p2p_request = (By.ID, "com.ezetap.service.demo:id/btnYesCancelPayment")
    btn_go_to_home = (By.ID, "com.ezetap.service.demo:id/btnGoToHome")
    btn_cheque = (By.XPATH, '//android.widget.TextView[@text = "Cheque"]')
    txt_enter_cheque_number = (By.ID, "com.ezetap.service.demo:id/txtInputEntryChequeNum")
    btn_bank_name = (AppiumBy.XPATH, "//*[@resource-id ='com.ezetap.service.demo:id/txtInputEntryBankName']")
    btn_select_date = (By.XPATH, "//*[@text='OK']")
    btn_ok =(By.XPATH, "//*[@text='Cheque Dated']")
    btn_cheque_submit = (By.ID, "com.ezetap.service.demo:id/btnConfirmCheque")
    btn_sign_required = (By.ID, "com.ezetap.service.demo:id/rltvSignRequired")
    btn_addSignature = (By.ID, "com.ezetap.service.demo:id/btnAddSignature")
    btn_signatureSubmit = (By.ID, "com.ezetap.service.demo:id/btnSubmitSign")
    btn_sign_submit =(By.ID, "com.ezetap.service.demo:id/btnSubmitSign")
    txt_signature_success_status = (By.ID, "com.ezetap.service.demo:id/tvSignSubmitted")
    btn_click_sign = (By.XPATH, "//*[@text='Click here to sign']")
    lbl_calender = (By.ID, "com.ezetap.service.demo:id/txtInputEntryChequeDate")
    btn_okk = (AppiumBy.ID, 'android:id/button1')
    btn_ifsc = (AppiumBy.ID, 'com.ezetap.service.demo:id/txtInputEntryIFSC')
    lbl_amount = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvAmount')
    txt_payment_status = (By.ID, 'com.ezetap.service.demo:id/tvTxnStatus')
    txt_payment_mode = (By.ID, 'com.ezetap.service.demo:id/tvPaymentType')
    txt_payment_amount = (By.ID, 'com.ezetap.service.demo:id/tvTxnAmount')
    txt_error_message = (By.ID, 'com.ezetap.service.demo:id/tvErrorMessage')
    btn_check_status_skip = (By.ID, 'com.ezetap.service.demo:id/btnSkip')
    btn_check_status = (By.ID, 'com.ezetap.service.demo:id/btn_check_status')
    btn_pan = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvSelectPan')
    btn_form60 = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvSelectForm60')
    txt_pan_number = (AppiumBy.ID, 'com.ezetap.service.demo:id/txtInputEntryPan')
    btn_confirm = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnConfirmPanForm')
    txt_payment_error_title = (By.ID, 'com.ezetap.service.demo:id/tvErrorTitle')
    txt_check_status_title = (By.ID, 'com.ezetap.service.demo:id/tvCheckStatusTitle')
    emi_on_card = (By.ID, "com.ezetap.service.demo:id/tvEmi")
    btn_emi_plan = (By.ID, "com.ezetap.service.demo:id/rbEMIPlan")
    pay_in_full = (By.ID, "com.ezetap.service.demo:id/tvPayInFull")
    btn_brand_emi = (By.XPATH, "//android.widget.TextView[@text='Brand EMI']")
    search_prod_or_brand = (By.ID, "com.ezetap.service.demo:id/actv_Brand_Product")
    select_brand = (By.ID, "com.ezetap.service.demo:id/tvSelectBrand")
    serial_no = (By.ID, "com.ezetap.service.demo:id/etBarCode")
    btn_proceed = (By.ID, "com.ezetap.service.demo:id/btn_proceed")
    err_msg_brand_emi = (By.ID, 'com.ezetap.service.demo:id/dialogText')
    plan = (By.ID, "com.ezetap.service.demo:id/tvPlanMonthlyTitle")
    btn_emi = (By.XPATH, "//*[@text='Bank EMI']")
    err_msg_normal_emi = (By.ID, 'com.ezetap.service.demo:id/tvErrorMessage')
    btn_eze_emi = (By.XPATH, "//*[@text='EMI Plus']")
    brand_list = (By.ID, "com.ezetap.service.demo:id/tvName")
    imei_no = (By.XPATH, "//*[@text='IMEI No/ Serial No']")
    customer_no = (By.ID, "com.ezetap.service.demo:id/et_mobile_no")
    btn_submit = (By.ID, "com.ezetap.service.demo:id/btn_validate_mobile")
    btn_use_wallet = (By.ID, "com.ezetap.service.demo:id/btnUseWallet")
    ok_error_btn = (By.ID, "com.ezetap.service.demo:id/rightButton")
    razorpay_emi_discount = (By.XPATH, f"//*[contains(@text,'Razorpay EMI Discount')]")
    bo_element = (By.XPATH, '//*[@text="Instant Discount(Offer)"]/following-sibling::android.widget.TextView[2]')
    txt_customer_mobile_number = (By.ID, 'com.ezetap.service.demo:id/tvSubtitle')
    txt_agent_mobile_number = (By.ID, 'com.ezetap.service.demo:id/tvSubtitleAgent')
    btn_remote_pay = (By.XPATH, "//*[@text='Pay Link']")
    btn_send_link = (By.ID, 'com.ezetap.service.demo:id/btnSendLink')
    err_msg_mobile_number_remote_pay = (By.ID, 'com.ezetap.service.demo:id/tvPhoneNoHelper')
    lbl_upi_err_msg = (By.XPATH, '//*[contains(@text,"Valid UPI configuration not found for merchant")]')

    btn_native_sample = (By.ID, 'com.ezeapi.sample:id/btnNative')
    btn_initialize_sample = (By.ID, 'com.ezeapi.sample:id/btnInitialize')
    btn_upi_txn_sample = (By.ID, 'com.ezeapi.sample:id/btnUPITxn')
    order_id_sample = (By.ID, 'com.ezeapi.sample:id/order_number')
    amount_sample = (By.ID, 'com.ezeapi.sample:id/payable_amount')
    gst_amount_sample = (By.ID, 'com.ezeapi.sample:id/et_GstAmount')
    btn_ok_sample = (By.ID, 'com.ezeapi.sample:id/confirm_button')
    txt_customer_name = (By.XPATH, "//*[@text='Customer Name']/following-sibling::android.widget.TextView[2]")
    txt_order_id = (By.XPATH, "//*[@text='Order Id']/following-sibling::android.widget.TextView[2]")
    txt_date = (By.XPATH, "//*[@text='Date']/following-sibling::android.widget.TextView[2]")
    txt_transaction_id = (By.XPATH, "//*[@text='Transaction Id']/following-sibling::android.widget.TextView[2]")
    txt_status = (By.XPATH, "//*[@text='Status']/following-sibling::android.widget.TextView[2]")
    txt_payer_name = (By.XPATH, "//*[@text='Payer Name']/following-sibling::android.widget.TextView[2]")
    txt_rrn = (By.XPATH, "//*[@text='RR Number']/following-sibling::android.widget.TextView[2]")
    txt_mid = (By.XPATH, "//*[@text='MID']/following-sibling::android.widget.TextView[2]")
    txt_tid = (By.XPATH, "//*[@text='TID']/following-sibling::android.widget.TextView[2]")
    payment_dialog_sample = (AppiumBy.XPATH,
                             "/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.TextView")
    btn_cancel_sample = (AppiumBy.ID, 'com.ezeapi.sample:id/cancel_button')
    result_sample = (AppiumBy.ID, "com.ezeapi.sample:id/resultView")
    postpaid_lob_btn = (By.XPATH, "//*[@text='Postpaid-Mobile']")
    bill_coll_active_btn = (By.XPATH, "//*[@text='Bill Collection - Active']")
    mobile_no_btn = (By.XPATH, "//*[@text='Mobile No.']")
    fetch_details_btn = (By.XPATH, "//*[@text='Fetch Details']")
    amount_field_btn = (By.XPATH, "//*[@text='1226']")
    checkout_btn = (By.XPATH, "//*[@text='Checkout']")
    txt_order_id_airtel = (By.ID, "com.ezetap.service.demo:id/tvOrderId")


    def __init__(self, driver):
        super().__init__(driver)

    def click_on_Upi_paymentMode(self):
        stale_element = True
        while stale_element:
            try:
                self.perform_click(self.btn_upi)
                stale_element = False
            except StaleElementReferenceException:
                print("STALE ELEMENT EXECPTION....!!!!!!!!!")
                stale_element = True

    def click_on_Bqr_paymentMode(self):
        self.scroll_to_text("Bharat QR")
        self.perform_click(self.btn_bqr)

    def click_on_Card_paymentMode(self):
        self.scroll_to_text("CARD")
        self.perform_click(self.btn_card)

    def click_on_credit_debit_card_mode(self):
        self.scroll_to_text("Card")
        self.perform_click(self.btn_credit_debit_card)

    def fetch_da_alert_message(self):
        return self.fetch_text(self.txa_daAlertMessage)

    def fetch_promo_offer(self):
        return self.fetch_text(self.txa_promoMessage)

    def click_on_Cash(self):
        self.scroll_to_text("Cash")
        self.perform_click(self.btn_cash)

    def click_on_DetailsBtn(self):
        self.perform_click(self.btn_Details)

    def get_Customer_email(self):
        return self.fetch_text(self.lbl_customerEmail)

    def get_MobileNo(self):
        return self.fetch_text(self.lbl_mobileNumber)

    def click_on_view_btn(self):
        self.perform_click(self.btn_Details)

    def click_on_dismiss(self):
        self.perform_click(self.btn_dismissDetails)

    def click_on_confirm(self):
        self.perform_click(self.btn_confirmPayment)

    def fetch_payment_status(self):
        return self.fetch_text(self.lbl_paymentStatus)

    def fetch_payment_mode(self):
        return self.fetch_text(self.lbl_paymentMode)

    def fetch_payment_amount(self):
        return self.fetch_text(self.lbl_paymentAmt)

    def click_on_proceed_homepage(self):
        """
        This method is used to proceed to homepage after successful transaction
        """
        self.wait_for_visibility_of_elements(self.btn_proceedToHomepage)
        self.perform_click(self.btn_proceedToHomepage)

    def click_on_back_btn(self):
        staleElement = True
        while (staleElement):
            try:
                self.perform_click(self.btn_back)
                staleElement = False
            except StaleElementReferenceException:
                print("STALE ELEMENT EXECPTION....!!!!!!!!!")
                staleElement = True

    def get_transaction_details(self):
        self.perform_click(self.btn_viewDetails)
        txn_id = self.fetch_text(self.txa_transactionId)
        print("Txn id APP:", txn_id)
        status = self.fetch_text(self.txa_status)
        print("Status APP:",status)
        self.perform_click(self.btn_closeTransactionDetails)
        return txn_id,status

    def validate_upi_bqr_payment_screen(self):
        return self.fetch_text(self.lbl_scanQRCode)

    def validate_upi_err_msg(self):
        return self.fetch_text(self.lbl_upi_err_msg)

    def is_payment_page_displayed(self, amount, order_id):
        try:
            self.wait_for_element(self.lbl_payWith, 6)
        except:
            self.wait_for_element(self.lbl_checkstatusTitle)
            self.perform_click(self.lbl_checkstatus)
            if self.fetch_text(self.lbl_paymentStatus) == "Payment Successful":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Failed":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_amount_and_order_number(amount, order_id)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Pending":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.lbl_skip)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_amount_and_order_number(amount, order_id)
            else:
                pass

    def is_payment_page_displayed_card(self, amount, order_id, device_serial):
        try:
            self.wait_for_element(self.lbl_payWith, 6)
        except:
            self.wait_for_element(self.lbl_checkstatusTitle)
            self.perform_click(self.lbl_checkstatus)
            if self.fetch_text(self.lbl_paymentStatus) == "Payment Successful":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Failed":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Pending":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.lbl_skip)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_amount_and_order_number_and_device_serial_for_card(amount, order_id, device_serial)
            else:
                pass

    def is_payment_page_displayed_card_with_tip(self, amount, order_id, tip_amt, device_serial):
        try:
            self.wait_for_element(self.lbl_payWith, 6)
        except:
            self.wait_for_element(self.lbl_checkstatusTitle)
            self.perform_click(self.lbl_checkstatus)
            if self.fetch_text(self.lbl_paymentStatus) == "Payment Successful":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Failed":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_tip_and_amount_and_order_number_and_device_serial_for_card(amount, order_id, tip_amt, device_serial)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Pending":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.lbl_skip)
                self.perform_click(self.btn_back_enter_amt_window)
                homePage = HomePage(self.driver)
                homePage.enter_tip_and_amount_and_order_number_and_device_serial_for_card(amount, order_id, tip_amt, device_serial)
            else:
                pass

    def is_payment_page_displayed_P2P(self):
        try:
            self.wait_for_element(self.lbl_payWith, 6)
        except:
            self.wait_for_element(self.lbl_checkstatusTitle)
            self.perform_click(self.lbl_checkstatus)
            if self.fetch_text(self.lbl_paymentStatus) == "Payment Successful":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Failed":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Pending":
                self.perform_click(self.lbl_skip)
            else:
                pass

    def is_qrcode_displayed_P2P(self):
        try:
            self.wait_for_element(self.lbl_scanQRCode, 6)
        except:
            self.wait_for_element(self.lbl_checkstatusTitle)
            self.perform_click(self.lbl_checkstatus)
            if self.fetch_text(self.lbl_paymentStatus) == "Payment Successful":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Failed":
                self.perform_click(self.btn_proceedToHomepage)
            elif self.fetch_text(self.lbl_paymentStatus) == "Payment Pending":
                self.perform_click(self.btn_proceedToHomepage)
                self.perform_click(self.lbl_skip)
            else:
                pass

    def click_on_transaction_cancel_yes(self):
        self.perform_click(self.btn_cancelTransactionYes)

    def click_on_cancel_p2p_request_ok(self):
        self.perform_click(self.btn_cancel_p2p_request)

    def click_on_goto_homepage(self):
        try:
            self.wait_for_element(self.btn_proceedToHomepage, 6)
        except:
            self.click_on_back_btn()
            self.click_on_transaction_cancel_yes()
            self.click_on_proceed_homepage()
            return False
        self.click_on_proceed_homepage()
        return True

    def click_on_proceed_to_home_page_for_failed_txn(self):
        """
        This method is used for proceed to home page after failed payment
        """
        self.perform_click(self.btn_go_to_home)

    def click_on_back_btn_in_enter_amt_window(self):
        """
        This method is used for proceed back from the enter amount window
        """
        self.perform_click(self.btn_back_enter_amt_window)

    def click_on_cheque(self):
        """
        Scrolls to the 'Cheque' option and performs a click action
        """
        self.scroll_to_text("Cheque")
        self.perform_click(self.btn_cheque)

    def fill_cheque_number(self, cheque_number: int):
        """
        Fill the cheque number field with the passed 'chequeNumber'.
        """
        self.perform_click(self.txt_enter_cheque_number)
        self.perform_sendkeys(self.txt_enter_cheque_number, cheque_number)

    def fill_bank_name(self, bank_name: str):
        """
        Clicks the bank name field, then enters 'bank_name' text into the input field
        """
        self.wait_for_element_to_be_clickable(self.btn_bank_name)
        self.perform_click(self.btn_bank_name)
        self.perform_sendkeys(self.btn_bank_name, bank_name)

    def get_relative_coordinate_for_bank(self):
        """
          Returns relative co-ordinates of Bank name text field on cheque txn page.
        """
        bounds_str = self.wait_for_element(self.btn_bank_name).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            x1 = int(matches[0]) * 4.29
            y1 = int(matches[1]) * 1.29
            y1 = round(y1)
            x1 = round(x1)
            return x1, y1
        else:
            logger.info("Not enough numeric values found in the string")

    def perform_click_to_bank(self, x: int, y: int):
        """Perform a tap action on the screen at the specified coordinates.
        Args:
            x (int): The x-coordinate for the tap.
            y (int): The y-coordinate for the tap.
        """
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def click_on_date(self, give_today_date: str):
        """Click a date in the calendar.
          Args:
              give_today_date (str): The date to be clicked in the calendar.
          """
        self.perform_click(self.lbl_calender)
        self.perform_click((AppiumBy.ACCESSIBILITY_ID, '' + give_today_date + ''))
        self.perform_click(self.btn_okk)

    def fill_ifsc_code(self, ifsc_code: str):
        """Fill the IFSC code field with the provided code.
        Args:
            ifsc_code (str): The IFSC code to be entered.
        """
        self.wait_for_element(self.btn_ifsc)
        self.perform_click(self.btn_ifsc)
        self.perform_sendkeys(self.btn_ifsc, ifsc_code)

    def get_relative_coordinate_for_ifsc_code(self):
        """
        Calculate and return relative coordinates for the IFSC code element
        """
        bounds_str = self.wait_for_element(self.btn_ifsc).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            x1 = int(matches[0]) * 3.59
            y1 = int(matches[1]) * 0.96
            y1 = round(y1)
            x1 = round(x1)
            return x1, y1
        else:
            logger.info("Not enough numeric values found in the string")

    def perform_touch_action_on_cheque_home_page(self, x: int, y: int):
        """
        Perform a touch action on the Cheque Home page to minimize keyboard
        """
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def click_on_cheque_submit(self):
        """
        Performs a click action on the 'Submit Cheque' button element.
        """
        self.perform_click(self.btn_cheque_submit)

    def click_on_signature_required(self):
        """
        Performs a click action on the 'Signature Required' button.
        """
        self.perform_click(self.btn_sign_required)

    def add_signature(self, x: int, y: int):
        """Add a signature by performing a swipe gesture from (x, y) to (x+60, y).
        Args:
            x (int): The starting x-coordinate of the signature.
            y (int): The y-coordinate of the signature.
        """
        x2 = x + 60
        TouchAction(self.driver).press(x=x, y=y).move_to(x=x2, y=y).release().perform()

    def signature_submit(self):
        """
        Clicks the 'Submit' button for the signature
        """
        self.perform_click(self.btn_sign_submit)

    def check_sign_success_status(self):
        """
        Check and returns the success status of a signature.
        """
        status = self.fetch_text(self.txt_signature_success_status)
        return status

    def get_relative_coordinate_for_signature(self):
        """
        Get relative coordinates for signature placement.
        Parses the bounds of amount and calculates relative x, y coordinates for signature placement.
        """
        bounds_str = self.wait_for_element(self.lbl_amount).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            x1 = int(matches[0]) * 5
            a1 = int(matches[1]) * 1.25
            y1 = round(a1)
            return x1, y1
        else:
            logger.info("Not enough numeric values found in the string")

    def fetch_payment_failed_status(self):
        """
        fetches the payment status text from check status pop up
        return: str
        """
        self.wait_for_element(self.txt_payment_status)
        return self.fetch_text(self.txt_payment_status)

    def fetch_payment_failed_amount(self):
        """
        fetches the payment amount from the check status pop up
        return: str
        """
        self.wait_for_element(self.txt_payment_amount)
        return self.fetch_text(self.txt_payment_amount)

    def fetch_payment_failed_error_message(self):
        """
        fetches the payment message form the check status pop up
        return: str
        """
        self.wait_for_element(self.txt_error_message)
        return self.fetch_text(self.txt_error_message)

    def fetch_add_auth_payment_failed_mode(self):
        """
        fetches the payment mode from the check status pop up
        return: str
        """
        self.wait_for_element(self.txt_payment_mode)
        return self.fetch_text(self.txt_payment_mode)

    def fetch_error_title(self):
        """
        fetches payment status title from the check status pop up
        return: str
        """
        return self.fetch_text(self.txt_payment_error_title)

    def fetch_check_status_title(self):
        """
        fetches title of the check status
        return: str
        """
        return self.fetch_text(self.txt_check_status_title)

    def fetch_skip_txt(self):
        """
        fetches text from skip button in the check status
        return: str
        """
        return self.fetch_text(self.btn_check_status_skip)

    def fetch_check_status_btn_txt(self):
        """
        fetches text from check status button in the check status
        return: str
        """
        return self.fetch_text(self.btn_check_status)

    def click_on_check_status(self):
        """
        performs click on the check status button
        """
        self.perform_click(self.btn_check_status)

    def perform_pan_entry(self, pan_number: str):
        """
        This method is used when user wants to perform PAN entry during cash txn
        """
        self.perform_click(self.btn_pan)
        self.wait_for_element(self.txt_pan_number).clear()
        self.perform_sendkeys(self.txt_pan_number, pan_number)
        self.perform_click(self.btn_confirm)


    def select_payment_option_emi_on_card(self):
        """
        This method is used to select payment option as emi on card
        """
        self.perform_click(self.emi_on_card)
        self.perform_click(self.btn_proceedToHomepage)

    def select_emi_plan(self, emi_plan_in_months: int):
        """
        This method is used to select emi plan
        param: emi_plan_in_months int
        """
        locator = (By.XPATH, f"//*[contains(@text,'{emi_plan_in_months}m')]")
        self.perform_click(locator)
        self.perform_click(self.btn_proceedToHomepage)

    def select_payment_option_pay_in_full(self):
        """
        This method is used to select payment option as pay in full
        """
        self.perform_click(self.pay_in_full)
        self.perform_click(self.btn_proceedToHomepage)

    def click_on_brand_emi_pmt_mode(self):
        """
        This method is used to click on brand EMI payment mode
        """
        self.scroll_to_text("Brand EMI")
        self.perform_click(self.btn_brand_emi)

    def click_and_enter_search_products_or_brands(self, prod: str):
        """
        This method is used to click and enter the search parameters for products or brands
        param: prod str
        """
        self.perform_click(self.search_prod_or_brand)
        self.perform_sendkeys(self.search_prod_or_brand, prod)
        self.perform_click(self.select_brand)

    def click_and_enter_imei_no(self, imei: int):
        """
        This method is used to enter imei no or serial no for brand EMI payment mode and click on proceed button
        :param imei: int
        """
        self.scroll_to_text("Enter number or Scan")
        self.perform_click(self.serial_no)
        self.perform_sendkeys(self.serial_no, imei)
        self.perform_click(self.btn_proceed)

    def fetch_error_msg_brand_emi(self):
        """
        This method is used to fetch error msg for brand emi
        return: str
        """
        return self.fetch_text(self.err_msg_brand_emi)

    def click_on_bank_emi_pmt_mode(self):
        """
         This method is used to click on bank emi payment mode
        """
        self.scroll_to_text("Bank EMI")
        self.perform_click(self.btn_emi)

    def fetch_error_msg_normal_emi(self):
        """
        This method is used to fetch error msg for normal emi
        return: str
        """
        return self.fetch_text(self.err_msg_normal_emi)

    def click_on_eze_emi_pmt_mode(self):
        """
        This method is used to click on eze emi payment mode
        """
        self.scroll_to_text("EMI Plus")
        self.perform_click(self.btn_eze_emi)

    def click_and_enter_customer_number(self, customer_no: str):
        """
        This method is used to enter customer number and click on proceed btn for eze emi flow
        param customer_no: str
        """
        self.perform_click(self.customer_no)
        self.perform_sendkeys(self.customer_no, customer_no)
        self.perform_click(self.btn_submit)

    def click_and_enter_imei_number_for_eze_emi(self, imei: int):
        """
        This method is used to enter imei number, click on use wallet and proceed btn for eze emi flow
        param imei: int
        """
        self.perform_click(self.serial_no)
        self.perform_sendkeys(self.serial_no, imei)
        self.scroll_to_text("Use Wallet")
        self.perform_click(self.btn_use_wallet)
        self.perform_click(self.btn_proceed)

    def select_emi_plan_for_eze_emi_brand_flow(self, emi_plan_in_months: int):
        """
        This method is used to select emi plan, click on use wallet and proceed btn for eze emi brand flow
        param: emi_plan_in_months int
        """
        locator = (By.XPATH, f"//*[contains(@text,'{emi_plan_in_months}m')]")
        self.perform_click(locator)
        self.perform_click(self.btn_use_wallet)
        self.perform_click(self.btn_proceedToHomepage)

    def click_on_ok_error_btn_for_brand_emi(self):
        """
        This method is used to click on ok button for brand emi
        """
        self.wait_for_visibility_of_elements(self.ok_error_btn)
        self.perform_click(self.ok_error_btn)

    def click_on_ok_error_btn_for_normal_Eze_emi(self):
        """
        This method is used to click on ok button for normal and eze emi
        """
        self.wait_for_visibility_of_elements(self.btn_proceedToHomepage)
        self.perform_click(self.btn_proceedToHomepage)

    def check_visibility_of_razorpay_emi_discount(self, emi_plan_in_months: int):
        """
        This method is used to check visibility of razorpay emi discount
        param: emi_plan_in_months int
        return: bool
        """
        locator = (By.XPATH, f"//*[contains(@text,'{emi_plan_in_months}m')]")
        self.perform_click(locator)
        try:
            self.visibility_of_elements(self.razorpay_emi_discount)
            return True
        except Exception as e:
            logger.exception(f"razorpay emi discount is not visible due to: {e}")
            return False

    def fetch_emi_cost_text(self, emi_plan: int):
        """
            This method is used to capture No cost EMI or Low cost EMI text
            param: emi_plan_in_months int
            return: str
        """
        locator = (By.XPATH, f"//*[@text='{emi_plan}m']/..//*[@resource-id='com.ezetap.service.demo:id/tvEMICost']")
        return self.fetch_text(locator)

    def list_of_brands(self):
        """
            This method returns lists of brand elements
            return: str
        """
        elements = self.wait_for_visibility_of_elements(self.brand_list)
        return [brand.text for brand in elements]

    def click_and_enter_imei_no_and_proceed_btn(self, imei: str):
        """
            This method is used to check proceed button is disabled or not
            :param imei: str
            return bool
        """
        self.perform_click(self.serial_no)
        self.perform_sendkeys(self.serial_no, imei)
        self.scroll_to_text("Use Wallet")
        self.perform_click(self.btn_use_wallet)
        try:
            self.wait_for_element_to_be_clickable(self.btn_proceed, time=15)
            logger.debug(f"Proceed button is clickable")
            return True
        except Exception as e:
            logger.exception(f"Proceed button is not clickable within 15 seconds due to : {e}")
            return False

    def is_imei_no_present(self):
        """
            This method is used to check the visibility of imei no
            return bool
        """
        try:
            self.wait_for_visibility_of_elements(self.imei_no)
            logger.debug(f"IMEI number is visible")
            return True
        except Exception as e:
            logger.exception(f"IMEI number is not visible due to : {e}")
            return False

    def is_use_wallet_btn_visible(self):
        """
            This method is used to check visibility of wallet button
            return bool
        """
        try:
            self.wait_for_visibility_of_elements(self.btn_use_wallet)
            logger.debug(f"Use wallet is visible")
            return True
        except Exception as e:
            logger.exception(f"Use wallet is not visible due to : {e}")
            return False

    def select_emi_plan_in_months(self, emi_plan_in_months: int):
        """
        This method is used to select emi plan and check for the wallet
        param: emi_plan_in_months int
        """
        locator = (By.XPATH, f"//*[contains(@text,'{emi_plan_in_months}m')]")
        self.perform_click(locator)

    def fetch_text_razorpay_emi_discount(self, sub_value: str):
        """
            This method is used to collect the razorpay emi discount subvention value
            param: sub_value str
            return str
        """
        razorpay_emi_dis = (By.XPATH, f"//*[@text= 'Razorpay EMI Discount(@{sub_value}%)']")
        return self.fetch_text(razorpay_emi_dis)

    def is_emi_discount_applied(self, sub_value: str):
        """
            This method is used to collect the emi discount
            param: sub_value str
        """
        try:
            emi_discount = (By.XPATH, f"//*[@text= 'EMI Discount(@{sub_value}%)']")
            self.wait_for_visibility_of_elements(emi_discount)
            logger.debug(f"EMI discount is visible")
        except Exception as e:
            logger.exception(f"EMI discount not visible : {e}")

    def check_for_bo_offer(self):
        """
            This method is used to check bo offer is present or not for eze emi
            return str
        """
        element = self.fetch_text(self.bo_element)
        return element

    def check_bank_emi_pmt_mode_present(self):
        """
        This method is used to check whether bank emi pmt mode is present or not
        return: bool
        """
        try:
            self.visibility_of_elements(self.btn_emi)
            return True
        except Exception as e:
            logger.exception(f"bank emi payment mode is not visible due to : {e}")
            return False

    def is_brand_emi_pmt_mode_visible(self):
        """
        This method is used to check the visibility of brand EMI payment option
        """
        self.wait_for_invisibility_of_elements(self.btn_brand_emi)

    def check_customer_mobile_number_field_visible(self):
        """
        This method is used to check whether customer mobile number field is visible or not for remote pay
        return: bool
        """
        try:
            self.visibility_of_elements(self.txt_customer_mobile_number)
            return True
        except Exception as e:
            logger.exception(f"customer mobile number field is not visible due to : {e}")
            return False

    def check_agent_mobile_number_field_visible(self):
        """
        This method is used to check whether agent mobile number field is visible or not for remote pay
        return: bool
        """
        try:
            self.visibility_of_elements(self.txt_agent_mobile_number)
            return True
        except Exception as e:
            logger.exception(f"agent mobile number field is not visible due to : {e}")
            return False

    def click_on_remote_pay_payment_mode(self):
        """
        This method is used to click on remote pay payment mode
        """
        self.scroll_to_text("Pay Link")
        self.perform_click(self.btn_remote_pay)

    def clink_on_send_link_btn(self):
        """
        This method is used to click on send link button for remote pay
        """
        self.perform_click(self.btn_send_link)

    def fetch_mobile_number_error_msg_for_remote_pay(self):
        """
        This method is used to fetch mobile number error msg for remote pay
        return: str
        """
        return self.fetch_text(self.err_msg_mobile_number_remote_pay)

    def upi_txn_in_sample_app(self):
        """
        This method is used to initialize merchant and select upi payment mode
        """
        self.perform_click(self.btn_native_sample)
        self.perform_click(self.btn_initialize_sample)
        self.scroll_to_text("UPI Transaction")
        self.perform_click(self.btn_upi_txn_sample)

    def enter_order_id_and_amount(self, order_id: str, amt: float):
        """
        This method is used to enter order_id and amount
        param: order_id: str
        param: amt: float
        """
        self.perform_sendkeys(self.order_id_sample, order_id)
        self.perform_sendkeys(self.amount_sample, amt)

    def enter_gst_amount(self, gst_amt: float):
        """
        This method is used to enter gst amount
        param: gst_amt: float
        """
        self.scroll_to_text("GST Amount")
        self.perform_sendkeys(self.gst_amount_sample, gst_amt)

    def confirm_upi_txn_in_sample_app(self):
        """
        This method is used to click on ok to confirm upi txn to generate QR
        """
        self.scroll_to_text("OK")
        self.perform_click(self.btn_ok_sample)

    def click_on_view_details_in_sample_app(self):
        """
        This method is used to click on view details after successful payment
        """
        self.perform_click(self.btn_viewDetails)

    def fetch_customer_name_text(self) -> str:
        """
        This method is used to fetch customer_name from view details page
        return: str
        """
        return self.fetch_text(self.txt_customer_name)

    def fetch_order_id_text(self) -> str:
        """
        This method is used to fetch order_id from view details page
        return: str
        """
        return self.fetch_text(self.txt_order_id)

    def fetch_date_text(self) -> str:
        """
        This method is used to fetch date from view details page
        return: str
        """
        return self.fetch_text(self.txt_date)

    def fetch_transaction_id_text(self) -> str:
        """
        This method is used to fetch transaction_id from view details page
        return: str
        """
        return self.fetch_text(self.txt_transaction_id)

    def fetch_status_text(self) -> str:
        """
        This method is used to fetch status from view details page
        return: str
        """
        return self.fetch_text(self.txt_status)

    def fetch_payer_name_text(self) -> str:
        """
        This method is used to fetch payer_name from view details page
        return: str
        """
        return self.fetch_text(self.txt_payer_name)

    def fetch_rrn_text(self) -> str:
        """
        This method is used to fetch rrn from view details page
        return: str
        """
        return self.fetch_text(self.txt_rrn)

    def fetch_mid_text(self) -> str:
        """
        This method is used to fetch mid from view details page
        return: str
        """
        return self.fetch_text(self.txt_mid)

    def fetch_tid_text(self) -> str:
        """
        This method is used to fetch tid from view details page
        return: str
        """
        return self.fetch_text(self.txt_tid)

    def getting_result_sample(self):
        self.wait_for_element(self.payment_dialog_sample)
        self.scroll_to_text("Cancel")
        self.perform_click(self.btn_cancel_sample)
        # self.scroll_to_text("Close")
        self.perform_swipeUp(7)
        return self.wait_for_element(self.result_sample)

    def click_on_post_paid_btn(self):
        self.perform_click(self.postpaid_lob_btn)

    def click_on_bill_coll_active_btn(self):
        self.perform_click(self.bill_coll_active_btn)

    def enter_mobile_no_and_fetch_details(self, mobile_no):
        self.perform_click(self.mobile_no_btn)
        self.perform_sendkeys(self.mobile_no_btn, mobile_no)
        self.perform_click(self.fetch_details_btn)

    def enter_amount_and_checkout(self, amount):
        self.perform_click(self.amount_field_btn)
        self.perform_sendkeys(self.amount_field_btn, amount)
        self.driver.back()
        self.perform_click(self.checkout_btn)

    def fetch_order_id_from_success_page(self):
        order_id = self.fetch_text(self.txt_order_id_airtel).split(' ')[-1]
        return order_id