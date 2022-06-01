from selenium.webdriver.common.by import By

from PageFactory.Portal_BasePage import BasePage


class PortalTransHistoryPage(BasePage):
    tbl_txns_xpath = (By.XPATH, "//table[@id='table_txns']")
    tbl_txnsHeader_xpath = (By.XPATH, "//table[@id='table_txns']/thead")
    tbl_txnsBody_xpath = (By.XPATH, "//table[@id='table_txns']/tbody")
    tbl_txnsRows_xpath = (By.XPATH, "//table[@id='table_txns']/tbody/tr")
    tbl_txnsCols_xpath = (By.XPATH, "//table[@id='table_txns']/thead//th")
    ddl_transaction_xpath = (By.XPATH, "//a[text()='Transactions ']")
    mnu_transactionSearch_xpath = (By.XPATH, "//a[text()='Search']")

    def __init__(self, driver):
        super().__init__(driver)

    def get_transaction_details_for_portal(self, txn_id):
        transactionRow = ""
        rowID = "ENT" + txn_id
        transactionDetails = {}
        total_transactions_count = len(self.driver.find_elements(By.XPATH, "//table[@id='table_txns']/tbody/tr"))
        total_attributes_count = len(self.driver.find_elements(By.XPATH, "//table[@id='table_txns']/thead//th"))
        for row in range(1, total_transactions_count + 1):
            element = self.driver.find_element(By.XPATH, "//table[@id='table_txns']/tbody/tr" + "[" + str(row) + "]")
            if element.get_attribute("id") == rowID:
                transactionRow = row
                break
        for col in range(1, total_attributes_count):
            attribute = self.driver.find_element(By.XPATH, "//table[@id='table_txns']/thead//th" + "[" + str(
                col) + "]").get_attribute(
                "aria-label")
            if attribute.__contains__(": activate to sort column ascending"):
                attribute = attribute.replace(": activate to sort column ascending", "")
            attributeValue = self.driver.find_element(By.XPATH, "//table[@id='table_txns']/tbody/tr" + "[" + str(transactionRow) + "]/td[" + str(
                                                          col) + "]").text
            transactionDetails[attribute] = attributeValue
        return transactionDetails
