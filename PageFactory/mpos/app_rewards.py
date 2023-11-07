import re
from datetime import datetime, timedelta
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from PageFactory.mpos.app_base_page import BasePage
from Utilities import DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


class Rewards(BasePage):
    btn_main_screen_my_rewards = (AppiumBy.XPATH, '//*[@text="My Rewards"]')
    btn_my_rewards_from_side_menu = (AppiumBy.ID, 'com.ezetap.basicapp:id/nav_rewards')
    btn_side_menu = (AppiumBy.ACCESSIBILITY_ID, 'Open navigation drawer')
    btn_goals = (AppiumBy.ID, 'com.ezetap.basicapp:id/ll_goals')
    btn_wins = (AppiumBy.ID, 'com.ezetap.basicapp:id/ll_wins')
    btn_rewards = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_rewards')
    txt_my_rewards = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTitle')
    txt_message_in_the_goals_tab_when_no_goals_are_created = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvText1')
    txt_tittle_goals = (AppiumBy.ID, 'com.ezetap.basicapp:id/goal_title')
    txt_cash_back_amount_goals = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_offer_one_name')
    txt_cash_back_amount_2_goals = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_offer_two_name')
    txt_tittle_wins = (AppiumBy.ID, 'com.ezetap.basicapp:id/goal_title')
    txt_cash_back_amount_wins = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_offer_one_name')
    txt_cash_back_amount_2_wins = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_offer_two_name')
    btn_rewards_claim = (AppiumBy.ID, 'com.ezetap.basicapp:id/btn_claimed')
    btn_process_1 = (AppiumBy.XPATH, '(//*[@text="Proceed"])[1]')
    btn_process_2 = (AppiumBy.XPATH, '(//*[@text="Proceed"])[2]')
    btn_claim_now = (AppiumBy.ID, 'com.ezetap.basicapp:id/btnClaimNow')
    btn_cancel = (AppiumBy.ID, 'com.ezetap.basicapp:id/buttonCancel')
    btn_rewards_claimed_from_rewards_tab = (
    AppiumBy.XPATH, '//*[@resource-id="com.ezetap.basicapp:id/rlCouponClaimed"]')
    txt_coupon_code = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCouponCode')
    txt_pin = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvPin')
    txt_rewards_claimed_tittle = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.basicapp:id/goal_title"])[1]')
    txt_coupon_code_from_wins_tab = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvCouponCode')
    btn_back = (AppiumBy.ID, 'com.ezetap.basicapp:id/ivBack')
    btn_previous_screen = (AppiumBy.XPATH, '//*[@resource-id = "com.ezetap.basicapp:id/imgToolbarBack"]')
    btn_back_go_to_home_screen = (AppiumBy.ID, 'com.ezetap.basicapp:id/imgToolbarBack')
    today_sales = (AppiumBy.ID, 'com.ezetap.basicapp:id/tvTodaySaleValue')
    txt_expiry = (AppiumBy.ID, 'com.ezetap.basicapp:id/tv_title')
    live_campaign = (AppiumBy.ID, '(//*[@index="0"])[17]')
    txt_percentage = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.basicapp:id/tv_progress"])[1]')
    txt_expiry_date = (AppiumBy.ID, 'com.ezetap.basicapp:id/goal_expiry_txt')
    btn_rewards_dashboard = (AppiumBy.ID, 'com.ezetap.basicapp:id/clGotoRewards')
    txt_goal_expiry_1 = (AppiumBy.XPATH, '(//*[@resource-id = "com.ezetap.basicapp:id/goal_expiry_txt"])[1]')
    txt_goal_expiry_2 = (AppiumBy.XPATH, '(//*[@resource-id = "com.ezetap.basicapp:id/goal_expiry_txt"])[2]')
    txt_goal_description = (AppiumBy.XPATH, '//*[@resource-id ="com.ezetap.basicapp:id/goal_title"]')
    txt_rewards = (AppiumBy.XPATH, '(//android.widget.ImageView[@content-desc="reward icon"])[2]')
    txt_expiry_status = (AppiumBy.XPATH, '//*[@resource-id = "com.ezetap.basicapp:id/btn_claimed"]')
    lbl_initial_percentage = (AppiumBy.XPATH, '//*[@text ="0%"]')
    lbl_final_percentage = (AppiumBy.XPATH, '//*[@text ="50%"]')
    btn_rewards_recent_claimed_rewards = (AppiumBy.XPATH, '(//*[@resource-id="com.ezetap.basicapp:id/rlCouponClaimed"])[1]')

    def __init__(self, driver):
        super().__init__(driver)

    def validate_my_rewards_tab_from_main_screen(self):
        """
        verifies the availability of the rewards button, after enabling rewards from org setting
        """
        self.wait_for_element(self.btn_main_screen_my_rewards)

    def click_on_my_rewards_tab_from_main_screen(self):
        """
        Clicks on the 'My Rewards' button from the main screen.
        """
        self.perform_click(self.btn_main_screen_my_rewards)

    def click_on_side_menu(self):
        """
        performs a click on the side menu from the home screen
        """
        self.wait_for_element_to_be_clickable(self.btn_side_menu)
        self.perform_click(self.btn_side_menu)

    def validate_my_rewards_tab_from_side_menu(self):
        """
        verifies the availability of the rewards button in the side menu after enabling rewards from org setting
        """
        self.wait_for_element(self.btn_my_rewards_from_side_menu)

    def click_on_my_rewards_from_side_menu(self):
        """
        performs click on the rewards button in the side menu after enabling rewards from org setting
        """
        self.wait_for_element_to_be_clickable(self.btn_my_rewards_from_side_menu)
        self.perform_click(self.btn_my_rewards_from_side_menu)

    def click_on_goals(self):
        """
        performs click on the goals tab
        """
        self.perform_click(self.btn_goals)

    def click_on_wins(self):
        """
        performs click on the wins tab
        """
        self.perform_click(self.btn_wins)

    def click_on_rewards_for_claimed_rewards(self):
        """
        performs click on the rewards tab to view the claimed rewards
        """
        self.perform_click(self.btn_rewards)

    def fetch_txt_from_my_rewards_screen(self):
        """
        fetches the tittle from the rewards home screen
        return: str
        """
        return self.fetch_text(self.txt_my_rewards)

    def fetch_txt_from_goals_tab(self):
        """
        fetches the text message that comes when there is no goals are created
        return: str
        """
        return self.fetch_text(self.txt_message_in_the_goals_tab_when_no_goals_are_created)

    def fetch_title_from_goals_tab(self):
        """
        fetches tittle from the LIVE goals
        return: str
        """
        self.wait_for_element(self.txt_tittle_goals)
        return self.fetch_text(self.txt_tittle_goals)

    def fetch_cash_back_from_goals_tab(self):
        """
        fetches cashback(coupon_enabled) amount from the goals tab
        return: str
        """
        self.wait_for_element(self.txt_cash_back_amount_goals)
        return self.fetch_text(self.txt_cash_back_amount_goals)

    def fetch_cash_back_from_goals_tab_2(self):
        """
        fetches amount from coupon type monthly fee cashback from the goals tab
        return: str
        """
        self.wait_for_element(self.txt_cash_back_amount_2_goals)
        return self.fetch_text(self.txt_cash_back_amount_2_goals)

    def fetch_title_from_wins_tab(self):
        """
        fetches tittle from completed goals,present in the wins tab
        return: str
        """
        self.wait_for_element(self.txt_tittle_wins)
        return self.fetch_text(self.txt_tittle_wins)

    def fetch_cash_back_from_wins_tab(self):
        """
        fetches amount for 'coupon type: monthly fee cashback' present in the wins tab
        return: str
        """
        self.wait_for_element(self.txt_cash_back_amount_wins)
        return self.fetch_text(self.txt_cash_back_amount_wins)

    def fetch_cash_back_from_wins_tab_2(self):
        """
        fetches cashback(coupon_enabled) amount from the wins tab
        return: str
        """
        self.wait_for_element(self.txt_cash_back_amount_2_wins)
        return self.fetch_text(self.txt_cash_back_amount_2_wins)

    def click_on_reward_btn(self):
        """
        performs click on the 'claim' button from the wins tab to claim rewards for completed goals
        return: str
        """
        self.perform_click(self.btn_rewards_claim)

    def click_on_proceed_btn_1(self):
        """
        performs click on the 1st coupon's(coupon_enabled) 'proceed' button
        """
        self.perform_click(self.btn_process_1)

    def click_on_proceed_btn_2(self):
        """
        performs click on the 2nd coupon's(monthly fee) 'proceed' button
        """
        self.perform_click(self.btn_process_2)

    def click_on_claim_now_btn(self):
        """
        performs click on the 'claim now' button to claim the rewards
        """
        self.perform_click(self.btn_claim_now)

    def click_on_cancel_btn(self):
        """
        performs click on the 'cancel' button present on 'send coupon details to merchants' popup screen
        """
        self.wait_for_element(self.btn_cancel)
        self.perform_click(self.btn_cancel)

    def fetch_txt_coupon_code(self):
        """
        Retrieves the coupon code from wins tab when claiming rewards.
        return : str
        """
        return self.fetch_text(self.txt_coupon_code_from_wins_tab)

    def click_on_back_btn(self):
        """
        performs click on the back button
        """
        self.perform_click(self.btn_back)

    def fetch_txt_coupon_code_from_rewards_tab(self):
        """
        Retrieves the coupon code from rewards tab after coupon is claimed.
        """
        return self.fetch_text(self.txt_coupon_code)

    def click_on_back_btn_to_go_main_page(self):
        """
        performs click on the back button to navigate to home screen
        """
        self.perform_click(self.btn_back_go_to_home_screen)

    def fetch_txt_expiry(self):
        """
        Retrieves the expiry text from expired goals
        return: str
        """
        return self.fetch_text(self.txt_expiry)

    def validate_live_campaign(self):
        """
        verifies the availability of the Live campaign in the goals tab
        """
        self.wait_for_element(self.live_campaign)

    def fetch_percentage_progress(self):
        """
        Retrieves the progression percentage from the live goals
        return: str
        """
        return self.fetch_text(self.txt_percentage)

    def wait_for_goals_tab_to_load(self):
        """
        waits until the rewards screen loaded successfully
        """
        self.wait_for_element(self.txt_message_in_the_goals_tab_when_no_goals_are_created)

    def click_on_recent_claimed_rewards(self):
        """
        performs click on the recently claimed rewards
        """
        self.perform_click(self.btn_rewards_recent_claimed_rewards)

    def fetch_pin(self):
        """
        Retrieves the pin from the coupon code from the coupon type 'Coupon_enabled(flipkart voucher)'
        return: str
        """
        return self.fetch_text(self.txt_pin)

    def scroll_to_expiry_text(self):
        """
       Performs scroll until the expiry block becomes visible.
        """
        self.scroll_to_text("expiry")

    def fetch_expiry_date(self):
        """
        Retrieves expiry date from expired campaign present in the goals or wins tab
        return: str
        """
        return self.fetch_text(self.txt_expiry_date)

    def fetch_campaign_expiry_status(self):
        """
        Retrieves the 'Expired' text from the expired goals present in the wins tab
        return: str
        """
        return self.fetch_text(self.btn_rewards_claim)

    def fetch_claimed_status(self):
        """
        Retrieves the claimed text from the claimed rewards present in the rewards tab
        return: str
        """
        return self.fetch_text(self.btn_rewards_claim)

    def get_rewards_dashboard_coordinates(self):
        """
        Retrieves the relative co_ordinates using bounds values of element from the rewards dashboard
        return: int
        """
        bounds_str = self.wait_for_element(self.txt_rewards).get_attribute("bounds")
        matches = re.findall(r'\d+', bounds_str)
        if len(matches) >= 2:
            b = int(matches[0])
            b1 = int(matches[0]) * 0.16
            c1 = int(matches[1])
            c1 = round(c1)
            b1 = round(b1)
            return b, b1, c1
        else:
            logger.info("Not enough numeric values found in the string")

    def scroll_to_element_horizontally(self, swipe_count: int, b: int, b1: int, c1: int):
        """
        performs scroll horizontally
        param: swipe_count: int
        param: b : int
        param: b1 : int
        param: c1 : int
        """
        for i in range(1, swipe_count + 1):
            action = TouchAction(self.driver)
            action.press(x=b, y=c1).move_to(x=b1, y=c1).release().perform()

    def click_on_rewards_from_dashboard(self):
        """
        performs click on the rewards button from rewards dashboard in the Home screen
        """
        self.perform_click(self.btn_rewards_dashboard)

    def fetch_text_goal_tab(self):
        """
        Clicks on the 'Goals' tab and returns its text content.
        """
        self.perform_click(self.btn_goals)
        return self.fetch_text(self.btn_goals)

    def fetch_text_rewards_tab(self):
        """
        Clicks on the 'Rewards' tab and returns its text content.
        """
        self.perform_click(self.btn_rewards)
        return self.fetch_text(self.btn_rewards)

    def fetch_text_win_tab(self):
        """
        Clicks on the 'Wins' tab and returns its text content.
        """
        self.perform_click(self.btn_wins)
        return self.fetch_text(self.btn_wins)

    def get_goal_expiry_date(self):
        """
        Returns expiry information(number of days or date) of a goal
        return: str
        """
        expiry_1 = self.fetch_text(self.txt_goal_expiry_1)
        expiry_2 = self.fetch_text(self.txt_goal_expiry_2)
        return expiry_1.strip(), expiry_2.strip()

    def get_goal_description(self):
        """
        Returns the description of the campaign
        return:  str
        """
        return self.fetch_text(self.txt_goal_description)

    def get_expiry_date(self):
        """
        Returns the expiry date of a goal.
        return:str
        """
        date = self.fetch_text(self.txt_expiry_date)
        return date.strip()

    def get_expiry_status(self):
        """
        Returns the expiry status of a goal
        return: str
        """
        return self.fetch_text(self.txt_expiry_status)

    def get_percentage_when_no_txn_done(self):
        """
        Gets the initial percentage without any transactions done.
        return: str
        """
        initial_percentage = self.fetch_text(self.lbl_initial_percentage)
        percentage_without_symbol = int(initial_percentage.strip('%').strip())
        return percentage_without_symbol

    def click_on_back_button(self):
        """
        Clicks the back button to navigate to the previous screen.
        """
        self.perform_click(self.btn_previous_screen)

    def get_percentage_when_txns_are_done(self):
        """
        Gets the final percentage after transactions are completed.
        """
        final_percentage = self.fetch_text(self.lbl_final_percentage)
        percentage_without_symbol = int(final_percentage.strip('%').strip())
        return percentage_without_symbol

    def remove_space(self, text: str):
        """Using regular expression to find the pattern ₹ followed by numbers """
        matches = re.findall(r'₹\s?(\d+)', text)
        if matches:
            amount = matches[0]
            return amount
        else:
            logger.info("No amount found in the text.")
            return None

