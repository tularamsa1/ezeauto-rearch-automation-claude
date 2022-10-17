import pandas

from Utilities import ConfigReader
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

excel_path = ConfigReader.read_config_paths("System",
                                            "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"
def get_config_details_from_excel(config_merchant: str) -> dict:
    """
    This method is used to fetch details of a specific entry from the ConfigDetails sheet of merchant_user_creation xlsx.
    :param config_merchant:str
    :return: dict
    """
    dict_config_details = {}
    try:
        df_config_details = pandas.read_excel(excel_path, sheet_name="ConfigDetails")
        df_config_details.set_index("ConfigMerchant", inplace=True)
        df_config_details.fillna("", inplace=True)
        column_names = df_config_details.columns
        for column_name in column_names:
            dict_config_details[column_name] = str(df_config_details[column_name][config_merchant])
    except Exception as e:
        logger.warning(f"Unable to read the Config details excel due to error {str(e)}")
    if dict_config_details:
        return dict_config_details
    else:
        return None