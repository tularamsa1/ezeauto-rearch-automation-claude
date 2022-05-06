from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage


class PaymentPage(BasePage):

    btn_cash = (By.XPATH, '//android.widget.TextView[@text = "Cash"]')
    btn_Details = (By.ID, 'com.ezetap.service.demo:id/btnDetails')
    btn_dismissDetails = (By.ID, 'com.ezetap.service.demo:id/btnDismiss')
    btn_confirmPayment = (By.ID, 'com.ezetap.service.demo:id/btnConfirm')
    lbl_customerEmail = (By.XPATH, "//android.widget.TextView[contains(text(),'.com')]")
    lbl_mobileNumber = (By.XPATH, "//android.widget.TextView[contains(text(),'9845698456')]")
    btn_upi = (By.XPATH, "//*[@text='UPI']")
    btn_bqr = (By.XPATH, "//*[@text='Bharat QR']")
    #    USER_ACTION_MESSAGE = (By.ID, 'com.ezetap.service.demo:id/txn_user_action_msg')
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


    def __init__(self, driver):
        super().__init__(driver)

    def click_on_Upi_paymentMode(self):
        self.perform_click(self.btn_upi)

    def click_on_Bqr_paymentMode(self):
        self.perform_click(self.btn_bqr)

    # def get_user_action_text(self):
    #     return self.get_text(self.USER_ACTION_MESSAGE)

    def fetch_da_alert_message(self):
        return self.fetch_text(self.txa_daAlertMessage)

    def fetch_promo_offer(self):
        return self.fetch_text(self.txa_promoMessage)


    def click_on_Cash(self):
        self.perform_touch_action_using_cordinates(323,1168, 323,618)
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

    def click_on_proceed_homepage(self):
        self.perform_click(self.btn_proceedToHomepage)

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