def collect_all_campaign_ids_for_org(org_code: str):
    """
    This method retrieves and returns campaign IDs for "IN_PROGRESS," "WON," and "CLAIMED" status from database
    param: org_code: str
    return: list
    """
    query = f"select * from campaign_target_base where org_code = '{str(org_code)}' and status = 'IN_PROGRESS' ;"
    result = DBProcessor.getValueFromDB(query, 'rewards')
    in_progress_list_ids = result['campaign_target_base_id'].tolist()
    logger.info(f"fetched campaign_target_base_id from Db for status = IN_PROGRESS and id: {in_progress_list_ids}")
    query = f"select * from campaign_target_base where org_code = '{str(org_code)}' and status = 'WON' ;"
    result = DBProcessor.getValueFromDB(query, 'rewards')
    won_list_ids = result['campaign_target_base_id'].tolist()
    logger.info("fetched campaign_target_base_id from Db for status = WON")
    query = f"select * from campaign_target_base where org_code = '{str(org_code)}' and status = 'CLAIMED' ;"
    result = DBProcessor.getValueFromDB(query, 'rewards')
    claimed_list_ids = result['campaign_target_base_id'].tolist()
    logger.info("fetched campaign_target_base_id from Db for status = CLAIMED")
    return in_progress_list_ids, won_list_ids, claimed_list_ids


