import json
import random
import sqlite3
import requests
from DataProvider import GlobalConstants
from Utilities import DBProcessor, merchant_creator, ConfigReader, sqlite_processor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


def configure_merchants():
    """
    This method is used to configure all the required settings for the merchant.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("select * from merchants where CreationStatus = 'Created';")
        available_merchants = cursor.fetchall()
        if len(available_merchants) > 0:
            clear_merchant_config_related_tables()
            sqlite_processor.update_pg_details()
            sqlite_processor.update_remotepay_settings()
            configure_bqr_settings_through_api()
            configure_upi_settings_through_api()
            configure_bqr_settings_through_db()
            configure_upi_settings_through_db()
            configure_cnp_settings_through_db()
            configure_pg_settings_through_db()
            refresh_db()
        else:
            logger.debug("Merchant configuration skipped since there are no new merchants created.")
    except Exception as e:
        logger.error(f"Unable to configure the merchants due to error {str(e)}")


def configure_bqr_settings_through_api():
    """
    This method is used to configure the bqr settings for the merchants after creation.
    """
    api_details = merchant_creator.get_api_details_from_db("configureBqr")
    url = ConfigReader.read_config("APIs", "baseurl") + api_details["EndPoint"]
    headers = json.loads(api_details["Header"])
    lst_bqr_settings_api_body = generate_bqr_setting_api_for_all_merchants()
    if lst_bqr_settings_api_body:
        for bqr_setting_api_body in lst_bqr_settings_api_body:
            merchant_code = get_merchant_code_using_mid(bqr_setting_api_body['acquisitions'][0]['terminals'][0]['mid'])
            acquirer_code = bqr_setting_api_body['acquisitions'][0]['acquirerCode']
            payment_gateway = bqr_setting_api_body['acquisitions'][0]['paymentGateway']
            visa_pan = bqr_setting_api_body['mvisaPan']
            master_pan = bqr_setting_api_body['masterpassPan']
            rupay_pan = bqr_setting_api_body['rupayPan']
            configure_terminal_dependency(merchant_code, acquirer_code, payment_gateway, "BQR")
            payload = json.dumps(bqr_setting_api_body)
            logger.debug(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.debug(response.text)
            result = json.loads(response.text)
            if result["success"]:
                logger.debug(f"BQR setting through api done successfully for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "BQR", "API")
                update_setting_generated_values(merchant_code, acquirer_code, payment_gateway, visa_pan, master_pan,
                                                rupay_pan)
            else:
                logger.debug(f"BQR setting  through api failed for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "BQR", "FAILED")
    else:
        logger.debug(f"There are no merchants available for performing bqr settings.")


def configure_upi_settings_through_api():
    """
    This method is used to configure the upi settings for the merchants after creation.
    """
    api_details = merchant_creator.get_api_details_from_db("configureUpi")
    url = ConfigReader.read_config("APIs", "baseurl") + api_details["EndPoint"]
    headers = json.loads(api_details["Header"])
    lst_upi_settings_api_body = generate_upi_setting_api_for_all_merchants()
    if lst_upi_settings_api_body:
        for upi_setting_api_body in lst_upi_settings_api_body:
            merchant_code = get_merchant_code_using_mid(upi_setting_api_body['acquisitions'][0]['terminals'][0]['mid'])
            acquirer_code = upi_setting_api_body['acquisitions'][0]['acquirerCode']
            payment_gateway = upi_setting_api_body['acquisitions'][0]['paymentGateway']
            configure_terminal_dependency(merchant_code, acquirer_code, payment_gateway, "UPI")
            payload = json.dumps(upi_setting_api_body)
            logger.debug(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            logger.debug(response.text)
            result = json.loads(response.text)
            if result["success"]:
                logger.debug(f"UPI setting through api done successfully for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "UPI", "API")
            else:
                logger.debug(f"UPI setting through api failed for {acquirer_code} with {payment_gateway} "
                             f"of {merchant_code}.")
                update_config_result(merchant_code, acquirer_code, payment_gateway, "UPI", "FAILED")
    else:
        logger.debug(f"There are no merchants available for performing upi settings.")


def configure_bqr_settings_through_db():
    """
        This method is used to configure the bqr settings for all the merchants whose setting failed through api.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT MerchantCode, AcquirerCode, PaymentGateway from configuration_results WHERE "
                       f"SettingType = 'BQR' and SetThrough = 'FAILED';")
        lst_merchant_details = cursor.fetchall()
        cursor.close()
        conn.close()
        if lst_merchant_details:
            for merchant_details in lst_merchant_details:
                setting_details = get_setting_details(merchant_details[0], merchant_details[1], merchant_details[2])
                bqr_config_id = get_bharatqr_provider_config_id(setting_details['bqr_bank_code'])
                terminal_info_id = get_terminal_info_id(setting_details['merchant_code'],
                                                        setting_details['acquirer_code'],
                                                        setting_details['payment_gateway'],
                                                        setting_details['mid'],
                                                        setting_details['tid'])
                if not check_if_bqr_setting_exists(merchant_details[0], bqr_config_id, terminal_info_id):
                    query = generate_bqr_settings_query_for_merchant(merchant_details[0], merchant_details[1],
                                                                     merchant_details[2])
                    logger.debug(query)
                    result = DBProcessor.setValueToDB(query)
                    rows_affected = len(result)
                    if rows_affected > 0:
                        if check_if_bqr_setting_exists(merchant_details[0], bqr_config_id, terminal_info_id):
                            logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                         f"{setting_details['payment_gateway']} of {merchant_details[0]} successful.")
                            update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                                 setting_details['payment_gateway'], "BQR", "DB")
                        else:
                            logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                         f"{setting_details['payment_gateway']} of {merchant_details[0]} failed.")
                            update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                                 setting_details['payment_gateway'], "BQR", "FAILED")
                            update_setting_generated_values(setting_details['merchant_code'],
                                                            setting_details['acquirer_code'],
                                                            setting_details['payment_gateway'], "N/A", "N/A","N/A")
                    else:
                        logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                     f"{setting_details['payment_gateway']} of {merchant_details[0]} failed.")
                        update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                             setting_details['payment_gateway'], "BQR", "FAILED")
                        update_setting_generated_values(setting_details['merchant_code'],
                                                        setting_details['acquirer_code'],
                                                        setting_details['payment_gateway'], "N/A", "N/A", "N/A")
                else:
                    logger.debug(f"Configuration for {setting_details['acquirer_code']} with "
                                 f"{setting_details['payment_gateway']} of {merchant_details[0]} is already available.")
        else:
            logger.debug(f"No merchants available for configuring BQR through db.")
    except Exception as e:
        logger.error(f"Unable to configure the bqr setting due to error {str(e)}")


