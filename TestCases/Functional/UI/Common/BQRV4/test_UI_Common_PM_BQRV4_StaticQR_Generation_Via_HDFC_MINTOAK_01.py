import random
import string
import requests
import json
import sys
import pytest
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_108_033():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Generation_Success_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying static QR generation via HDFC_MINTOAK
    TC naming code description: 100: payment method, 108: BQRV4 Static QR, 033: TC033
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

        query = f"select * from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from bharatqr_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            res_generateqr_publish_id = response["publishId"]
            logger.debug(f"Response received for static_qrcode_generate_HDFC_MINTOAK api is : {response}")

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
                    "org_code": org_code,
                    "merchant_pan": db_bqr_config_merchant_pan,
                    "vpa": db_upi_config_vpa,
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "qr_type": "BHARATQR",
                    "intent_type": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from staticqr_intent where publish_id='{str(res_generateqr_publish_id)}'"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                db_staticqr_intent_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_org_code}")
                db_staticqr_intent_merchant_pan = result["merchant_pan"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_merchant_pan}")
                db_staticqr_intent_vpa = result["vpa"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_vpa}")
                db_staticqr_intent_user_mobile = result["user_mobile"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_user_mobile}")
                db_staticqr_intent_user_name = result["user_name"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_user_name}")
                db_staticqr_intent_mid = result["mid"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_mid}")
                db_staticqr_intent_tid = result["tid"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_tid}")
                db_staticqr_intent_qrtype = result["qr_type"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_qrtype}")
                db_staticqr_intent_intent_type = result["intent_type"].values[0]
                logger.debug(f"Fetching org code : {db_staticqr_intent_intent_type}")

                actual_db_values = {
                    "org_code": db_staticqr_intent_org_code,
                    "merchant_pan": db_staticqr_intent_merchant_pan,
                    "vpa": db_staticqr_intent_vpa,
                    "user_mobile": db_staticqr_intent_user_mobile,
                    "user_name": db_staticqr_intent_user_name,
                    "mid": db_staticqr_intent_mid,
                    "tid": db_staticqr_intent_tid,
                    "qr_type": db_staticqr_intent_qrtype,
                    "intent_type": db_staticqr_intent_intent_type
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
def test_common_100_108_034():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Regeneration_With_Diff_App_Username_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying static QR regeneration with different app user via HDFC_MINTOAK
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 034: Testcase ID
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = f"select * from bharatqr_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------------------PreConditions(Completed)-------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api for first QR is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"generateqr_publish_id for first QR is : {generateqr_publish_id}")

            query = f"select username from org_employee where org_code='{org_code}';"
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
            if is_user_required:
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
                    api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrCodeType": "BHARAT",
                        "qrOrgCode": org_code,
                        "qrUserMobileNo": second_app_username,
                        "qrUserName": second_app_username,
                        "qrCodeFormat": "STRING",
                        "mid": db_bqr_config_mid,
                        "tid": db_bqr_config_tid,
                        "merchantPan": db_bqr_config_merchant_pan,
                        "merchantVpa": db_upi_config_vpa
                    })
                    response = APIProcessor.send_request(api_details)
                    logger.debug(
                        f"Response received for static_qrcode_generate_hdfc_mintoak api for second QR is : {response}")
                    regenerateqr_publish_id = response["publishId"]
                    logger.debug(f"regenerateqr_publish_id is : {regenerateqr_publish_id}")
                else:
                    logger.error(f"User creation failed : {response}")
            else:
                api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrCodeType": "BHARAT",
                    "qrOrgCode": org_code,
                    "qrUserMobileNo": second_app_username,
                    "qrUserName": second_app_username,
                    "qrCodeFormat": "STRING",
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "merchantPan": db_bqr_config_merchant_pan,
                    "merchantVpa": db_upi_config_vpa
                })
                response = APIProcessor.send_request(api_details)
                logger.debug(
                    f"Response received for regenerating static_qrcode_hdfc_mintoak api second QR is : {response}")
                regenerateqr_publish_id = response["publishId"]
                logger.debug(f"regenerateqr_publish_id is : {regenerateqr_publish_id}")

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
                    "org_code": org_code,
                    "merchant_pan": db_bqr_config_merchant_pan,
                    "vpa": db_upi_config_vpa,
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "qr_type": "BHARATQR",
                    "intent_type": "STATIC_QR",

                    "publish_id_2": regenerateqr_publish_id,
                    "org_code_2": org_code,
                    "merchant_pan_2": db_bqr_config_merchant_pan,
                    "vpa_2": db_upi_config_vpa,
                    "user_mobile_2": second_app_username,
                    "user_name_2": second_app_username,
                    "mid_2": db_bqr_config_mid,
                    "tid_2": db_bqr_config_tid,
                    "qr_type_2": "BHARATQR",
                    "intent_type_2": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from staticqr_intent where publish_id='{generateqr_publish_id}';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug("Fetching details for Static QR Intent:")
                db_staticqr_intent_publish_id = result["publish_id"].values[0]
                logger.debug(f"Fetching Publish ID from staticqr_intent table: {db_staticqr_intent_publish_id}")
                db_staticqr_intent_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching Org Code from staticqr_intent table: {db_staticqr_intent_org_code}")
                db_staticqr_intent_merchant_pan = result["merchant_pan"].values[0]
                logger.debug(f"Fetching Merchant PAN from staticqr_intent table: {db_staticqr_intent_merchant_pan}")
                db_staticqr_intent_vpa = result["vpa"].values[0]
                logger.debug(f"Fetching VPA from staticqr_intent table: {db_staticqr_intent_vpa}")
                db_staticqr_intent_user_mobile = result["user_mobile"].values[0]
                logger.debug(f"Fetching User Mobile from staticqr_intent table: {db_staticqr_intent_user_mobile}")
                db_staticqr_intent_user_name = result["user_name"].values[0]
                logger.debug(f"Fetching MID from db_staticqr_intent_user_name table: {db_staticqr_intent_user_name}")
                db_staticqr_intent_mid = result["mid"].values[0]
                logger.debug(f"Fetching MID from staticqr_intent table: {db_staticqr_intent_mid}")
                db_staticqr_intent_tid = result["tid"].values[0]
                logger.debug(f"Fetching TID from staticqr_intent table: {db_staticqr_intent_tid}")
                db_staticqr_intent_qrtype = result["qr_type"].values[0]
                logger.debug(f"Fetching QR Type from staticqr_intent table: {db_staticqr_intent_qrtype}")
                db_staticqr_intent_intent_type = result["intent_type"].values[0]
                logger.debug(f"Fetching Intent Type from staticqr_intent table: {db_staticqr_intent_intent_type}")

                query = f"select * from staticqr_intent where publish_id='{regenerateqr_publish_id}';"
                logger.debug(f"Query to fetch data from staticqr_intent table for second publish id : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result for second publish_id: {result}")
                db_staticqr_intent_publish_id_2 = result["publish_id"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_publish_id_2: {db_staticqr_intent_publish_id_2}")
                db_staticqr_intent_org_code_2 = result["org_code"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_org_code_2: {db_staticqr_intent_org_code_2}")
                db_staticqr_intent_merchant_pan_2 = result["merchant_pan"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_merchant_pan_2: {db_staticqr_intent_merchant_pan_2}")
                db_staticqr_intent_vpa_2 = result["vpa"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_vpa_2: {db_staticqr_intent_vpa_2}")
                db_staticqr_intent_user_mobile_2 = result["user_mobile"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_user_mobile_2: {db_staticqr_intent_user_mobile_2}")
                db_staticqr_intent_user_name_2 = result["user_name"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_user_name_2: {db_staticqr_intent_user_name_2}")
                db_staticqr_intent_mid_2 = result["mid"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_mid_2: {db_staticqr_intent_mid_2}")
                db_staticqr_intent_tid_2 = result["tid"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_tid_2: {db_staticqr_intent_tid_2}")
                db_staticqr_intent_qrtype_2 = result["qr_type"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_qrtype_2: {db_staticqr_intent_qrtype_2}")
                db_staticqr_intent_intent_type_2 = result["intent_type"].values[0]
                logger.debug(
                    f" static_qr_intent values for second publish id db_staticqr_intent_intent_type_2: {db_staticqr_intent_intent_type_2}")

                actual_db_values = {
                    "publish_id": db_staticqr_intent_publish_id,
                    "org_code": db_staticqr_intent_org_code,
                    "merchant_pan": db_staticqr_intent_merchant_pan,
                    "vpa": db_staticqr_intent_vpa,
                    "user_mobile": db_staticqr_intent_user_mobile,
                    "user_name": db_staticqr_intent_user_name,
                    "mid": db_staticqr_intent_mid,
                    "tid": db_staticqr_intent_tid,
                    "qr_type": db_staticqr_intent_qrtype,
                    "intent_type": db_staticqr_intent_intent_type,

                    "publish_id_2": db_staticqr_intent_publish_id_2,
                    "org_code_2": db_staticqr_intent_org_code_2,
                    "merchant_pan_2": db_staticqr_intent_merchant_pan_2,
                    "vpa_2": db_staticqr_intent_vpa_2,
                    "user_mobile_2": db_staticqr_intent_user_mobile_2,
                    "user_name_2": db_staticqr_intent_user_name_2,
                    "mid_2": db_staticqr_intent_mid_2,
                    "tid_2": db_staticqr_intent_tid_2,
                    "qr_type_2": db_staticqr_intent_qrtype_2,
                    "intent_type_2": db_staticqr_intent_intent_type_2
                }

                logger.debug(f"actual_db_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation-------------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_108_035():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Regeneration_With_Same_App_Username_Via_HDFC_MINTOAk
    Sub Feature Description: Verifying static QR regeneration with same app user via HDFC MINTOAK
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 035: Testcase ID
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        query = f"select * from bharatqr_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        logger.debug(f"deleting data from qrcode_audit table for org_code : {org_code}")
        query = "delete from qrcode_audit where org_code ='" + str(org_code) + "'"
        result = DBProcessor.delete_value_from_db(query)
        logger.debug(f"Query result : {result}")

        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for generating static_qrcode_hdfc_mintoak api is : {response}")
            res_generateqr_publish_id = response["publishId"]
            logger.debug(
                f"Publish id received for generating static_qrcode_hdfc_mintoak api is : {res_generateqr_publish_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for regenerating static_qrcode_hdfc_mintoak api is : {response}")
            regeneration_publish_id = response["publishId"]
            logger.debug(f"fetching publish_id for regeneration from api response is : {regeneration_publish_id}")

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
                    "merchant_pan": db_bqr_config_merchant_pan,
                    "vpa": db_upi_config_vpa,
                    "user_mobile": app_username,
                    "user_name": app_username,
                    "mid": db_bqr_config_mid,
                    "tid": db_bqr_config_tid,
                    "qr_type": "BHARATQR",
                    "intent_type": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from staticqr_intent where publish_id='{regeneration_publish_id}';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                logger.debug("Fetching details for staticqr_intent table:")
                db_staticqr_intent_publish_id = result["publish_id"].values[0]
                logger.debug(f"Fetching Publish ID from staticqr_intent table: {db_staticqr_intent_publish_id}")
                db_staticqr_intent_org_code = result["org_code"].values[0]
                logger.debug(f"Fetching Org Code from staticqr_intent table: {db_staticqr_intent_org_code}")
                db_staticqr_intent_merchant_pan = result["merchant_pan"].values[0]
                logger.debug(f"Fetching Merchant PAN from staticqr_intent table: {db_staticqr_intent_merchant_pan}")
                db_staticqr_intent_vpa = result["vpa"].values[0]
                logger.debug(f"Fetching VPA from staticqr_intent table: {db_staticqr_intent_vpa}")
                db_staticqr_intent_user_mobile = result["user_mobile"].values[0]
                logger.debug(f"Fetching User Mobile from staticqr_intent table: {db_staticqr_intent_user_mobile}")
                db_staticqr_intent_user_name = result["user_name"].values[0]
                logger.debug(
                    f"Fetching db_staticqr_intent_user_name from staticqr_intent table: {db_staticqr_intent_user_name}")
                db_staticqr_intent_mid = result["mid"].values[0]
                logger.debug(f"Fetching MID from staticqr_intent table: {db_staticqr_intent_mid}")
                db_staticqr_intent_tid = result["tid"].values[0]
                logger.debug(f"Fetching TID from staticqr_intent table: {db_staticqr_intent_tid}")
                db_staticqr_intent_qrtype = result["qr_type"].values[0]
                logger.debug(f"Fetching QR Type from staticqr_intent table: {db_staticqr_intent_qrtype}")
                db_staticqr_intent_intent_type = result["intent_type"].values[0]
                logger.debug(f"Fetching Intent Type from staticqr_intent table: {db_staticqr_intent_intent_type}")

                actual_db_values = {
                    "publish_id": db_staticqr_intent_publish_id,
                    "org_code": db_staticqr_intent_org_code,
                    "merchant_pan": db_staticqr_intent_merchant_pan,
                    "vpa": db_staticqr_intent_vpa,
                    "user_mobile": db_staticqr_intent_user_mobile,
                    "user_name": db_staticqr_intent_user_name,
                    "mid": db_staticqr_intent_mid,
                    "tid": db_staticqr_intent_tid,
                    "qr_type": db_staticqr_intent_qrtype,
                    "intent_type": db_staticqr_intent_intent_type
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
def test_common_100_108_036():
    """
        Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Generation_Failed_Via_HDFC_MINTOAK
        Sub Feature Description: Verifying failed static QR generation with app username via HDFC_MINTOAK
        TC naming code description: 100: payment method, 108: BQRV4 Static QR, 036: TC036
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

        query = f"select * from org_employee where username='{str(app_username)}'"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code=org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from bharatqr_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{str(org_code)}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username=portal_username,
                                                                          portal_password=portal_password,
                                                                          org_code=org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": app_username,
                "password": app_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
                "merchantPan": db_bqr_config_merchant_pan,
                "merchantVpa": db_upi_config_vpa
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_HDFC_MINTOAK api is : {response}")
            res_success = response["success"]
            logger.debug(f"Fetching res_success form api : {res_success}")
            res_message = response["message"]
            logger.debug(f"Fetching res_message form api : {res_message}")
            res_error_code = response["errorCode"]
            logger.debug(f"Fetching res_error_code form api : {res_error_code}")
            res_error_message = response["errorMessage"]
            logger.debug(f"Fetching res_error_message form api : {res_error_message}")
            res_real_code = response["realCode"]
            logger.debug(f"Fetching res_real_code form api : {res_real_code}")

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
                expected_api_values = {
                    "success": False,
                    "message": "You do not have permission to perform this operation.",
                    "errorCode": "EZETAP_0000193",
                    "errorMessage": "You do not have permission to perform this operation.",
                    "realCode": "UNAUTHORIZED_OPERATION"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": res_success,
                    "message": res_message,
                    "errorCode": res_error_code,
                    "errorMessage": res_error_message,
                    "realCode": res_real_code
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
def test_common_100_108_037():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Generation_Failed_With_Invalid_Username_Via_HDFC_MINTOAK
    Sub Feature Description: Verifying failed static qr generation with a username not registered with that merchant.
    TC naming code description: 100: payment method, 108: BQRV4 Static QR, 037: Testcase ID
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

        query = f"select * from org_employee where username='{app_username}';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC_MINTOAK',
                                                           portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = f"select * from bharatqr_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_bqr_config_id = result['id'].values[0]
        logger.info(f"fetched config id is : {db_bqr_config_id}")
        db_bqr_config_mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {db_bqr_config_mid}")
        db_bqr_config_tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {db_bqr_config_tid}")
        db_bqr_config_merchant_pan = result['merchant_pan'].values[0]
        logger.info(f"fetched merchant_pan is : {db_bqr_config_merchant_pan}")

        query = f"select * from upi_merchant_config where org_code ='{org_code}' AND status = 'ACTIVE' AND bank_code = 'HDFC_MINTOAK';"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        db_upi_config_vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {db_upi_config_vpa}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_org_code(portal_username, portal_password, org_code)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            dummy_mid = str(random.randint(111, 999)) + "@invalidMID"
            logger.debug(f"generated random invalid vpa is : {dummy_mid}")

            dummy_username = str(random.randint(1111111111, 9999999999))
            logger.debug(f"generated random username is : {dummy_username}")

            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_HDFC_MINTOAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrUserMobileNo": app_username,
                "qrUserName": dummy_username,
                "qrCodeFormat": "STRING",
                "mid": db_bqr_config_mid,
                "tid": db_bqr_config_tid,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_hdfc_mintoak api is : {response}")
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
                expected_api_values = {
                    "success": False,
                    "errorCode": "EZETAP_0001606",
                    "errorMessage": "User Login Name does not match with qrUserName"
                }
                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": res_success,
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
