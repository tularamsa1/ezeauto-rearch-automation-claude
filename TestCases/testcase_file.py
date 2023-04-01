# class Solution:
#     def searchInsert(self, nums: list, target: int) -> int:
#         if len(nums) > 0 and nums.__contains__(target):
#             return nums.index(target)
#         elif len(nums) == 0:
#             return 0
#         elif not nums.__contains__(target):
#             for i in range(len(nums)):
#                 if nums[i] < target:
#                     continue
#                 else:
#                     nums.insert(i, target)
#                     return i
#             return len(nums)
#
#
# solution = Solution()
# print(solution.searchInsert(nums = [1,3,5,6], target = 5))
# print(solution.searchInsert(nums = [1,3,5,6], target = 2))
# print(solution.searchInsert(nums = [1,3,5,6,10], target = 11))
#
import re
import time

from playwright.sync_api import Page, expect, Playwright
from DataProvider import GlobalVariables
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage


def test_sample(playwright: Playwright) -> None:
    # go to any web page
    # browser = playwright.firefox.launch(headless=False)
    # context = browser.new_context()
    # page1 = context.new_page()
    # page2 = context.new_page()
    # page1.goto('https://www.google.com')
    # page2.goto('https://www.bing.com')
    # browser.close()

    browser = playwright.firefox.launch(headless=False)

    # Create a new page and a new context
    page1 = browser.new_page()
    context = browser.new_context()
    page2 = context.new_page()

    # Set the viewport size of page1 to a very small size so that it is effectively hidden
    page1.set_viewport_size(viewport_size={'width': 1, 'height': 1})

    # Navigate each page to a different URL
    page1.goto('https://www.google.com')
    page2.goto('https://www.bing.com')

    # Close the browser instance
    browser.close()

    # browser = playwright.chromium.launch(headless=False)
    # context = browser.new_context()
    #
    # page = context.new_page()
    # page.goto('https://dev16.ezetap.com/cnp/remotepay/pay/?token=MPv8nLbsFJDy99UtquxA')
    # page.get_by_role("button", name="Credit Card").click()
    # page.get_by_placeholder("Name on Card").click()
    # page.get_by_placeholder("Name on Card").fill("Sandeep")
    # page.get_by_placeholder("Card number").click()
    # page.get_by_placeholder("Card number").click()
    # page.get_by_placeholder("Card number").fill("4000000000000119")
    # ddl_cardExpiryMonth = "//*[@id='cdk-accordion-child-0']/div/div/div[3]/div/select"
    # ddl_cardExpiryYear = "//*[@id='cdk-accordion-child-0']/div/div/div[4]/div/select"
    # page.locator(ddl_cardExpiryMonth).select_option("3")
    # time.sleep(3)
    # dropdown_element = page.select_option(ddl_cardExpiryMonth+f'/option[text="{3}"]')
    # print(dropdown_element)
    # dropdown_element.click()
    # dropdown_element.select_option(f'option[text="{ddl_cardExpiryYear}"]')
    # page.get_by_role("combobox").first.select_option("3")
    # page.get_by_role("combobox").nth(1).select_option("2048")
    #
    # page.get_by_placeholder("Enter CVV").click()
    # page.get_by_placeholder("Enter CVV").fill("123")
    # page.get_by_role("button", name="Proceed to pay").click()
    # page.wait_for_selector('//*[@id="page-wrapper"]/div/div/div/div/h3')



    # login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
    # login_page_portal.perform_login_to_portal(username="9660867345", password="A123456")
    # home_page_portal = PortalHomePage(GlobalVariables.portal_page)
    # home_page_portal.wait_for_home_page_load()
    # home_page_portal.search_merchant_name(str("DEV16TESTORG_9"))
    # # home_page_portal.page.locator('//button[.="switch"]').click()
    # home_page_portal.click_switch_button(str("DEV16TESTORG_9"))
    # # home_page_portal.perform_merchant_switched_verfication()
    # home_page_portal.click_transaction_search_menu()
    # # GlobalVariables.portal_page.locator("input[name=\"q\"]").fill("DEV16TESTORG_9")
    # # GlobalVariables.portal_page.keyboard.press("Enter")
    # # GlobalVariables.portal_page.get_by_role("button", name="switch").click(timeout=90000)
    # # GlobalVariables.portal_page.get_by_role("link", name="Transactions").click(timeout=90000)
    # # GlobalVariables.portal_page.get_by_role("link", name="Search", exact=True).click(timeout=90000)
    # GlobalVariables.portal_page.wait_for_load_state('domcontentloaded', timeout=300000)
    # portal_trans_history_page = PortalTransHistoryPage(GlobalVariables.portal_page)