def configure_upi_settings_through_db():
    """
        This method is used to configure the upi settings for all the merchants whose setting failed through api.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT MerchantCode, AcquirerCode, PaymentGateway from configuration_results WHERE "
                       f"SettingType = 'UPI' and SetThrough = 'FAILED';")
        lst_merchant_details = cursor.fetchall()
        cursor.close()
        conn.close()
        if lst_merchant_details:
            for merchant_details in lst_merchant_details:
                setting_details = get_setting_details(merchant_details[0], merchant_details[1], merchant_details[2])
                terminal_info_id = get_terminal_info_id(setting_details['merchant_code'],
                                                        setting_details['acquirer_code'],
                                                        setting_details['payment_gateway'],
                                                        setting_details['mid'],
                                                        setting_details['tid'])
                if not check_if_upi_setting_exists(merchant_details[0], terminal_info_id):
                    query = generate_upi_settings_query_for_merchant(merchant_details[0], merchant_details[1],
                                                                     merchant_details[2])
                    logger.debug(query)
                    result = DBProcessor.setValueToDB(query)
                    rows_affected = len(result)
                    if rows_affected > 0:
                        if check_if_upi_setting_exists(merchant_details[0], terminal_info_id):
                            logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                         f"{setting_details['payment_gateway']} of {merchant_details[0]} successful.")
                            update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                                 setting_details['payment_gateway'], "UPI", "DB")
                        else:
                            logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                         f"{setting_details['payment_gateway']} of {merchant_details[0]} failed.")
                            update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                                 setting_details['payment_gateway'], "UPI", "FAILED")
                    else:
                        logger.debug(f"Setting for {setting_details['acquirer_code']} with "
                                     f"{setting_details['payment_gateway']} of {merchant_details[0]} failed.")
                        update_config_result(setting_details['merchant_code'], setting_details['acquirer_code'],
                                             setting_details['payment_gateway'], "UPI", "FAILED")
                else:
                    logger.debug(f"Configuration for {setting_details['acquirer_code']} with "
                                 f"{setting_details['payment_gateway']} of {merchant_details[0]} is already available.")
        else:
            logger.debug(f"No merchants available for configuring upi through db.")
    except Exception as e:
        logger.error(f"Unable to configure the bqr setting due to error {str(e)}")


def configure_cnp_settings_through_db():
    """
        This method is used to configure the cnp settings for all the merchants.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select * from merchants where CreationStatus in ('Created') and "
                       f"Availability = 'Available';")
        merchants = cursor.fetchall()
        if merchants:
            for merchant in merchants:
                merchant_code = merchant[0]
                configure_cnp_setting_for_merchant(merchant_code)
        else:
            logger.debug(f"CNP configuration skipped since there is no new merchant created.")
    except Exception as e:
        logger.error(f"Unable to configure the cnp setting due to error {str(e)}")


def configure_pg_settings_through_db():
    """
        This method is used to configure the pg settings for all the merchants.
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select * from merchants where CreationStatus in ('Created') and "
                       f"Availability = 'Available';")
        merchants = cursor.fetchall()
        if merchants:
            for merchant in merchants:
                merchant_code = merchant[0]
                configure_pg_settings_for_merchant(merchant_code)
        else:
            logger.debug("PG configuration skipped since there are no new merchant created.")
    except Exception as e:
        logger.error(f"Unable to configure the cnp setting due to error {str(e)}")


def configure_pg_settings_for_merchant(merchant_code: str):
    """
    This method is used to generate the query for merchant pg configuration.
    :param merchant_code str
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pg_details;")
        lst_pg_details = cursor.fetchall()
        for pg_detail in lst_pg_details:
            if check_if_payment_gateway_exists_in_terminal_info_table(pg_detail[1]):
                payment_gateway = pg_detail[1]
            else:
                payment_gateway = get_payment_gateway_from_terminal_details(pg_detail[0])
            acquirer_code = pg_detail[0]
            setting_details = get_setting_details(merchant_code, acquirer_code, payment_gateway)
            merchant_id = mid = setting_details['mid']
            tid = setting_details['tid']
            terminal_info_id = get_terminal_info_id(merchant_code, acquirer_code, payment_gateway, mid, tid)
            api_key = pg_detail[2]
            secret = pg_detail[3]
            api_key2 = pg_detail[4]
            secret2 = pg_detail[5]
            api_key3 = pg_detail[6]
            secret3 = pg_detail[7]
            lock_id = pg_detail[8]
            hash_algo = pg_detail[9]
            mle_enabled = pg_detail[10]
            nb_enabled = pg_detail[11]
            nb_selected = pg_detail[12]
            cnp_cardpay_enabled = pg_detail[13]
            acc_label_id = pg_detail[14]
            transaction_timeout = pg_detail[15]
            payment_gateway = pg_detail[1]
            query = "INSERT INTO merchant_pg_config (org_code, payment_gateway, merchant_id, status, priority, " \
                    "api_key, secret, created_by, created_time, lock_id, modified_by, modified_time, hash_algo, " \
                    "mle_enabled, api_key2, secret2, nb_enabled, nb_selected, cnp_cardpay_enabled, terminal_info_id, " \
                    "acc_label_id, mid, tid, bank_code, api_key3, secret3, transaction_timeout) VALUES ('<org_code>'," \
                    "'<payment_gateway>','<merchant_id>','ACTIVE',0,'<api_key>','<secret>','ezetap',now(),<lock_id>," \
                    "'ezetap',now(),'<hash_algo>','<mle_enabled>','<api_key2>','<secret2>','<nb_enabled>'," \
                    "'<nb_selected>','<cnp_cardpay_enabled>', '<terminal_info_id>',<acc_label_id>,'<mid>','<tid>'," \
                    "'<bank_code>','<api_key3>','<secret3>',<transaction_timeout>);"
            query = query.replace('<org_code>', merchant_code)
            query = query.replace('<payment_gateway>', payment_gateway)
            query = query.replace('<merchant_id>', merchant_id)
            query = query.replace('<api_key>', api_key)
            query = query.replace('<secret>', secret)
            query = query.replace('<lock_id>', lock_id)
            query = query.replace('<hash_algo>', hash_algo)
            query = query.replace('<mle_enabled>', mle_enabled)
            query = query.replace('<api_key2>', api_key2)
            query = query.replace('<secret2>', secret2)
            query = query.replace('<nb_enabled>', nb_enabled)
            query = query.replace('<nb_selected>', nb_selected)
            query = query.replace('<cnp_cardpay_enabled>', cnp_cardpay_enabled)
            query = query.replace('<terminal_info_id>', str(terminal_info_id))
            query = query.replace('<acc_label_id>', acc_label_id)
            query = query.replace('<mid>', mid)
            query = query.replace('<tid>', tid)
            query = query.replace('<bank_code>', acquirer_code)
            query = query.replace('<api_key3>', api_key3)
            query = query.replace('<secret3>', secret3)
            query = query.replace('<transaction_timeout>', transaction_timeout)
            logger.debug(f"PG setting query of {merchant_code} is {query}")
            if not check_if_pg_config_exists(merchant_code, payment_gateway):
                logger.debug(f"Query for PG setting of {merchant_code} is {query}")
                result = DBProcessor.setValueToDB(query)
                if DBProcessor.set_value_to_db_query_passed(result):
                    if check_if_pg_config_exists(merchant_code, payment_gateway):
                        logger.debug(f"Pg configured successfully for {merchant_code} with {payment_gateway}.")
                        update_config_result(merchant_code, acquirer_code, payment_gateway, "PGconfig", "DB")
                    else:
                        logger.debug(f"PG configuration failed for {merchant_code} with {payment_gateway}.")
                        update_config_result(merchant_code, acquirer_code, payment_gateway, "PGconfig", "FAILED")
                else:
                    logger.debug(f"PG configuration failed for {merchant_code} with {payment_gateway}.")
                    update_config_result(merchant_code, acquirer_code, payment_gateway, "PGconfig", "FAILED")
            else:
                logger.debug(f"PG configuration already exists for {merchant_code} with {payment_gateway}.")


    except Exception as e:
        logger.error(f"Unable to generate the query for pg configuration due to error {str(e)}")


