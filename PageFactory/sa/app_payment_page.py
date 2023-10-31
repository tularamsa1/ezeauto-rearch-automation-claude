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

