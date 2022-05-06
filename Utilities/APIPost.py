import requests
import json


def post(payload,url):
        #url = 'https://demo1.ezetap.com/api/2.0/emi/preFetch'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        json_resp = response.json()
        return json_resp