def configure_cnp_setting_for_merchant(merchant_code: str):
    """
    This method is used to generate the query to be executed for setting the cnp for merchant
    :param merchant_code str
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("select * from remotepay_settings;")
        remotepay_settings_detail = cursor.fetchall()
        for i in range(0, len(remotepay_settings_detail)):
            query = "INSERT INTO remotepay_setting (created_by, created_time, modified_by, modified_time, entity, " \
                    "entity_id, setting_name, setting_value, lock_id, component, inheritable, org_code) VALUES " \
                    "('<created_by>',now(),'<modified_by>',now(),'<entity>','<entity_id>','<setting_name>'," \
                    "'<setting_value>',<lock_id>,'<component>',<inheritable> '','<org_code>');"
            setting_name = remotepay_settings_detail[i][0]
            setting_value = remotepay_settings_detail[i][1]
            component = remotepay_settings_detail[i][2]
            lock_id = remotepay_settings_detail[i][3]
            entity = remotepay_settings_detail[i][4]
            entity_id = remotepay_settings_detail[i][5]
            inheritable = remotepay_settings_detail[i][6]
            query = query.replace('<created_by>', merchant_code)
            query = query.replace('<modified_by>', merchant_code)
            query = query.replace('<setting_name>', setting_name)
            query = query.replace('<setting_value>', setting_value)
            query = query.replace('<component>', component)
            query = query.replace('<lock_id>', lock_id)
            query = query.replace('<entity>', entity)
            query = query.replace('<entity_id>', entity_id)
            query = query.replace('<inheritable>', inheritable)
            query = query.replace('<org_code>', merchant_code)
            logger.debug(f"Query for cnp setting {setting_name} of {merchant_code} is {query}")
            if not check_if_remotepay_setting_exists(org_code=merchant_code, setting_name=setting_name):
                logger.debug(f"Query for cnp setting of {merchant_code} is {query}")
                result = DBProcessor.setValueToDB(query)
                if DBProcessor.set_value_to_db_query_passed(result):
                    if check_if_remotepay_setting_exists(merchant_code, setting_name):
                        logger.debug(f"{setting_name} setting for {merchant_code} done successfully.")
                        update_config_result(merchant_code, setting_name, 'N/A', "CNP", "DB")
                    else:
                        logger.debug(f"{setting_name} setting for {merchant_code} failed.")
                        update_config_result(merchant_code, setting_name, 'N/A', "CNP", "FAILED")
                else:
                    logger.debug(f"{setting_name} setting for {merchant_code} failed.")
                    update_config_result(merchant_code, setting_name, 'N/A', "CNP", "FAILED")
            else:
                logger.debug(f"{setting_name} setting for {merchant_code} is already available.")
    except Exception as e:
        logger.debug(f"Unable to generate the query for remotepay setting due to error {str(e)}")


def configure_terminal_dependency(merchant_code: str, acquirer_code: str, payment_gateway: str, payment_mode: str):
    """
    This method is used to configure the terminal dependency for a merchant.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :param payment_mode str
    """
    try:
        if payment_mode.lower() == 'upi':
            payment_mode = "UPI"
        else:
            payment_mode = "BHARATQR"

        if check_if_terminal_dependant(acquirer_code, payment_gateway, payment_mode) == "true":
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
                logger.debug(f"Query for configuring terminal dependency of {merchant_code} is {query}")
                result = DBProcessor.setValueToDB(query)
                if DBProcessor.set_value_to_db_query_passed(result):
                    logger.debug(f"Terminal dependency successfully configured for {acquirer_code} of {merchant_code}")
                else:
                    logger.debug(f"Terminal dependency configuration failed for {acquirer_code} of {merchant_code}")
        else:
            logger.debug(f"{payment_mode} of {acquirer_code} with {payment_gateway} is not terminal dependant.")
    except Exception as e:
        logger.error(f"Unable to configure the terminal dependency for {merchant_code} due to error {str(e)}")


def generate_bqr_setting_api_for_all_merchants() -> list or None:
    """
    This method is used to generate the bqr setting api body for all the available merchants
    :return: list
    """
    lst_bqr_settings = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MerchantCode FROM merchants WHERE CreationStatus IN ('Created');")
        merchant_details = cursor.fetchall()
        cursor.close()
        conn.close()
        if merchant_details:
            lst_merchants_code = []
            for merchant_details in merchant_details:
                lst_merchants_code.append(merchant_details[0])
            acquisitions_with_details = get_all_acquisition_details()
            lst_acquisition_details = []
            for acquisition_with_detail in acquisitions_with_details:
                if check_if_bqr_setting_required(acquisition_with_detail[0], acquisition_with_detail[1]):
                    acq_det = [acquisition_with_detail[0], acquisition_with_detail[1]]
                    lst_acquisition_details.append(acq_det)
            for merchant_code in lst_merchants_code:
                for acquisition in lst_acquisition_details:
                    lst_bqr_settings.append(generate_bqr_setting_api_body(merchant_code, acquisition[0], acquisition[1]))
        else:
            logger.debug(f"BQR configuration through api skipped since there is no new merchant created.")
    except Exception as e:
        logger.error(f"Unable to brq setting api list due to error {str(e)}")
        lst_bqr_settings = None
    return lst_bqr_settings


def generate_upi_setting_api_for_all_merchants() -> list or None:
    """
    This method is used to generate the upi setting api body for all the available merchants
    :return: list
    """
    lst_upi_settings = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MerchantCode FROM merchants WHERE CreationStatus IN ('Created');")
        merchant_details = cursor.fetchall()
        cursor.close()
        conn.close()
        if merchant_details:
            lst_merchants_code = []
            for merchant_details in merchant_details:
                lst_merchants_code.append(merchant_details[0])
            acquisitions_with_details = get_all_acquisition_details()
            lst_acquisition_details = []
            for acquisition_with_detail in acquisitions_with_details:
                if check_if_upi_setting_required(acquisition_with_detail[0], acquisition_with_detail[1]):
                    acq_det = [acquisition_with_detail[0], acquisition_with_detail[1]]
                    lst_acquisition_details.append(acq_det)
            for merchant_code in lst_merchants_code:
                for acquisition in lst_acquisition_details:
                    lst_upi_settings.append(generate_upi_setting_api_body(merchant_code, acquisition[0], acquisition[1]))
        else:
            logger.debug(f"UPI configuration through api skipped since there is no new merchant created.")
    except Exception as e:
        logger.error(f"Unable to upi setting api list due to error {str(e)}")
        lst_upi_settings = None
    return lst_upi_settings


def generate_bqr_setting_api_body(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict or None:
    """
    This method is used to generate the bqr setting api body for a specific acquirer code and payment
    gateway of a merchant.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: dict (merchant config api body)
    """
    try:
        merchant_configuration_api = json.loads(merchant_creator.get_api_details_from_db("configureBqr")['RequestBody'])
        settings = get_setting_details(merchant_code, acquirer_code, payment_gateway)
        merchant_configuration_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
        merchant_configuration_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
        merchant_configuration_api['bankCode'] = settings['bank_code']
        merchant_configuration_api['bharatQrBankCode'] = settings['bqr_bank_code']
        merchant_configuration_api['categoryCode'] = settings['category_code']
        merchant_configuration_api['name'] = settings['merchant_name']
        brand_pan_numbers = get_brand_pan_number(merchant_code, acquirer_code, payment_gateway)
        merchant_configuration_api['mvisaPan'] = brand_pan_numbers['visa_pan']
        merchant_configuration_api['masterpassPan'] = brand_pan_numbers['master_pan']
        merchant_configuration_api['rupayPan'] = brand_pan_numbers['rupay_pan']
        merchant_configuration_api['mVisaId'] = brand_pan_numbers['visa_pan']
        merchant_configuration_api['pan'] = str(settings['tid']).upper()
        merchant_configuration_api['acquisitions'][0]['acquirerCode'] = settings['acquirer_code']
        merchant_configuration_api['acquisitions'][0]['paymentGateway'] = settings['payment_gateway']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['mid'] = settings['mid']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['tid'] = settings['tid']
        if check_if_virtual_mid_required_for_bqr(acquirer_code, payment_gateway) == "True":
            merchant_configuration_api['virtualMid'] = 'V' + settings['mid']
        logger.debug(merchant_configuration_api)
        return merchant_configuration_api
    except Exception as e:
        logger.error(f"Unable to generate the merchant config api due to error {str(e)}")
        return None


def generate_upi_setting_api_body(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict or None:
    """
    This method is used to generate the upi setting api body for a specific acquirer code and payment
    gateway of a merchant.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: dict (merchant config api body)
    """
    try:
        merchant_configuration_api = json.loads(merchant_creator.get_api_details_from_db("configureUpi")['RequestBody'])
        settings = get_setting_details(merchant_code, acquirer_code, payment_gateway)
        merchant_configuration_api["username"] = ConfigReader.read_config("SuperUserCredentials", "username")
        merchant_configuration_api["password"] = ConfigReader.read_config("SuperUserCredentials", "password")
        merchant_configuration_api['bankCode'] = settings['bank_code']
        merchant_configuration_api['pspBankCode'] = settings['upi_bank_code']
        merchant_configuration_api['categoryCode'] = settings['category_code']
        merchant_configuration_api['name'] = settings['merchant_name']
        merchant_configuration_api['merchantCode'] = merchant_code
        merchant_configuration_api['pgMerchantId'] = settings['tid']
        merchant_configuration_api['acquisitions'][0]['acquirerCode'] = settings['acquirer_code']
        merchant_configuration_api['acquisitions'][0]['paymentGateway'] = settings['payment_gateway']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['mid'] = settings['mid']
        merchant_configuration_api['acquisitions'][0]['terminals'][0]['tid'] = settings['tid']
        add_key_to_upi_setting_api_body(merchant_configuration_api)
        merchant_configuration_api['vpa'] = settings['tid'] + "@upi"
        logger.debug(merchant_configuration_api)
        return merchant_configuration_api
    except Exception as e:
        logger.error(f"Unable to generate the merchant config api due to error {str(e)}")
        return None


def generate_bqr_settings_query_for_merchant(org_code: str, acquirer_code: str, payment_gateway: str) -> str or None:
    """
    This method is used to configure the bqr settings of all available merchants through db.
    :param org_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: str
    """
    try:
        setting_details = get_setting_details(org_code, acquirer_code, payment_gateway)
        mid = setting_details['mid']
        tid = setting_details['tid']
        merchant_name = setting_details['merchant_name']
        provider_name = setting_details['bqr_bank_code']
        category_code = setting_details['category_code']
        bank_code = setting_details['bank_code']
        bharatqr_provider_config_id = get_bharatqr_provider_config_id(provider_name)
        terminal_info_id = get_terminal_info_id(org_code, acquirer_code, payment_gateway, mid, tid)
        random_numbers = get_brand_pan_number(org_code, acquirer_code, payment_gateway)
        visa_pan =  random_numbers['visa_pan']
        master_pan = random_numbers['master_pan']
        rupay_pan = random_numbers['rupay_pan']
        query = f"insert into bharatqr_merchant_config (org_code,visa_merchant_id_primary," \
                f"mastercard_merchant_id_primary,npci_merchant_id_primary,merchant_ifsc,merchant_account_number," \
                f"currency_code,country_code,provider_id,status,merchant_name,merchant_city,merchant_pin_code," \
                f"merchant_category_code,bank_code,merchant_pan,terminal_info_id,created_by,created_time,modified_by," \
                f"modified_time) values ('<org_code>','<visa_pan>','<master_pan>','<rupay_pan>','KKBK0004589'," \
                f"'123456789012','356','IN','<bharatqr_provider_config_id>','ACTIVE','<merchant_name>'," \
                f"'MerchantCity','100000','<category_code>','<bank_code>','<merchant_pan>','<terminal_info_id>'," \
                f"'ezetap',now(),'ezetap',now());"
        query = query.replace("<org_code>",org_code)
        query = query.replace("<acquirer_code>", acquirer_code)
        query = query.replace("<payment_gateway>", payment_gateway)
        query = query.replace("<visa_pan>", visa_pan)
        query = query.replace("<master_pan>", master_pan)
        query = query.replace("<rupay_pan>", rupay_pan)
        query = query.replace("<provider_name>", provider_name)
        query = query.replace("<merchant_name>", merchant_name)
        query = query.replace("<category_code>", category_code)
        query = query.replace("<bank_code>", bank_code)
        query = query.replace("<merchant_pan>", tid)
        query = query.replace("<mid>", mid)
        query = query.replace("<tid>", tid)
        query = query.replace("<bharatqr_provider_config_id>", str(bharatqr_provider_config_id))
        query = query.replace("<terminal_info_id>", str(terminal_info_id))
        update_setting_generated_values(org_code, acquirer_code, payment_gateway, visa_pan, master_pan, rupay_pan)
        return query
    except Exception as e:
        logger.error(f"Unable to configure bqr settings through db due to error {str(e)}")
        return None


def generate_upi_query_template(acquirer_code: str, payment_gateway: str) -> str:
    """
    This method is used to generate the query template based on the acquisition and payment gateway.
    :param acquirer_code str
    :param payment_gateway str
    :return: str
    """
    try:
        query = "INSERT INTO upi_merchant_config (created_by, created_time, modified_by, modified_time, bank_code, " \
                "merchant_code, mid, name, org_code, pgMerchantId, status, terminal_info_id, tid, vpa, upi_app_key, " \
                "encKey, virtual_mid, virtual_tid) VALUES ('ezetap', now(), 'ezetap', now(), '<bank_code>', " \
                "'<category_code>', '<mid>', '<merchant_name>', '<org_code>', '<pgMerchantId>', 'ACTIVE', " \
                "'<terminal_info_id>', '<tid>', '<vpa>', '<upi_app_key>', '<encKey>', '<vmid>', '<vtid>');"
        if acquirer_code == "HDFC" and payment_gateway == "HDFC" or \
                acquirer_code == "AXIS" and payment_gateway == "AXIS" or \
                acquirer_code == "ICICI" and payment_gateway == "FDC":
            query = query.replace(", encKey, virtual_mid, virtual_tid", "")
            query = query.replace(", '<encKey>', '<vmid>', '<vtid>'","")
        elif acquirer_code == "YES" and payment_gateway == "ATOS" or \
                acquirer_code == "AXIS" and payment_gateway == "ATOS_TLE" or \
                acquirer_code == "KOTAK" and payment_gateway == "KOTAK_WL":
            query = query.replace(", upi_app_key, encKey, virtual_mid, virtual_tid", "")
            query = query.replace(", '<upi_app_key>', '<encKey>', '<vmid>', '<vtid>'", "")
        elif acquirer_code == "AIRP" and payment_gateway == "APB":
            query = query.replace(", virtual_mid, virtual_tid", "")
            query = query.replace(", '<vmid>', '<vtid>'", "")
        elif acquirer_code == "AXIS" and payment_gateway == "ATOS":
            query = query.replace(", upi_app_key, encKey", "")
            query = query.replace(", '<upi_app_key>', '<encKey>'", "")
        return query
    except Exception as e:
        logger.error(f"Unable to generate the query upi query template for {acquirer_code} with {payment_gateway}.")


def update_upi_values_to_query(query: str, acquirer_code: str, payment_gateway: str,
                               upi_app_key: str, encKey: str, virtual_mid: str, virtual_tid: str) -> str:
    """
    This method is used to update the values to the upi settings query.
    :param query str
    :param acquirer_code str
    :param payment_gateway str
    :param upi_app_key str
    :param encKey str
    :param virtual_mid str
    :param virtual_tid str
    :return: str
    """
    try:
        if acquirer_code == "HDFC" and payment_gateway == "HDFC" or \
                acquirer_code == "AXIS" and payment_gateway == "AXIS" or \
                acquirer_code == "ICICI" and payment_gateway == "FDC":
            query = query.replace("<upi_app_key>", upi_app_key)
        elif acquirer_code == "YES" and payment_gateway == "ATOS" or \
                acquirer_code == "AXIS" and payment_gateway == "ATOS_TLE" or \
                acquirer_code == "KOTAK" and payment_gateway == "KOTAK_WL":
            pass
        elif acquirer_code == "AIRP" and payment_gateway == "APB":
            query = query.replace("<upi_app_key>", upi_app_key)
            query = query.replace("<encKey>", encKey)
        elif acquirer_code == "AXIS" and payment_gateway == "ATOS":
            query = query.replace("<vmid>", virtual_mid)
            query = query.replace("<vtid>", virtual_tid)
        return query
    except Exception as e:
        logger.error(f"Unable to update upi setting values into query due to error {str(e)}")


def generate_upi_settings_query_for_merchant(org_code: str, acquirer_code: str, payment_gateway: str) -> str or None:
    """
    This method is used to generate query of upi settings for a merchant.
    :param org_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: str
    """
    try:
        setting_details = get_setting_details(org_code, acquirer_code, payment_gateway)
        mid = setting_details['mid']
        tid = setting_details['tid']
        bank_code = setting_details['upi_bank_code']
        category_code = setting_details['category_code']
        merchant_name = setting_details['merchant_name']
        pg_merchant_id = tid
        terminal_info_id = get_terminal_info_id(org_code, acquirer_code, payment_gateway, mid, tid)
        vpa = tid + "@upi"
        upi_app_key = setting_details['app_key_for_upi']
        enc_key = setting_details['enc_key_for_upi']
        if upi_app_key == 'N/A':
            upi_app_key = ''
        vmid = mid
        vtid = tid
        query = generate_upi_query_template(acquirer_code, payment_gateway)
        query = query.replace('<bank_code>', bank_code)
        query = query.replace('<category_code>', category_code)
        query = query.replace('<mid>', mid)
        query = query.replace('<merchant_name>', merchant_name)
        query = query.replace('<org_code>', org_code)
        query = query.replace('<pgMerchantId>', pg_merchant_id)
        query = query.replace('<terminal_info_id>', str(terminal_info_id))
        query = query.replace('<tid>', tid)
        query = query.replace('<vpa>', vpa)
        query = update_upi_values_to_query(query, acquirer_code, payment_gateway, upi_app_key, enc_key, vmid, vtid)
        return query
    except Exception as e:
        logger.error(f"Unable to generate upi setting for {acquirer_code} with {payment_gateway} of {org_code}.")
        return None


def check_if_pan_exists(pan_number: str) -> bool or None:
    """
    This method is used to check if the pan number exists in the environment.
    :param pan_number str
    :return: bool or None
    """
    try:
        query = "SELECT visa_merchant_id_primary, mastercard_merchant_id_primary, npci_merchant_id_primary, " \
                "visa_merchant_id_secondary, mastercard_merchant_id_secondary, npci_merchant_id_secondary, " \
                "merchant_pan FROM bharatqr_merchant_config;"
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


def add_key_to_upi_setting_api_body(merchant_configuration_api_body: dict) -> dict:
    """
    This method is used to add key to the merchant configuration api body if needed.
    :param merchant_configuration_api_body dict
    :return: dict
    """
    try:
        acquirer = merchant_configuration_api_body['acquisitions'][0]['acquirerCode']
        payment_gateway = merchant_configuration_api_body['acquisitions'][0]['paymentGateway']
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT AppKeyForUpi, EncKeyForUpi FROM acquisitions WHERE AcquirerCode = '{acquirer}' and "
                       f"PaymentGateway = '{payment_gateway}';")
        key = cursor.fetchone()
        if key[0] != 'N/A' and key[1] != 'N/A':
            merchant_configuration_api_body['upiAppKey'] = key[0]
            merchant_configuration_api_body['encKey'] = key[1]
        elif key[0] != 'N/A':
            merchant_configuration_api_body['key'] = key[0]
    except Exception as e:
        logger.error(f"Unable to add key to the merchant configuration request body due to error {str(e)}")
    return merchant_configuration_api_body


def get_setting_details(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict:
    """
    This method is used to retrieve all the setting related details from the db
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: dict
    """
    setting_details = {}
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM acquisitions WHERE AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        acquisition_details = cursor.fetchone()
        setting_details['acquirer_code'] = acquisition_details[0]
        setting_details['payment_gateway'] = acquisition_details[1]
        setting_details['number_of_terminals'] = acquisition_details[2]
        setting_details['hsm_name'] = acquisition_details[3]
        setting_details['bank_code'] = acquisition_details[4]
        setting_details['bqr_bank_code'] = acquisition_details[5]
        setting_details['upi_bank_code'] = acquisition_details[6]
        setting_details['bqr_terminal_dependant'] = acquisition_details[7]
        setting_details['upi_terminal_dependant'] = acquisition_details[8]
        setting_details['app_key_for_upi'] = acquisition_details[9]
        setting_details['virtual_mid_required'] = acquisition_details[10]
        setting_details['bqr_settings_required'] = acquisition_details[11]
        setting_details['upi_settings_required'] = acquisition_details[12]
        setting_details['enc_key_for_upi'] = acquisition_details[13]
        cursor.execute(f"SELECT TID, DeviceSerial, CategoryCode, MID, MerchantCode, MerchantName FROM terminal_details "
                       f"WHERE MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        terminal_details = cursor.fetchone()
        setting_details['tid'] = terminal_details[0]
        setting_details['device_serial'] = terminal_details[1]
        setting_details['category_code'] = terminal_details[2]
        setting_details['mid'] = terminal_details[3]
        setting_details['merchant_code'] = terminal_details[4]
        setting_details['merchant_name'] = terminal_details[5]
    except Exception as e:
        logger.error(f"Unable to get the setting details due to error {str(e)}")
    cursor.close()
    conn.close()
    return setting_details


def get_brand_pan_number(merchant_code: str, acquirer_code: str, payment_gateway: str) -> dict or None:
    """
    This method is used to get the pan number of the specified branch.
    This will either return the available pan or a newly generated one.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :return: str or None
    """
    conn = ""
    cursor = ""
    brands_pan = {}
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT VisaPrimaryPan, MasterPrimaryPan, RupayPrimaryPan FROM settings_generated_values"
                       f" WHERE MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code.upper()}' AND "
                       f"PaymentGateway = '{payment_gateway.upper()}';")
        entry_available = cursor.fetchone()
        if entry_available:
            logger.debug(f"Picking the available pan numbers for {acquirer_code} with {payment_gateway} "
                         f"of {merchant_code}")
            brands_pan['visa_pan'] = entry_available[0]
            brands_pan['master_pan'] = entry_available[1]
            brands_pan['rupay_pan'] = entry_available[2]
        else:
            logger.debug(f"Generating unique number for {acquirer_code} with {payment_gateway} "
                         f"of {merchant_code}")
            brands_pan['visa_pan'] = get_unique_pan_for_bqr_settings(16)
            brands_pan['master_pan'] = get_unique_pan_for_bqr_settings(16)
            brands_pan['rupay_pan'] = get_unique_pan_for_bqr_settings(16)
    except Exception as e:
        logger.error(f"Unable to get the brand pan number due to error {str(e)}")
        brands_pan = None
    cursor.close()
    conn.close()
    return brands_pan


def get_unique_pan_for_bqr_settings(digits: int) -> str or None:
    """
    This method is used to generate the unique pan for bqr settings
    :param digits int
    :return str
    """
    try:
        pan_number = generate_random_number(digits)
        while check_if_pan_exists(str(pan_number)):
            pan_number = generate_random_number(digits)
        logger.debug(f"Unique number {str(pan_number)} was generated for bqr settings.")
        return str(pan_number)
    except Exception as e:
        logger.error(f"Unable to get unique pan number due to error {str(e)}")
        return None


def get_merchant_code_using_mid(mid: str) -> str or None:
    """
    This method is used to get the merchant code associated with a mid.
    """
    merchant_code = None
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select DISTINCT(MerchantCode) from terminal_details where MID = '{mid}';")
        merchant_code = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to get the merchant code for mid {mid} due to error {str(e)}.")
    return merchant_code


def update_setting_generated_values(merchant_code: str, acquirer_code: str, payment_gateway: str, visa_pan: str,
                                    master_pan: str, rupay_pan: str):
    """
    This method is used to update the setting generated values in the table.
    :param merchant_code str
    :param acquirer_code str
    :param payment_gateway str
    :param visa_pan str
    :param master_pan str
    :param rupay_pan str
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM settings_generated_values WHERE MerchantCode = '{merchant_code}' AND "
                       f"AcquirerCode = '{acquirer_code}' AND PaymentGateway = '{payment_gateway}';")
        result = cursor.fetchone()
        if result:
            cursor.execute(f"UPDATE settings_generated_values SET VisaPrimaryPan = '{visa_pan}', "
                           f"MasterPrimaryPan = '{master_pan}', RupayPrimaryPan = '{rupay_pan}' WHERE "
                           f"MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                           f"PaymentGateway = '{payment_gateway}';")
            conn.commit()
        else:
            cursor.execute(f"INSERT INTO settings_generated_values(MerchantCode, AcquirerCode, PaymentGateway, "
                           f"VisaPrimaryPan, MasterPrimaryPan, RupayPrimaryPan)VALUES('{merchant_code}',"
                           f"'{acquirer_code}','{payment_gateway}','{visa_pan}','{master_pan}','{rupay_pan}');")
            conn.commit()
    except Exception as e:
        logger.error(f"Unable to update the setting generated values due to error {str(e)}")


def update_config_result(merchant_code: str, acquirer_code: str, payment_gateway: str, setting_type: str,
                         set_through: str):
    """
    This method is used to update the configuration results table.
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM configuration_results WHERE MerchantCode = '{merchant_code}' AND "
                       f"AcquirerCode = '{acquirer_code}' AND PaymentGateway = '{payment_gateway}' AND "
                       f"SettingType = '{setting_type}';")
        result_count = len(cursor.fetchall())
        if result_count > 0:
            cursor.execute(f"UPDATE configuration_results SET SetThrough = '{set_through}' WHERE "
                           f"MerchantCode = '{merchant_code}' AND AcquirerCode = '{acquirer_code}' AND "
                           f"PaymentGateway = '{payment_gateway}' AND SettingType = '{setting_type}'; ")
            conn.commit()
            logger.debug(f"{setting_type} setting result updated for {acquirer_code} with {payment_gateway} of "
                         f"{merchant_code}.")
        else:
            cursor.execute(f"INSERT INTO configuration_results(MerchantCode, AcquirerCode, PaymentGateway, "
                           f"SettingType, SetThrough)VALUES('{merchant_code}','{acquirer_code}',"
                           f"'{payment_gateway}','{setting_type}','{set_through}');")
            logger.debug(f"New entry added for {acquirer_code} with {payment_gateway} of {merchant_code} for "
                         f"{setting_type} setting.")
            conn.commit()
    except Exception as e:
        logger.error(f"Unable update the config results due to error {str(e)}")
    cursor.close()
    conn.close()


def clear_merchant_config_related_tables():
    """
    This method is used to clear the tables that hosts the values of merchant configuration
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MerchantCode FROM merchants WHERE CreationStatus IN ('Created','Existed');")
        lst_merchants = [x[0] for x in cursor.fetchall()]
        cursor.execute("Select DISTINCT(MerchantCode) from settings_generated_values;")
        lst_merchants_to_be_removed = []
        for merchant_to_remove in [x[0] for x in cursor.fetchall()]:
            if not merchant_to_remove in lst_merchants:
                lst_merchants_to_be_removed.append(merchant_to_remove)
        for remove_merchant in lst_merchants_to_be_removed:
            cursor.execute(f"DELETE FROM settings_generated_values where MerchantCode = '{remove_merchant}';")
            conn.commit()
            logger.debug(f"Merchant {remove_merchant} has been removed from settings_generated_values table.")
        cursor.execute("Select DISTINCT(MerchantCode) from configuration_results;")
        lst_merchants_to_be_removed = []
        for merchant_to_remove in [x[0] for x in cursor.fetchall()]:
            if not merchant_to_remove in lst_merchants:
                lst_merchants_to_be_removed.append(merchant_to_remove)
        for remove_merchant in lst_merchants_to_be_removed:
            cursor.execute(f"DELETE FROM configuration_results where MerchantCode = '{remove_merchant}';")
            conn.commit()
            logger.debug(f"Merchant {remove_merchant} has been removed from configuration_results table.")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Unable to clear the merchant config related tables due to error {str(e)}")


def check_if_virtual_mid_required_for_bqr(acquirer_code: str, payment_gateway: str) -> bool:
    """
    This method is used to check if virtual mid is required in the merchant configuration api body.
    :param acquirer_code str
    :param payment_gateway str
    :return: bool
    """
    conn = ""
    cursor = ""
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT VirtualMidRequired FROM acquisitions WHERE AcquirerCode = '{acquirer_code}' AND "
                       f"PaymentGateway = '{payment_gateway}';")
        result = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to check if virtual mid is required, due to error {str(e)}")
        result = None
    cursor.close()
    conn.close()
    return result


