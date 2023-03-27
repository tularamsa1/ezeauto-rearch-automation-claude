import pandas
import pandas as pd
import pymysql
import sshtunnel
import os
import sqlite3
import json
from jinja2 import Template
import redis
from pymongo import MongoClient
from pandas import DataFrame as df
from DataProvider import GlobalConstants
from PageFactory import Base_Actions
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
from DataProvider.GlobalConstants import SQLITE_DB_PATH

logger = EzeAutoLogger(__name__)

api_details_excel_path = ConfigReader.read_config_paths("System", "automation_suite_path") + "/Runtime/api_details.xlsx"


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
            logger.error(
                f"RequestBody and ExpectedResult are not present in the DB for the given api name ({api_name})")

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


def get_api_details(api_name: str, request_body: dict = None, expected_result: dict = None,
                    curl_data: dict = None) -> dict:
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
                        logger.warning(
                            f"RequestBody of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['RequestBody'][key] = request_body[key]
            else:
                logger.error(f"RequestBody is not a dict")

        if expected_result:
            if isinstance(expected_result, dict):
                for key in expected_result:
                    if key in details['ExpectedResult']:
                        details['ExpectedResult'][key] = expected_result[key]
                    else:
                        logger.warning(
                            f"ExpectedResult of ({api_name}) does not contain the key {key}. Hence adding the key {key} ")
                        details['ExpectedResult'][key] = expected_result[key]
            else:
                logger.error(f"ExpectedResult is not a dict")

        if curl_data:
            if isinstance(curl_data, dict):
                if isinstance(details['CurlData'], str):
                    details['CurlData'] = render_curl_data(details['CurlData'], curl_data)
                else:
                    logger.error(
                        f"The curl_data_template received from DB is not a string but is of type - {type(details['CurlData'])}")
            else:
                logger.error(f"curl_data is not a dictionary")

        logger.debug(f"Query fetched the result: {details}")

    return details


def get_value_from_db(query):
    return getValueFromDB(query)


def getValueFromDB(query: str, db_name: str = 'ezetap_demo'):
    """
    This method is used to run a query and fetch the results from the specified db.
    :param query:str db_name: str
    """

    envi = ConfigReader.read_config("environment", "str_exe_env")
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
    df_query_result = ""
    try:
        dict_db_credentials = get_db_credentials_from_excel()
        logger.info(
            f"Trying to connect to {db_name} db with username '{dict_db_credentials['username']}' and password '{dict_db_credentials['password']}'")

        actual_db_name = get_db_name_from_excel(db_name)

        logger.info(f"DB name in environment is {actual_db_name}")

        conn = pymysql.connect(host='localhost', user=dict_db_credentials['username'],
                               passwd=dict_db_credentials['password'], database=actual_db_name,
                               port=tunnel.local_bind_port)

        df_query_result = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        logger.error(f"Unable to connect to run query in db due to error {str(e)}")
    tunnel.close()
    return df_query_result


def setValueToDB(query, db_name="ezetap_demo") -> str:
    """
        This method is for running the DML query on the database.
        This takes database name and query as parameters.
        :return: string
        """
    envi = ConfigReader.read_config("environment", "str_exe_env")
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
        dict_db_credentials = get_db_credentials_from_excel()
        logger.info(
            f"Trying to connect to {db_name} db with username '{dict_db_credentials['username']}' and password '{dict_db_credentials['password']}'")
        db_name_in_environment = get_db_name_from_excel(db_name)
        conn = pymysql.connect(host='localhost', user=dict_db_credentials['username'],
                               passwd=dict_db_credentials['password'], database=db_name_in_environment,
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


def update_api_details_db(api_details_list: list):
    """
    This method is used to update the api_details table of ezeauto.db.

    :param api_details_list : list
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        for api in api_details_list:
            try:
                if str(api['CurlData']) == '':
                    cursor.execute(
                        f"insert into api_details(ApiName, Protocol, Method, EndPoint, Header, RequestBody, ExpectedResult, CurlData)values(\'{api['ApiName']}\', \'{api['Protocol']}\', \'{api['Method']}\', \'{api['EndPoint']}\', \'{api['Header']}\', \'{api['RequestBody']}\', \'{api['ExpectedResult']}\', \'{str(api['CurlData'])}\');")
                    conn.commit()
                    logger.info(f"Details of API {api['ApiName']} successfully added to the api_details db.")
                else:
                    # For curl data to be entered, single quote should be given
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


def get_api_details_list_from_excel() -> list:
    """
    This method is used for pulling the list of api's along with details that are added in the api_detail excel.
    :return: list
    """
    api_detail_excel_data = pandas.read_excel(api_details_excel_path, sheet_name="api_details", na_filter=False)
    api_list = []
    if len(api_detail_excel_data) > 0:
        for i in range(0, len(api_detail_excel_data)):
            api_details = api_detail_excel_data.loc[i].to_dict()
            api_list.append(api_details)
    else:
        logger.warning("There are no entries in the api_details.xlsx file")
    return api_list


def get_db_name_from_excel(db_name: str) -> str:
    """
    This method is used to get the name of the db in the specific environment.
    :param db_name:str
    :return: str
    """
    db_name_in_envi = None
    try:
        df_db_details = pd.read_excel(GlobalConstants.DB_DETAILS_EXCEL_PATH, sheet_name="db")
        df_db_details.set_index("DB", inplace=True)
        df_db_details.fillna("", inplace=True)
        environments_in_excel = df_db_details.columns
        db_names_in_excel = df_db_details.index
        configured_environment = ConfigReader.read_config("environment", "str_exe_env")
        if db_name in db_names_in_excel:
            if configured_environment in environments_in_excel:
                db_name_in_envi = df_db_details[configured_environment][db_name]
                if db_name_in_envi == "":
                    logger.warning(f"No value set for {db_name} db of {configured_environment} envi in db_details.xlsx")
                    db_name_in_envi = None
            else:
                logger.error(f"Configured environment is not available in the db_details excel.")
        else:
            logger.error(f"Db {db_name} is not available in the db_details excel.")
    except Exception as e:
        logger.error(f"Unable to get the db name in the envi {configured_environment} due to error {str(e)}")
    return db_name_in_envi


def get_db_credentials_from_excel() -> dict:
    """
    This method is used to get the username and password associated with an envi.
    :return: dict
    """
    dict_credentials = {}
    configured_environment = ConfigReader.read_config("environment", "str_exe_env")
    try:
        df_credentials = pd.read_excel(GlobalConstants.DB_DETAILS_EXCEL_PATH, sheet_name="credentials")
        df_credentials.set_index("environment", inplace=True)
        available_environments = df_credentials.index
        if configured_environment in available_environments:
            dict_credentials['username'] = df_credentials['username'][configured_environment]
            dict_credentials['password'] = df_credentials['password'][configured_environment]
        else:
            logger.warning(f"Configured environment '{configured_environment}' is not available in db details excel.")
    except Exception as e:
        logger.error(f"Unable to get the db credentials from excel due to error {str(e)}")
    if dict_credentials:
        return dict_credentials
    else:
        return None


def set_value_to_db_query_passed(query_result: str) -> bool:
    """
    This method is to validate if the set value to db query was successful.
    This is validated by checking if at least one row was updated.
    :param query_result str
    :return: bool
    """
    rows_affected = int(query_result[0:query_result.index(",record(s) affected")])
    if rows_affected > 0:
        return True
    else:
        return False


def delete_value_from_db(query, db_name="ezetap_demo") -> str:
    """
        This method is for running the DML query on the database.
        This takes database name and query as parameters.
        :return: string
        """
    envi = ConfigReader.read_config("environment", "str_exe_env")
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
        dict_db_credentials = get_db_credentials_from_excel()
        logger.info(
            f"Trying to connect to {db_name} db with username '{dict_db_credentials['username']}' and password '{dict_db_credentials['password']}'")
        db_name_in_environment = get_db_name_from_excel(db_name)
        conn = pymysql.connect(host='localhost', user=dict_db_credentials['username'],
                               passwd=dict_db_credentials['password'], database=db_name_in_environment,
                               port=tunnel.local_bind_port)
        mycursor = conn.cursor()
        try:
            mycursor.execute(query)
            conn.commit()
        except:
            print("Running Delete query failed..!")
            logger.error("Running Delete query failed..!")

        data = str(mycursor.rowcount) + ",record(s) affected"
        conn.close()
        tunnel.close()
    except:
        print("Not able to connect to Database for running delete query")
        logger.error("Not able to connect to Database for running delete query")
    return data


def get_redis_data(data):
    try:
        logger.info(f"Device data to be checked in redis is {data}")
        logger.info(f"Connecting to redis")

        try:
            host_ip = Base_Actions.get_environment("str_exe_env_ip")
            pool = redis.ConnectionPool(host=host_ip, port=6379)  # host= ip address of dev envi, port should be redis configured Port
            r = redis.Redis(connection_pool=pool)

            result_server_1 = r.smembers('LIVE_P2P_server-1')
            result_server_2 = r.smembers('LIVE_P2P_server-2')
        except:
            logger.debug(f"Redis connection data, {r}")
            logger.error(f"Exception in redis connection")

        logger.info(f"Elements in server-1 , {result_server_1}")
        logger.info(f"Elements in server-2 , {result_server_2}")

        redis_device_conn_1 = False
        redis_device_conn_2 = False

        # Both servers are empty
        if len(result_server_1) == 0 and len(result_server_2) == 0:
            logger.info(f"Both redis servers are empty")
            redis_device_conn_1 = False
            redis_device_conn_2 = False

        # Both the servers are not empty
        elif len(result_server_1) > 0 and len(result_server_2) > 0:
            logger.info(f"Both redis servers are populated")
            for element in result_server_1:
                logger.info(f"Element in server-1 is {element}")
                if str(element) == data:
                    logger.debug(f"Element found in server-1 : {element}")
                    redis_device_conn_1 = True
                    break
                else:
                    redis_device_conn_1 = False
                    continue

            for element in result_server_2:
                logger.info(f"Element in server-2 is {element}")
                if str(element) == data:
                    logger.debug(f"Element found in server-2 : {element}")
                    redis_device_conn_2 = True
                    break
                else:
                    redis_device_conn_2 = False
                    continue

        # One of the server is not empty
        else:
            logger.info(f"One of the server is having data")
            if len(result_server_1) > 0:
                logger.info(f"Server-1 has data, and server-2 is empty")
                for element in result_server_1:
                    logger.info(f"Element in server-1 is {element}")
                    if str(element) == data:
                        logger.debug(f"Element found in server-1 : {element}")
                        redis_device_conn_1 = True
                        break
                    else:
                        redis_device_conn_1 = False
                        continue
            else:
                logger.info(f"Server-1 is empty")

            if len(result_server_2) > 0:
                logger.info(f"Server-2 has data, and server-1 is empty")
                for element in result_server_2:
                    logger.info(f"Element in server-2 is {element}")
                    if str(element) == data:
                        logger.debug(f"Element found in server-2 : {element}")
                        redis_device_conn_2 = True
                        break
                    else:
                        redis_device_conn_2 = False
                        continue
            else:
                logger.info(f"Server-2 is empty")

        if redis_device_conn_1 == True and redis_device_conn_2 == True:
            logger.error(f"Device is connected in both servers in redis")
            return True

        elif redis_device_conn_1 == True or redis_device_conn_2 == True:
            logger.debug(f"Device is connected with one redis server")
            return True

        else:
            logger.error(f"Device is not connected with redis server")
            return False
    except:
        logger.error(f"Exception in retrieving data from redis server")


def getvaluefromMongo(db_name: str, collection: str, query: str):
    env_ip = ConfigReader.read_config("environment","str_exe_env_ip")
    try:
        conn = MongoClient(f"mongodb://{env_ip}:27017")
        mydb = conn[db_name]
        mycol = mydb[collection]
        mydoc = df(mycol.find(query))
        return mydoc
    except Exception as e:
        logger.error(f"Unable to connect to Mongo DB from Environment:{env_ip} due to error {str(e)}")


def getAggregateValueFromMongo(db_name: str, collection: str, query: str):
    env_ip = ConfigReader.read_config("environment","str_exe_env_ip")
    try:
        conn = MongoClient(f"mongodb://{env_ip}:27017")
        mydb = conn[db_name]
        mycol = mydb[collection]
        mydoc = df(mycol.aggregate(query))
        return mydoc
    except Exception as e:
        logger.error(f"Unable to connect to Mongo DB for aggregate method from Environment:{env_ip} due to error {str(e)}")