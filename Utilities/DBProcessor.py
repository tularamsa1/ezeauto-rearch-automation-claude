import mysql
import pandas as pd
import pymysql
import sshtunnel
import os
import sqlite3
import json
from jinja2 import Template
from urllib.parse import urlencode
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
from DataProvider.GlobalConstants import SQLITE_DB_PATH


logger = EzeAutoLogger(__name__)


def _get_raw_api_details(api_name) -> dict:
    """
    This function gets api details in raw format from the sqlite3 database based on the api name
    params: api_name: str
    return: dict
    """
    

    try:
        if not os.path.isfile(SQLITE_DB_PATH):
            logger.error(f"Unable to find the DB file ({SQLITE_DB_PATH})")
            result = None
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            logger.info("Successfully connected to SQLITE DB")
            cursor = conn.cursor()
            col_name = 'ApiName'
            cursor.execute(f'''SELECT * FROM api_details WHERE {col_name} = "{api_name}"''')
            result = cursor.fetchone()
            columns = (col[0] for col in cursor.description)
            if result is None:
                logger.warning(f"No result found for the given api name ({api_name})")
 
    except Exception as e:
        logger.exception(e, exc_info=True)
        print(e)
        result = None

    finally:
        if result:
            output = {col: val for col, val in zip(columns, result)} 
            logger.debug(f"Query fetched the raw details: {output}")
        else:
            
            output = None

    return output


def _get_obj_api_details(api_name):
    """This is a private function to get the api details from the sqlite3 database based on the api name and converting the text json\
        to a dict"""
    res = _get_raw_api_details(api_name=api_name)

    if res:
        list_of_cols_to_be_converted_to_objects = ["Header", "RequestBody", "ExpectedResult"]

        # checking if details have RequestBody and ExpectedResult as keys
        if not (("RequestBody" in res) and ("ExpectedResult" in res)):
            logger.error(f"RequestBody and ExpectedResult are not present in the DB for the given api name ({api_name})")

        for key in list_of_cols_to_be_converted_to_objects:
            if key in res:
                try:
                    if res[key] is not None:  # dealing an issue of NULL in db
                        res[key] = json.loads(res[key])
                except Exception as e:
                    logger.exception(f"The passed dictionary is not json format string. Error: '{e}'", exc_info=True)
                    res = None
                    logger.critical("Output dictionary will be set to None")
                    print(e)
                    break
            else:
                logger.warning(f"{key} is not present in the DB for the given api name ({api_name})")
    else:
        logger.warning(f"No result found for the given api name ({api_name})")
    return res


def render_curl_data(curl_data_template, curl_data_to_insert):
    '''This function renders the curl data template with the curl data to insert'''
    logger.info("Curl Data Template is going to be populated with the curl data to insert")
    template = Template(curl_data_template)
    rendered_curl_data = template.render(curl_data_to_insert)
    # logger.info("Curl Data Template is going to be populated with the curl data to insert")
    return rendered_curl_data


def get_api_details(api_name:str, request_body:dict=None, expected_result:dict=None, curl_data:dict=None) -> dict:
    """
    This function gets api details from the sqlite3 database based on the api name
        params: 
            api_name: str
            request_body: dict (optional)
            expected_result: dict (optional)
        return: dict (or NoneType if not raws are fetched)

    """
    details = _get_obj_api_details(api_name=api_name)
    
    if details:
        
        if request_body:
            if isinstance(request_body, dict):
                for key in request_body:
                    if key in details['RequestBody']:
                        details['RequestBody'][key] = request_body[key]
                    else:
                        logger.warning(f"ReqestBody of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['RequestBody'][key] = request_body[key]
            else:
                logger.error(f"RequestBody is not a dict")

        if expected_result:
            if isinstance(expected_result, dict):
                for key in expected_result:
                    if key in details['ExpectedResult']:
                        details['ExpectedResult'][key] = expected_result[key]
                    else:
                        logger.warning(f"ExpectedResult of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['ExpectedResult'][key] = expected_result[key]
            else:
                logger.error(f"ExpectedResult is not a dict")

        if curl_data:
            if isinstance(curl_data, dict):
                if isinstance(details['CurlData'], str):
                    details['CurlData'] = render_curl_data(details['CurlData'], curl_data)
                else:
                    logger.error(f"The curl_data_template received from DB is not a string but is of type - {type(details['CurlData'])}")
            else:
                logger.error(f"curl_data is not a dictionary")


        logger.debug(f"Query fetched the result: {details}")
    
    return details


def get_value_from_db(query):
    return getValueFromDB(query)


def getValueFromDB(query):

    envi = ConfigReader.read_config("APIs", "env")
    try:
        ssh_private_key_password = ConfigReader.read_config("SSH", "ssh_private_key_password")
    except Exception as e:
        logger.warning(e)
        ssh_private_key_password = None


    tunnel = sshtunnel.SSHTunnelForwarder(
        ssh_address_or_host=envi.lower(), 
        remote_bind_address=('localhost', 3306),
        ssh_private_key_password=ssh_private_key_password
    )
    
    tunnel.start()
    conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database='ezetap_demo',
                           port=tunnel.local_bind_port)

    data = pd.read_sql_query(query, conn)
    conn.close()
    tunnel.close()
    return data

def setValueToDB(query):
    envi = ConfigReader.read_config("APIs", "env")
    try:
        ssh_private_key_password = ConfigReader.read_config("SSH", "ssh_private_key_password")
    except Exception as e:
        logger.warning(e)
        ssh_private_key_password = None

    tunnel = sshtunnel.SSHTunnelForwarder(
        ssh_address_or_host=envi.lower(),
        remote_bind_address=('localhost', 3306),
        ssh_private_key_password=ssh_private_key_password
    )

    tunnel.start()
    try:
        conn = mysql.connector.connect(host='localhost', user='ezedemo', passwd='abc123', database='ezetap_demo',
                                       port=tunnel.local_bind_port)
        mycursor = conn.cursor()
        try:
            mycursor.execute(query)
            conn.commit()
        except:
            print("Running Update query failed..!")
            logger.error("Running Update query failed..!")

        data = str(mycursor.rowcount) + ",record(s) affected"
        conn.close()
        tunnel.close()
    except:
        print("Not able to connect to Database for running update query")
        logger.error("Not able to connect to Database for running update query")
    return data


def convertDictToStr(payload):
    updated_data = urlencode(payload)
    return updated_data
    # data = '''pgMerchantId=7842823949384&meRes
    # =844E6E80B0963655D270BE20D2D4FCB1F90142289D55195860BB86EDB4DDC274F7383E6F7FE2A56ED1E3213ED8CAFC9D3154E071FE683ED7CEDDBA5D7292A66CFB75D15F4042654BD1CF4F35D7300E756046F975C18D886673DC5933C7054EA76A91671FF700D839439A86A7752A2D76DF0715ACB42422CEB2551A80F311EAC7751B7617BC560400DCA8D94211D5D6621316B25A34C1FCC74B038F9F6760AF40EF378EAC6AF547BF831B403349BFAEBB58A3112290902ED7AC53623FB2FE89FA259A1F14B97C07A1C332DE4600080A6708DDA96BF1704BFFED7438A67316D1C2BB7985D3CE0C6124BF2'''
    #
    # out = parse_qs(data)
    # key_value_details = {key: value[0] for key, value in out.items() if type(value) == list and len(value) == 1}
    #
    # # changing whatever is value to be changed
    # key_value_details['pgMerchantId'] = "7842823949399"
    #
    # updated_data = urlencode(key_value_details)
    # updated_data
