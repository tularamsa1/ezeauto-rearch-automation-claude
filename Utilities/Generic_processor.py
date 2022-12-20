import pandas

from Utilities import ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

excel_path = ConfigReader.read_config_paths("System",
                                            "automation_suite_path") + "/DataProvider/merchant_user_creation.xlsx"

def get_generic_details_from_excel(generic_merchant: str) -> dict:

    """
    This method is used to fetch details of a specific entry from the Generic Details sheet of merchant_user_creation xlsx.
    :param generic_merchant:str
    :return: dict
    """

    dict_generic = {}
    try:
        df_generic = pandas.read_excel(excel_path, sheet_name="Generic")
        df_generic.set_index("GenericMerchant", inplace=True)
        df_generic.fillna("", inplace=True)
        column_names = df_generic.columns
        for column_name in column_names:
            dict_generic[column_name] = str(df_generic[column_name][generic_merchant])
    except Exception as e:
        logger.warning(f"Unable to read the Generic details excel due to error {str(e)}")
    if dict_generic:
        return dict_generic
    else:
        return None


def update_org_employee_table(password_hash,org_code,username,portal_username,portal_password):

    """
    This method is used to update the password_hash value for org_employee table
    """

    update_query = "update org_employee set password_hash='" + password_hash + "' where username='" + str(username) + "';"
    logger.debug(f"Query to update org_employee table : {update_query}")
    update_result = DBProcessor.setValueToDB(update_query, "ezetap_demo")
    logger.debug(f"Query result for update: {update_result}")

    api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                          "password": portal_password})
    response = APIProcessor.send_request(api_details)
    logger.debug(f"Response received for DB refresh is : {response}")