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
        df_card_details = pandas.read_excel(excel_path, sheet_name= "card_details")
        df_card_details.set_index("Transaction Type", inplace=True)
        df_card_details.fillna("", inplace=True)
        column_names = df_card_details.columns
        for column_name in column_names:
            dict_card_details[column_name] = str(df_card_details[column_name][transaction_type])
    except Exception as e:
        logger.warning(f"Unable to read the card details excel due to error {str(e)}")
    if dict_card_details:
        return dict_card_details
    else:
        return None


def get_device_data_details(ezetap_device_data: str) -> dict:
    """
    This method is used to decode the ezetap device data and get the details.

    :param ezetap_device_data:str
    :return: dict
    """
    current_start_position = 0
    current_end_position = 0
    current_tag = ""
    current_tag_length = 0
    current_tag_value = ""
    tags_with_value = {}
    while(current_end_position < len(ezetap_device_data)):
        current_end_position = current_end_position + 2
        current_tag = ezetap_device_data[current_start_position:current_end_position]
        if current_tag not in GlobalConstants.TWO_DIGIT_TAGS:
            current_end_position = current_end_position + 2
            current_tag = ezetap_device_data[current_start_position:current_end_position]
        if current_tag in GlobalConstants.DEVICE_DATA_TAGS.values():
            current_start_position = current_end_position
            current_end_position = current_end_position + 2
            if current_tag in GlobalConstants.TAGS_WITH_LENGTH_IN_HEX:
                current_tag_length = (int(ezetap_device_data[current_start_position:current_end_position], 16)) * 2
            else:
                current_tag_length = (int(ezetap_device_data[current_start_position:current_end_position])) * 2
            current_start_position = current_end_position
            current_end_position = current_end_position + current_tag_length
            current_tag_value = ezetap_device_data[current_start_position:current_end_position]
            tag_name = list(GlobalConstants.DEVICE_DATA_TAGS.keys())[list(GlobalConstants.DEVICE_DATA_TAGS.values()).index(current_tag)]
            tags_with_value[tag_name] = current_tag_value
        else:
            logger.error(f"Ezetap device data contains tag that is not available in known tags list.")
            tags_with_value = {}
            break
        current_start_position = current_end_position

    if tags_with_value:
        return tags_with_value
    else:
        return None


