import random
import string
import sys
import pytest
import requests
import json
from Configuration import Configuration, testsuite_teardown, TestSuiteSetup
from DataProvider import GlobalVariables
from Utilities import Validator, DBProcessor, ConfigReader, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_100_107_013():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Success_Via_IDFC
    Sub Feature Description: Verifying UPI static QR generation via IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 013: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")
        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)--------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")
            res_generateqr_success = response["success"]
            res_generateqr_username = response["username"]
            res_generateqr_publish_id = response["publishId"]
            res_generateqr_org_code = response["merchantCode"]
            res_generateqr_mid = response["mid"]
            res_generateqr_tid = response["tid"]

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
            try:
                expected_api_values = {"success": True,
                                       "username": portal_username,
                                       "tid": db_upi_config_tid,
                                       "mid": db_upi_config_mid,
                                       "merchantCode": org_code
                                       }

                actual_api_values = {"success": res_generateqr_success,
                                     "username": res_generateqr_username,
                                     "tid": res_generateqr_tid,
                                     "mid": res_generateqr_mid,
                                     "merchantCode": res_generateqr_org_code
                                    }

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "org_code" : org_code,
                    "vpa" :db_upi_config_vpa,
                    "user_mobile" :app_username,
                    "user_name" :app_username,
                    "mid" :db_upi_config_mid,
                    "tid" :db_upi_config_tid,
                    "qr_type" :"UPI",
                    "intent_type" :"STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(res_generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_staticqrIntent_org_code = result["org_code"].iloc[0]
                db_staticqrIntent_vpa = result["vpa"].iloc[0]
                db_staticqrIntent_user_mobile = result["user_mobile"].iloc[0]
                db_staticqrIntent_user_name = result["user_name"].iloc[0]
                db_staticqrIntent_mid = result["mid"].iloc[0]
                db_staticqrIntent_tid = result["tid"].iloc[0]
                db_staticqrIntent_qrtype = result["qr_type"].iloc[0]
                db_staticqrIntent_intent_type = result["intent_type"].iloc[0]

                actual_db_values = {
                    "org_code" : db_staticqrIntent_org_code,
                    "vpa" :db_staticqrIntent_vpa,
                    "user_mobile" :db_staticqrIntent_user_mobile,
                    "user_name" :db_staticqrIntent_user_name,
                    "mid" :db_staticqrIntent_mid,
                    "tid" :db_staticqrIntent_tid,
                    "qr_type" :db_staticqrIntent_qrtype,
                    "intent_type" :db_staticqrIntent_intent_type
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
@pytest.mark.dbVal
def test_common_100_107_014():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Regeneration_Success_Via_IDFC
    Sub Feature Description: Verifying UPI static QR regeneration with different app user via IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 014: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")
        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        # testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)
        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        logger.debug(f"deleting data from qrcode_audit table for org_code : {org_code}")

        query = "delete from qrcode_audit where org_code ='" + str(org_code) + "'"
        result = DBProcessor.delete_value_from_db(query)
        logger.debug(f"Query result : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")
            res_generateqr_publish_id = response["publishId"]

            # Select another user for regenerating static QR for same org
            query = "select username from org_employee where org_code='" + str(org_code) + "';"
            logger.debug(f"Query to fetch all user under the {org_code} org_code from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
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
            if is_user_required:  # Create a new user via API
                second_app_username = str(random.randint(1000000000, 9999999999))
                name = "EzeAuto" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
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
                endPoint = api_details['EndPoint']
                method = api_details['Method']
                headers = api_details['Header']
                url = ConfigReader.read_config("APIs", "baseUrl") + endPoint
                url = url.replace('EZETAP', org_code)
                resp = requests.request(method=method, url=str(url), headers=headers, data=json.dumps(payload))
                APIProcessor.update_api_details_to_report_variables(resp)
                response = json.loads(resp.text)
                logger.debug(f"response received for createUser api is : {response}")
                if response["success"]:
                    # Regenerating static qr with new user under same org
                    api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrCodeType": "UPI",
                        "qrOrgCode": org_code,
                        "qrUserMobileNo": second_app_username,
                        "qrUserName": second_app_username,
                        "qrCodeFormat": "string",
                        "merchantVpa": db_upi_config_vpa
                    })
                    response = APIProcessor.send_request(api_details)
                    regenerateqr_publish_id = response["publishId"]
                    logger.info(f"re_generated publish id : {regenerateqr_publish_id}")
                else:
                    logger.error(f"User creation failed : {response}")
            else:
                # Regenerating static qr with another existing user under same org
                api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrCodeType": "UPI",
                    "qrOrgCode": org_code,
                    "qrUserMobileNo": second_app_username,
                    "qrUserName": second_app_username,
                    "qrCodeFormat": "string",
                    "merchantVpa": db_upi_config_vpa
                })
                response = APIProcessor.send_request(api_details)
                regenerateqr_publish_id = response["publishId"]
                logger.info(f"re_generated publish id : {regenerateqr_publish_id}")

            logger.debug(f"Response received for regenerating static_qrcode_IDFC api is : {response}")
            publish_id = response["publishId"]
            logger.debug(f"fetching publish_id from api response is : {publish_id}")

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
                    "publish_id": res_generateqr_publish_id,
                    "org_code": org_code,
                    "vpa": db_upi_config_vpa,
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "mid": db_upi_config_mid,
                    "tid": db_upi_config_tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",

                    "publish_id_2": regenerateqr_publish_id,
                    "org_code_2": org_code,
                    "vpa_2": db_upi_config_vpa,
                    "user_mobile_2": second_app_username,
                    "user_name_2": second_app_username,
                    "mid_2": db_upi_config_mid,
                    "tid_2": db_upi_config_tid,
                    "qr_type_2": "UPI",
                    "intent_type_2": "STATIC_QR",
                    # "audit_publish_id": publish_id,
                    # "audit_org_code": org_code,
                    # "audit_qr_type": "UPI",
                    # "audit_intent_type": "STATIC_QR",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(res_generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_staticqrIntent_publish_id = result["publish_id"].iloc[0]
                db_staticqrIntent_org_code = result["org_code"].iloc[0]
                db_staticqrIntent_vpa = result["vpa"].iloc[0]
                db_staticqrIntent_user_mobile = result["user_mobile"].iloc[0]
                db_staticqrIntent_user_name = result["user_name"].iloc[0]
                db_staticqrIntent_mid = result["mid"].iloc[0]
                db_staticqrIntent_tid = result["tid"].iloc[0]
                db_staticqrIntent_qrtype = result["qr_type"].iloc[0]
                db_staticqrIntent_intent_type = result["intent_type"].iloc[0]

                query = "select * from staticqr_intent where publish_id='" + str(regenerateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_staticqrIntent_publish_id_2 = result["publish_id"].iloc[0]
                logger.debug(
                    f"Fetching publish_id from staticqr_intent table for regeneration: {db_staticqrIntent_publish_id_2}")
                db_staticqrIntent_org_code_2 = result["org_code"].iloc[0]
                logger.debug(
                    f"Fetching org_code from staticqr_intent table for regeneration: {db_staticqrIntent_org_code_2}")
                db_staticqrIntent_vpa_2 = result["vpa"].iloc[0]
                logger.debug(f"Fetching vpa from staticqr_intent table for regeneration: {db_staticqrIntent_vpa_2}")
                db_staticqrIntent_user_mobile_2 = result["user_mobile"].iloc[0]
                logger.debug(
                    f"Fetching user_mobile from staticqr_intent table for regeneration: {db_staticqrIntent_user_mobile_2}")
                db_staticqrIntent_user_name_2 = result["user_name"].iloc[0]
                logger.debug(
                    f"Fetching user_name from staticqr_intent table for regeneration: {db_staticqrIntent_user_name_2}")
                db_staticqrIntent_mid_2 = result["mid"].iloc[0]
                logger.debug(f"Fetching mid from staticqr_intent table for regeneration: {db_staticqrIntent_mid_2}")
                db_staticqrIntent_tid_2 = result["tid"].iloc[0]
                logger.debug(f"Fetching tid from staticqr_intent table for regeneration: {db_staticqrIntent_tid_2}")
                db_staticqrIntent_qrtype_2 = result["qr_type"].iloc[0]
                logger.debug(
                    f"Fetching qr_type from staticqr_intent table for regeneration: {db_staticqrIntent_qrtype_2}")
                db_staticqrIntent_intent_type_2 = result["intent_type"].iloc[0]
                logger.debug(
                    f"Fetching intent_type from staticqr_intent table for regeneration: {db_staticqrIntent_intent_type_2}")

                # query = "select * from qrcode_audit where org_code='" + org_code + "'"
                # logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                # result = DBProcessor.getValueFromDB(query)
                # logger.debug(f"Query result : {result}")
                # audit_publish_id_db = result["publish_id"].iloc[0]
                # audit_org_code_db = result["org_code"].iloc[0]
                # audit_qr_type_db = result['qr_type'].values[0]
                # audit_intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "publish_id": db_staticqrIntent_publish_id,
                    "org_code": db_staticqrIntent_org_code,
                    "vpa": db_staticqrIntent_vpa,
                    "user_mobile": db_staticqrIntent_user_mobile,
                    "user_name": db_staticqrIntent_user_name,
                    "mid": db_staticqrIntent_mid,
                    "tid": db_staticqrIntent_tid,
                    "qr_type": db_staticqrIntent_qrtype,
                    "intent_type": db_staticqrIntent_intent_type,

                    "publish_id_2": db_staticqrIntent_publish_id_2,
                    "org_code_2": db_staticqrIntent_org_code_2,
                    "vpa_2": db_staticqrIntent_vpa_2,
                    "user_mobile_2": db_staticqrIntent_user_mobile_2,
                    "user_name_2": db_staticqrIntent_user_name_2,
                    "mid_2": db_staticqrIntent_mid_2,
                    "tid_2": db_staticqrIntent_tid_2,
                    "qr_type_2": db_staticqrIntent_qrtype_2,
                    "intent_type_2": db_staticqrIntent_intent_type_2,
                    # "audit_publish_id": audit_publish_id_db,
                    # "audit_org_code": audit_org_code_db,
                    # "audit_qr_type": audit_qr_type_db,
                    # "audit_intent_type": audit_intent_type_db,
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
@pytest.mark.dbVal
def test_common_100_107_015():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Failed_Via_IDFC
    Sub Feature Description: Verifying UPI static QR generation via IDFC
    TC naming code description:: 100: payment method, 107: UPI Static QR, 015: Testcase ID
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
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")
        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)----------------------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": app_username,
                "password": app_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")
            res_success = response["success"]
            res_message = response["message"]
            res_errorCode = response["errorCode"]
            res_errorMessage = response["errorMessage"]
            res_realCode = response["realCode"]

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
            try:
                expected_api_values = {"success": False,
                                       "message": "You do not have permission to perform this operation.",
                                       "errorCode": "EZETAP_0000193",
                                       "errorMessage": "You do not have permission to perform this operation.",
                                       "realCode": "UNAUTHORIZED_OPERATION"
                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {"success": res_success,
                                     "message": res_message,
                                     "errorCode": res_errorCode,
                                     "errorMessage": res_errorMessage,
                                     "realCode": res_realCode
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
@pytest.mark.apiVal
def test_common_100_107_027():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Failed_With_Invalid_VPA_Via_IDFC
    Sub Feature Description: Performing failed qr generation when invalid VPA is used in the static QR.
    TC naming code description:: 100: payment method, 107: UPI Static QR, 027: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")
        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)
        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # generating random invalid vpa
            dummy_vpa = str(random.randint(11111111, 99999999)) + "@invalidupi"
            logger.debug(f"generated random vpa is : {dummy_vpa}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": dummy_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")
            res_success = response["success"]
            res_error_code = response["errorCode"]
            res_error_message = response["errorMessage"]

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
            try:
                expected_api_values = {"success": False,
                                       "errorCode": "EZETAP_500083",
                                       "errorMessage": "UPI_MERCHANT_CONFIG_NOT_FOUND"
                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {"success": res_success,
                                     "errorCode": res_error_code,
                                     "errorMessage": res_error_message,
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
@pytest.mark.apiVal
def test_common_100_107_028():
    """
    Sub Feature Code: UI_Common_PM_StaticQR_UPI_QR_Generation_Failed_With_Invalid_Username_Via_IDFC
    Sub Feature Description: Verifying failed qr generation with a username which is not registered with that merchant.
    TC naming code description:: 100: payment method, 107: UPI Static QR, 028: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='IDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # Get details from upi_merchant_config table
        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'IDFC';"
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_id = result['id'].values[0]
        logger.info(f"fetched upi config id is : {db_upi_config_id}")
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")
        db_upi_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_upi_config_mid}")
        db_upi_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_upi_config_tid}")

        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, db_upi_config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------------------

        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # generating random invalid username
            dummy_username = str(random.randint(1111111111, 9999999999))
            logger.debug(f"generated random username is : {dummy_username}")

            api_details = DBProcessor.get_api_details('upi_staticqr_generation_IDFC', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": dummy_username ,
                "qrCodeFormat" : "string",
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc api is : {response}")
            res_success = response["success"]
            res_error_code = response["errorCode"]
            res_error_message = response["errorMessage"]

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
            try:
                expected_api_values = {"success": False,
                                       "errorCode": "EZETAP_0001606",
                                       "errorMessage": "USER_DETAILS_NOT_MATCHED"
                                       }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {"success": res_success,
                                     "errorCode": res_error_code,
                                     "errorMessage": res_error_message,
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