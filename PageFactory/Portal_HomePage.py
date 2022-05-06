from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PageFactory.Portal_BasePage import BasePage


class PortalHomePage(BasePage):
    txt_merchantSearch = (By.ID, 'q')
    btn_switch = (By.XPATH, '//button[.="switch"]')
    mnu_transactions = (By.XPATH, '//a[contains(text(),"Transactions ")]')
    ddl_transactionSearch = (By.XPATH, '//ul/li[.="Search"]')
    txt_referenceNumber = (By.ID, 'refNumber')
    txt_authCode = (By.ID, 'authCode')
    lbl_status = (By.XPATH, '(//table[@id="table_txns"]/tbody/tr/td)[6]')
    lbl_date = (By.XPATH, '(//table[@id="table_txns"]/tbody/tr/td/a)[1]')
    btn_chargeSlip = (By.XPATH, '(//a[@title="Customer Receipt"])[1]')
    lbl_sale = (By.XPATH, '//table/tbody/tr/td/strong[contains(text(),"lbl_sale")]')


    def __init__(self, driver):
        super().__init__(driver)

    def search_merchant_name(self, org_code):
        self.perform_sendkeys(self.txt_merchantSearch, org_code)
        self.perform_sendkeys(self.txt_merchantSearch, Keys.ENTER)

    def click_switch_button(self):
        self.perform_click(self.btn_switch)

    def click_transaction_search_menu(self):
        self.perform_click(self.mnu_transactions)
        self.perform_click(self.ddl_transactionSearch)

    def search_by_auth_code(self, rr_number):
        self.perform_sendkeys(self.txt_authCode, rr_number)
        self.perform_sendkeys(self.txt_authCode, Keys.ENTER)

    def fetch_status_of_transaction(self):
        return self.fetch_text(self.lbl_status)

    def click_charge_slip_of_transaction(self):
        self.driver.implicitly_wait(10)
        self.perform_click(self.lbl_date)
        self.perform_click(self.btn_chargeSlip)
        self.driver.switch_to.window(self.driver.window_handles[1])
        return self.fetch_text(self.lbl_sale)

    def fetch_status_from_transaction_id(self,txn_id):
        locator = (By.XPATH,'(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td/following-sibling::td)[5]')
        text=self.fetch_text(locator)
        if text.upper() == "SETTLED":
            text= "AUTHORIZED"
        return text


