import base64
import json
import os
import random
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd
import requests
from PageFactory import Base_Actions
from Utilities import ConfigReader, DBProcessor
from DataProvider import GlobalVariables, GlobalConstants
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)


def post(payload, API):
    url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", API)
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    json_resp = json.loads(resp.text)
    # print("")
    # print("")
    # log.logger.info("================= Execution Logs : " + API + " API response =================")
    # log.logger.info(str(json_resp))
    # assert json_resp['success'] == True, "API call for " + API + " failed. Response:" + str(json_resp)
    return json_resp


def send_request(api_details):
    payload = api_details['RequestBody']
    endPoint = api_details['EndPoint']
    protocol = api_details['Protocol']
    method = api_details['Method']
    headers = api_details['Header']
    url = ConfigReader.read_config("APIs", "baseUrl") + endPoint
    timeout = 180
    try:
        if api_details['ApiName'] == 'cybersource_success_callback':
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {json.dumps(payload)} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        if api_details['ApiName'] == 'callBackUpiMerchantRes':
            payload = urlencode(payload)
            resp = requests.request(method=method, url=str(url), headers=headers, data=payload)
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {payload} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        if api_details['ApiName'] == 'confirm_axisdirect' or api_details['ApiName'] == 'Submit_review':
            if api_details['ApiName'] == 'Submit_review':
                payload = payload
                resp = requests.request(method=method, url=str(url), data=payload)
            else:
                payload = payload['data']
                resp = requests.request(method=method, url=str(url), headers=headers, data=payload)
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {payload} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        if api_details['ApiName'] == 'apb_hash_generate':
            router_ip = Base_Actions.get_environment("str_exe_env_ip")
            query = "select psp_base_url from upi_psp_config where bank_code='APB';"
            logger.debug(f"Query to fetch psp_base_url from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            psp_base_url = result['psp_base_url'].values[0]
            logger.debug(f"psp_base_url from the upi_psp_config table is : {psp_base_url}")
            url = str(psp_base_url).replace('localhost', str(router_ip)) + endPoint
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {json.dumps(payload)} to trigger the {url} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        if api_details['ApiName'] == 'callbackBQRKotakAtos' or api_details['ApiName'] == 'callbackUpiKotakAtos':
            router_ip = Base_Actions.get_environment("str_exe_env_ip")
            url = str(protocol+"://" + router_ip + ":8002") + endPoint
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {json.dumps(payload)} to trigger the {url} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        if api_details['ApiName'] == 'axisfc_hash':
            router_ip = Base_Actions.get_environment("str_exe_env_ip")
            query = "select psp_base_url from upi_psp_config where bank_code='HDFC';"
            logger.debug(f"Query to fetch psp_base_url from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            psp_base_url = result['psp_base_url'].values[0]
            logger.debug(f"psp_base_url from the upi_psp_config table is : {psp_base_url}")
            url = str(psp_base_url).replace('localhost', str(router_ip)) + endPoint
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {json.dumps(payload)} to trigger the {url} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        # For IDFC Callback
        if api_details['ApiName'] == 'hmac_merch_cred':
            router_ip = Base_Actions.get_environment("str_exe_env_ip")
            query = "select psp_base_url from upi_psp_config where bank_code='IDFC';"
            logger.debug(f"Query to fetch psp_base_url from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            psp_base_url = result['psp_base_url'].values[0]
            logger.debug(f"psp_base_url from the upi_psp_config table is : {psp_base_url}")
            url = str(psp_base_url).replace('localhost', str(router_ip)) + endPoint
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            update_api_details_to_report_variables(resp)
            return resp

        if api_details['ApiName'] == 'callbackgeneratorUpiICICI':
            router_ip = Base_Actions.get_environment("str_exe_env_ip")
            query = "select psp_base_url from upi_psp_config where bank_code='ICICI_DIRECT';"
            logger.debug(f"Query to fetch psp_base_url from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            psp_base_url = result['psp_base_url'].values[0]
            logger.debug(f"psp_base_url from the upi_psp_config table is : {psp_base_url}")
            url = str(psp_base_url).replace('localhost', str(router_ip)) + endPoint
            resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
            update_api_details_to_report_variables(resp)
            json_resp = json.loads(resp.text)
            logger.debug(
                f"payload : {json.dumps(payload)} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
            return json_resp

        resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload), timeout=timeout)
        update_api_details_to_report_variables(resp)
        json_resp = resp.text if "{" not in resp.text else json.loads(resp.text)
        logger.debug(
            f"payload : {json.dumps(payload)} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
        return json_resp
    except requests.exceptions.Timeout:
        print("API server is not responding. Stopping the process...")
        logger.error(f"API server is not responding. Stopping the process...")
        os.system("pkill python3.8")


def update_api_details_to_report_variables(response: requests.models.Response):
    """
    This method is used to set the global variables that print the api details to the excel report
    :param response: Response
    """
    try:
        api_response_code = response.status_code
        api_response_time = response.elapsed.total_seconds().__round__(2)
        api_response_size = ((len(response.content))/1000).__round__(2)
        logger.debug(f"API response code is {api_response_code}")
        GlobalVariables.str_api_response_code = api_response_code
        logger.debug(f"API response time is {api_response_time}")
        GlobalVariables.str_api_response_time = api_response_time
        logger.debug(f"API response size is {api_response_size}")
        GlobalVariables.str_api_response_size = api_response_size
    except Exception as e:
        logger.error(f"Unable to update the api details to report due to error {str(e)}")


def get_request(api_details):
    headers = api_details['Header']
    endPoint = api_details['EndPoint']
    url = ConfigReader.read_config("APIs", "baseUrl") + endPoint
    resp = requests.get(url, headers=headers)
    json_resp = json.loads(resp.text)
    return json_resp


def create_campaign_reward(username: str, password: str, org_code: str, formatted_end_date: str, reward_name : str):
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
    end_date = datetime.now()+ timedelta(days=3)
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
