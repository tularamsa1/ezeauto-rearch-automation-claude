import time

#import pyautogui
from selenium.webdriver.common.by import By
from PageFactory.Portal_BasePage import BasePage
from Utilities import ConfigReader


class remotePayTxnPage(BasePage):
    btn_creditCardClickAndExpand = (By.XPATH, "//mat-panel-title[contains(text(),'Credit Card')]")
    lbl_NameOnCard = (By.XPATH, "//input[@placeholder='Name on Card']")
    lbl_cardNumber = (By.XPATH, "//input[@placeholder='Card number']")
    ddl_cardExpiryMonth = (By.XPATH, "//*[@id='cdk-accordion-child-0']/div/div/div[3]/div/select")
    ddl_cardExpiryYear = (By.XPATH, "//*[@id='cdk-accordion-child-0']/div/div/div[4]/div/select")
    lbl_cardCvv = (By.XPATH, "//input[@placeholder='Enter CVV']")

    btn_debitClickAndExpand = (By.XPATH, "//mat-panel-title[contains(text(),'Debit Card')]")
    ddl_debitCardExpiryMonth = (By.XPATH, "//body/my-app[1]/div[1]/div[1]/div[1]/div[1]/mat-accordion[1]/div[1]/div[2]/mat-expansion-panel[1]/div[1]/div[1]/div[1]/div[3]/div[1]/select[1]")
    ddl_debitCardExpiryYear = (By.XPATH, "//body/my-app[1]/div[1]/div[1]/div[1]/div[1]/mat-accordion[1]/div[1]/div[2]/mat-expansion-panel[1]/div[1]/div[1]/div[1]/div[4]/div[1]/select[1]")


    btn_proceedToPay = (By.XPATH, "//button[contains(text(),'Proceed to pay')]")
    btn_submitButton = (By.XPATH, "//input[@value='Submit']")
    btn_successMessage = (By.XPATH, "//h3[contains(text(),'Your payment is successfully completed! You may cl')]")
    # txt_failedMessage = (By.XPATH, "//h3[contains(text(),'Sorry! Your payment could not be processed. Please')]")
    # txt_timeoutMessage = (By.XPATH, "//h3[contains(text(),'Your payment attempt failed, Sorry for the inconve')]")
    txt_timeoutMessage = (By.XPATH, "//h3[contains(text(),'Sorry! Your payment could not be processed. Any am')]")
    # txt_expiryMessage = (By.XPATH,"//h3[contains(text(),'Sorry!You have exceeded the time available to comp')]")
    txt_expiryMessage = (By.XPATH,"//h3[contains(text(),'Remote payment link has expired, Use a different m')]")
    txt_maxAttempts = (By.XPATH,"//h3[contains(text(),'Maximum number of attempts for this url exceeded. ')]")

    txt_failedMessage = (By.XPATH,"// h3[contains(text(), 'Your payment attempt failed, Sorry for the inconve')]")
    btn_remotePayUpi = (By.XPATH,"//mat-panel-title[contains(text(),'UPI')]")
    btn_remotePayLaunchUpi = (By.XPATH,"//button[contains(text(),'Launch a UPI app ')]")
    btn_remotePayCancelUpi = (By.XPATH,"//button[@data-target='#confirmCancel']")
    btn_remotePayProceed = (By.XPATH,"//button[contains(text(),'Proceed')]")

    btn_remotePayUpiCollectLaunch = (By.XPATH,"//label[contains(text(),'Pay by UPI ID')]")
    btn_remotePayUpiCollectAppSelect = (By.XPATH, "//div[@id='googlepay']")
    txt_remotePayUpiCollectId = (By.CSS_SELECTOR, "#inputCollect")
    dropdown_remotePayUpiCollectSelectBank = (By.XPATH, "//select[@id='upiHandles']")
    btn_remotePayUpiCollectVpaValidation = (By.XPATH, "//b[contains(text(),'Verify')]")
    btn_remotePayUpiCollectProceed = (By.XPATH, "//button[@class='btn button-orange btn-block']")


    def __init__(self, driver):
        super().__init__(driver)

    def clickOnCreditCardToExpand(self):
        # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
        # self.driver.get(url)
        # self.driver.maximize_window()
        self.perform_click_cnp(self.btn_creditCardClickAndExpand)

    def enterNameOnTheCard(self,value):
        self.perform_click_cnp(self.lbl_NameOnCard)
        self.perform_sendkeys(self.lbl_NameOnCard, value)

    def enterCreditCardNumber(self, value):
        self.perform_sendkeys(self.lbl_cardNumber, value)

    def enterCreditCardExpiryMonth(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryMonth, value)

    def enterCreditCardExpiryYear(self, value):
        self.select_from_drop_down(self.ddl_cardExpiryYear,value)

    def enterCreditCardCvv(self, value):
        self.perform_sendkeys(self.lbl_cardCvv, value)

    def clickOnProceedToPay(self):
        self.perform_click_cnp(self.btn_proceedToPay)

    def clickOnSubmitButton(self):
        self.perform_click_cnp(self.btn_submitButton)

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
        self.perform_sendkeys(self.txt_remotePayUpiCollectId, value)

    def clickOnRemotePayUpiCollectDropDown(self, value):
        self.select_from_drop_down(self.dropdown_remotePayUpiCollectSelectBank, value)

    def clickOnRemotePayUpiCollectVpaValidation(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectVpaValidation)

    def clickOnRemotePayUpiCollectProceed(self):
        self.perform_click_cnp(self.btn_remotePayUpiCollectProceed)

    def clickOnDebitCardToExpand(self):
        self.perform_click_cnp(self.btn_debitClickAndExpand)

    def enterDebitCardExpiryMonth(self,value):
        self.select_from_drop_down(self.ddl_debitCardExpiryMonth, value)

    def enterDebitCardExpiryYear(self,value):
        self.select_from_drop_down(self.ddl_debitCardExpiryYear,value)

    def waitForExpiryElement(self):
        self.wait_for_visibility_of_Element(self.txt_expiryMessage)

    def waitForTimeoutElement(self):
        self.wait_for_visibility_of_Element(self.txt_timeoutMessage)

    def wait_for_failed_message(self):
        self.wait_for_element(self.txt_failedMessage)


