import pandas as pd
import pymysql
import sshtunnel
import os
import sqlite3
import json
from urllib.parse import parse_qs, urlencode
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
        list_of_cols_to_be_converted_to_objects = ["Header", "RequestBody", "ResponseValidation"]

        # checking if details have RequestBody and ResponseValidation as keys
        if not (("RequestBody" in res) and ("ResponseValidation" in res)):
            logger.error(
                f"RequestBody and ResponseValidation are not present in the DB for the given api name ({api_name})")

        for key in list_of_cols_to_be_converted_to_objects:
            if key in res:
                try:
                    res[key] = json.loads(res[key])
                except Exception as e:
                    logger.exception(e, exc_info=True)
                    print(e)
            else:
                logger.warning(f"{key} is not present in the DB for the given api name ({api_name})")
    else:
        logger.warning(f"No result found for the given api name ({api_name})")
    return res


def get_api_details(api_name: str, request_body: dict = None, response_validation: dict = None):
    """
    This function gets api details from the sqlite3 database based on the api name
        params: 
            api_name: str
            request_body: dict (optional)
            response_validation: dict (optional)
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
                        logger.warning(
                            f"ReqestBody of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['RequestBody'][key] = request_body[key]
            else:
                logger.error(f"RequestBody is not a dict")

        if response_validation:
            if isinstance(response_validation, dict):
                for key in response_validation:
                    if key in details['ResponseValidation']:
                        details['ResponseValidation'][key] = response_validation[key]
                    else:
                        logger.warning(
                            f"ResponseValidation of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['ResponseValidation'][key] = response_validation[key]
            else:
                logger.error(f"ResponseValidation is not a dict")

        logger.debug(f"Query fetched the result: {details}")

    return details


def getValueFromDB(query):
    envi = ConfigReader.read_config("APIs", "env")

    tunnel = sshtunnel.SSHTunnelForwarder(ssh_address_or_host=envi.lower(), remote_bind_address=('localhost', 3306))
    tunnel.start()
    conn = pymysql.connect(host='localhost', user='ezedemo', passwd='abc123', database='ezetap_demo',
                           port=tunnel.local_bind_port)

    data = pd.read_sql_query(query, conn)
    conn.close()
    tunnel.close()
    return data


def convertDictToStr(data):
    # out = parse_qs(data)
    # key_value_details = {key: value[0] for key, value in out.items() if type(value) == list and len(value) == 1}

    # changing whatever is value to be changed

    updated_data = urlencode(data)
    return updated_data