def revert_back_to_original_status(in_progress_list_ids: list, won_list_ids: list, claimed_list_ids: list):
    """
    Reverts campaign statuses to their original state from 'EXPIRY' status and updates claim expiry dates.
    param:
        in_progress_list_ids (list): List of campaign IDs in 'IN_PROGRESS' status.
        won_list_ids (list): List of campaign IDs in 'WON' status.
        claimed_list_ids (list): List of campaign IDs in 'CLAIMED' status.
    """
    end_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    for campaign_target_base_id in in_progress_list_ids:
        query = f"UPDATE campaign_target_base SET status = 'IN_PROGRESS', claim_expiry = '{str(end_date)}' WHERE status = 'EXPIRY' AND campaign_target_base_id = {str(campaign_target_base_id)};"
        DBProcessor.setValueToDB(query, 'rewards')
    for campaign_target_base_id in won_list_ids:
        query = f"UPDATE campaign_target_base SET status = 'WON', claim_expiry = '{str(end_date)}' WHERE status = 'EXPIRY' AND campaign_target_base_id = {str(campaign_target_base_id)} ;"
        DBProcessor.setValueToDB(query, 'rewards')
    for campaign_target_base_id in claimed_list_ids:
        query = f"UPDATE campaign_target_base SET status = 'CLAIMED', claim_expiry = '{str(end_date)}' WHERE status = 'EXPIRY' AND campaign_target_base_id = {str(campaign_target_base_id)};"
        DBProcessor.setValueToDB(query, 'rewards')
