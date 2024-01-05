from selenium.webdriver.common.by import By
from PageFactory.merchant_portal.portal_base_page import BasePage


class RemotePayTxnPage(BasePage):
    btn_creditCardClickAndExpand = "//mat-panel-title[contains(text(),'Credit Card')]"
    lbl_NameOnCard = "//input[@placeholder='Name on Card']"
    lbl_cardNumber = "//input[@placeholder='Card number']"
    ddl_cardExpiryMonth = "//*[@id='cdk-accordion-child-0']/div/div/div[3]/div/select"
    ddl_cardExpiryYear = "//*[@id='cdk-accordion-child-0']/div/div/div[4]/div/select"
    lbl_cardCvv = "//input[@placeholder='Enter CVV']"

    btn_debitClickAndExpand = "//mat-panel-title[contains(text(),'Debit Card')]"
    # ddl_debitCardExpiryMonth = (By.XPATH, "//body/my-app[1]/div[1]/div[1]/div[1]/div[1]/mat-accordion[1]/div[
    # 1]/div[2]/mat-expansion-panel[1]/div[1]/div[1]/div[1]/div[3]/div[1]/select[1]")
    ddl_debitCardExpiryMonth = "//*[@id='cdk-accordion-child-1']//div/div[3]/div/select"
    ddl_debitCardExpiryYear = "//*[@id='cdk-accordion-child-1']//div/div[4]/div/select"
    # ddl_debitCardExpiryYear = (By.XPATH, "//body/my-app[1]/div[1]/div[1]/div[1]/div[1]/mat-accordion[1]/div[1]/div[
    # 2]/mat-expansion-panel[1]/div[1]/div[1]/div[1]/div[4]/div[1]/select[1]")

    btn_proceedToPay = "//button[contains(text(),'Proceed to pay')]"
    btn_submitButton = "//input[@value='Submit']"
    btn_successMessage = "//h3[contains(text(),'Your payment is successfully completed! You may cl')]"
    # btn_successMessage = "//h3[contains(text(),'Your payment was successful. You may close the bro')]"
    # txt_failedMessage = (By.XPATH, "//h3[contains(text(),'Sorry! Your payment could not be processed. Please')]")
    # txt_timeoutMessage = (By.XPATH, "//h3[contains(text(),'Your payment attempt failed, Sorry for the inconve')]")
    txt_timeoutMessage = "//h3[contains(text(),'Sorry! Your payment could not be processed. Any am')]"
    # txt_expiryMessage = (By.XPATH,"//h3[contains(text(),'Sorry!You have exceeded the time available to comp')]")
    txt_expiryMessage = "//h3[contains(text(),'Remote payment link has expired, Use a different m')]"
    txt_maxAttempts = "//h3[contains(text(),'Maximum number of attempts for this url exceeded. ')]"

    txt_failedMessage = "//h3[contains(text(), 'Your payment attempt failed, Sorry for the inconve')]"
    btn_remotePayUpi = "//mat-panel-title[contains(text(),'UPI')]"
    btn_remotePayLaunchUpi = "//button[contains(text(),'Launch a UPI app ')]"
    btn_remotePayCancelUpi = "//button[@data-target='#confirmCancel']"
    btn_remotePayProceed = "//button[contains(text(),'Proceed')]"

    btn_remotePayUpiCollectLaunch = "//label[contains(text(),'Pay by UPI ID')]"
    btn_remotePayUpiCollectAppSelect = "//div[@id='googlepay']"
    txt_remotePayUpiCollectId = "#inputCollect"
    dropdown_remotePayUpiCollectSelectBank = "//select[@id='upiHandles']"
    btn_remotePayUpiCollectVpaValidation = "//b[contains(text(),'Verify')]"
    btn_remotePayUpiCollectProceed = "//button[@class='btn button-orange btn-block']"

    btn_netbanking = "//mat-panel-title[contains(text(),'Net Banking')]"
    btn_click_netbanking = "select"
    # btn_select_netbanking = "//option[@value='470']"
    btn_select_netbanking = "470"
    btn_proceed_netbanking = "//button[contains(text(),'Proceed to pay')]"
    # btn_netbanking_customerId = "cid"
    btn_netbanking_customerId = "//*[@name='cid']"
    # btn_netbanking_customerpwd = "pwd"
    btn_netbanking_customerpwd = "//*[@name='pwd']"
    btn_netbanking_proceed = "proceed"
    btn_netbanking_cancel = (By.NAME, "cancel")

    txt_otp_field = "//input[@placeholder='OTP']"
    btn_submit_otp = "//button[@type='submit']"
    btn_failure = "//button[text()='Failure']"
    btn_success = "//button[text()='Success']"
    txt_failure_msg = "//*[@id='page-wrapper']/div/div/div/div/h3/text()"
    lbl_input_debit_card_num = "//input[@placeholder='Card number']"
    btn_select_netbanking_Rzp = "AU Small Finance Bank"

    def __init__(self, page):
        super().__init__(page)

    def remote_pay_netbanking(self):
        self.perform_click_cnp(self.btn_netbanking)

    def remote_pay_click_and_expand_netbanking(self):
        self.perform_click_cnp(self.btn_click_netbanking)

    def remote_pay_select_netbanking(self):
        self.select_from_drop_down_combobox(self.btn_select_netbanking)

    def remote_pay_proceed_netbanking(self):
        self.perform_click_cnp(self.btn_proceed_netbanking)

    def remote_pay_netbanking_customerId(self, value):
        self.perform_fill(self.btn_netbanking_customerId, value)

    def remote_pay_netbanking_customerpwd(self, value):
        self.perform_fill(self.btn_netbanking_customerpwd, value)

    def remote_pay_netbanking_proceed(self):
        self.click_submit_button()

    def remote_pay_netbanking_cancel(self):
        self.perform_click_cnp(self.btn_netbanking_cancel)

    def clickOnCreditCardToExpand(self):
        self.perform_click_cnp(self.btn_creditCardClickAndExpand)

    def enterNameOnTheCard(self, value):
        self.perform_click_cnp(self.lbl_NameOnCard)
        self.perform_fill(self.lbl_NameOnCard, value)

    def enterCreditCardNumber(self, value):
        self.perform_fill(self.lbl_cardNumber, value)

    def enterCreditCardExpiryMonth(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryMonth, value)

    def enterCreditCardExpiryYear(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryYear, value)

    def enterCreditCardCvv(self, value):
        self.perform_fill(self.lbl_cardCvv, value)

    def clickOnProceedToPay(self):
        self.perform_click_cnp(self.btn_proceedToPay)

    def clickOnSubmitButton(self):
        self.perform_click_cnp(self.btn_submitButton)

    def wait_for_success_message(self):
        self.wait_for_element(self.btn_successMessage)

    def succcessScreenMessage(self):
        return self.fetch_text(self.btn_successMessage)

    def expiryMessage(self):
        return self.fetch_text(self.txt_expiryMessage)

    def failedScreenMessage(self):
        return self.fetch_text(self.txt_failedMessage)

    def timeoutScreenMessage(self):
        return self.fetch_text(self.txt_timeoutMessage)

    def maxAttemptsMessage(self):
        return self.fetch_text(self.txt_maxAttempts)

    def clickOnRemotePayUPI(self):
        self.perform_click_cnp(self.btn_remotePayUpi)

    def clickOnRemotePayLaunchUPI(self):
        self.perform_click_cnp(self.btn_remotePayLaunchUpi)

    def clickOnRemotePayCancelUPI(self):
        self.perform_click_cnp(self.btn_remotePayCancelUpi)

    def clickOnRemotePayProceed(self):
        self.perform_click_cnp(self.btn_remotePayProceed)

    def clickOnRemotePayUpiCollect(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectLaunch)

    def clickOnRemotePayUpiCollectAppSelection(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectAppSelect)

    def clickOnRemotePayUpiCollectId(self, value):
        self.perform_fill(self.txt_remotePayUpiCollectId, value)

    def clickOnRemotePayUpiCollectDropDown(self, value):
        self.select_from_drop_down(self.dropdown_remotePayUpiCollectSelectBank, value)

    def clickOnRemotePayUpiCollectVpaValidation(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectVpaValidation)

    def clickOnRemotePayUpiCollectProceed(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectProceed)

    def clickOnDebitCardToExpand(self):
        self.perform_click_cnp(self.btn_debitClickAndExpand)

    def enterDebitCardExpiryMonth(self, value):
        self.select_from_drop_down(self.ddl_debitCardExpiryMonth, value)

    def enterDebitCardExpiryYear(self, value):
        self.select_from_drop_down(self.ddl_debitCardExpiryYear, value)

    def waitForExpiryElement(self):
        self.wait_for_element(self.txt_expiryMessage)

    def waitForTimeoutElement(self):
        self.wait_for_element(self.txt_timeoutMessage)

    def wait_for_failed_message(self):
        self.wait_for_element(self.txt_failedMessage)

    def enter_otp(self, otp):
        self.wait_for_element(self.txt_otp_field)
        self.perform_fill(self.txt_otp_field, otp)

    def submit_otp(self):
        self.wait_for_element(self.btn_submit_otp)
        self.perform_click_cnp(self.btn_submit_otp)

    def click_failure_pmt_btn(self):
        self.wait_for_element(self.btn_failure)
        self.perform_click(self.btn_failure)

    def fetch_failure_message(self):
        self.wait_for_element(self.txt_failure_msg)
        self.fetch_text(self.txt_failure_msg)

    def click_success_pmt_btn(self):
        self.wait_for_element(self.btn_success)
        self.perform_click(self.btn_success)

    def remote_pay_select_netbanking_Rzp(self):
        self.select_from_drop_down_combobox(self.btn_select_netbanking_Rzp)

    def enter_debit_card_number(self, value):
        self.perform_fill(self.lbl_input_debit_card_num, value)

    def enter_debit_card_cvv(self, value):
        self.perform_fill(self.lbl_cardCvv, value)