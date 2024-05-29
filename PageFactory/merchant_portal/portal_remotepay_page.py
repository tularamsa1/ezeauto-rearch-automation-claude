import json

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

    # below locator are for emi on cnp flow
    lbl_card_number = '//*[@id="card-number"]'
    lbl_expiry_month = '// *[ @ id = "valid-through-expiry-month"]'
    lbl_expiry_year = '//*[@id="valid-through-expiry-year"]'
    lbl_cvv = '//*[@id="valid-through-cvv"]'
    lbl_name_on_card = '//app-emi-options-landing-page/div/div[1]/app-card-details/div/div/div[3]/input'
    btn_proceed = "//button[text()='Proceed']"
    btn_three_months_emi_plan = '//p[normalize-space(text()="3 EMI")]'
    btn_six_months_emi_plan = '//p[normalize-space(text()="6 EMI")]'
    btn_nine_months_emi_plan = '//p[normalize-space(text()="9 EMI")]'
    btn_twelve_months_emi_plan = '//p[normalize-space(text()="12 EMI")]'
    txt_warning_msg = "//h3[@class='message-title']"
    iframe_cybsource = "css=[id^='cardinal-stepUpIframe-']"
    btn_cyberSourceSubmitButton = "//input[@value='SUBMIT']"

    txt_otp_field = "//input[@placeholder='OTP']"
    btn_submit_otp = "//button[@type='submit']"
    btn_failure = "//button[text()='Failure']"
    btn_success = "//button[text()='Success']"
    txt_failure_msg = "//*[@id='page-wrapper']/div/div/div/div/h3/text()"
    lbl_input_debit_card_num = "//input[@placeholder='Card number']"
    btn_select_netbanking_Rzp = "AU Small Finance Bank"

    txn_invalid_debit_card_message = "//div[@role='alert']"
    txn_invalid_credit_card_message = "//div[@role='alert']"
    text_json = "//pre[contains(text(),'{')]"
    text_card_err_msg = "//h3[contains(text(),'Card Not Supported.')]"
    txt_no_active_pmt_method = "//h3[contains(text(),'No active payment method found for {0}.Sorry for t')]"

    txt_totalAmountValue = "//span[@class='totalAmount']"
    txt_serviceFeeValue = "//span[@class='serviceFeeAmount']"
    txt_orderAmountValue = "//span[@class='amount']"
    txt_serviceFeeConfigErrorMessage = "//div[contains(@aria-label, 'An error occured. Please try another payment method or contact')]"
    btn_failureMessage = "//h3[contains(text(),'Your payment attempt failed, Sorry for the inconve')]"
    btn_failureMessageMaxAttempt = "//h3[contains(text(),'Maximum number of attempts for this url exceeded. Pleas')]"
    btn_messageAfterSuccessTxn = "//h3[contains(text(),'The transaction has been completed already! Pl')]"
    btn_successButton = "//button[contains(text(),'Success')]"
    txt_in_progress_message = "//h3[contains(text(),'Transaction for the Reference Number:')]"

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

    def enter_card_details_emi(self, card_number: str, expiry_month: str, expiry_year: str, cvv: str, name_on_card: str):
        """
        This method is used to enter card details for EMI on CNP flow
        param: card_number str
        param: expiry_month str
        param: expiry_year str
        param: cvv str
        param: name_on_card str
        """
        self.perform_fill(self.lbl_card_number, card_number)
        self.perform_fill(self.lbl_expiry_month, expiry_month)
        self.perform_fill(self.lbl_expiry_year, expiry_year)
        self.perform_fill(self.lbl_cvv, cvv)
        self.perform_fill(self.lbl_name_on_card, name_on_card)

    def click_on_proceed(self):
        """
        This method is used to click on proceed button
        """
        self.wait_for_element(self.btn_proceed)
        self.perform_click(self.btn_proceed)

    def select_emi_plan(self, emi_plan_in_months: int):
        """
        This method is used to select emi plan
        param: emi_plan_in_months int
        """
        if emi_plan_in_months == 3:
            self.perform_click(self.btn_three_months_emi_plan)
        elif emi_plan_in_months == 6:
            self.perform_click(self.btn_six_months_emi_plan)
        elif emi_plan_in_months == 9:
            self.perform_click(self.btn_nine_months_emi_plan)
        elif emi_plan_in_months == 12:
            self.perform_click(self.btn_twelve_months_emi_plan)
        else:
            raise Exception("Preferred emi plan is invalid")

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

    def switch_to_iframe(self):
        """Below method is used to pass the iframe locator path to switch the context to iframe"""
        iframe_element = self.page.frame_locator(self.iframe_cybsource)
        iframe_element.get_by_placeholder(" Enter Code Here").fill("1234")
        iframe_element.locator(self.btn_cyberSourceSubmitButton).click()

    def fetch_credit_card_payment_mode_text(self) -> str:
        """
        This method is used to fetch credit card text from browser.
        return: Credit Card: str
        """
        return self.fetch_text(self.btn_creditCardClickAndExpand)

    def fetch_debit_card_payment_mode_text(self) -> str:
        """
        This method is used to fetch debit card text from browser.
        return: Debit Card: str
        """
        return self.fetch_text(self.btn_debitClickAndExpand)

    def fetch_upi_payment_mode_text(self) -> str:
        """
        This method is used to fetch upi text from browser.
        return: UPI: str
        """
        return self.fetch_text(self.btn_remotePayUpi)

    def fetch_net_banking_payment_mode_text(self) -> str:
        """
        This method is used to fetch net banking text from browser.
        return: Net Banking: str
        """
        return self.fetch_text(self.btn_netbanking)

    def fetch_warning_msg_txt(self) -> str:
        """
        This method is used to fetch warning msg text from browser.
        return: warning msg : str
        """
        return self.fetch_text(self.txt_warning_msg)

    def is_credit_debit_netbanking_and_upi_visible(self, loc) -> str:
        """
        This method is used to check invisiblity of credit, debit, netbanking & UPI payment mode from browser.
        return: Credit: str
        """
        locator = "//mat-panel-title[contains(text(),'Credit Card')]"
        return self.wait_for_element_invisible(locator)

    def invalid_debit_card_error_message(self):
        return self.fetch_text(self.txn_invalid_debit_card_message)

    def invalid_credit_card_error_message(self):
        return self.fetch_text(self.txn_invalid_credit_card_message)

    def fetch_json(self):
        fetched_json = self.fetch_text(self.text_json)
        fetched_json = json.loads(fetched_json)
        return fetched_json

    def fetch_card_not_supported_message(self):
        return self.fetch_text(self.text_card_err_msg)

    def select_bank_from_list(self, bank_name):
        self.select_from_drop_down_combobox(bank_name)

    def fetch_no_active_pmt_method_message(self):
        return self.fetch_text(self.txt_no_active_pmt_method)

    def enter_debit_expiry_month_debit_only(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryMonth, value)

    def enter_debit_expiry_year_debit_only(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryYear, value)

    def clickOnSuccessBtn(self):
        self.perform_click_cnp(self.btn_successButton)

    def failureScreenMessage(self):
        return self.fetch_text(self.btn_failureMessage)

    def failureScreenMessageMaxAttempt(self):
        return self.fetch_text(self.btn_failureMessageMaxAttempt)

    def messageAfterSuccessTxn(self):
        return self.fetch_text(self.btn_messageAfterSuccessTxn)

    def fetch_service_fee(self):
        return self.fetch_text(self.txt_serviceFeeValue)

    def fetch_order_amount(self):
        return self.fetch_text(self.txt_orderAmountValue)

    def fetch_total_amount(self):
        return self.fetch_text(self.txt_totalAmountValue)

    def wait_for_success_btn(self):
        """
        This method is used to wait till success btn is visible in browser.
        """
        self.wait_for_element(self.btn_success)

    def in_progress_screen_message(self) -> str:
        """
        This method is used to fetch progress msg text from browser.
        return: progress msg: str
        """
        return self.fetch_text(self.txt_in_progress_message)

    def serviceFeeConfigErrorMessage(self):
        """
        This method is used to fetch serviceFee config error message from browser.
        return: serviceFee config error message msg: str
        """
        return self.fetch_text(self.txt_serviceFeeConfigErrorMessage)

    def remote_pay_select_netbanking_bank_select(self, bank):
        """
        This method is used to select netbanking bank from dropdown
        """
        self.select_from_drop_down_combobox(bank)


