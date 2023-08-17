from selenium.webdriver.common.by import By
from PageFactory.mpos.App_BasePage import BasePage


class CardPage(BasePage):

    FDC_EMVCTLS_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='FDC_EMVCTLS_CREDIT_MASTER']")
    FDC_EMVCTLS_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='FDC_EMVCTLS_CREDIT_VISA']")
    FDC_EMVCTLS_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='FDC_EMVCTLS_DEBIT_RUPAY']")
    FDC_EMVCTLS_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='FDC_EMVCTLS_DEBIT_MASTER']")
    FDC_EMVCTLS_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='FDC_EMVCTLS_CREDIT_RUPAY']")
    FDC_EMV_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='FDC_EMV_DEBIT_MASTER']")
    FDC_EMV_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='FDC_EMV_DEBIT_VISA']")
    FDC_EMV_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='FDC_EMV_CREDIT_VISA']")
    FDC_EMV_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='FDC_EMV_CREDIT_MASTER']")

    PRIZMV2_EMVCTLS_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMVCTLS_DEBIT_VISA']")
    PRIZMV2_EMVCTLS_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMVCTLS_CREDIT_MASTER']")
    PRIZMV2_EMVCTLS_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMVCTLS_CREDIT_VISA']")
    PRIZMV2_EMV_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMV_DEBIT_RUPAY']")
    PRIZMV2_EMV_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMV_CREDIT_RUPAY']")
    PRIZMV2_EMV_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='PRIZMV2_EMV_DEBIT_VISA']")

    ATOS_TLE_EMVCTLS_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMVCTLS_CREDIT_MASTER']")
    ATOS_TLE_EMVCTLS_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMVCTLS_CREDIT_VISA']")
    ATOS_TLE_EMVCTLS_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMVCTLS_DEBIT_MASTER']")
    ATOS_TLE_EMVCTLS_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMVCTLS_DEBIT_VISA']")
    ATOS_TLE_EMV_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMV_CREDIT_VISA']")
    ATOS_TLE_EMV_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMV_CREDIT_RUPAY']")
    ATOS_TLE_EMV_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMV_DEBIT_RUPAY']")
    ATOS_TLE_EMV_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='ATOS_TLE_EMV_DEBIT_VISA']")

    HDFC_EMVCTLS_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMVCTLS_DEBIT_RUPAY']")
    HDFC_EMVCTLS_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMVCTLS_DEBIT_MASTER']")
    HDFC_EMVCTLS_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMVCTLS_CREDIT_RUPAY']")
    HDFC_EMVCTLS_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMVCTLS_CREDIT_VISA']")
    HDFC_EMV_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMV_DEBIT_MASTER']")
    HDFC_EMV_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMV_CREDIT_RUPAY']")
    HDFC_EMV_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='HDFC_EMV_DEBIT_RUPAY']")

    IDFC_EMVCTLS_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='IDFC_EMVCTLS_CREDIT_MASTER']")
    IDFC_EMVCTLS_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='IDFC_EMVCTLS_CREDIT_VISA']")
    IDFC_MSR_DEBIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='IDFC_MSR_DEBIT_RUPAY']")
    IDFC_MSR_CREDIT_VISA = (By.XPATH, "//android.widget.TextView[@text='IDFC_MSR_CREDIT_VISA']")
    IDFC_EMV_DEBIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='IDFC_EMV_DEBIT_MASTER']")
    IDFC_EMV_CREDIT_MASTER = (By.XPATH, "//android.widget.TextView[@text='IDFC_EMV_CREDIT_MASTER']")
    IDFC_EMV_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='IDFC_EMV_DEBIT_VISA']")
    IDFC_MSR_CREDIT_RUPAY = (By.XPATH, "//android.widget.TextView[@text='IDFC_MSR_CREDIT_RUPAY']")
    IDFC_MSR_DEBIT_VISA = (By.XPATH, "//android.widget.TextView[@text='IDFC_MSR_DEBIT_VISA']")

    txt_error_code = (By.ID, "com.ezetap.service.demo:id/dialogTitle")
    txt_error_message = (By.ID, "com.ezetap.service.demo:id/dialogText")
    btn_error_confirm = (By.ID, "com.ezetap.service.demo:id/rightButton")

    def __init__(self, driver):
        super().__init__(driver)

    def select_cardtype(self, text):
        print("Preferred card type is ", text)
        self.scroll_to_text(text)
        if text == "FDC_EMVCTLS_CREDIT_MASTER":
            self.perform_long_press(self.FDC_EMVCTLS_CREDIT_MASTER)
        elif text == "FDC_EMVCTLS_CREDIT_VISA":
            self.perform_long_press(self.FDC_EMVCTLS_CREDIT_VISA)
        elif text == "FDC_EMV_DEBIT_MASTER":
            self.perform_long_press(self.FDC_EMV_DEBIT_MASTER)
        elif text == "FDC_EMV_DEBIT_VISA":
            self.perform_long_press(self.FDC_EMV_DEBIT_VISA)
        elif text == "FDC_EMV_CREDIT_VISA":
            self.perform_long_press(self.FDC_EMV_CREDIT_VISA)
        elif text == "FDC_EMVCTLS_DEBIT_MASTER":
            self.perform_long_press(self.FDC_EMVCTLS_DEBIT_MASTER)
        elif text == "FDC_EMVCTLS_CREDIT_RUPAY":
            self.perform_long_press(self.FDC_EMVCTLS_CREDIT_RUPAY)
        elif text == "FDC_EMVCTLS_DEBIT_RUPAY":
            self.perform_long_press(self.FDC_EMVCTLS_DEBIT_RUPAY)
        elif text == "FDC_EMV_CREDIT_MASTER":
            self.perform_long_press(self.FDC_EMV_CREDIT_MASTER)

        elif text == "PRIZMV2_EMVCTLS_DEBIT_VISA":
            self.perform_long_press(self.PRIZMV2_EMVCTLS_DEBIT_VISA)
        elif text == "PRIZMV2_EMVCTLS_CREDIT_MASTER":
            self.perform_long_press(self.PRIZMV2_EMVCTLS_CREDIT_MASTER)
        elif text == "PRIZMV2_EMVCTLS_CREDIT_VISA":
            self.perform_long_press(self.PRIZMV2_EMVCTLS_CREDIT_VISA)
        elif text == "PRIZMV2_EMV_DEBIT_RUPAY":
            self.perform_long_press(self.PRIZMV2_EMV_DEBIT_RUPAY)
        elif text == "PRIZMV2_EMV_CREDIT_RUPAY":
            self.perform_long_press(self.PRIZMV2_EMV_CREDIT_RUPAY)
        elif text == "PRIZMV2_EMV_DEBIT_VISA":
            self.perform_long_press(self.PRIZMV2_EMV_DEBIT_VISA)

        elif text == "ATOS_TLE_EMVCTLS_CREDIT_MASTER":
            self.perform_long_press(self.ATOS_TLE_EMVCTLS_CREDIT_MASTER)
        elif text == "ATOS_TLE_EMVCTLS_CREDIT_VISA":
            self.perform_long_press(self.ATOS_TLE_EMVCTLS_CREDIT_VISA)
        elif text == "ATOS_TLE_EMVCTLS_DEBIT_MASTER":
            self.perform_long_press(self.ATOS_TLE_EMVCTLS_DEBIT_MASTER)
        elif text == "ATOS_TLE_EMVCTLS_DEBIT_VISA":
            self.perform_long_press(self.ATOS_TLE_EMVCTLS_DEBIT_VISA)
        elif text == "ATOS_TLE_EMV_CREDIT_VISA":
            self.perform_long_press(self.ATOS_TLE_EMV_CREDIT_VISA)
        elif text == "ATOS_TLE_EMV_CREDIT_RUPAY":
            self.perform_long_press(self.ATOS_TLE_EMV_CREDIT_RUPAY)
        elif text == "ATOS_TLE_EMV_DEBIT_RUPAY":
            self.perform_long_press(self.ATOS_TLE_EMV_DEBIT_RUPAY)
        elif text == "ATOS_TLE_EMV_DEBIT_VISA":
            self.perform_long_press(self.ATOS_TLE_EMV_DEBIT_VISA)

        elif text == "HDFC_EMVCTLS_DEBIT_RUPAY":
            self.perform_long_press(self.HDFC_EMVCTLS_DEBIT_RUPAY)
        elif text == "HDFC_EMVCTLS_DEBIT_MASTER":
            self.perform_long_press(self.HDFC_EMVCTLS_DEBIT_MASTER)
        elif text == "HDFC_EMVCTLS_CREDIT_RUPAY":
            self.perform_long_press(self.HDFC_EMVCTLS_CREDIT_RUPAY)
        elif text == "HDFC_EMVCTLS_CREDIT_VISA":
            self.perform_long_press(self.HDFC_EMVCTLS_CREDIT_VISA)
        elif text == "HDFC_EMV_DEBIT_MASTER":
            self.perform_long_press(self.HDFC_EMV_DEBIT_MASTER)
        elif text == "HDFC_EMV_CREDIT_RUPAY":
            self.perform_long_press(self.HDFC_EMV_CREDIT_RUPAY)
        elif text == "HDFC_EMV_DEBIT_RUPAY":
            self.perform_long_press(self.HDFC_EMV_DEBIT_RUPAY)

        elif text == "IDFC_EMVCTLS_CREDIT_MASTER":
            self.perform_long_press(self.IDFC_EMVCTLS_CREDIT_MASTER)
        elif text == "IDFC_EMVCTLS_CREDIT_VISA":
            self.perform_long_press(self.IDFC_EMVCTLS_CREDIT_VISA)
        elif text == "IDFC_MSR_DEBIT_RUPAY":
            self.perform_long_press(self.IDFC_MSR_DEBIT_RUPAY)
        elif text == "IDFC_MSR_CREDIT_VISA":
            self.perform_long_press(self.IDFC_MSR_CREDIT_VISA)
        elif text == "IDFC_EMV_DEBIT_MASTER":
            self.perform_long_press(self.IDFC_EMV_DEBIT_MASTER)
        elif text == "IDFC_EMV_CREDIT_MASTER":
            self.perform_long_press(self.IDFC_EMV_CREDIT_MASTER)
        elif text == "IDFC_EMV_DEBIT_VISA":
            self.perform_long_press(self.IDFC_EMV_DEBIT_VISA)
        elif text == "IDFC_MSR_CREDIT_RUPAY":
            self.perform_long_press(self.IDFC_MSR_CREDIT_RUPAY)
        elif text == "IDFC_MSR_DEBIT_VISA":
            self.perform_long_press(self.IDFC_MSR_DEBIT_VISA)

        else:
            raise Exception("Preferred card is invalid")

    def fetch_error_code_text(self):
        return str(self.fetch_text(self.txt_error_code))

    def fetch_error_message_text(self):
        return str(self.fetch_text(self.txt_error_message))

    def click_on_ok_error_mssg(self):
        self.perform_click(self.btn_error_confirm)