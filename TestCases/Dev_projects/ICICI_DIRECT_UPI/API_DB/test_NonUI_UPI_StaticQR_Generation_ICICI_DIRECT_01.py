import json
import string
import sys
import random
import pytest
import requests
from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, APIProcessor, DBProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d102_107_001():
    """
    Sub Feature Code: NonUI_Common_StaticQR_UPI_QR_Generation_Success_ICICI_DIRECT
    Sub Feature Description: Performing static QR generation success via ICICI DIRECT
    TC naming code description: d102: ICICI DIRECT UPI Dev, 107: UPI STATIC QR, 001: TC001
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        tid = result['virtual_tid'].values[0]
        logger.info(f"fetched tid is : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.info(f"fetched mid is : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username,portal_password,vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

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
                                       "user_name" : portal_username,
                                       "org_code" : org_code
                                       }

                actual_api_values = {"success": success_api,
                                       "user_name" : username_api,
                                       "org_code" : org_code_api
                                       }
                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "publish_id": publish_id,
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa,
                    "user_mobile": mobile_number,
                    "user_name": app_username,
                    "mid": mid,
                    "tid": tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where config_id='" + str(upi_mc_id) + "'"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                publish_id_db = result["publish_id"].iloc[0]
                org_code_db = result["org_code"].iloc[0]
                config_id_db = result["config_id"].iloc[0]
                vpa_db = result["vpa"].iloc[0]
                user_mobile_db = result["user_mobile"].iloc[0]
                username_db = result["user_name"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "publish_id": publish_id_db,
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db
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
def test_d102_107_002():
    """
    Sub Feature Code: NonUI_Common_StaticQR_UPI_QR_Re_Generation_ICICI_DIRECT
    Sub Feature Description: Re-generate the static QR using UPI and verify the tables getting updated.
    TC naming code description: d102: ICICI-DIRECT UPI Dev, 107: UPI STATIC QR, 002: TC002
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                    portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        tid = result['virtual_tid'].values[0]
        logger.info(f"fetched tid is : {tid}")
        mid = result['virtual_mid'].values[0]
        logger.info(f"fetched mid is : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username,portal_password,vpa)

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
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            mid_api = response["mid"]
            tid_api = response["tid"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "qrOrgCode": org_code,
                "merchantVpa": vpa,
                "mid": mid,
                "tid": tid
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id_2 = response["publishId"]
            success_api_2 = response["success"]
            username_api_2 = response["username"]
            org_code_api_2 = response["merchantCode"]
            mid_api_2 = response["mid"]
            tid_api_2 = response["tid"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

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
                                       "user_name" : portal_username,
                                       "org_code" : org_code,
                                       "mid": mid,
                                       "tid": tid,
                                       "success_2": True,
                                       "user_name_2": portal_username,
                                       "org_code_2": org_code,
                                       "mid_2": mid,
                                       "tid_2": tid,
                                       "publish_id": publish_id,
                                       }

                actual_api_values = {"success": success_api,
                                     "user_name" : username_api,
                                     "org_code" : org_code_api,
                                     "mid": mid_api,
                                     "tid": tid_api,
                                     "success_2": success_api_2,
                                     "user_name_2": username_api_2,
                                     "org_code_2": org_code_api_2,
                                     "mid_2": mid_api_2,
                                     "tid_2": tid_api_2,
                                     "publish_id": publish_id_2,
                                       }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "publish_id": publish_id,
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa,
                    "user_mobile": mobile_number,
                    "user_name": app_username,
                    "mid": mid,
                    "tid": tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR",
                    "audit_publish_id": publish_id,
                    "audit_org_code": org_code,
                    "audit_qr_type": "UPI",
                    "audit_intent_type": "STATIC_QR",
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from qrcode_audit where org_code='" + org_code + "'"
                logger.debug(f"Query to fetch data from qrcode_audit table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                audit_publish_id_db = result["publish_id"].iloc[0]
                audit_org_code_db = result["org_code"].iloc[0]
                audit_qr_type_db = result['qr_type'].values[0]
                audit_intent_type_db = result['intent_type'].values[0]

                query = "select * from staticqr_intent where org_code='" + org_code + "'"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                publish_id_db = result["publish_id"].iloc[0]
                org_code_db = result["org_code"].iloc[0]
                config_id_db = result["config_id"].iloc[0]
                vpa_db = result["vpa"].iloc[0]
                user_mobile_db = result["user_mobile"].iloc[0]
                username_db = result["user_name"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "publish_id": publish_id_db,
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db,
                    "audit_publish_id": audit_publish_id_db,
                    "audit_org_code": audit_org_code_db,
                    "audit_qr_type": audit_qr_type_db,
                    "audit_intent_type": audit_intent_type_db,
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
def test_d102_107_003():
    """
    Sub Feature Code: NonUI_Common_StaticQR_UPI_QR_Generation_With_AppUser_ICICI_DIRECT
    Sub Feature Description: Performing static QR generation with app user instead of portal user via ICICI DIRECT
    TC naming code description: d102: Payment Method, 107: UPI STATIC QR, 003: TC003
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        tid = result['tid'].values[0]
        logger.info(f"fetched tid is : {tid}")
        mid = result['mid'].values[0]
        logger.info(f"fetched mid is : {mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username,portal_password,vpa)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": app_username,
                "password": app_password,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for static_qrcode_generate_icici direct api is : {response}")

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

        # -----------------------------------------Start of API Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "success": False,
                    "message": "You do not have permission to perform this operation.",
                    "realCode": "UNAUTHORIZED_OPERATION"
                }
                logger.debug(f"expected_api_values: {expected_db_values}")

                success_api = response['success']
                message_api = response['message']
                real_code_api = response['realCode']

                actual_db_values = {
                    "success": success_api,
                    "message": message_api,
                    "realCode": real_code_api
                }
                logger.debug(f"actual_api_values : {actual_db_values}")

                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
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
@pytest.mark.dbVal
def test_d102_107_004():
    """
    Sub Feature Code: NonUI_Common_StaticQR_UPI_QR_Regeneration_Different_User_ICICI_DIRECT
    Sub Feature Description: Re-generate the static QR using UPI with different user and verify the tables getting updated.
    TC naming code description: d102: ICICI-DIRECT UPI Dev, 107: UPI STATIC QR, 004: Testcase ID
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
        mobile_number = result['mobile_number'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='ICICI_DIRECT', portal_un=portal_username,
                                                    portal_pw=portal_password, payment_mode='UPI',bank_code_bqr='HDFC')
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'ICICI_DIRECT'"
        logger.debug(f"Query to fetch data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        upi_mc_id = result['id'].values[0]
        logger.info(f"fetched upi_mc_id is : {upi_mc_id}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.info(f"fetched pg_merchant_id is : {pg_merchant_id}")
        vpa = result['vpa'].values[0]
        logger.info(f"fetched vpa is : {vpa}")
        virtual_tid = result['virtual_tid'].values[0]
        logger.info(f"fetched virtual tid is : {virtual_tid}")
        virtual_mid = result['virtual_mid'].values[0]
        logger.info(f"fetched virtual mid is : {virtual_mid}")

        testsuite_teardown.delete_staticqr_intent_table_entry_by_vpa(portal_username,portal_password,vpa)

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
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
        # ---------------------------------------- Preconditions Completed ------------------------------------
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrCodeType": "UPI",
                "qrOrgCode": org_code,
                "qrUserMobileNo": mobile_number,
                "qrUserName": app_username,
                "upiMerchantConfigId": str(upi_mc_id),
                "merchantVpa": vpa,
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
            publish_id = response["publishId"]
            success_api = response["success"]
            username_api = response["username"]
            org_code_api = response["merchantCode"]
            mid_api = response["mid"]
            tid_api = response["tid"]
            logger.debug(f"fetching success status,publish_id, username, org code from api response is : "
                         f"{success_api},{publish_id},{username_api},{org_code_api}")

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
                    # Regenerating static qr with another user for same org
                    api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrCodeType": "UPI",
                        "qrOrgCode": org_code,
                        "qrUserMobileNo": second_app_username,
                        "qrUserName": second_app_username,
                        "upiMerchantConfigId": str(upi_mc_id),
                        "merchantVpa": vpa,
                    })
                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
                    publish_id_second = response["publishId"]
                    success_api_second = response["success"]
                    username_api_second = response["username"]
                    org_code_api_second = response["merchantCode"]
                    mid_api_second = response["mid"]
                    tid_api_second = response["tid"]
                    logger.debug(f"fetching success status,publish_id, username, org code from second api response is : "
                                 f"{success_api_second},{publish_id_second},{username_api_second},{org_code_api_second}")
                else:
                    logger.error(f"User creation failed : {response}")
            else:
                # Regenerating static qr with another existing user for same org
                api_details = DBProcessor.get_api_details('static_qrcode_generate_icici_direct', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrCodeType": "UPI",
                    "qrOrgCode": org_code,
                    "qrUserMobileNo": second_app_username,
                    "qrUserName": second_app_username,
                    "upiMerchantConfigId": str(upi_mc_id),
                    "merchantVpa": vpa,
                })
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response received for static_qrcode_generate_icici_direct api is : {response}")
                publish_id_second = response["publishId"]
                success_api_second = response["success"]
                username_api_second = response["username"]
                org_code_api_second = response["merchantCode"]
                mid_api_second = response["mid"]
                tid_api_second = response["tid"]
                logger.debug(f"fetching success status,publish_id, username, org code from second api response is : "
                             f"{success_api_second},{publish_id_second},{username_api_second},{org_code_api_second}")

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
                    "success": True,
                    "success_2": True,
                    "user_name" : portal_username,
                    "user_name_2": portal_username,
                    "org_code" : org_code,
                    "org_code_2": org_code,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "mid_2": virtual_mid,
                    "tid_2": virtual_tid,
                    "publish_id": publish_id,
               }

                actual_api_values = {
                    "success": success_api,
                    "success_2": success_api_second,
                    "user_name" : username_api,
                    "user_name_2": username_api_second,
                    "org_code" : org_code_api,
                    "org_code_2": org_code_api_second,
                    "mid": mid_api,
                    "tid": tid_api,
                    "mid_2": mid_api_second,
                    "tid_2": tid_api_second,
                    "publish_id": publish_id_second,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

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
                    "org_code": org_code,
                    "config_id": upi_mc_id,
                    "vpa": vpa,
                    "user_mobile": second_app_username,
                    "user_name": second_app_username,
                    "mid": virtual_mid,
                    "tid": virtual_tid,
                    "qr_type": "UPI",
                    "intent_type": "STATIC_QR"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + publish_id + "'"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                org_code_db = result["org_code"].iloc[0]
                config_id_db = result["config_id"].iloc[0]
                vpa_db = result["vpa"].iloc[0]
                user_mobile_db = result["user_mobile"].iloc[0]
                username_db = result["user_name"].iloc[0]
                tid_db = result['tid'].values[0]
                mid_db = result['mid'].values[0]
                qr_type_db = result['qr_type'].values[0]
                intent_type_db = result['intent_type'].values[0]

                actual_db_values = {
                    "org_code": org_code_db,
                    "config_id": config_id_db,
                    "vpa": vpa_db,
                    "user_mobile": user_mobile_db,
                    "user_name": username_db,
                    "mid": mid_db,
                    "tid": tid_db,
                    "qr_type": qr_type_db,
                    "intent_type": intent_type_db
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

