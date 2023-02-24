import pandas

from Utilities import ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

excel_path = ConfigReader.read_config_paths("System",
                                            "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"

def get_ezegro_details_from_excel(user_type: str) -> dict:

    """
    This method is used to fetch details of a specific entry from the EzeGro Details sheet of merchant_user_creation xlsx.
    :param user_type:str
    :return: dict
    """

    dict_ezegro = {}
    try:
        df_ezegro = pandas.read_excel(excel_path, sheet_name="EzeGro")
        df_ezegro.set_index("UserType", inplace=True)
        df_ezegro.fillna("", inplace=True)
        column_names = df_ezegro.columns
        for column_name in column_names:
            dict_ezegro[column_name] = str(df_ezegro[column_name][user_type])
    except Exception as e:
        logger.warning(f"Unable to read the EzeGro details excel due to error {str(e)}")
    if dict_ezegro:
        return dict_ezegro
    else:
        return None