def get_all_acquisition_details() -> list:
    """
    This method is used to get all the acquisition details available.
    :return: list
    """
    conn = ""
    cursor = ""
    acquisition_details = []
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("Select * from acquisitions;")
        acquisition_details = cursor.fetchall()
    except Exception as e:
        logger.error(f"Unable to get the acquisition details due to error {str(e)}")
        acquisition_details = None
    cursor.close()
    conn.close()
    return acquisition_details


def get_bharatqr_provider_config_id(provider_name: str) -> str or None:
    """
    This method is used to get the bharatqr provider config id from the ezetap db.
    :param provider_name str
    :return: str
    """
    try:
        query = f"select id from bharatqr_provider_config where provider_name='{provider_name}';"
        result = DBProcessor.getValueFromDB(query=query)
        return result['id'][0]
    except Exception as e:
        logger.error(f"Unable to get the bharatqr provider config id due to error {str(e)}")
        return None


def get_terminal_info_id(org_code: str, acquirer_code: str, payment_gateway: str, mid: str, tid: str) -> str or None:
    """
    This method is used to get the terminal info id of a merchant from the ezetap db.
    :param org_code str
    :param acquirer_code str
    :param payment_gateway str
    :param mid str
    :param tid str
    :return: str
    """
    try:
        query = f"select id from terminal_info where org_code='{org_code}' and acquirer_code='{acquirer_code}' and " \
                f"payment_gateway='{payment_gateway}' and mid='{mid}' and tid='{tid}';"
        result = DBProcessor.getValueFromDB(query=query)
        return result['id'][0]
    except Exception as e:
        logger.error(f"Unable to get the terminal info id of {org_code} due to error {str(e)}")
        return None


