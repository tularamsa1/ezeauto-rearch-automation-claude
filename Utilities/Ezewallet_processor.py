import pandas

from Utilities import DBProcessor, ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger



logger = EzeAutoLogger(__name__)

org_code = ConfigReader.read_config("Ezewallet", "org")
admin_user = ConfigReader.read_config("Ezewallet", "admin_user")
admin_password = ConfigReader.read_config("Ezewallet", "admin_password")
agent_user = ConfigReader.read_config("Ezewallet", "agent_user")
agent_password = ConfigReader.read_config("Ezewallet", "agent_password")
logger.info(f"Ezewallet org and User details: {org_code}, {admin_user}, {admin_password}, {agent_user}, {agent_password}")


excel_path = ConfigReader.read_config_paths("System",
                                            "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"


def get_ezewallet_details_from_excel(eze_wallet_merchant: str) -> dict:

    """
    This method is used to fetch specific entry from the Ezewallet sheet of merchant_user_creation
    :param eze_wallet_merchant:str
    :return: dict
    """

    dict_eze_wallet = {}
    try:
        df_eze_wallet = pandas.read_excel(excel_path, sheet_name="Ezewallet")
        df_eze_wallet.set_index("EzewalletMerchant", inplace=True)
        df_eze_wallet.fillna("", inplace=True)
        column_names = df_eze_wallet.columns
        for column_name in column_names:
            dict_eze_wallet[column_name] = str(df_eze_wallet[column_name][eze_wallet_merchant])
    except Exception as e:
        logger.warning(f"Unable to read the Ezewallet details excel due to error {str(e)}")
    if dict_eze_wallet:
        return dict_eze_wallet
    else:
        return None

def db_reset():
    delete_wallet_txn_leg = "delete from wallet_txn_leg where wallet_txn_id in (select wallet_txn_id from wallet_txn where merchant_id = '" + org_code+ "');"
    delete_wallet_txn = "delete from wallet_txn where merchant_id = '" + org_code + "';"
    update_agency_account = "update account set balance = '0.00' where entity_id = '" + org_code + "';"
    update_admin_account = "update account set balance = '0.00' where entity_id = '" + admin_user + "';"
    update_agent_account = "update account set balance = '0.00' where entity_id = '" + agent_user + "';"
    querylist = [delete_wallet_txn_leg, delete_wallet_txn, update_agency_account, update_admin_account, update_agent_account]
    logger.info("============Data setting on ClosedLoop DB "+org_code+"===============")
    try:
        for li in querylist:
            DBProcessor.setValueToDB(li, "closedloop")
        logger.info("============Data setting is Successfull===============")
    except:
        logger.info("============Data setting is Failed===============")


def setup_ezewallet():
    db_reset()