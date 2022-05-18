from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage


class TransHistoryPage(BasePage):


    lbl_summary = (By.ID, 'com.ezetap.service.demo:id/tvLblSummary')
    btn_backHome = (By.ID, 'com.ezetap.service.demo:id/iVBackArrow')
    btn_filters = (By.ID, 'com.ezetap.service.demo:id/csFilter')
    lbl_transactions = (By.ID, '//android.widget.TextView[@text = "Transactions"]')
    lbl_noTransactionsAvailable = (By.ID, "com.ezetap.service.demo:id/tv_ErrorMsg")
    txa_amountField = (By.ID, 'com.ezetap.service.demo:id/tvAmount')
    txa_statusField = (By.ID, "com.ezetap.service.demo:id/tvTxnStatus")
    btn_printReceipt = (By.ID, 'com.ezetap.service.demo:id/btnPrintReceipt')
    btn_printCustomerCopy = (By.ID, "com.ezetap.service.demo:id/btnNegative")
    btn_skip = (By.ID, "com.ezetap.service.demo:id/btnPositive")
    btn_addSignature = (By.ID, "com.ezetap.service.demo:id/btnAddSignature")
    btn_sendEReceipt = (By.ID, "com.ezetap.service.demo:id/btnSendReceipt")
    txt_phoneNumberField = (By.ID, "com.ezetap.service.demo:id/etvPhoneNumber")
    btn_signatureSubmit = (By.ID, "com.ezetap.service.demo:id/btnSubmitSign")
    btn_voidTransaction = (By.ID, "com.ezetap.service.demo:id/btnVoidTxn")
    btn_voidTransactionYes = (By.ID, "com.ezetap.service.demo:id/btnPositive")
    txa_finalStatusField = (By.ID, "com.ezetap.service.demo:id/tvTxnFinalStatus")
    snp_fetchingChargeSlipMessage = (By.XPATH, "//*[contains(@text, 'Fetching Charge-slip')]")
    lnk_chargeSlip = (By.XPATH, "//*[contains(@text,'Click Here')]")
    lbl_receipt = (By.ID, "com.ezetap.service.demo:id/tvAmount")
    lbl_receiptNotFound = (By.XPATH, "//android.view.View[@content-desc='Not Found']")
    txa_authCode = (By.XPATH, "//*[@text='Auth Code']/following-sibling::android.widget.TextView")
    btn_toggleStausArrow = (By.ID, 'com.ezetap.service.demo:id/iv_ToggleStatus')
    txt_txnType = (By.ID, "com.ezetap.service.demo:id/tvTransactionType")
    txt_txnID = (By.XPATH, "//*[@text='TRANSACTION ID']/following-sibling::android.widget.TextView")
    txt_txnAmount = (By.ID, "com.ezetap.service.demo:id/tvTxnAmount")
    btn_backTransactionDetails = (By.ID, "com.ezetap.service.demo:id/ivBackArrow")

    def __init__(self, driver):
        super().__init__(driver)

    def get_summary_text(self):
        return self.fetch_text(self.lbl_summary)

    def click_back_Btn(self):
        self.perform_click(self.btn_backHome)

    def click_first_amount_field(self):
        el = self.wait_for_all_elements(self.txa_amountField)
        print(el[1].text())
        return el[1].text()

    def check_for_elements_in_txn_history(self):
        return self.wait_for_all_elements(self.txa_amountField)

    def click_print_receipt(self):
        self.perform_click(self.btn_printReceipt)

    def click_customer_copy(self):
        self.perform_click(self.btn_printCustomerCopy)
        sleep(1.5)

    def click_signature_page(self):
        self.perform_click(self.btn_addSignature)

    def click_status_arrow_button(self):
        self.perform_click(self.btn_toggleStausArrow)

    def send_e_receipt(self, text):
        self.perform_click(self.btn_sendEReceipt)
        self.perform_sendkeys(self.txt_phoneNumberField, text)
        self.perform_click(self.btn_sendEReceipt)
        sleep(1.5)

    def add_signature(self):
        self.perform_click(self.btn_addSignature)
        sleep(3)
        TouchAction(self.driver).press(x=118, y=600).move_to(x=232, y=756).release().perform()
        TouchAction(self.driver).press(x=228, y=739).move_to(x=247, y=566).release().perform()
        TouchAction(self.driver).press(x=241, y=574).move_to(x=127, y=718).release().perform()
        self.perform_click(self.btn_signatureSubmit)
        sleep(0.8)

    def click_filter(self):
        self.perform_click(self.btn_filters)

    def click_void_tarnsaction(self):
        self.perform_click(self.btn_voidTransaction)
        self.perform_click(self.btn_voidTransactionYes)
        self.wait_for_element(self.snp_fetchingChargeSlipMessage)
        self.perform_click(self.btn_skip)
        return self.fetch_text(self.txa_finalStatusField)

    def fetch_auth_code_text(self):
        return self.fetch_text(self.txa_authCode)

    def fetch_txn_id_text(self):
        return self.fetch_text(self.txt_txnID)

    def fetch_txn_status_text(self):
        return str(self.fetch_text(self.txa_finalStatusField))

    def fetch_txn_type_text(self):
        return str(self.fetch_text(self.txt_txnType))

    def fetch_txn_amount_text(self):
        return str(self.fetch_text(self.txt_txnAmount))

    def click_charge_slip(self):
        self.perform_click(self.lnk_chargeSlip)
        return self.fetch_text(self.lbl_receipt)

    def check_receipt_not_shown(self):
        return self.wait_for_element(self.lbl_receiptNotFound)

    def check_transaction_status(self, total_transactions):
        import math
        action = ActionChains(self.driver)
        count = (total_transactions + 1) / 6
        swipe = math.ceil(count)
        li = []
        for i in range(swipe):
            el1 = self.wait_for_all_elements(self.txa_statusField)
            #el1 = self.driver.find_elements()
            for el in range(len(el1)):
                text = el1[el].text
                li.append(text)
            action.drag_and_drop(el1[-1], el1[0]).perform()
        return li

    def click_on_transaction_by_order_id(self, order_id):
        locator = (
        By.XPATH, '//*[@resource-id="com.ezetap.service.demo:id/tvTxnId" and @text="' + order_id + '"]/../..')
        self.perform_click(locator)

    def click_back_Btn_transaction_details(self):
        self.perform_click(self.btn_backTransactionDetails)

    def click_on_second_transaction_by_order_id(self, order_id):
        locator = (
        By.XPATH, '(//*[@resource-id="com.ezetap.service.demo:id/tvTxnId" and @text="' + order_id + '"]/../..)[2]')
        self.perform_click(locator)