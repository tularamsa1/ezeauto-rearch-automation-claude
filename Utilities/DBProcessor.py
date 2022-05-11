import pandas as pd
import pymysql
import sshtunnel

from Utilities import ConfigReader


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