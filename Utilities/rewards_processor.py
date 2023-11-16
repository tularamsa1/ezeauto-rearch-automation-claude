import base64
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import requests
from Utilities import ConfigReader
from DataProvider import GlobalConstants


def create_campaign_reward(username: str, password: str, org_code: str, formatted_end_date: str, reward_name: str):
    """
    Creates a campaign for rewards with the specified parameters and returns the API response.
    param: username : str
    param: password: str
    param: org_code: str
    param: formatted_end_date: str
    param: reward_name : str
    return: Api response
    """
    automation_suite_path = GlobalConstants.EZEAUTO_MAIN_DIR
    base_url = ConfigReader.read_config("APIs", "baseUrl")
    url = base_url + "/reward/api/1.0/campaign/createCustom"
    csv_file = automation_suite_path + "/Runtime/ORGS.csv"
    data = pd.read_csv(csv_file)
    data["Org_code"] = org_code
    data.to_csv(csv_file, index=False)
    tomorrow = datetime.now() + timedelta(days=1)
    formatted_date = tomorrow.strftime('%Y-%m-%d')
    random_number = random.randint(10000, 99999)
    amount = "{:,}".format(random_number)
    description = f"=========coupon enabled : {amount} ========="
    payload = {
        'campaignDto': '{"description": "' + description + '", "tnc": " Transactions below Rs. 50 will not be cons! check ","startDate": "' + formatted_date + '", "endDate": "' + formatted_end_date + '", "criticalTnc": " Transactions below Rs. 50 will not be consider ", "imgLink": "https://www.ezetap.com/images/logos/reward_card.png", "type": "VOLUME", "controlGroupPercentage": 5, "goal": [{"key": "filterKey", "value": "card_txn_amount", "operator": "EQ"}, {"key": "value", "value": "20000", "operator": "GOE"}, {"key": "minAmount", "value": "500", "operator": "GOE"}], "reward": [{"rewardName": "' + reward_name + '", "imgLink": "https://www.ezetap.com/images/logos/reward_flipkart.png", "xlImgLink": "https://www.ezetap.com/images/logos/reward_flipkart.png", "amount": 100, "criticaltnc": " Voucher can be partially redeemed across multiple purchases |  ", "tnc": " Flipkart houses everything one can possibly imagine, in-vo your life  ", "howToUse": " Please contact Flipkart at the toll free number  ", "rewardType": "COUPON_ENABLED", "denomination": "100:1"}, {"rewardName": "Discount on Monthly Fee", "imgLink": "https://www.ezetap.com/images/logos/reward_all_payment.png", "xlImgLink": "https://www.ezetap.com/images/logos/reward_all_payment.png", "amount": 100, "criticaltnc": " Discount in the form ", "tnc": " Lorem Ipsum is simply d ", "howToUse": "Click on the link", "rewardType": "CASHBACK"}]}'}
    orgs_code_file = [
        ('csvFile', ('ORGS.csv', open(csv_file, 'rb'), 'text/csv'))
    ]
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=orgs_code_file)
    return response


def update_campaign(username: str, password: str, campaign_id: str):
    """
    Updates a campaign's start date and status to 'PROD_READY' via API using provided credentials.
    param: username: str
    param: password: str
    param: campaign_id: str
    return: Api response
    """
    base_url = ConfigReader.read_config("APIs", "baseUrl")
    url = base_url + "reward/api/1.0/campaign/update"
    today_date = datetime.now().strftime('%Y-%m-%d')
    payload = {"campaignId": campaign_id, "startDate": today_date, "status": "PROD_READY"}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response


