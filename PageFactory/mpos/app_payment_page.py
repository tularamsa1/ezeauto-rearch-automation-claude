import re
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from PageFactory.mpos.app_base_page import BasePage
from PageFactory.mpos.app_home_page import HomePage


class PaymentPage(BasePage):
    btn_cash = (By.XPATH, '//android.widget.TextView[@text = "Cash"]')
    btn_Details = (By.ID, 'com.ezetap.service.demo:id/btnDetails')
    btn_dismissDetails = (By.ID, 'com.ezetap.service.demo:id/btnDismiss')
    btn_confirmPayment = (By.ID, 'com.ezetap.service.demo:id/btnConfirm')
    lbl_customerEmail = (By.XPATH, "//android.widget.TextView[contains(text(),'.com')]")
    lbl_mobileNumber = (By.XPATH, "//android.widget.TextView[contains(text(),'9845698456')]")
    btn_upi = (By.XPATH, "//*[@text='UPI']")
    btn_bqr = (By.XPATH, "//*[@text='Bharat QR']")
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
    btn_pan = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvSelectPan')
    btn_form60 = (AppiumBy.ID, 'com.ezetap.service.demo:id/tvSelectForm60')
    txt_pan_number = (AppiumBy.ID, 'com.ezetap.service.demo:id/txtInputEntryPan')
    btn_confirm = (AppiumBy.ID, 'com.ezetap.service.demo:id/btnConfirmPanForm')
    btn_cheque = (By.XPATH, '//android.widget.TextView[@text = "Cheque"]')
    txt_enterChequeNumber = (By.ID, "com.ezetap.service.demo:id/txtInputEntryChequeNum")
    btn_selectbankName = (By.ID, "com.ezetap.service.demo:id/txtInputEntryBankName")
    btn_select_date = (By.XPATH, "//*[@text='OK']")
    btn_ok =(By.XPATH, "//*[@text='Cheque Dated']")
    btn_cheque_submit = (By.ID, "com.ezetap.service.demo:id/btnConfirmCheque")
    btn_sign_required = (By.ID, "com.ezetap.service.demo:id/rltvSignRequired")
    btn_addSignature = (By.ID, "com.ezetap.service.demo:id/btnAddSignature")
    btn_signatureSubmit = (By.ID, "com.ezetap.service.demo:id/btnSubmitSign")
    btn_sign_submit =(By.ID, "com.ezetap.service.demo:id/btnSubmitSign")
    txt_signature_success_status = (By.ID, "com.ezetap.service.demo:id/tvSignSubmitted")
    btn_click_sign = (By.XPATH, "//*[@text='Click here to sign']")
    lbl_amount = (By.ID, 'com.ezetap.service.demo:id/tvAmount')

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
        print("Status APP:", status)
        self.perform_click(self.btn_closeTransactionDetails)
        return txn_id, status

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

    def perform_pan_entry(self, pan_number):
        """
        This method is used when user wants to perform PAN entry during cash trx
        """
        self.perform_click(self.btn_pan)
        self.wait_for_element(self.txt_pan_number).clear()
        self.perform_sendkeys(self.txt_pan_number, pan_number)
        self.perform_click(self.btn_confirm)

    def perform_form60(self):
        """
        This method is used when user wants to perform FORM60  during cash trx
        """
        self.wait_for_element(self.btn_form60)
        self.perform_click(self.btn_form60)
        self.perform_click(self.btn_confirm)
