import charge_slip_validator
from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger
import sshtunnel, pymysql
import pandas as pd

logger = EzeAutoLogger(__name__)


def get_value_from_db(query: str, db_name: str = 'ezetap_demo'):
    """
    This method is used to run a query and fetch the results from the specified db.
    :param query:str db_name: str
    """

    envi = "dev11"
    try:
        ssh_private_key_password = "sanmar"
    except Exception as e:
        print(e)
        ssh_private_key_password = None

    tunnel = sshtunnel.SSHTunnelForwarder(
        ssh_address_or_host=envi.lower(),
        remote_bind_address=('localhost', 3306),
        ssh_private_key_password=ssh_private_key_password
    )

    tunnel.start()
    df_query_result = ""
    try:
        db_username = ConfigReader.read_config("DBCredentials", "db_username")
        db_password = ConfigReader.read_config("DBCredentials", "db_password")
        logger.info(f"db_username : {db_username}, db_password : {db_password}")
        dict_db_credentials = {'username': f'{db_username}','password': f'{db_password}'}  # get_db_credentials_from_excel()
        logger.info(f"Trying to connect to {db_name} db with username '{dict_db_credentials['username']}' and password '{dict_db_credentials['password']}'")

        actual_db_name = db_name  # get_db_name_from_excel(db_name)
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



# ORIGINAL ===========================================================


def get_txn_record_details(txn_id:str) -> pd.Series:
    query = f'select * from txn where id="{txn_id}"'
    result = get_value_from_db(query)

    if result.shape[0]:
        if result.shape[0] == 1:
            pass   # the pass takes out of the if section. in all other cases exceptions are raised
        else:
            print(f"it seems multiple rows are there for txn_id: {txn_id}")
            raise Exception(f"it seems multiple rows are there for txn_id: {txn_id}")
    else:
        print(f"No records found for the txn_id: {txn_id}")
        raise Exception(f"No records found for the txn_id: {txn_id}")

    txn_details_from_db = result.iloc[0]
    return txn_details_from_db


def get_acquirer_code_n_payment_gateway_from_txn_id(txn_id:str):
    txn_details_from_db = get_txn_record_details(txn_id)
    return dict(
        acquirer_code=txn_details_from_db['acquirer_code'], 
        payment_gateway=txn_details_from_db['payment_gateway']
    )


banks_with_fiserv_ezetap_logo = {
    "ICICI": "FDC",
    "IDFC": "IDFC_FDC",
}  # this could read of json file


# txn_id = "230208164623518E010073286" # AXIS, ezetap
# url = "https://dev11.ezetap.com/r/o/SjAsWEYr/"  # AXIS, ezetap
# txn_id = "221220065151624E010023461"  # HDFC
# url = "https://dev11.ezetap.com/r/o/H2ma5l3w/"  # HDFC
# txn_id = "221220064941906E010037450"   # YES
# url = "https://dev11.ezetap.com/r/o/TkOVtk9v/"  # YES

# txn_id = "221220075216183E010073890" # KOTAK
# url = "https://dev11.ezetap.com/r/o/FcxpbCBt/"  # kOTAK

txn_id = "221220112224710E010078782"  # IDFC
url = ""   # IDC .....

txn_id = "221220075100689E010067887"  # APB
url = "https://dev11.ezetap.com/r/o/k5WNwhbk/"  # APB


acquirer_n_pg = get_acquirer_code_n_payment_gateway_from_txn_id(txn_id)
acquirer = acquirer_n_pg['acquirer_code']
pg = acquirer_n_pg['payment_gateway']

if pg in banks_with_fiserv_ezetap_logo.values():
    ezetap_logo = 'fiserv.ezetap'
else:
    ezetap_logo = 'ezetap'

company_logo_valid, bank_logo_valid = charge_slip_validator.validate_chargeslip_image_logos_from_url(url, bank=acquirer, company=ezetap_logo, visualize=False)
# company_logo_valid, bank_logo_valid

print(company_logo_valid, bank_logo_valid)

