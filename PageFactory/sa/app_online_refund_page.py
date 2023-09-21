from selenium.webdriver.common.by import By
from PageFactory.mpos.app_base_page import BasePage


class RefundPage(BasePage):

    ref_amount_field = (By.ID, 'com.ezetap.basicapp:id/amountView')
    card_type_desc_field = (By.ID, 'com.ezetap.basicapp:id/cardChequeLabel')
    date_time_field = (By.ID, 'com.ezetap.basicapp:id/dateView')
    status_field = (By.ID, 'com.ezetap.basicapp:id/statusText')
    device_serial_field = (By.ID, 'com.ezetap.basicapp:id/externalRef2Value')
    ref3_field = (By.ID, 'com.ezetap.basicapp:id/externalRef3Value')
    customer_name_field = (By.ID, 'com.ezetap.basicapp:id/customerNameValue')
    auth_code_field = (By.ID, 'com.ezetap.basicapp:id/authCodeValue')
    mid_field = (By.ID, 'com.ezetap.basicapp:id/midValue')
    tid_field = (By.ID, 'com.ezetap.basicapp:id/tidValue')
    rrn_field = (By.ID, 'com.ezetap.basicapp:id/rrnValue')
    batch_number_field = (By.ID, 'com.ezetap.basicapp:id/batchNoValue')
    invoice_no_field = (By.ID, 'com.ezetap.basicapp:id/invoiceNoValue')

    def __init__(self, driver):
        super().__init__(driver)

    def fetch_amount_text(self) -> str:
        """
        This method is used to fetch amount on refund page
        return: amount: str
        """
        return self.fetch_text(self.ref_amount_field)

    def fetch_card_type_desc_text(self) -> str:
        """
        This method is used to fetch card type desc on refund page
        return: card_type_desc: str
        """
        return self.fetch_text(self.card_type_desc_field)

    def fetch_date_time_text(self) -> str:
        """
        This method is used to fetch date and time on refund page
        return: date_time: str
        """
        return self.fetch_text(self.date_time_field)

    def fetch_status_text(self) -> str:
        """
        This method is used to fetch status on refund page
        return: status: str
        """
        return self.fetch_text(self.status_field)

    def fetch_device_serial_text(self) -> str:
        """
        his method is used to fetch device serial on refund page
        return: device_serial: str
        """
        return self.fetch_text(self.device_serial_field)

    def fetch_ref3_text(self) -> str:
        """
        This method is used to fetch ref 3 on refund page
        return: ref_3: str
        """
        return self.fetch_text(self.ref3_field)

    def fetch_customer_name_text(self) -> str:
        """
        This method is used to fetch customer name on refund page
        return: customer_name: str
        """
        return self.fetch_text(self.customer_name_field)

    def fetch_auth_code_text(self) -> str:
        """
        This method is used to fetch auth code on refund page
        return: auth_code: str
        """
        return self.fetch_text(self.auth_code_field)

    def fetch_mid_text(self) -> str:
        """
         This method is used to fetch mid on refund page
         return: mid: str
        """
        return self.fetch_text(self.mid_field)

    def fetch_tid_text(self) -> str:
        """
         This method is used to fetch tid on refund page
         return: tid: str
        """
        return self.fetch_text(self.tid_field)

    def fetch_rrn_text(self) -> str:
        """
         This method is used to fetch rrn on refund page
         return: rrn: str
        """
        return self.fetch_text(self.rrn_field)

    def fetch_batch_number_text(self) -> str:
        """
         This method is used to fetch batch_no on refund page
         return: batch_no: str
        """
        return self.fetch_text(self.batch_number_field)
