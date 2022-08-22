import json
from urllib.parse import urlencode
import requests

from PageFactory import Base_Actions
from Utilities import ConfigReader, DBProcessor
from DataProvider import GlobalVariables
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

    if api_details['ApiName'] == 'callBackUpiMerchantRes':
        payload = urlencode(payload)
        resp = requests.request(method=method, url=str(url), headers=headers, data=payload)
        json_resp = json.loads(resp.text)
        logger.debug(
            f"payload : {payload} to trigger the {endPoint} api and the API_OUTPUT is : {json_resp}")
        return json_resp

    if api_details['ApiName'] == 'confirm_axisdirect':
        payload = payload['data']
        resp = requests.request(method=method, url=str(url), headers=headers, data=payload)
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
        logger.debug(f"psp_base_url from the upi_merchant_config table is : {psp_base_url}")
        url = str(psp_base_url).replace('localhost', str(router_ip)) + endPoint
        resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
        json_resp = json.loads(resp.text)
        logger.debug(
            f"payload : {payload} to trigger the {url} api and the API_OUTPUT is : {json_resp}")
        return json_resp

    resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
    update_api_details_to_report_variables(resp)
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