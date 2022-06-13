import json

import requests

from Utilities import ConfigReader
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

    # print("url", type(url))
    # print("endPoint", endPoint)
    # print("protocol", protocol)
    # print("method", method)
    # print("payload", type(payload))
    # print("payload", payload)
    # print("header",type(headers))

    resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
    json_resp = json.loads(resp.text)
    logger.debug(
        f"payload : {payload} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
    return json_resp


def sample():
    url = 'https://dev11.ezetap.com/api/2.0/txn/list'
    headers = {'Content-Type': 'application/json'}
    payload = {"username": "5784758454", "password": "A123456"}

    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    json_resp = json.loads(resp.text)
    print(json_resp)

# sample()