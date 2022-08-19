import pandas
from DataProvider import GlobalConstants
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

def get_card_details_from_excel(transaction_type: str) -> dict:
    """
    This method is used to fetch details of a specific entry from the card details xlsx.
    :param transaction_type:str
    :return: dict
    """
    dict_card_details = {}
    try:
        excel_path = GlobalConstants.DATAPROVIDER_DIR+"/"+GlobalConstants.STR_CARD_DETAILS_FILE
        df_card_details = pandas.read_excel(excel_path)
        df_card_details.set_index("Transaction Type", inplace=True)
        df_card_details.fillna("", inplace=True)
        column_names = df_card_details.columns
        for column_name in column_names:
            dict_card_details[column_name] = df_card_details[column_name][transaction_type]
    except Exception as e:
        logger.warning(f"Unable to read the card details excel due to error {str(e)}")
    if dict_card_details:
        return dict_card_details
    else:
        return None