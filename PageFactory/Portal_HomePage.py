from time import sleep

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
    lbl_refund_window = (By.XPATH, '//*[@class="loader"]')
    lbl_refund_window_before_load = (By.XPATH, '//*[@class="loader active"]')
    txt_refundAmtField = (By.ID, "userrefund_refund")
    btn_confirmRefund = (By.XPATH, '(//button[.="Confirm"])[1]')
    btn_refund = (By.XPATH, '(//button[.="Refund"])[1]')
    btn_switchedMerchant = (By.XPATH, '/html/body/div/div[10]/div[1]/div[1]/button[2]')
    lbl_resultValueSearch = (By.CSS_SELECTOR,"#max")
    btn_txnSearch = (By.XPATH, "//button[contains(text(),'Search')]")
    btn_txnClick = (By.PARTIAL_LINK_TEXT, "Transactio")
    btn_txnSearch = (By.LINK_TEXT, "Search")
    txt_homepageTitle = (By.XPATH, '//title[contains(text(),"Manage Merchants")]')


    def __init__(self, driver):
        super().__init__(driver)

    def wait_for_home_page_load(self):
        self.wait_for_element(self.txt_homepageTitle)

    def search_merchant_name(self, org_code):
        self.perform_sendkeys(self.txt_merchantSearch, org_code)
        self.perform_sendkeys(self.txt_merchantSearch, Keys.ENTER)

    def click_switch_button(self, org_code):
        self.perform_click(self.btn_switch)
        locator = (By.XPATH, '//button[contains(text(),"' + org_code + '")]')
        self.wait_for_element(locator)

    def click_transaction_search_menu(self):
        self.perform_click(self.mnu_transactions)
        self.perform_click(self.ddl_transactionSearch)

    def search_by_auth_code(self, rr_number):
        self.perform_sendkeys(self.txt_authCode, rr_number)
        self.perform_sendkeys(self.txt_authCode, Keys.ENTER)

    def fetch_status_of_transaction(self):
        return self.fetch_text(self.lbl_status)

    def click_charge_slip_of_transaction(self):
        sleep(5)
        self.perform_click(self.lbl_date)
        self.perform_click(self.btn_chargeSlip)
        self.driver.switch_to.window(self.driver.window_handles[1])
        return self.fetch_text(self.lbl_sale)

    def fetch_status_from_transaction_id(self,txn_id):
        locator = (By.XPATH,'(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td/following-sibling::td)[4]')
        text=self.fetch_text(locator)
        return text

    def fetch_amount_from_transaction_id(self,txn_id):
        locator = (By.XPATH,'(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td/following-sibling::td)[5]')
        text=self.fetch_text(locator)
        return text

    def fetch_transaction_type_from_transaction_id(self,txn_id):
        locator = (By.XPATH,'(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td/following-sibling::td)[3]')
        text=self.fetch_text(locator)
        return text

    def perform_refund_of_txn(self, amount):
        self.wait_for_element_invisible(self.lbl_refund_window_before_load, 20)
        self.wait_for_element(self.lbl_refund_window)
        self.wait_for_element(self.txt_refundAmtField).clear()
        self.perform_sendkeys(self.txt_refundAmtField, str(amount))
        self.perform_click(self.btn_confirmRefund)
        self.wait_for_alert_and_accept()

    def click_on_transaction_details_based_on_transaction_id(self,txn_id):
        locator = (By.XPATH,'(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td)[1]')
        return self.perform_click(locator)

    def click_on_refund_button(self):
        return self.perform_click(self.btn_refund)

    # def perform_merchant_switched_verfication(self):
    #     return self.wait_for_element(self.btn_switchedMerchant)

    def perform_clear_txt(self):
        self.perform_click1(self.lbl_resultValueSearch)
        return self.perform_clear_text(self.lbl_resultValueSearch)

    def perform_txn_count_search(self, value):
        return self.perform_sendkeys(self.lbl_resultValueSearch, value)

    def perform_txn_search(self):
        return self.perform_click(self.btn_txnSearch)

    # def perform_merchant_switched_verfication(self):
    #     return self.wait_for_element(self.btn_switchedMerchant)

    def perform_merchant_verfication(self):
        return self.perform_click_cnp(self.btn_switchedMerchant)

    def perform_merchant_switched_verfication(self):
        return self.fetch_text(self.btn_switchedMerchant)

    def search_merchant_name(self, org_code):
        self.perform_sendkeys(self.txt_merchantSearch, org_code)
        self.perform_sendkeys(self.txt_merchantSearch, Keys.ENTER)

    def perfrom_search_Txn(self):
        self.perform_click(self.btn_txnClick)
        self.perform_click(self.btn_txnClick)


        return self.fetch_text(self.btn_switchedMerchant)


    def perfrom_search_Txn(self):
        self.perform_click(self.btn_txnClick)
        self.perform_click(self.btn_txnClick)


        return self.fetch_text(self.btn_switchedMerchant)