def check_if_bqr_setting_exists(org_code: str, bqr_provider_id: str, terminal_info_id: str) -> bool or None:
    """
    This method is used to confirm if the bqr settings for an org code is already available.
    :param org_code str
    :param bqr_provider_id str
    :param terminal_info_id str
    :return: bool or None
    """
    try:
        query = f"select * from bharatqr_merchant_config where org_code = '{org_code}' and " \
                f"provider_id = '{bqr_provider_id}' and terminal_info_id = '{terminal_info_id}';"
        result = DBProcessor.getValueFromDB(query)
        no_of_entries = len(result)
        if no_of_entries > 0:
            logger.debug(f"BQR setting for {org_code} already exists.")
            return True
        else:
            logger.debug(f"BQR setting for {org_code} is not available.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if the bqr setting is available for {org_code}, due to error {str(e)}")
        return None


def get_payment_gateway_from_terminal_details(acquirer_code: str) -> str:
    """
    This method is used to fetch the payment gateway of an acquirer.
    In case of multiple payment gateways availability, first one will be picked.
    :param acquirer_code
    :return: str or None
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"select PaymentGateway from terminal_details where AcquirerCode = '{acquirer_code}';")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Unable to get the pg due to error {str(e)}")


def check_if_upi_setting_exists(org_code: str, terminal_info_id: str) -> bool or None:
    """
    This method is used to check if the upi setting exists for a merchant.
    :param org_code str
    :param terminal_info_id str
    :return: bool or None
    """
    try:
        query = f"SELECT * FROM upi_merchant_config where org_code = '{org_code}' and " \
                f"terminal_info_id = '{terminal_info_id}';"
        result = DBProcessor.getValueFromDB(query)
        no_of_entries = len(result)
        if no_of_entries > 0:
            logger.debug(f"UPI setting available for {org_code} with terminal info id {terminal_info_id}.")
            return True
        else:
            logger.debug(f"UPI setting not available for {org_code} with terminal info id {terminal_info_id}.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if the upi setting is available for {org_code}, due to error {str(e)}")
        return None


def check_if_remotepay_setting_exists(org_code: str, setting_name: str) -> bool or None:
    """
    This method is used to check if the remotepay setting is available for the merchant.
    :param org_code str
    :param setting_name str
    :return bool or None
    """
    try:
        query = f"select * from remotepay_setting where org_code = '{org_code}' and setting_name = '{setting_name}'; "
        result = DBProcessor.getValueFromDB(query)
        if len(result) > 0:
            logger.debug(f"{setting_name} setting for {org_code} is already available.")
            return True
        else:
            logger.debug(f"{setting_name} setting for {org_code} is not available.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if the remote pay setting exists for {org_code}, due to error {str(e)}")
        return None


def check_if_payment_gateway_exists_in_terminal_info_table(payment_gate: str) -> bool:
    """
    This method is used to check if the payment gateway exists in the environment.
    :param payment_gate str
    :return: bool
    """
    try:
        query = f"select * from terminal_info where payment_gateway = '{payment_gate}';"
        result = DBProcessor.getValueFromDB(query)
        if len(result)>0:
            logger.debug(f"{payment_gate} is available in terminal info table.")
            return True
        else:
            logger.debug(f"{payment_gate} is not available in terminal info table.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if {payment_gate} is available in terminal info table due to error {str(e)}")


def check_if_pg_config_exists(org_code: str, payment_gateway: str) -> bool:
    """
    This method is used to check if the pg configuration is available for the merchant.
    :param org_code str
    :param payment_gateway str
    :return bool
    """
    try:
        query = f"select * from merchant_pg_config where org_code = '{org_code}'and " \
                f"payment_gateway = '{payment_gateway}';"
        result = DBProcessor.getValueFromDB(query)
        if len(result) > 0:
            logger.debug(f"PG config is available for {org_code} with {payment_gateway}")
            return True
        else:
            logger.debug(f"PG config is not available for {org_code} with {payment_gateway}")
            return False
    except Exception as e:
        logger.error(f"Unable to check if pg is available for {org_code} with {payment_gateway} due to error {str(e)}")


def refresh_db():
    """
    This method is used to refresh the db.
    """
    try:
        username = ConfigReader.read_config("SuperUserCredentials", "username")
        password = ConfigReader.read_config("SuperUserCredentials", "password")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": username,
                                                                              "password": password})
        response = APIProcessor.send_request(api_details)
        if response['success']:
            logger.debug(f"DB was refreshed successfully.")
        else:
            logger.debug(f"DB refresh failed.")
    except Exception as e:
        logger.debug(f"Unable to refresh the db due to error {str(e)}")


def check_if_bqr_setting_required(acquirer_code: str, payment_gateway: str) -> bool:
    """
    This method is used to check if bqr setting is required for a combination of acquirer and payment gateway.
    :param acquirer_code str
    :param payment_gateway str
    :return: bool
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT BqrSettingRequired FROM acquisitions where AcquirerCode = '{acquirer_code}' "
                       f"and PaymentGateway = '{payment_gateway}';")
        if str(cursor.fetchone()[0]).lower() == 'yes':
            logger.debug(f"BQR setting is required for {acquirer_code} with {payment_gateway}.")
            return True
        else:
            logger.debug(f"BQR setting is not required for {acquirer_code} with {payment_gateway}.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if bqr setting is required for {acquirer_code} with {payment_gateway}.")


