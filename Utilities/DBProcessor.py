import pandas as pd
import pymysql
import sshtunnel
import os
import sqlite3

from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
from DataProvider.GlobalConstants import SQLITE_DB_PATH


logger = EzeAutoLogger(__name__)


def get_api_details(api_name) -> dict:
    """
    This function gets api details from the sqlite3 database based on the api name
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
            cursor.execute(f'''SELECT * FROM api_details where {col_name} = "{api_name}"''')
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
            logger.info(f"Query fetched the result: {output}")
        else:
            
            output = None

    return output



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


