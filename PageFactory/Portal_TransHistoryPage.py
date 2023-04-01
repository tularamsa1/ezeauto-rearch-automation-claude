from PageFactory.Portal_BasePage import BasePage


class PortalTransHistoryPage(BasePage):
    tbl_txns_xpath = "//table[@id='table_txns']"
    tbl_txnsHeader_xpath = "//table[@id='table_txns']/thead"
    tbl_txnsBody_xpath = "//table[@id='table_txns']/tbody"
    tbl_txnsRows_xpath = "//table[@id='table_txns']/tbody/tr"
    tbl_txnsCols_xpath = "//table[@id='table_txns']/thead//th"
    ddl_transaction_xpath = "//a[text()='Transactions ']"
    mnu_transactionSearch_xpath = "//a[text()='Search']"

    def __init__(self, page):
        super().__init__(page)

    def get_transaction_details_for_portal(self, txn_id):
        transactionRow = ""
        rowID = "ENT" + txn_id
        transactionDetails = {}
        total_transactions_count = self.page.locator("//table[@id='table_txns']/tbody/tr").count()
        total_attributes_count = self.page.locator("//table[@id='table_txns']/thead//th").count()
        print(total_transactions_count, total_attributes_count)

        for row in range(1, total_transactions_count + 1):
            element = self.page.locator("//table[@id='table_txns']/tbody/tr" + "[" + str(row) + "]")
            if element.get_attribute("id") == rowID:
                transactionRow = row
                break
        for col in range(1, total_attributes_count):
            attribute = self.page.locator("//table[@id='table_txns']/thead//th" + "[" + str(
                col) + "]").get_attribute("aria-label")
            if attribute.__contains__(": activate to sort column ascending"):
                attribute = attribute.replace(": activate to sort column ascending", "")
            attributeValue = self.page.locator(
                "//table[@id='table_txns']/tbody/tr" + "[" + str(transactionRow) + "]/td[" + str(
                    col) + "]").inner_text()
            transactionDetails[attribute] = attributeValue
        print(f"transactionDetails on portal : {transactionDetails}")
        return transactionDetails
