from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage


class TransHistoryPage(BasePage):

    lbl_summary = (By.ID, 'com.ezetap.service.demo:id/tvLblSummary')
    btn_backHome = (By.ID, 'com.ezetap.service.demo:id/iVBackArrow')
    btn_backTransactionDetails = (By.ID, "com.ezetap.service.demo:id/ivBackArrow")
    btn_filters = (By.ID, 'com.ezetap.service.demo:id/csFilter')
    lbl_transactions = (By.ID, '//android.widget.TextView[@text = "Transactions"]')
    lbl_noTransactionsAvailable = (By.ID, "com.ezetap.service.demo:id/tv_ErrorMsg")
    txa_amountField = (By.ID, 'com.ezetap.service.demo:id/tvAmount')
    txa_statusField = (By.ID, "com.ezetap.service.demo:id/tvTxnStatus")
    txt_orderIdField = (By.ID, "com.ezetap.service.demo:id/tvOderId")
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
    txa_payment_status_message = (By.ID, "com.ezetap.service.demo:id/tv_PaymentStatus")
    snp_fetchingChargeSlipMessage = (By.XPATH, "//*[contains(@text, 'Fetching Charge-slip')]")
    lnk_chargeSlip = (By.XPATH, "//*[contains(@text,'Click Here')]")
    lbl_receipt = (By.ID, "com.ezetap.service.demo:id/tvAmount")
    lbl_receiptNotFound = (By.XPATH, "//android.view.View[@content-desc='Not Found']")
    txa_authCode = (By.XPATH, "//*[@text='AUTH CODE']/following-sibling::android.widget.TextView")
    btn_toggleStausArrow = (By.ID, 'com.ezetap.service.demo:id/iv_ToggleStatus')
    txt_txnType = (By.ID, "com.ezetap.service.demo:id/tvTransactionType")
    txt_txnID = (By.XPATH, "//*[@text='TRANSACTION ID']/following-sibling::android.widget.TextView")
    txt_txnAmount = (By.ID, "com.ezetap.service.demo:id/tvTxnAmount")
    txt_rrNumber = (By.XPATH, "//*[@text='RR NUMBER']/following-sibling::android.widget.TextView")
    txt_customer_name = (By.XPATH, "//*[@text='CUSTOMER NAME']/following-sibling::android.widget.TextView")
    txt_payer_name = (By.XPATH, "//*[@text='PAYER NAME']/following-sibling::android.widget.TextView")
    txt_settlement_status = (By.XPATH, "//*[@text='SETTLEMENT STATUS']/following-sibling::android.widget.TextView")
    txt_date_time = (By.XPATH, "//*[@text='DATE']/following-sibling::android.widget.TextView")
    txt_batch_number = (By.XPATH, "//*[@text='BATCH NO.']/following-sibling::android.widget.TextView")
    txt_mid = (By.XPATH, "//*[@text='MID']/following-sibling::android.widget.TextView")
    txt_tid = (By.XPATH, "//*[@text='TID']/following-sibling::android.widget.TextView")
    txt_tip_amt = (By.XPATH, "//*[@text='TIP AMOUNT']/following-sibling::android.widget.TextView")
    txt_cash_amt = (By.XPATH, "//*[@text='CASH AMOUNT']/following-sibling::android.widget.TextView")
    txt_sale_amt = (By.XPATH, "//*[@text='SALE AMOUNT']/following-sibling::android.widget.TextView")
    txt_card_type_desc = (By.XPATH, "//*[@text='CARD TXN TYPE DESC']/following-sibling::android.widget.TextView")
    txt_device_serial = (By.XPATH, "//*[@text='REFERENCE NO. 2']/following-sibling::android.widget.TextView")
    btn_void_txn = (By.ID, "com.ezetap.service.demo:id/ll_VoidRefund")
    btn_void_yes = (By.ID, "com.ezetap.service.demo:id/btnPositive")
    btn_void_no = (By.ID, "com.ezetap.service.demo:id/btnNegative")
    btn_rel_pre_auth = (By.ID, "com.ezetap.service.demo:id/btnRelPreAuth")
    btn_confirm_pre_auth = (By.ID, "com.ezetap.service.demo:id/btnCnfPreAuth")
    txt_ref_num_2 = (By.XPATH, "//*[@text='REFERENCE NO. 2']/following-sibling::android.widget.TextView")
    btn_conf_pre_auth_popup = (By.ID, "com.ezetap.service.demo:id/rightButton")
    btn_confirmation = (By.XPATH, "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout[2]/android.widget.EditText")
    txt_payment_msg_field = (By.ID, "com.ezetap.service.demo:id/tv_PaymentStatus")

    def __init__(self, driver):
        super().__init__(driver)

    def get_summary_text(self):
        return self.fetch_text(self.lbl_summary)

    def click_back_Btn(self):
        self.perform_click(self.btn_backHome)

    def click_back_Btn_transaction_details(self):
        self.perform_click(self.btn_backTransactionDetails)

    def click_first_amount_field(self):
        el = self.wait_for_all_elements(self.txa_amountField)
        el[0].click()

    def click_on_transaction_by_order_id(self, order_id: str):
        """
          This method clicks on the search bar in history page and clicks on the transaction on the basis of order_id
          param order_id: str
        """
        locator = (By.ID, 'com.ezetap.service.demo:id/searchView')
        self.perform_click(locator)
        self.perform_sendkeys(locator, order_id)
        locator = (By.ID, 'com.ezetap.service.demo:id/clTxnView')
        self.perform_click(locator)

    def click_on_release_pre_auth(self):
        """
            This method is used to click on rlease pre-auth txn.
        """
        self.perform_click(self.btn_rel_pre_auth)

    def click_on_confirm_pre_auth(self):
        """
            This method is used to click on confirm pre-auth txn.
        """
        self.perform_click(self.btn_confirm_pre_auth)

    def click_on_confirmation_btn_for_amt(self, amount):
        """
            This method is used to click on confirm the amount for pre-auth txn.
        """
        self.perform_click(self.btn_confirmation)
        self.perform_sendkeys(self.btn_confirmation, amount)

    def click_on_conf_pre_auth_popup(self):
        """
            This method is used to click on confirm pre-auth pop ups
        """
        self.perform_click(self.btn_conf_pre_auth_popup)
        self.perform_click(self.btn_conf_pre_auth_popup)

    def click_on_transaction_by_txn_id(self, txn_id):
        locator = (By.ID, 'com.ezetap.service.demo:id/searchView')
        self.perform_click(locator)
        self.perform_sendkeys(locator, txn_id)
        locator = (By.ID, 'com.ezetap.service.demo:id/clTxnView')
        self.perform_click(locator)

    def click_on_second_transaction_by_order_id(self, order_id):
        locator = (By.XPATH, '(//*[@resource-id="com.ezetap.service.demo:id/tvTxnId" and @text="'+order_id+'"]/../..)[2]' )
        self.perform_click(locator)

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

    def fetch_RRN_text(self):
        return self.fetch_text(self.txt_rrNumber)

    def fetch_txn_payment_msg_text(self):
        return str(self.fetch_text(self.txt_payment_msg_field))

    def fetch_settlement_status_text(self):
        return self.fetch_text(self.txt_settlement_status)

    def fetch_txn_status_text(self):
        return str(self.fetch_text(self.txa_finalStatusField))

    def fetch_txn_payment_message_text(self):
        return str(self.fetch_text(self.txa_payment_status_message))

    def fetch_txn_type_text(self):
        return str(self.fetch_text(self.txt_txnType))

    def fetch_order_id_text(self):
        return str(self.fetch_text(self.txt_orderIdField))

    def fetch_txn_amount_text(self):
        return str(self.fetch_text(self.txt_txnAmount))

    def fetch_customer_name_text(self):
        return self.fetch_text(self.txt_customer_name)

    def fetch_payer_name_text(self):
        return self.fetch_text(self.txt_payer_name)

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
            for el in range(len(el1)):
                text = el1[el].text
                li.append(text)
            action.drag_and_drop(el1[-1], el1[0]).perform()
        return li

    def fetch_date_time_text(self):
        return self.fetch_text(self.txt_date_time)

    def fetch_batch_number_text(self):
        return self.fetch_text(self.txt_batch_number)

    def fetch_mid_text(self):
        return self.fetch_text(self.txt_mid)

    def fetch_tid_text(self):
        return self.fetch_text(self.txt_tid)

    def fetch_tip_amt_text(self):
        self.scroll_to_text("TIP AMOUNT")
        return self.fetch_text(self.txt_tip_amt)

    def fetch_cash_amt_text(self):
        self.scroll_to_text("CASH AMOUNT")
        return self.fetch_text(self.txt_cash_amt)

    def fetch_sale_amt_text(self):
        self.scroll_to_text("SALE AMOUNT")
        return self.fetch_text(self.txt_sale_amt)

    def fetch_card_type_desc_text(self):
        return self.fetch_text(self.txt_card_type_desc)

    def click_on_void_card_txn(self):
        self.perform_click(self.btn_void_txn)
        self.perform_click(self.btn_void_yes)

    def fetch_device_serial_text(self) -> str:
        """
        This method is used to fetch device serial number on transaction history page.
        return: device_serial: str
        """
        return self.fetch_text(self.txt_ref_num_2)
