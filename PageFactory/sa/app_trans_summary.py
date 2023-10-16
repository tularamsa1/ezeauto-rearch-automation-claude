import re
from selenium.webdriver.common.by import By
from PageFactory.App_BasePage import BasePage


class Trans_summary(BasePage):

    btn_txn_summary = (By.ID,'com.ezetap.service.demo:id/cl_Summary')
    txt_sales_volume =(By.ID,'com.ezetap.service.demo:id/tv_SalesVolume')
    txt_total_sales_count = (By.ID,'com.ezetap.service.demo:id/tv_SalesCount')
    txt_payment_mode_1 = (By.ID,'com.ezetap.service.demo:id/tv_Card')
    txt_payment_mode_2 = (By.ID,'com.ezetap.service.demo:id/tv_Upi')
    txt_payment_mode_3 = (By.ID,'com.ezetap.service.demo:id/tv_BrandEmi')
    txt_others = (By.ID,"com.ezetap.service.demo:id/tv_Others")
    txt_payment_mode_4 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[1]')
    txt_payment_mode_5 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[2]')
    txt_payment_mode_6 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[3]')
    txt_payment_mode_7 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[4]')
    txt_grand_total = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[5]')
    txt_payment_mode_9 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[6]')
    txt_payment_mode_10 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvHeader"])[7]')
    txt_payment_sales_count_1 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[1]')
    txt_payment_sales_count_2 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[2]')
    txt_payment_sales_count_3 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[3]')
    txt_payment_sales_count_4 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[4]')
    txt_payment_sales_count_5 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[5]')
    txt_payment_sales_count_6 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[6]')
    txt_payment_sales_count_7 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[7]')
    txt_payment_sales_count_8 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[8]')
    txt_payment_sales_count_9 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[9]')
    txt_payment_sales_count_10 = (By.XPATH, '(//*[@resource-id="com.ezetap.service.demo:id/tvCount"])[10]')
    txt_payment_total_amount_1 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[1]')
    txt_payment_total_amount_2 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[2]')
    txt_payment_total_amount_3 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[3]')
    txt_payment_total_amount_4 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[4]')
    txt_payment_total_amount_5 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[5]')
    txt_payment_total_amount_6 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[6]')
    txt_payment_total_amount_7 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[7]')
    txt_payment_total_amount_8 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[8]')
    txt_payment_total_amount_9 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[9]')
    txt_payment_total_amount_10 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvValue"])[10]')
    txt_payment_status_1 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[1]')
    txt_payment_status_2 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[2]')
    txt_payment_status_3 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[3]')
    txt_payment_status_4 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[4]')
    txt_payment_status_5 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[5]')
    txt_payment_status_6 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[6]')
    txt_payment_status_7 = (By.XPATH,'(//*[@resource-id="com.ezetap.service.demo:id/tvName"])[7]')

    def __init__(self, driver):
        super().__init__(driver)

    def fetch_total_volume(self):
        """
        fetches the volume(total amount of txn) from the txn summary page
        return: txt_sales_volume: str
        """
        return self.fetch_text(self.txt_sales_volume)

    def fetch_total_sales(self):
        """
        fetches the total count of sales done for today from txn summary
        return: txt_total_sales_count :str
        """
        return self.fetch_text(self.txt_total_sales_count)

    def fetch_first_highest_payment_mode_and_amount(self):
        """
        fetches the first highest amount and respective  pay mode
        return: txt_payment_mode_1 :str
        """
        return self.fetch_text(self.txt_payment_mode_1)

    def fetch_second_highest_payment_mode_and_amount(self):
        """
         fetches the second highest amount and respective  pay mode
         return: txt_payment_mode_2 :str
         """
        return self.fetch_text(self.txt_payment_mode_2)

    def fetch_third_highest_payment_mode_and_amount(self):
        """
         fetches the third highest amount and respective  pay mode
         return: txt_payment_mode_3 :str
         """
        return self.fetch_text(self.txt_payment_mode_3)

    def fetch_other_payment_mode_and_amount(self):
        """
         fetches the other amount and respective  pay mode
         return: txt_others :str
         """
        return self.fetch_text(self.txt_others)

    def click_on_txn_summary(self):
        """
        performs clicking on the txn summary button from the transaction page
        """
        self.perform_click(self.btn_txn_summary)

    def extract_data(self, input_str: str):
        """
        Use regular expressions to extract text and numeric values
        param: input :str
        """
        match = re.search(r'([\w\s]+)\n.*?([\d,.]+)', input_str)
        if match:
            primary_text = match.group(1).strip()
            numeric_value = match.group(2)

            return [primary_text, numeric_value]
        else:
            return None




