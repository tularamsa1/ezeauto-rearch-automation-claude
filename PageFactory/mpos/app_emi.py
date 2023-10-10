import re
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from PageFactory.App_BasePage import BasePage


class EmiCalc(BasePage):
    lbl_emi_calculator = (AppiumBy.XPATH,'(//*[@resource-id="com.ezetap.basicapp:id/tvFeature"])[3]')
    txt_emi_message = (AppiumBy.XPATH, '//*[@text = "Enter Transaction Amount"]')
    txt_enter_amount = (AppiumBy.XPATH, '//*[@resource-id="com.ezetap.basicapp:id/etLoanAmount"]')
    btn_proceed = (AppiumBy.XPATH, '//*[@text = "Proceed"]')
    chk_bank_1 = (AppiumBy.XPATH, '(//*[@class="android.widget.CheckBox"])[1]')
    chk_bank_2 = (AppiumBy.XPATH, '(//*[@class="android.widget.CheckBox"])[2]')
    btn_edit_amount = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgEditAmount')
    btn_bank_proceed = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnProceed')
    btn_flexi_pay = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvFlexipay')
    btn_tenure = (AppiumBy.XPATH, '//*[@resource-id = "com.ezetap.basicapp:id/imgDropDown"]')
    btn_select_tenure = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTenure')
    lbl_selected_period = (AppiumBy.XPATH, '//*[@resource-id = "com.ezetap.basicapp:id/tvTenure"]')
    lbl_plan = (AppiumBy.XPATH, '//*[@resource-id ="com.ezetap.basicapp:id/tvEmiTenure"]')

    def __init__(self, driver):
        super().__init__(driver)

    def emi_calc_is_available(self):
        """
        This method fetches text for emi calculator button present on homepage
        """
        return self.fetch_text(self.lbl_emi_calculator)

    def click_on_emi_calculator(self):
        """
          This method clicks on EMI calculator button present on home screen
        """
        self.perform_click(self.lbl_emi_calculator)

    def click_on_buy_now_pay_later(self):
        self.wait_for_element(self.btn_flexi_pay)
        self.perform_click(self.btn_flexi_pay)

    def fetch_message_for_emi_calculator(self):
        return self.fetch_text(self.txt_emi_message)

    def enter_txn_amount(self, amount):
        self.perform_click(self.txt_enter_amount)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, amount)

    def click_on_proceed(self):
        self.wait_for_element_to_be_clickable(self.btn_proceed)
        self.perform_click(self.btn_proceed)

    def select_multiple_banks(self):
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)
        self.wait_for_element(self.chk_bank_2)
        self.perform_click(self.chk_bank_2)

    def select_single_bank(self):
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)

    def click_edit_amount(self):
        self.wait_for_element(self.btn_edit_amount)
        self.perform_click(self.btn_edit_amount)

    def select_bank_for_flexipay(self):
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)

    def click_on_proceed_for_multiple_banks(self):
        self.wait_for_element(self.btn_bank_proceed)
        self.perform_click(self.btn_bank_proceed)

    def click_on_proceed_for_flexipay_bank(self):
        self.wait_for_element(self.btn_bank_proceed)
        self.perform_click(self.btn_bank_proceed)

    def click_on_tenure(self):
        self.perform_click(self.btn_tenure)

    def wait_for_tenure_to_load(self):
        self.wait_for_element_to_be_clickable(self.btn_tenure)

    def get_cordinates(self):
        """
          This method returns relative co-ordinates of tenure element
        """
        bounds_str = self.wait_for_element(self.btn_select_tenure).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            x1 = int(matches[0])*1.25
            a1 = int(matches[1])*1.5
            y1 = round(a1)
            x1 = round(x1)
            return x1, y1
        else:
            print("Not enough numeric values found in the string")

    def select_data_from_drop_down(self, x, y):
        """
          This method perform touch action from show dropdown tenures
        """
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def validate_tenure_period_selected(self):
        """
          This method returns tenure name
        """
        selected_period = self.fetch_text(self.lbl_selected_period)
        return selected_period

    def validate_shown_plan(self, selected_period):
        """
          This method returns emi plan details for credit/debit cards
        """
        plan = self.fetch_text(self.lbl_plan)
        if selected_period == "3 month" or selected_period == "6 month" or selected_period == "9 month" or selected_period == "12 month":
            return [plan]
        else:
            selected_period == "All"
            total_plans = self.fetch_elements(self.lbl_plan)
            plan_details_when_selected_all = []
            for i in range(1, total_plans + 1):
                plan = f'(//*[@resource-id ="com.ezetap.basicapp:id/tvEmiTenure"])[{i}]'
                tenure = self.fetch_text(locator=(AppiumBy.XPATH, plan))
                plan_details_when_selected_all.append(tenure)
            return plan_details_when_selected_all

    def validate_shown_plan_flexi_pay(self, selected_period):
        """
          This method returns plan details for pay later
        """
        plan = self.fetch_text(self.lbl_plan)
        if selected_period == "15 days" or selected_period == "30 days" or selected_period == "60 days" or selected_period == "90 days":
            print("about to return plan")
            return [plan]
        else:
            selected_period == "All"
            print("All block is getting executed")
            total_plans = self.fetch_elements(self.lbl_plan)
            print(total_plans)
            plan_details_when_selected_all = []
            for i in range(1, total_plans + 1):
                plan = f'(//*[@resource-id ="com.ezetap.basicapp:id/tvEmiTenure"])[{i}]'
                z = self.fetch_text(locator=(AppiumBy.XPATH, plan))
                plan_details_when_selected_all.append(z)
            return plan_details_when_selected_all

    def plan_details_without_interest_rate(self, plan):
        plan_without_interest = []
        for i in plan:
            result = (re.search(r'\d+\s*EMI', i)).group()
            plan_without_interest.append(result)
        return plan_without_interest

    def plan_details_without_intrest_rate_flexi_pay(self, plan):
        plan_without_interest = []
        for i in plan:
            result = i.split('@')[0].strip()
            plan_without_interest.append(result)
        return plan_without_interest









