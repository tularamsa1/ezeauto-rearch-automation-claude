import random
import re
import time
from datetime import datetime
import pyautogui
from playwright.sync_api import Playwright, expect, Page

from DataProvider import GlobalVariables


def test_sample(playwright: Playwright) -> None:
    # go to any web page
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    page.goto("https://dev16.ezetap.com/portal/login/")
    page.locator("input[name=\"username\"]").fill("9660867344")
    page.locator("input[name=\"password\"]").fill("A123456")
    org_code = "DEV16TESTORG_9"
    page.get_by_role("button", name="Sign In").click()
    page.locator("input[name=\"q\"]").click()
    page.locator("input[name=\"q\"]").fill(org_code)
    page.keyboard.press("Enter")
    page.wait_for_load_state('networkidle', timeout=45000)
    # page.get_by_role("button", name="switch").click()
    page.wait_for_selector(selector='//button[.="switch"]', timeout=45000, state='visible').click()
    # page.click('//button[.="switch"]')
    # page.wait_for_timeout(45000)
    # page.locator('//button[.="switch"]').click(timeout=45000)
    locator = '//button[contains(text(),"' + org_code + '")]'
    # page.wait_for_load_state('networkidle', timeout=45000)
    page.wait_for_selector(selector=locator, timeout=45000, state="visible")
    context.close()
    page.close()
# from PageFactory.portal_remotePayPage import RemotePayTxnPage
# from Utilities import APIProcessor, DBProcessor
#
#
# def test_sample_1(playwright: Playwright) -> None:
#     # go to any web page
#     browser = playwright.chromium.launch(headless=False, slow_mo=2000)
#     context = browser.new_context()
#     page = context.new_page()
#
#     amount = random.randint(300, 399)
#     order_id = datetime.now().strftime('%m%d%H%M%S')
#     api_details = DBProcessor.get_api_details('Remotepay_Initiate',
#                                               request_body={"amount": amount, "externalRefNumber": order_id,
#                                                             "username": "7869657434", "password": "A123456"})
#     response = APIProcessor.send_request(api_details)
#     print(f"response received for the remotepay initiate : {response}")
#     paymentLinkUrl = response['paymentLink']
#     externalRef = response.get('externalRefNumber')
#     payment_intent_id = response.get('paymentIntentId')
#     page.goto(paymentLinkUrl)
#     remotePayUpiTxn = RemotePayTxnPage(page)
#     remotePayUpiTxn.clickOnRemotePayUPI()
#     remotePayUpiTxn.clickOnRemotePayLaunchUPI()
#
#     pyautogui.press("esc")
#     remotePayUpiTxn.clickOnRemotePayCancelUPI()
#     print('after canceling')
#     remotePayUpiTxn.clickOnRemotePayProceed()
#
#
#     # page.locator("input[name=\"username\"]").fill("9660867344")
#     # page.locator("input[name=\"password\"]").fill("A123456")
#     #
#     # page.get_by_role("button", name="Sign In").click()
#     # page.locator("input[name=\"q\"]").click()
#     # page.locator("input[name=\"q\"]").fill("DEV16TESTORG_9")
#     # page.keyboard.press("Enter")
#     # page.get_by_role("button", name="switch").click()
#     # page.get_by_role("link", name="Transactions").click()
#     # page.get_by_role("link", name="Search", exact=True).click()
#     # get_transaction_details_for_portal(page, '230303053801485E010068678')
#     page.close()
#     context.close()
#
#
# def get_transaction_details_for_portal(driver, txn_id):
#     transactionRow = ""
#     rowID = "ENT" + txn_id
#     transactionDetails = {}
#     total_transactions_count = len(driver.locator("//table[@id='table_txns']/tbody/tr"))
#     total_attributes_count = len(driver.locator("//table[@id='table_txns']/thead//th"))
#     for row in range(1, total_transactions_count + 1):
#         element = driver.locator("//table[@id='table_txns']/tbody/tr" + "[" + str(row) + "]")
#         if element.get_attribute("id") == rowID:
#             transactionRow = row
#             break
#     for col in range(1, total_attributes_count):
#         attribute = driver.locator("//table[@id='table_txns']/thead//th" + "[" + str(col) + "]").get_attribute("aria-label")
#         if attribute.__contains__(": activate to sort column ascending"):
#             attribute = attribute.replace(": activate to sort column ascending", "")
#         attributeValue = driver.locator("//table[@id='table_txns']/tbody/tr" + "[" + str(transactionRow) + "]/td[" + str(
#                                                       col) + "]").text
#         transactionDetails[attribute] = attributeValue
#     return transactionDetails
