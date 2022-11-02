import pandas
from DataProvider import GlobalConstants, GlobalVariables
from Utilities import DBProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)
excel_path = GlobalConstants.DATAPROVIDER_DIR+"/"+GlobalConstants.STR_CARD_DETAILS_FILE


def get_card_details_from_excel(transaction_type: str) -> dict:
    """
    This method is used to fetch details of a specific entry from the card details xlsx.
    :param transaction_type:str
    :return: dict
    """
    dict_card_details = {}
    try:
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



def check_if_bin_exists(bin: str) -> bool:
    """
    This method is used for checking if the bin is already available in the system
    :param name: str
    :return: bool
    """
    try:
       df_bin_result = DBProcessor.getValueFromDB(f"select * from bin_info where bin = '{bin}';")
       if df_bin_result.empty:
           logger.info(f"Bin {bin} does not exist in this environment")
           return False
       else:
           logger.info(f"Bin {bin} already exist in this environment")
           return True
    except Exception as e:
        logger.error(f"Unable to search bin from db due to error {str(e)}")


def check_if_bin_brand_and_type_exists(bin: str, card_brand: str, card_type: str) -> bool:
    """
    This method is used for checking if the bin for specific card brand and type is already available in the system
    :param name: str
    :return: bool
    """
    try:
        df_bin_info_result = DBProcessor.getValueFromDB(f"select * from bin_info where bin ='{bin}' and payment_card_brand like '%{card_brand}%' and payment_card_type= '{card_type}';")
        if df_bin_info_result.empty:
            logger.info(f"Bin {bin} for card_brand {card_brand} and card_type {card_type} does not exist in this environment")
            return False
        else:
            logger.info(f"Bin {bin} for card_brand {card_brand} and card_type {card_type} already exist in this environment")
            return True
    except Exception as e:
        logger.error(f"Unable to search bin_info from db due to error {str(e)}")


def insert_bin_details_to_DB(bin: str, card_brand: str, card_type: str):
    try:
        query = f"INSERT INTO bin_info(bin,created_by,created_time,modified_by,modified_time,bank,country2_iso," \
                f"country3_iso,info,iso_country,payment_card_brand,payment_card_type,phone,www,classification," \
                f"lock_id,origin,emi_enabled,bank_code,cash_enabled) VALUES " \
                f"('{bin}','ezetap',now(),'ezetap',now(),'HDFC','IND','356',NULL,'INDIA','{card_brand}','{card_type}',NULL," \
                f"'http://www.ezetap.com',NULL,0,'HDFC',b'1','HDFC',b'0');"
        logger.debug(f"Query for Inserting bin {bin} in bin_info table: {query} ")
        result = DBProcessor.setValueToDB(query)
        if DBProcessor.set_value_to_db_query_passed(result):
            logger.debug(f"Bin: {bin} for card_brand: {card_brand} and card_type: {card_type} is successfully inserted to the system")
        else:
            logger.debug(f"Bin: {bin} for card_brand: {card_brand} and card_type: {card_type} is not inserted to the system")
    except Exception as e:
        logger.error(f"Unable to add bin: {bin} to the system due to error {str(e)}")



def update_bin_details_to_DB(bin: str, card_brand: str, card_type: str):
    try:
        if card_brand == "MASTER":
            card_brand = "MASTER_CARD"
        query = f"UPDATE bin_info set payment_card_brand = '{card_brand}', payment_card_type = '{card_type}' where bin = '{bin}';"
        logger.debug(f"Query for updating bin {bin} in bin_info table: {query}")
        result = DBProcessor.setValueToDB(query)
        if DBProcessor.set_value_to_db_query_passed(result):
            logger.debug(f"Bin: {bin} for card_brand: {card_brand} and card_type: {card_type} is successfully updated to the system")
        else:
            logger.debug(f"Bin: {bin} for card_brand: {card_brand} and card_type: {card_type} is not updated to the system")
    except Exception as e:
        logger.error(f"Unable to add bin: {bin} to the system due to error {str(e)}")


def update_card_bin_details():
    try:
        df_bin_details = pandas.read_excel(excel_path, sheet_name="bin_info")
        df_bin_details.fillna("", inplace=True)
        for index, data in df_bin_details.iterrows():
            bin_no = str(data['bin_no'])
            card_brand = str(data['card_brand'])
            card_type = str(data['card_type'])
            if check_if_bin_exists(bin_no):
                if not check_if_bin_brand_and_type_exists(bin_no, card_brand, card_type):
                    update_bin_details_to_DB(bin_no, card_brand, card_type)
            else:
                insert_bin_details_to_DB(bin_no, card_brand, card_type)

    except Exception as e:
        logger.warning(f"Unable to update the bin number due to error {str(e)}")











