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
def test_common_100_108_020():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Generation_Success_Via_KOTAK
    Sub Feature Description: Verifying static QR generation via KOTAK
    TC naming code description: 100: payment method, 108: BQRV4 Static QR, 020: Testcase ID
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
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for org_employee table : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query to fetch bharatqr_merchant_config : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching config_id from the bharatqr_merchant_config table : config_id : {config_id}")

        # to delete the publisher_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch upi_merchant_config : {result}")
            vpa = result['vpa'].values[0]
            logger.debug(f"Fetching mid from the upi_merchant_config table : vpa : {vpa}")

            #generating STATIC QR
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_KOTAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrCodeFormat": "STRING",
                "mid": mid,
                "tid": tid,
                "merchantPan": merchant_pan,
                "merchantVpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"generate_BQRV4_staticqr_KOTAK Response is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"generateqr_publish_id is : {generateqr_publish_id}")

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
                    "org_code" : org_code,
                    "merchant_pan" : merchant_pan,
                    "vpa" :vpa,
                    "user_mobile" :app_username,
                    "user_name" :app_username,
                    "mid" :mid,
                    "tid" :tid,
                    "qr_type" :"BHARATQR",
                    "intent_type" :"STATIC_QR"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"staticqr_intent_org_code_db is : {staticqr_intent_org_code_db}")
                staticqr_intent_merchant_pan_db = result["merchant_pan"].iloc[0]
                logger.debug(f"staticqr_intent_merchant_pan_db is : {staticqr_intent_merchant_pan_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"staticqr_intent_vpa_db is : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"staticqr_intent_user_mobile_db is : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"staticqr_intent_user_name_db is : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"staticqr_intent_mid_db is : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"staticqr_intent_tid_db is : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"staticqr_intent_qrtype_db is : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"staticqr_intent_intent_type_db is : {staticqr_intent_intent_type_db}")

                actual_db_values = {
                    "org_code" : staticqr_intent_org_code_db,
                    "merchant_pan" : staticqr_intent_merchant_pan_db,
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
        # -----------------------------------------End of DB Validation------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
def test_common_100_108_021():
    """
    Sub Feature Code: UI_Common_PM_BQRV4_StaticQR_Regeneration_Via_KOTAK
    Sub Feature Description: Verifying static QR regeneration via KOTAK
    TC naming code description: 100: Payment method, 108: BQRV4 Static QR, 021: Testcase ID
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

        query = "select * from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query result for org_employee, result : {result}")
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_WL', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from bharatqr_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
        logger.debug(f"Query to fetch data from the bharatqr_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"Query to fetch bharatqr_merchant_config : {result}")
        mid = result['mid'].values[0]
        logger.debug(f"Fetching mid from the bharatqr_merchant_config table : mid : {mid}")
        tid = result['tid'].values[0]
        logger.debug(f"Fetching tid from the bharatqr_merchant_config table : tid : {tid}")
        merchant_pan = result['merchant_pan'].values[0]
        logger.debug(f"Fetching merchant_pan from the bharatqr_merchant_config table : merchant_pan : {merchant_pan}")
        config_id = result['id'].values[0]
        logger.debug(f"Fetching config_id from the bharatqr_merchant_config table : config_id : {config_id}")

        # to delete the publisher_id which was generated previously
        testsuite_teardown.delete_staticqr_intent_table_entry(portal_username, portal_password, config_id)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            query = "select * from upi_merchant_config where org_code ='" + str(org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_WL';"
            logger.debug(f"Query to fetch upi_mc_id from the upi_merchant_config for the {org_code} : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch upi_merchant_config : {result}")
            vpa = result['vpa'].values[0]
            logger.debug(f"Fetching mid from the upi_merchant_config table : vpa : {vpa}")

            # Generate static QR for first user
            api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_KOTAK', request_body={
                "username": portal_username,
                "password": portal_password,
                "qrUserMobileNo": app_username,
                "qrUserName": app_username,
                "qrCodeType": "BHARAT",
                "qrOrgCode": org_code,
                "qrCodeFormat": "STRING",
                "mid": mid,
                "tid": tid,
                "merchantPan": merchant_pan,
                "merchantVpa": vpa
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"generate_BQRV4_staticqr_KOTAK Response is : {response}")
            generateqr_publish_id = response["publishId"]
            logger.debug(f"generateqr_publish_id is : {generateqr_publish_id}")

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
                    api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_KOTAK', request_body={
                        "username": portal_username,
                        "password": portal_password,
                        "qrCodeType": "BHARAT",
                        "qrOrgCode": org_code,
                        "qrUserMobileNo": second_app_username,
                        "qrUserName": second_app_username,
                        "qrCodeFormat": "STRING",
                        "mid": mid,
                        "tid": tid,
                        "merchantPan": merchant_pan,
                        "merchantVpa": vpa
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Response is : {response}")
                    publish_id = response["publishId"]
                    logger.debug(f"fetching publish_id from api response is : {publish_id}")
                    logger.debug(f"Response received for static_qrcode_generate_axisfc api is : {response}")

                else:
                    logger.error(f"User creation failed : {response}")
            else:
                # Regenerating static qr with another existing user for same org
                api_details = DBProcessor.get_api_details('generate_BQRV4_staticqr_KOTAK', request_body={
                    "username": portal_username,
                    "password": portal_password,
                    "qrCodeType": "BHARAT",
                    "qrOrgCode": org_code,
                    "qrUserMobileNo": second_app_username,
                    "qrUserName": second_app_username,
                    "qrCodeFormat": "STRING",
                    "mid": mid,
                    "tid": tid,
                    "merchantPan": merchant_pan,
                    "merchantVpa": vpa
                })
                response = APIProcessor.send_request(api_details)
                logger.debug(f"Response of static qr with another existing user for same org : {response}")

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
                    "merchant_pan" : merchant_pan,
                    "vpa" :vpa,
                    "user_mobile" :second_app_username,
                    "user_name" :second_app_username,
                    "mid" :mid,
                    "tid" :tid,
                    "qr_type" :"BHARATQR",
                    "intent_type" :"STATIC_QR"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from staticqr_intent where publish_id='" + str(generateqr_publish_id) + "';"
                logger.debug(f"Query to fetch data from staticqr_intent table : {query}")

                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")

                staticqr_intent_publish_id_db = result["publish_id"].iloc[0]
                logger.debug(f"staticqr_intent_publish_id_db is : {staticqr_intent_publish_id_db}")
                staticqr_intent_org_code_db = result["org_code"].iloc[0]
                logger.debug(f"staticqr_intent_org_code_db is : {staticqr_intent_org_code_db}")
                staticqr_intent_merchant_pan_db = result["merchant_pan"].iloc[0]
                logger.debug(f"staticqr_intent_merchant_pan_db is : {staticqr_intent_merchant_pan_db}")
                staticqr_intent_vpa_db = result["vpa"].iloc[0]
                logger.debug(f"staticqr_intent_vpa_db is : {staticqr_intent_vpa_db}")
                staticqr_intent_user_mobile_db = result["user_mobile"].iloc[0]
                logger.debug(f"staticqr_intent_user_mobile_db is : {staticqr_intent_user_mobile_db}")
                staticqr_intent_user_name_db = result["user_name"].iloc[0]
                logger.debug(f"staticqr_intent_user_name_db is : {staticqr_intent_user_name_db}")
                staticqr_intent_mid_db = result["mid"].iloc[0]
                logger.debug(f"staticqr_intent_mid_db is : {staticqr_intent_mid_db}")
                staticqr_intent_tid_db = result["tid"].iloc[0]
                logger.debug(f"staticqr_intent_tid_db is : {staticqr_intent_tid_db}")
                staticqr_intent_qrtype_db = result["qr_type"].iloc[0]
                logger.debug(f"staticqr_intent_qrtype_db is : {staticqr_intent_qrtype_db}")
                staticqr_intent_intent_type_db = result["intent_type"].iloc[0]
                logger.debug(f"staticqr_intent_intent_type_db is : {staticqr_intent_intent_type_db}")

                actual_db_values = {
                    "publish_id": staticqr_intent_publish_id_db,
                    "org_code": staticqr_intent_org_code_db,
                    "merchant_pan": staticqr_intent_merchant_pan_db,
                    "vpa": staticqr_intent_vpa_db,
                    "user_mobile": staticqr_intent_user_mobile_db,
                    "user_name": staticqr_intent_user_name_db,
                    "mid": staticqr_intent_mid_db,
                    "tid": staticqr_intent_tid_db,
                    "qr_type": staticqr_intent_qrtype_db,
                    "intent_type": staticqr_intent_intent_type_db
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
