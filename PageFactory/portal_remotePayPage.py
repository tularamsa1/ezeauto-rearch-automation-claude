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


    def __init__(self, driver):
        super().__init__(driver)

    def clickOnCreditCardToExpand(self):
        # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
        # self.driver.get(url)
        # self.driver.maximize_window()
        self.perform_click(self.txt_creditCardClickAndExpand)

    def enterNameOnTheCard(self,value):
        self.perform_click(self.txt_NameOnCard)
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
        self.perform_click(self.btn_proceedToPay)

    def clickOnSubmitButton(self):
        self.perform_click(self.btn_submitButton)

    def succcessScreenMessage(self):
        self.fetch_text(self.txt_successMessage)

    def failedScreenMessage(self):
        self.fetch_text(self.txt_failedMessage)

    def timeoutScreenMessage(self):
        self.fetch_text(self.txt_timeoutMessage)

    def clikOnRemotePayUPI(self):
        self.perform_click(self.btn_remotePayUpi)

    def clikOnRemotePayLaunchUPI(self):
        self.perform_click(self.btn_remotePayLaunchUpi)

    def clikOnRemotePayCancelUPI(self):
        self.perform_click(self.btn_remotePayCancelUpi)

    def clikOnRemotePayProceed(self):
        self.perform_click(self.btn_remotePayProceed)