def check_if_upi_setting_required(acquirer_code: str, payment_gateway: str) -> bool:
    """
    This method is used to check if upi setting is required for a combination of acquirer and payment gateway.
    :param acquirer_code str
    :param payment_gateway str
    :return: bool
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT UpiSettingRequired FROM acquisitions where AcquirerCode = '{acquirer_code}' "
                       f"and PaymentGateway = '{payment_gateway}';")
        if str(cursor.fetchone()[0]).lower() == 'yes':
            logger.debug(f"UPI setting is required for {acquirer_code} with {payment_gateway}.")
            return True
        else:
            logger.debug(f"UPI setting is not required for {acquirer_code} with {payment_gateway}.")
            return False
    except Exception as e:
        logger.error(f"Unable to check if UPI setting is required for {acquirer_code} with {payment_gateway}.")


def check_if_terminal_dependant(acquirer_code: str, payment_gateway: str, payment_mode: str) -> str:
    """
    This method is used to check if terminal dependency entry should be created for the acquirer and pg.
    :param acquirer_code str
    :param payment_gateway str
    :param payment_mode str
    :return: bool
    """
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        if payment_mode.lower() == 'upi':
            column_to_pick = "UpiTerminalDependant"
        else:
            column_to_pick = "BqrTerminalDependant"
        cursor.execute(f"select {column_to_pick} from acquisitions where AcquirerCode = '{acquirer_code}' and "
                       f"PaymentGateway = '{payment_gateway}';")
        setting_required = cursor.fetchone()[0]
        return setting_required.lower()
    except Exception as e:
        logger.debug(f"Unable to check if {acquirer_code} with {payment_gateway} is terminal dependant, due to "
                     f"error {str(e)}")