import time

import pyautogui
from selenium.webdriver.common.by import By
from PageFactory.Portal_BasePage import BasePage
from Utilities import ConfigReader


class remotePayTxnPage(BasePage):
    txt_creditCardClickAndExpand = (By.XPATH, "//mat-panel-title[contains(text(),'Credit Card')]")
    txt_NameOnCard = (By.XPATH, "//input[@placeholder='Name on Card']")
    txt_cardNumber = (By.XPATH, "//input[@placeholder='Card number']")
    txt_cardExpiryMonth = (By.XPATH, "//*[@id='cdk-accordion-child-0']/div/div/div[3]/div/select")
    txt_cardExpiryYear = (By.XPATH, "//*[@id='cdk-accordion-child-0']/div/div/div[4]/div/select")
    txt_cardCvv = (By.XPATH, "//input[@placeholder='Enter CVV']")
    btn_proceedToPay = (By.XPATH, "//button[contains(text(),'Proceed to pay')]")
    btn_submitButton = (By.XPATH, "//input[@value='Submit']")
    btn_successMessage = (By.XPATH, "//h3[contains(text(),'Your payment is successfully completed! You may cl')]")
    txt_failedMessage = (By.XPATH, "//h3[contains(text(),'Sorry! Your payment could not be processed. Please')]")
    txt_successMessage = (By.XPATH, "//h3[contains(text(),'Your payment is successfully completed! You may cl')]")
    txt_timeoutMessage = (By.XPATH, "")

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
        self.perform_click_cnp(self.txt_creditCardClickAndExpand)

    def enterNameOnTheCard(self,value):
        self.perform_click_cnp(self.txt_NameOnCard)
        self.perform_sendkeys(self.txt_NameOnCard, value)

    def enterCreditCardNumber(self, value):
        self.perform_sendkeys(self.txt_cardNumber, value)

    def enterCreditCardExpiryMonth(self, value):
        self.select_from_drop_down(self.txt_cardExpiryMonth, value)

    def enterCreditCardExpiryYear(self, value):
        self.select_from_drop_down(self.txt_cardExpiryYear,value)

    def enterCreditCardCvv(self, value):
        self.perform_sendkeys(self.txt_cardCvv, value)

    def clickOnProceedToPay(self):
        self.perform_click_cnp(self.btn_proceedToPay)

    def clickOnSubmitButton(self):
        self.perform_click_cnp(self.btn_submitButton)

    def succcessScreenMessage(self):
        self.fetch_text(self.txt_successMessage)

    def failedScreenMessage(self):
        self.fetch_text(self.txt_failedMessage)

    def timeoutScreenMessage(self):
        self.fetch_text(self.txt_timeoutMessage)

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

