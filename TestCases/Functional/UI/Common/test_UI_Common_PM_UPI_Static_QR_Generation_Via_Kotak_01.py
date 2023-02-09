import random
import string
import sys
import pytest
import requests
import json
from Configuration import testsuite_teardown, Configuration
from DataProvider import GlobalVariables
from Utilities import ResourceAssigner, DBProcessor, APIProcessor, ConfigReader, Validator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_107_030():
    """
    Sub Feature Code: UI_Common_PM_UPI_Static_QR_Generation_Success_Via_KOTAK
    Sub Feature Description: Verifying UPI static QR generation via KOTAK
    TC naming code description: 100: payment method, 107: UPI Static QR, 030: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_aduit_table_entry(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False,
                                                   cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generating UPI STATIC QR
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation response : {generateqr_publish_id}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": generateqr_publish_id,
                    "org_code" : org_code,
                    "vpa" :vpa,
                    "user_mobile" :app_username,
                    "user_name" :app_username,
                    "mid" :mid,
                    "tid" :tid,
                    "qr_type" :"UPI",
                    "intent_type" :"STATIC_QR"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

                actual_db_values = {
                    "publish_id": staticqr_intent_publish_id_db,
                    "org_code" : staticqr_intent_org_code_db,
                    "vpa" :staticqr_intent_vpa_db,
                    "user_mobile" :staticqr_intent_user_mobile_db,
                    "user_name" :staticqr_intent_user_name_db,
                    "mid" :staticqr_intent_mid_db,
                    "tid" :staticqr_intent_tid_db,
                    "qr_type" :staticqr_intent_qrtype_db,
                    "intent_type" :staticqr_intent_intent_type_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_107_031():
    """
    Sub Feature Code: UI_Common_PM_UPI_Static_QR_Regeneration_Via_KOTAK
    Sub Feature Description: Verifying UPI static QR regeneration with different user via KOTAK
    TC naming code description: 100: Payment method, 107: UPI Static QR, 031: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_aduit_table_entry(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # Generate UPI static QR for first user
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response of static qr generation for first user is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation for first user is : {generateqr_publish_id}")

            # Select another user for regenerating static QR for same org
            query = "select username from org_employee where org_code='" + str(org_code) + "';"
            logger.debug(f"Query to fetch all user under the {org_code} org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Response for org_employee table : {result}")
            is_user_required = False
            second_app_username = ''

            for i in range(len(result)):
                if result['username'][i] == app_username:
                    is_user_required = True
                    logger.debug(f"user creation is required")
                    continue
                else:
                    is_user_required = False
                    second_app_username = result['username'][i]
                    logger.debug(f"user creation is not required")
                    break

            if is_user_required: # Create a new user via API
                second_app_username = str(random.randint(1000000000, 9999999999))
                logger.debug(f"second_app_username is : {second_app_username}")
                name = "EzeAuto" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
                logger.debug(f"name is : {name}")
                api_details = DBProcessor.get_api_details('createUser', request_body={
                    "mobileNumber": second_app_username,
                    "name": name,
                    "roles": [
                        "ROLE_CLADMIN", "ROLE_CLAGENTPORTAL", "ROLE_CLAGENTVOID",
                        "ROLE_CLAGENT", "ROLE_CLAGENT_REFUND", "ROLE_CLREFUND"
                    ],
                    "userPassword": "A123456",
                    "userToken": second_app_username,
                    "username": portal_username,
                    "password": portal_password
                })

                payload = api_details['RequestBody']
                logger.debug(f"payload is : {payload}")
                end_point = api_details['EndPoint']
                logger.debug(f"end_point is : {end_point}")
                method = api_details['Method']
                logger.debug(f"method is : {method}")
                headers = api_details['Header']
                logger.debug(f"headers is : {headers}")
                url = ConfigReader.read_config("APIs", "baseUrl") + end_point
                logger.debug(f"url is : {url}")
                url = url.replace('EZETAP', org_code)
                resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
                logger.debug(f"resp is : {resp}")
                APIProcessor.update_api_details_to_report_variables(resp)
                response = json.loads(resp.text)
                logger.debug(f"response of update_api_details_to_report_variables is : {response}")
                logger.debug(f"response received for createUser api is : {response}")

                if response["success"]:
                    # Regenerating static qr with another user for same org
                    api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrUserMobileNo": second_app_username,
                        "qrUserName": second_app_username,
                        "qrCodeType": "UPI",
                        "merchantVpa": vpa,
                        "qrCodeFormat": "STRING"
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Response of static qr generation for another user with same org is : {response}")
                    publish_id = response["publishId"]
                    logger.debug(f"Value of publishId obtained from static qr generation for another user with same org is  : {publish_id}")

                else:
                    logger.error(f"User creation failed : {response}")
            else:
                # Regenerating UPI static qr with another existing user for same org
                api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrUserMobileNo": second_app_username,
                    "qrUserName": second_app_username,
                    "qrCodeType": "UPI",
                    "merchantVpa": vpa,
                    "qrCodeFormat": "STRING"
                })
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response of static qr generation for another existing user with same org is : {response}")
                publish_id = response["publishId"]
                logger.debug(f"Value of publishId obtained from static qr generation for another existing user with same org is  : {publish_id}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": generateqr_publish_id,
                    "org_code" : org_code,
                    "vpa" :vpa,
                    "mid" :mid,
                    "tid" :tid,
                    "user_mobile": str(second_app_username),
                    "user_name": str(second_app_username),
                    "qr_type" :"UPI",
                    "intent_type" :"STATIC_QR",
                    "audit_publish_id": publish_id,
                    "audit_org_code": org_code,
                    "audit_qr_type": "UPI",
                    "audit_intent_type": "STATIC_QR",
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from qrcode_audit where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of qrcode_audit table : {result}")
                audit_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from qrcode_audit table : {audit_publish_id_db}")
                audit_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from qrcode_audit table : {audit_org_code_db}")
                audit_qr_type_db = result['qr_type'].values[0]
                logger.debug(f"Fetching qr_type from qrcode_audit table : {audit_qr_type_db}")
                audit_intent_type_db = result['intent_type'].values[0]
                logger.debug(f"Fetching intent_type from qrcode_audit table : {audit_intent_type_db}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

                actual_db_values = {
                    "publish_id": staticqr_intent_publish_id_db,
                    "org_code": staticqr_intent_org_code_db,
                    "vpa": staticqr_intent_vpa_db,
                    "mid": staticqr_intent_mid_db,
                    "tid": staticqr_intent_tid_db,
                    "user_mobile": staticqr_intent_user_mobile_db,
                    "user_name": staticqr_intent_user_name_db,
                    "qr_type": staticqr_intent_qrtype_db,
                    "intent_type": staticqr_intent_intent_type_db,
                    "audit_publish_id": audit_publish_id_db,
                    "audit_org_code": audit_org_code_db,
                    "audit_qr_type": audit_qr_type_db,
                    "audit_intent_type": audit_intent_type_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_107_032():
    """
    Sub Feature Code: UI_Common_PM_UPI_Static_QR_Generation_Failure_With_Invalid_Username_Via_KOTAK
    Sub Feature Description: Confirm qr generation is failing when we try to generate with a username which is not registered with that merchant via KOTAK
    TC naming code description: 100: Payment method, 107: UPI Static QR, 032: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_aduit_table_entry(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")

        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generating UPI STATIC QR with Username which is not registered with this merchant
            generate_random_username = random.randint(0, 10 ** 10)
            logger.debug(f"Generating random value for username : {generate_random_username}")

            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": generate_random_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            success = response['success']
            logger.debug(f"Value of success obtained from static qr generation response : {success}")
            error_message = response['errorMessage']
            logger.debug(f"Value of error_message obtained from static qr generation response : {error_message}")
            error_code = response['errorCode']
            logger.debug(f"Value of error_code obtained from static qr generation response : {error_code}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            expected_success = False
            expected_error_message = 'USER_DETAILS_NOT_MATCHED'
            expected_error_code = 'EZETAP_0001606'

            try:
                expected_api_values = {
                    "success" : expected_success,
                    "error_message" : expected_error_message,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message" : error_message,
                    "error_code": error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation-------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_107_036():
    """
    Sub Feature Code: UI_COMMON_PM_UPI_Static_QR_Generation_With_UPI_Invalid_VPA_Via_KOTAK
    Sub Feature Description: Verifying Static QR generation is getting failed with invalid VPA
    TC naming code description: 100: Payment method, 107: UPI Static QR, 036: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publish_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_aduit_table_entry(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generating random vpa
            characters = string.ascii_letters + string.digits + string.punctuation
            generate_random_vpa = ''.join(random.choice(characters) for i in range(8))
            logger.debug(f"Generating random value for vpa : {generate_random_vpa}")

            # generating STATIC QR for UPI, pass the random_vpa_generated
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": generate_random_vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            success = response['success']
            logger.debug(f"Value of success obtained from static qr generation response : {success}")
            error_message = response['errorMessage']
            logger.debug(f"Value of error_message obtained from static qr generation response : {error_message}")
            error_code = response['errorCode']
            logger.debug(f"Value of error_code obtained from static qr generation response : {error_code}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            expected_success = False
            expected_error_message = "UPI_MERCHANT_CONFIG_NOT_FOUND"
            expected_error_code = "EZETAP_500083"

            try:
                expected_api_values = {
                    "success": expected_success,
                    "error_message" : expected_error_message,
                    "error_code": expected_error_code
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": success,
                    "error_message" : error_message,
                    "error_code": error_code
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
def test_common_100_107_037():
    """
    Sub Feature Code: UI_COMMON_PM_UPI_Static_QR_Regeneration_With_Same_VPA_Via_KOTAK
    Sub Feature Description: Verifying multiple static QR is not regenerating for same VPA
    TC naming code description: 100: payment method, 107: UPI Static QR, 037: Testcase ID
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the org_employee table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Fetching org_code from org_employee table : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from upi_merchant_config table : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result of upi_merchant_config table : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from upi_merchant_config table : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from upi_merchant_config table : {tid}")
        vpa = result['vpa'].values[0]
        logger.debug(f"Fetching vpa from upi_merchant_config table : {vpa}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching id from upi_merchant_config table : {config_id}")

        # to delete the publisher_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        # to delete all entries from qrcode_audit table which was generated previously
        testsuite_teardown.delete_qrcode_aduit_table_entry(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False,
                                                   cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generating UPI STATIC QR
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for generating static qr for pure upi is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr generation response : {generateqr_publish_id}")

            # regenerating UPI STATIC QR  # Verify multiple static QR is not regenerating for same VPA
            api_details = DBProcessor.get_api_details('pure_upi_kotak', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "UPI",
                "merchantVpa": vpa,
                "qrCodeFormat": "STRING"
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response obtained for regenerating static qr for pure upi is : {response}")
            generateqr_publish_id_2 = response["publishId"]
            logger.debug(f"Value of publishId obtained from static qr regeneration response : {generateqr_publish_id_2}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution------------------------------------------------

        # -----------------------------------------Start of Validation--------------------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "publish_id": generateqr_publish_id
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "publish_id": generateqr_publish_id_2
                }
                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "publish_id": generateqr_publish_id,
                    "org_code" : org_code,
                    "vpa" :vpa,
                    "user_mobile" :app_username,
                    "user_name" :app_username,
                    "mid" :mid,
                    "tid" :tid,
                    "qr_type" :"UPI",
                    "intent_type" :"STATIC_QR",
                    "audit_publish_id": generateqr_publish_id,
                    "audit_org_code": org_code,
                    "audit_qr_type": "UPI",
                    "audit_intent_type": "STATIC_QR"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from qrcode_audit where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of qrcode_audit table : {result}")
                audit_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from qrcode_audit table : {audit_publish_id_db}")
                audit_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from qrcode_audit table : {audit_org_code_db}")
                audit_qr_type_db = result['qr_type'].values[0]
                logger.debug(f"Fetching qr_type from qrcode_audit table : {audit_qr_type_db}")
                audit_intent_type_db = result['intent_type'].values[0]
                logger.debug(f"Fetching intent_type from qrcode_audit table : {audit_intent_type_db}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result of staticqr_intent table : {result}")
                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"Fetching publish_id from staticqr_intent table : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"Fetching org_code from staticqr_intent table : {staticqr_intent_org_code_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"Fetching user_mobile from staticqr_intent table : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"Fetching user_name from staticqr_intent table : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"Fetching qr_type from staticqr_intent table : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"Fetching intent_type from staticqr_intent table : {staticqr_intent_intent_type_db}")

                actual_db_values = {
                    "publish_id": staticqr_intent_publish_id_db,
                    "org_code" : staticqr_intent_org_code_db,
                    "vpa" :staticqr_intent_vpa_db,
                    "user_mobile" :staticqr_intent_user_mobile_db,
                    "user_name" :staticqr_intent_user_name_db,
                    "mid" :staticqr_intent_mid_db,
                    "tid" :staticqr_intent_tid_db,
                    "qr_type" :staticqr_intent_qrtype_db,
                    "intent_type" :staticqr_intent_intent_type_db,
                    "audit_publish_id": audit_publish_id_db,
                    "audit_org_code": audit_org_code_db,
                    "audit_qr_type": audit_qr_type_db,
                    "audit_intent_type": audit_intent_type_db
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation--------------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)