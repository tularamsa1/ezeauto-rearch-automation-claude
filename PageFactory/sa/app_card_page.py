from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage


class CardPage(BasePage):

    CTLS_VISA_DEBIT_476173 = (By.XPATH, "//android.widget.TextView[@text='CTLS_VISA_DEBIT_476173']")
    CTLS_WITH_PIN_VISA_DEBIT_476173 = (By.XPATH, "//android.widget.TextView[@text='CTLS_WITH_PIN_VISA_DEBIT_476173']")
    CTLS_MASTER_DEBIT_222360 = (By.XPATH, "//android.widget.TextView[@text='CTLS_MASTER_DEBIT_222360']")
    CTLS_WITH_PIN_MASTER_DEBIT_222360 = (By.XPATH, "//android.widget.TextView[@text='CTLS_WITH_PIN_MASTER_DEBIT_222360']")
    CTLS_RUPAY_DEBIT_608326 = (By.XPATH, "//android.widget.TextView[@text='CTLS_RUPAY_DEBIT_608326']")
    CTLS_WITH_PIN_RUPAY_DEBIT_608326 = (By.XPATH, "//android.widget.TextView[@text='CTLS_WITH_PIN_RUPAY_DEBIT_608326']")
    CTLS_VISA_CREDIT_417666 = (By.XPATH, "//android.widget.TextView[@text='CTLS_VISA_CREDIT_417666']")
    CTLS_MASTER_CREDIT_541333 = (By.XPATH, "//android.widget.TextView[@text='CTLS_MASTER_CREDIT_541333']")
    CTLS_WITH_PIN_VISA_CREDIT_417666 = (By.XPATH, "//android.widget.TextView[@text='CTLS_WITH_PIN_VISA_CREDIT_417666']")
    CTLS_WITH_PIN_MASTER_CREDIT_541333 = (By.XPATH, "//android.widget.TextView[@text='CTLS_WITH_PIN_MASTER_CREDIT_541333']")
    EMV_WITH_PIN_VISA_DEBIT_428090 = (By.XPATH, "//android.widget.TextView[@text='EMV_WITH_PIN_VISA_DEBIT_428090']")
    EMV_WITH_PIN_RUPAY_DEBIT_608326 = (By.XPATH, "//android.widget.TextView[@text='EMV_WITH_PIN_RUPAY_DEBIT_608326']")
    EMV_VISA_DEBIT_476173 = (By.XPATH, "//android.widget.TextView[@text='EMV_VISA_DEBIT_476173']")
    EMV_MASTER_DEBIT_222360 = (By.XPATH, "//android.widget.TextView[@text='EMV_MASTER_DEBIT_222360']")
    EMV_RUPAY_DEBIT_608326 = (By.XPATH, "//android.widget.TextView[@text='EMV_RUPAY_DEBIT_608326']")
    EMV_WITH_PIN_VISA_CREDIT_417666 = (By.XPATH, "//android.widget.TextView[@text='EMV_WITH_PIN_VISA_CREDIT_417666']")
    EMV_WITH_PIN_MASTER_CREDIT_541333 = (By.XPATH, "//android.widget.TextView[@text='EMV_WITH_PIN_MASTER_CREDIT_541333']")
    EMV_VISA_CREDIT_417666 = (By.XPATH, "//android.widget.TextView[@text='EMV_VISA_CREDIT_417666']")
    EMV_MASTER_CREDIT_541333 = (By.XPATH, "//android.widget.TextView[@text='EMV_MASTER_CREDIT_541333']")

    txt_error_code = (By.ID, "com.ezetap.service.demo:id/dialogTitle")
    txt_error_message = (By.ID, "com.ezetap.service.demo:id/dialogText")
    btn_error_confirm = (By.ID, "com.ezetap.service.demo:id/rightButton")

    def __init__(self, driver):
        super().__init__(driver)

    def select_cardtype(self, text):
        print("Preferred card type is ", text)
        self.scroll_to_text(text)
        if text == "CTLS_VISA_CREDIT_417666":
            self.perform_long_press(self.CTLS_VISA_CREDIT_417666)
        elif text == "CTLS_WITH_PIN_VISA_CREDIT_417666":
            self.perform_long_press(self.CTLS_WITH_PIN_VISA_CREDIT_417666)
        elif text == "CTLS_MASTER_CREDIT_541333":
            self.perform_long_press(self.CTLS_MASTER_CREDIT_541333)
        elif text == "CTLS_WITH_PIN_MASTER_CREDIT_541333":
            self.perform_long_press(self.CTLS_WITH_PIN_MASTER_CREDIT_541333)
        elif text == "CTLS_VISA_DEBIT_476173":
            self.perform_long_press(self.CTLS_VISA_DEBIT_476173)
        elif text == "CTLS_WITH_PIN_VISA_DEBIT_476173":
            self.perform_long_press(self.CTLS_WITH_PIN_VISA_DEBIT_476173)
        elif text == "CTLS_MASTER_DEBIT_222360":
            self.perform_long_press(self.CTLS_MASTER_DEBIT_222360)
        elif text == "CTLS_RUPAY_DEBIT_608326":
            self.perform_long_press(self.CTLS_RUPAY_DEBIT_608326)
        elif text == "CTLS_WITH_PIN_MASTER_DEBIT_222360":
            self.perform_long_press(self.CTLS_WITH_PIN_MASTER_DEBIT_222360)
        elif text == "CTLS_WITH_PIN_RUPAY_DEBIT_608326":
            self.perform_long_press(self.CTLS_WITH_PIN_RUPAY_DEBIT_608326)
        elif text == "EMV_WITH_PIN_VISA_DEBIT_428090":
            self.perform_long_press(self.EMV_WITH_PIN_VISA_DEBIT_428090)
        elif text == "EMV_WITH_PIN_RUPAY_DEBIT_608326":
            self.perform_long_press(self.EMV_WITH_PIN_RUPAY_DEBIT_608326)
        elif text == "EMV_VISA_DEBIT_476173":
            self.perform_long_press(self.EMV_VISA_DEBIT_476173)
        elif text == "EMV_MASTER_DEBIT_222360":
            self.perform_long_press(self.EMV_MASTER_DEBIT_222360)
        elif text == "EMV_RUPAY_DEBIT_608326":
            self.perform_long_press(self.EMV_RUPAY_DEBIT_608326)
        elif text == "EMV_WITH_PIN_VISA_CREDIT_417666":
            self.perform_long_press(self.EMV_WITH_PIN_VISA_CREDIT_417666)
        elif text == "EMV_WITH_PIN_MASTER_CREDIT_541333":
            self.perform_long_press(self.EMV_WITH_PIN_MASTER_CREDIT_541333)
        elif text == "EMV_VISA_CREDIT_417666":
            self.perform_long_press(self.EMV_VISA_CREDIT_417666)
        elif text == "EMV_MASTER_CREDIT_541333":
            self.perform_long_press(self.EMV_MASTER_CREDIT_541333)

        else:
            raise Exception("Preferred card is invalid")

    def fetch_error_code_text(self):
        return str(self.fetch_text(self.txt_error_code))

    def fetch_error_message_text(self):
        return str(self.fetch_text(self.txt_error_message))

    def click_on_ok_error_msg(self):
        self.perform_click(self.btn_error_confirm)
