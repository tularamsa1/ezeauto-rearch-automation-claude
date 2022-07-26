# import mysql
import pandas as pd
import pymysql
import sshtunnel
import os
import sqlite3
import json
from jinja2 import Template
from urllib.parse import urlencode

from DataProvider import GlobalConstants
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
from DataProvider.GlobalConstants import SQLITE_DB_PATH


logger = EzeAutoLogger(__name__)

api_details_excel_path = ConfigReader.read_config_paths("System", "automation_suite_path")+"/Runtime/api_details.xlsx"

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
                        logger.warning(f"RequestBody of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
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


def getValueFromDB(query:str, db_name: str = None):
    """
    This method is used to run a query and fetch the results from the specified db.
    Only following values should be passed for the db_name:
    1. information schema
    2. acquirer
    3. auth
    4. closedloop
    5. cnpware
    6. config
    7. ea
    8. elm
    9. eze_upi
    10. ezetap_demo
    11. khata
    12. mware
    13. rewards
    14. rule_engine
    15. sonar
    16. vas
    17. wware

    :param query:str db_name: str
    """
    dev11_db_names = {"information schema": "information_schema", "acquirer":"acquirer_demo",\
                      "auth": "auth_demo", "closedloop": "closedloop_demo", "cnpware": "cnpware_demo", \
                      "config": "config_apps", "ea": "ea", "elm": "elm", "eze_upi": "eze_upi", \
                      "ezetap_demo": "ezetap_demo", "khata": "khata", "mware": "mware_demo", \
                      "rewards": "rewards", "rule_engine": "rule_engine", "sonar": "sonar", "vas":"vas",\
                      "wware": "wware"}
    actual_db_name = ""
    if db_name is None:
        actual_db_name = dev11_db_names.get("ezetap_demo")
    else:
        actual_db_name = dev11_db_names.get(db_name)

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
    conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database=actual_db_name,
                           port=tunnel.local_bind_port)

    data = pd.read_sql_query(query, conn)
    conn.close()
    tunnel.close()
    return data

def setValueToDB(query, db_name="ezetap_demo") -> str:
    """
        This method is for running the DML query on the database.
        This takes database name and query as parameters.
        :return: string
        """
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
        conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database=db_name,
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



def update_api_details_db(api_details_list : list):
    """
    This method is used to update the api_details table of ezeauto.db.

    :param api_details_list : list
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        for api  in api_details_list:
                try:
                    if str(api['CurlData']) == '':
                        cursor.execute(f"insert into api_details(ApiName, Protocol, Method, EndPoint, Header, RequestBody, ExpectedResult, CurlData)values(\'{api['ApiName']}\', \'{api['Protocol']}\', \'{api['Method']}\', \'{api['EndPoint']}\', \'{api['Header']}\', \'{api['RequestBody']}\', \'{api['ExpectedResult']}\', \'{str(api['CurlData'])}\');")
                        conn.commit()
                        logger.info(f"Details of API {api['ApiName']} successfully added to the api_details db.")
                    else:
                        #For curl data to be entered, single quote should be given
                        curl_data = str(api['CurlData']).replace("'", """''""")
                        cursor.execute(
                            f"insert into api_details(ApiName, Protocol, Method, EndPoint, Header, RequestBody, ExpectedResult, CurlData)values(\"{api['ApiName']}\", \"{api['Protocol']}\", \"{api['Method']}\", \"{api['EndPoint']}\", \"{api['Header']}\", \"{api['RequestBody']}\", \"{api['ExpectedResult']}\", \'{curl_data}\');")
                        conn.commit()
                        logger.info(f"Details of API {api['ApiName']} successfully added to the api_details db.")
                except Exception as e:
                    logger.error(f"Unable to add details of API {api['ApiName']} into db due to error {e}")
    except Exception as e:
        logger.error(f"Unable to connect to the db due to error {e}")
    cursor.close()
    conn.close()


def get_api_details_list_from_excel() ->list:
    """
    This method is used for pulling the list of api's along with details that are added in the api_detail excel.
    :return: list
    """
    api_detail_excel_data = pandas.read_excel(api_details_excel_path, sheet_name="api_details", na_filter= False)
    api_list = []
    if len(api_detail_excel_data)>0:
        for i in range(0,len(api_detail_excel_data)):
            api_details = api_detail_excel_data.loc[i].to_dict()
            api_list.append(api_details)
    else:
        logger.warning("There are no entries in the api_details.xlsx file")
    return api_list