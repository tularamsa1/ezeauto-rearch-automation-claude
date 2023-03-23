import pandas
from Utilities import ConfigReader, DBProcessor
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

def delete_existing_ezegro_user(user: str):
    try:
        query1 = f"DELETE from merchant where mobile_number = '{user}';"
        logger.debug(f"Query for deleting user from merchant table: {query1}")
        result1 = DBProcessor.setValueToDB(query1,"ezestore")

        query2 = f"DELETE from user where mobile_number = '{user}';"
        logger.debug(f"Query for deleting user from user table: {query2}")
        result2 = DBProcessor.setValueToDB(query2, "ezestore")

        query3 = f"DELETE from agent where mobile_number = '{user}';"
        logger.debug(f"Query for deleting user from ezestore.agent table: {query3}")
        result3 = DBProcessor.setValueToDB(query3, "ezestore")

        query4 = f"DELETE from agent where mobile_number = '{user}';"
        logger.debug(f"Query for deleting user from clw.agent table: {query4}")
        result4 = DBProcessor.setValueToDB(query3, "closedloop")

        if DBProcessor.set_value_to_db_query_passed(result1) and DBProcessor.set_value_to_db_query_passed(result2) and DBProcessor.set_value_to_db_query_passed(result3)\
                and DBProcessor.set_value_to_db_query_passed(result4):
            logger.debug(f"User is successfully deleted from the ezestore system {result1, result2,result3}")
        else:
            logger.debug(f"User is not deleted from the ezestore system {result1, result2,result3}")
    except Exception as e:
        logger.error(f"Unable to delete user details from the system due to error {str(e)}")

def delete_existing_ezegro_customer(customer: str):
    try:
        query = f"DELETE from customer where mobile_number like '"+ str(customer)+"';"
        logger.debug(f"Query for deleting customer from customer table: {query}")
        result = DBProcessor.setValueToDB(query,"ezestore")
        logger.debug(f"Query result for delete: {result}")
    except Exception as e:
        logger.error(f"Unable to delete customer details from the system due to error {str(e)}")


def delete_existing_pickup_address(mobile_no: str):
    try:
        query = f"DELETE from address where mobile_number like '"+ str(mobile_no)+"';"
        logger.debug(f"Query for deleting pickup address mobile number from address table: {query}")
        result = DBProcessor.setValueToDB(query,"ezestore")
        logger.debug(f"Query result for delete: {result}")
    except Exception as e:
        logger.error(f"Unable to delete pickup address details from the system due to error {str(e)}")


