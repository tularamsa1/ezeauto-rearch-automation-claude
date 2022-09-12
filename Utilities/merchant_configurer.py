import random
from Utilities import DBProcessor, sqlite_processor
from Utilities.execution_log_processor import EzeAutoLogger
logger = EzeAutoLogger(__name__)



def check_if_pan_exists(pan_number: str) -> bool or None:
    """
    This method is used to check if the pan number exists in the environment.
    :param pan_number str
    :return: bool or None
    """
    try:
        query = "SELECT visa_merchant_id_primary, mastercard_merchant_id_primary, npci_merchant_id_primary, " \
                "visa_merchant_id_secondary, mastercard_merchant_id_secondary, npci_merchant_id_secondary FROM " \
                "bharatqr_merchant_config;"
        result = DBProcessor.getValueFromDB(query)
        column_names = result.columns
        for i in range(0, len(result)):
            for j in range(0, len(column_names)):
                if result[column_names[j]][i] == pan_number:
                    logger.debug(f"Pan number {pan_number} is available in the environment")
                    return True
        logger.debug(f"Pan number {pan_number} is not available in the environment")
        return False
    except Exception as e:
        logger.error(f"Unable to check if the pan number exists in the environment due to error {str(e)}")
        return None


def configure_terminal_dependency(merchant_code: str, acquirer_code: str, payment_gateway: str, payment_mode: str):
    """
    This method is used to configure the terminal dependency for a merchant.
    :param merchant_code str
    :param acquirer_code
    :param payment_gateway
    :param payment_mode
    """
    try:
        if payment_mode.lower() == 'upi':
            payment_mode = "UPI"
        else:
            payment_mode = "BHARATQR"
        query = f"SELECT * from terminal_dependency_config where org_code = '{merchant_code}' and " \
                f"payment_mode = '{payment_mode}' and acquirer_code = '{acquirer_code}' and " \
                f"payment_gateway = '{payment_gateway}';"
        result = DBProcessor.getValueFromDB(query)
        if len(result) > 0:
            logger.debug(f"Terminal dependency is already configured for {acquirer_code} of {merchant_code}")
        else:
            query = f"INSERT INTO terminal_dependency_config(org_code, payment_mode, acquirer_code, payment_gateway, " \
                    f"terminal_dependent_enabled, created_by, created_time, modified_by, modified_time) VALUES " \
                    f"('{merchant_code}', '{payment_mode}',  '{acquirer_code}', '{payment_gateway}',  1,  'ezetap', " \
                    f"now(), 'ezetap', now());"
            result = DBProcessor.setValueToDB(query)
            if DBProcessor.set_value_to_db_query_passed(result):
                logger.debug(f"Terminal dependency successfully configured for {acquirer_code} of {merchant_code}")
            else:
                logger.debug(f"Terminal dependency configuration failed for {acquirer_code} of {merchant_code}")

    except Exception as e:
        logger.error(f"Unable to configure the terminal dependency for {merchant_code} due to error {str(e)}")


def generate_random_number(number_of_digits: int) -> int:
    """
    This method is used to generate the random of a specific length in digits.
    :param number_of_digits int
    :return int
    """
    try:
        length_string = ""
        for i in range(0, number_of_digits):
            length_string = length_string + '9'
        lower_limit = int(length_string[:-1])
        upper_limit = int(length_string)
        return random.randint(lower_limit, upper_limit)
    except Exception as e:
        logger.error(f"Unable to generate the random number due to error {str(e)}")