def create_campaign(username: str, password: str, org_code: str, reward_name: str):
    """
    Creates a campaign for rewards with the specified parameters and returns the API response.
    param: username : str
    param: password: str
    param: org_code: str
    param: reward_name : str
    return: Api response
    """
    automation_suite_path = GlobalConstants.EZEAUTO_MAIN_DIR
    base_url = ConfigReader.read_config("APIs", "baseUrl")
    url = base_url + "/reward/api/1.0/campaign/createCustom"
    csv_file = automation_suite_path + "/Runtime/ORGS.csv"
    data = pd.read_csv(csv_file)
    data["Org_code"] = org_code
    data.to_csv(csv_file, index=False)
    tomorrow = datetime.now() + timedelta(days=1)
    formatted_date = tomorrow.strftime('%Y-%m-%d')
    random_number = random.randint(10000, 99999)
    end_date = datetime.now() + timedelta(days=3)
    formatted_end_date = end_date.strftime('%Y-%m-%d')
    amount = "{:,}".format(random_number)
    description = f"=========coupon enabled : {amount} ========="
    payload = {
        'campaignDto': '{"description": "' + description + '", "tnc": " Transactions below Rs. 50 will not be cons! check ","startDate": "' + formatted_date + '", "endDate": "' + formatted_end_date + '", "criticalTnc": " Transactions below Rs. 50 will not be consider ", "imgLink": "https://www.ezetap.com/images/logos/reward_card.png", "type": "VOLUME", "controlGroupPercentage": 5, "goal": [{"key": "filterKey", "value": "card_txn_amount", "operator": "EQ"}, {"key": "value", "value": "20000", "operator": "GOE"}, {"key": "minAmount", "value": "500", "operator": "GOE"}], "reward": [{"rewardName": "' + reward_name + '", "imgLink": "https://www.ezetap.com/images/logos/reward_flipkart.png", "xlImgLink": "https://www.ezetap.com/images/logos/reward_flipkart.png", "amount": 100, "criticaltnc": " Voucher can be partially redeemed across multiple purchases |  ", "tnc": " Flipkart houses everything one can possibly imagine, in-vo your life  ", "howToUse": " Please contact Flipkart at the toll free number  ", "rewardType": "COUPON_ENABLED", "denomination": "100:1"}, {"rewardName": "Discount on Monthly Fee", "imgLink": "https://www.ezetap.com/images/logos/reward_all_payment.png", "xlImgLink": "https://www.ezetap.com/images/logos/reward_all_payment.png", "amount": 100, "criticaltnc": " Discount in the form ", "tnc": " Lorem Ipsum is simply d ", "howToUse": "Click on the link", "rewardType": "CASHBACK"}]}'}
    orgs_code_file = [
        ('csvFile', ('ORGS.csv', open(csv_file, 'rb'), 'text/csv'))
    ]
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=orgs_code_file)
    return response


def create_coupon(username: str, password: str, coupon_code: str, pin: int, unq_reward_name: str):
    """
    Creates a unique coupon code and pin for coupon type Coupon_Enabled
    param: username: str
    param: password: str
    param: coupon_code: str
    param: pin: int
    param: unq_reward_name: str
    return: response status_code
    """
    amount = 100
    reward_name = unq_reward_name
    tomorrow = datetime.now() + timedelta(days=3)
    coupon_code_expiry_date = tomorrow.strftime('%Y-%m-%d')
    extra_info = "voucherAct"
    txt1 = "for 10000txn"
    automation_suite_path = GlobalConstants.EZEAUTO_MAIN_DIR
    base_url = ConfigReader.read_config("APIs", "baseUrl")
    url = base_url + "reward/api/v1/coupon/populate"
    csv_file = automation_suite_path + "/Runtime/PopulateRewards.csv"
    print(csv_file)
    data = pd.read_csv(csv_file)
    data["REWARDNAME"] = reward_name
    data["AMOUNT"] = amount
    data["COUPONCODE"] = coupon_code
    data["PIN"] = str(pin)
    data["COUPONEXPIRY(YYYY-MM-DD)"] = coupon_code_expiry_date
    data["+extra info"] = extra_info
    data["txt1"] = txt1
    data.to_csv(csv_file, index=False)
    orgs_code_file = [
        ('csvFile', ('Populate rewards.csv', open(csv_file, 'rb'), 'text/csv'))
    ]
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    response = requests.request("POST", url, headers=headers, files=orgs_code_file)
    return response.status_code
