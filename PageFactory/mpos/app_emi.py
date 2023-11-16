import re
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from bs4 import element

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
    btn_side_menu = (AppiumBy.ACCESSIBILITY_ID, 'Open navigation drawer')
    btn_emi_from_side_menu = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_emi_cal')

    def __init__(self, driver):
        super().__init__(driver)

    def emi_calc_is_available(self):
        """
        Fetches and retrieve text for emi calculator button
        """
        self.wait_for_element(self.btn_side_menu)
        self.perform_click(self.btn_side_menu)
        self.wait_for_element(self.btn_emi_from_side_menu)
        return self.fetch_text(self.btn_emi_from_side_menu)

    def click_on_emi_calculator(self):
        """
          Clicks on EMI calculator button from side menu
        """
        self.wait_for_element(self.btn_side_menu)
        self.perform_click(self.btn_side_menu)
        self.wait_for_element(self.btn_emi_from_side_menu)
        self.perform_click(self.btn_emi_from_side_menu)

    def click_on_buy_now_pay_later(self):
        """
         Performs a click action on the 'Buy Now, Pay Later' button
        """
        self.wait_for_element(self.btn_flexi_pay)
        self.perform_click(self.btn_flexi_pay)

    def fetch_message_for_emi_calculator(self):
        """
          Retrieve and returns ""Enter Transaction Amount""
        """
        return self.fetch_text(self.txt_emi_message)

    def enter_txn_amount(self, amount):
        """
        Enters txn amount in the txn field
        """
        self.perform_click(self.txt_enter_amount)
        self.wait_for_element(self.txt_enter_amount).clear()
        self.perform_sendkeys(self.txt_enter_amount, amount)

    def click_on_proceed(self):
        """
        Performs a click on Proceed button
        """
        self.wait_for_element_to_be_clickable(self.btn_proceed)
        self.perform_click(self.btn_proceed)

    def select_multiple_banks(self):
        """
        Select multiple banks by clicking their respective checkboxes
        """
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)
        self.wait_for_element(self.chk_bank_2)
        self.perform_click(self.chk_bank_2)

    def select_single_bank(self):
        """
        Select single bank by clicking checkbox
        """
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)

    def click_edit_amount(self):
        """
        Performs a click action on the 'Edit Amount' button
        """
        self.wait_for_element(self.btn_edit_amount)
        self.perform_click(self.btn_edit_amount)

    def select_bank_for_flexipay(self):
        """
        Clicks the checkbox for FlexiPay
        """
        self.wait_for_element(self.chk_bank_1)
        self.perform_click(self.chk_bank_1)

    def click_on_proceed_for_multiple_banks(self):
        """
        Click the 'Proceed' button for multiple banks.
        """
        self.wait_for_element(self.btn_bank_proceed)
        self.perform_click(self.btn_bank_proceed)

    def click_on_proceed_for_flexipay_bank(self):
        """
        Click the 'Proceed' button for FlexiPay.
        """
        self.wait_for_element(self.btn_bank_proceed)
        self.perform_click(self.btn_bank_proceed)

    def click_on_tenure(self):
        """
        Perform a click action on tenure button
        """
        self.perform_click(self.btn_tenure)

    def wait_for_tenure_to_load(self):
        """
        Waits for tenure button to load
        """
        self.wait_for_element_to_be_clickable(self.btn_tenure)

    def get_cordinates(self):
        """
          Returns relative co-ordinates of tenure element on EMI page.
          Currently, tenure element is not identifiable using appium inspector
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
          Select an item from a drop-down menu at the specified coordinates.
        """
        TouchAction(self.driver).tap(x=x, y=y).perform()

    def validate_tenure_period_selected(self):
        """Retrieve and return the selected tenure period.
        Returns:
            str: The selected tenure period as text.
        """
        selected_period = self.fetch_text(self.lbl_selected_period)
        return selected_period

    def validate_shown_plan(self, selected_period):
        """Validate and return plan details based on the selected period.
        Args:
            selected_period (str): The selected plan period.
        Returns:
            list: List of plan details for the chosen period or all plans if 'selected_period' is 'All'.
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
        """Return plan details based on the selected period for pay later.
        Args:
            selected_period (str): The selected plan period.
        Returns:
            list: List of plan details for the chosen period or all plans if 'selected_period' is 'All'.
        """
        plan = self.fetch_text(self.lbl_plan)
        if selected_period == "15 days" or selected_period == "30 days" or selected_period == "60 days" or selected_period == "90 days":
            return [plan]
        else:
            selected_period == "All"
            total_plans = self.fetch_elements(self.lbl_plan)
            plan_details_when_selected_all = []
            for i in range(1, total_plans + 1):
                plan = f'(//*[@resource-id ="com.ezetap.basicapp:id/tvEmiTenure"])[{i}]'
                z = self.fetch_text(locator=(AppiumBy.XPATH, plan))
                plan_details_when_selected_all.append(z)
            return plan_details_when_selected_all

    def plan_details_without_interest_rate(self, plan):
        """Extract and return plan details without interest rates.
        Args:
            plan (list): List of plans containing interest rates.
        Returns:
            list: List of plans with only EMI details, excluding interest rates.
        """
        plan_without_interest = []
        for i in plan:
            result = (re.search(r'\d+\s*EMI', i)).group()
            plan_without_interest.append(result)
        return plan_without_interest

    def plan_details_without_intrest_rate_flexi_pay(self, plan):
        """
        Extract and return plan details without interest rates for flexi pay
        """
        plan_without_interest = []
        for i in plan:
            result = i.split('@')[0].strip()
            plan_without_interest.append(result)
        return plan_without_interest


