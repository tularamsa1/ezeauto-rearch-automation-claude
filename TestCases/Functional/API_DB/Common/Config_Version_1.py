import requests
import json
import time
import pandas as pd
import pymysql as pymysql
import sshtunnel as sshtunnel
from tabulate import tabulate

script_exec_start = time.time()


def clean_json(text):
    return json.dumps(json.loads(str(text)), separators=(',', ':'))


def replace_quotes(text):
    return str(text).replace("'", '"')


def compare_text(text1, text2):
    if str(text1[:15]) == str(text2[:15]):
    #if str(text1) == str(text2):
        return 'Pass'
    else:
        return 'Fail'


env = 'dev11'
url = 'https://' + env + '.ezetap.com/api/2.0/ca/portal/fetch/data'
headers = {'Content-Type': 'application/json'}

df_raw = pd.read_csv('/home/ezetap/Downloads/config_inputs.csv')

actual_response_list = []
query_count = []
payload_list = df_raw['payload'].tolist()
fetch_key_list = df_raw['fetch_name'].tolist()
tunnel = sshtunnel.SSHTunnelForwarder(ssh_address_or_host="dev11", remote_bind_address=('localhost', 3306))
tunnel.start()
conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database='config_apps',
                         port=tunnel.local_bind_port)
for pl, fetch_key in zip(payload_list, fetch_key_list):
    #print(fetch_key)
    payload = pl.strip()
    # print(json.dumps(payload))
    response = requests.post(url, headers=headers, data=payload)
    json_resp = response.json()
    # print(json_resp)
    actual_response_list.append(json_resp)
    query = "select count(*) from external_api_adapter where rule_id = (select id from rule where fetch_option_id = (select id from fetch_option where fetch_key = '" + fetch_key + "') and active = 1);"
    data = pd.read_sql_query(query,conn)
    query_count.append(data['count(*)'].iloc[0])

df = df_raw.copy()
df['actual_response'] = actual_response_list

df['expected_response'] = df['expected_response'].apply(lambda x: replace_quotes(x))
df['actual_response'] = df['actual_response'].apply(lambda x: replace_quotes(x))
df['Result'] = df.apply(lambda x: compare_text(x['expected_response'], x['actual_response']), axis=1)
df['query_count']= query_count

df.to_csv('result.csv', index=None)


#Database query fetch
# tunnel = sshtunnel.SSHTunnelForwarder(ssh_address_or_host="dev11", remote_bind_address=('localhost', 3306))
# tunnel.start()
# conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database='config_apps',
#                            port=tunnel.local_bind_port)
# data = pd.read_sql_query("select count(*) from external_api_adapter where rule_id = (select id from rule where fetch_option_id = (select id from fetch_option where fetch_key = 'get_tax_outstandingV3') and active = 1);", conn)
# conn.close()
# tunnel.close()
# print(data['count(*)'].iloc[0])
# #print(tabulate(data, tablefmt='psql'))

script_exec_end = time.time()
print('TC Count := ', len(df))
print('Test Script Completed & Results Saved: Time taken is ', round((script_exec_end - script_exec_start), 2),
      'seconds')