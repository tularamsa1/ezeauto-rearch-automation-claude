from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from PageFactory.merchant_portal.Portal_BasePage import BasePage


class PortalHomePage(BasePage):
    txt_merchantSearch = "input[name=\"q\"]"
    btn_switch = '//button[.="switch"]'
    mnu_transactions = '//a[contains(text(),"Transactions ")]'
    ddl_transactionSearch = '//ul/li[.="Search"]'
    txt_referenceNumber = (By.ID, 'refNumber')
    txt_authCode = (By.ID, 'authCode')
    lbl_status = (By.XPATH, '(//table[@id="table_txns"]/tbody/tr/td)[6]')
    lbl_date = (By.XPATH, '(//table[@id="table_txns"]/tbody/tr/td/a)[1]')
    btn_chargeSlip = (By.XPATH, '(//a[@title="Customer Receipt"])[1]')
    lbl_sale = (By.XPATH, '//table/tbody/tr/td/strong[contains(text(),"lbl_sale")]')
    lbl_refund_window = '//*[@class="loader"]'
    lbl_refund_window_before_load = '//*[@class="loader active"]'
    txt_refundAmtField = "#userrefund_refund"
    btn_confirmRefund = '(//button[.="Confirm"])[1]'
    btn_refund = '(//button[.="Refund"])[1]'
    btn_switchedMerchant = '/html/body/div/div[10]/div[1]/div[1]/button[2]'
    lbl_resultValueSearch = "#max"
    btn_txnSearch = "//button[contains(text(),'Search')]"
    btn_txnClick = (By.PARTIAL_LINK_TEXT, "Transactio")
    # btn_txnSearch = (By.LINK_TEXT, "Search")
    txt_homepageTitle = '//title[contains(text(),"Manage Merchants")]'

    def __init__(self, page):
        super().__init__(page)

    def wait_for_home_page_load(self):
        self.wait_for_all_elements()

    def search_merchant_name(self, org_code):
        self.perform_fill(self.txt_merchantSearch, org_code)
        self.page.keyboard.press("Enter")

    def click_switch_button(self, org_code):
        self.perform_click(self.btn_switch)
        locator = '//button[contains(text(),"' + org_code + '")]'
        self.wait_for_element(locator)
        self.wait_for_all_elements()

    def click_transaction_search_menu(self, no_of_txn_to_search: str = "4"):
        self.perform_click(self.mnu_transactions)
        self.perform_click(self.ddl_transactionSearch)
        self.perform_fill(self.lbl_resultValueSearch, str(no_of_txn_to_search))
        self.perform_click(self.btn_txnSearch)
        self.wait_for_load_state()

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
        self.wait_for_element_invisible(self.lbl_refund_window_before_load)
        self.wait_for_all_elements()
        self.wait_for_element(self.txt_refundAmtField)
        self.perform_fill(self.txt_refundAmtField, str(amount))
        self.perform_click(self.btn_confirmRefund)
        self.wait_for_alert_and_accept()

    def perform_refund_of_txn_and_fetch_alert_msg(self, amount):
        self.wait_for_element_invisible(self.lbl_refund_window_before_load, 40)
        self.wait_for_element(self.lbl_refund_window)
        self.wait_for_element(self.txt_refundAmtField).clear()
        self.perform_sendkeys(self.txt_refundAmtField, str(amount))
        self.perform_click(self.btn_confirmRefund)
        return self.wait_for_alert_read_text_and_accept()

    def click_on_transaction_details_based_on_transaction_id(self,txn_id):
        locator = '(//table[@id="table_txns"]/tbody/tr/td[contains(text(),"'+txn_id+'")]/../td/a)[1]'
        locator2 = '//td[@style="display:none;" and contains(text(),"'+txn_id+'")]'
        self.wait_for_element_invisible(locator2)
        print("Element is invisible now")
        return self.perform_click(locator)

    def click_on_refund_button(self):
        return self.perform_click(self.btn_refund)

    # def perform_merchant_switched_verfication(self):
    #     return self.wait_for_element(self.btn_switchedMerchant)

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

    def perfrom_search_Txn(self):
        self.perform_click(self.btn_txnClick)
        self.perform_click(self.btn_txnClick)
        return self.fetch_text(self.btn_switchedMerchant)


