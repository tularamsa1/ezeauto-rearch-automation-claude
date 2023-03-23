import sys
import pytest
import random
import string
import numpy as np
from datetime import datetime
from datetime import timedelta
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, EzeGro_processor

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_001():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Generate_and_Validate_OTP_For_NewUser
    Sub Feature Description: API: Validate for New user by hitting generate_otp and validate_otp api
    TC naming code description: 600: EzeGro, 601: Sale, 001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        mobile_number = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["MobileNumber"]
        logger.info(f"mobile_number is {mobile_number}")
        application_Key = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["ApplicationKey"]
        logger.info(f"application_Key is {application_Key}")
        device_identifier = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifier"]
        logger.info(f"device_identifier is {device_identifier}")
        device_identifier_type = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifierType"]
        logger.info(f"device_identifier_type is {device_identifier_type}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        EzeGro_processor.delete_existing_ezegro_user(mobile_number)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                    "mobileNumber": mobile_number,
                    "applicationKey": application_Key,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")
            generate_otp_application_key = response['applicationKey']
            logger.info(f"Value of applicationKey obtained from generate otp : {generate_otp_application_key}")
            generate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from generate otp : {generate_otp_device_identifier}")
            generate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from generate otp : {generate_otp_device_identifier_type}")
            generate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from generate otp : {generate_otp_mobile_number}")
            generate_otp_new_merchant = response['newMerchant']
            logger.info(f"Value of newMerchant obtained from generate otp : {generate_otp_new_merchant}")
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")
            generate_otp_resend_count_left = response['resendCountLeft']
            logger.info(f"Value of resendCountLeft obtained from generate otp : {generate_otp_resend_count_left}")
            generate_otp_success = response['success']
            logger.info(f"Value of success obtained from generate otp : {generate_otp_success}")

            push_token = str(random.randint(0,5))
            api_details = DBProcessor.get_api_details('validate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "otp": generate_otp_response,
                "pushToken": push_token,
                "customerVersion": "0",
                "orderVersion": "0",
                "reviewVersion": "0",
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for validate otp is: {response}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from validate otp : {validate_otp_device_identifier}")
            validate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from validate otp : {validate_otp_device_identifier_type}")
            validate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from validate otp : {validate_otp_mobile_number}")
            validate_otp_customer_version = response['customerVersion']
            logger.info(f"Value of customerVersion obtained from validate otp : {validate_otp_customer_version}")
            validate_otp_order_version = response['orderVersion']
            logger.info(f"Value of orderVersion obtained from validate otp : {validate_otp_order_version}")
            validate_otp_review_version = response['reviewVersion']
            logger.info(f"Value of reviewVersion obtained from validate otp : {validate_otp_review_version}")
            validate_otp_check_status_after = response['settings']['checkStatusAfter']
            logger.info(f"Value of checkStatusAfter obtained from validate otp : {validate_otp_check_status_after}")
            validate_otp_check_status_interval = response['settings']['checkStatusInterval']
            logger.info(f"Value of checkStatusInterval obtained from validate otp : {validate_otp_check_status_interval}")
            validate_otp_check_status_count = response['settings']['checkStatusCount']
            logger.info(f"Value of checkStatusCount obtained from validate otp : {validate_otp_check_status_count}")
            validate_otp_min_agent_balance = response['settings']['minAgentBalance']
            logger.info(f"Value of minAgentBalance obtained from validate otp : {validate_otp_min_agent_balance}")
            validate_otp_min_amount = response['settings']['minAmount']
            logger.info(f"Value of minAmount obtained from validate otp : {validate_otp_min_amount}")
            validate_otp_max_amount = response['settings']['maxAmount']
            logger.info(f"Value of maxAmount obtained from validate otp : {validate_otp_max_amount}")
            validate_otp_max_agent_balance = response['settings']['maxAgentBalance']
            logger.info(f"Value of maxAgentBalance obtained from validate otp : {validate_otp_max_agent_balance}")
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            store_name = f"Mobile Stores {random.choice(string.ascii_uppercase)}"
            pd_category = "APPAREL"
            api_details = DBProcessor.get_api_details('updateMerchant', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "merchant": {
                "storeName": store_name ,
                "mobileNumber": mobile_number,
                "productCategory": pd_category,
                "optedForCommunication": True
                }
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for updateMerchant {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Update Merchant is: {response}")
            merchant_store_name = response['merchant']['storeName']
            logger.info(f"Value of Store Name obtained from Merchant Update : {merchant_store_name}")
            merchant_pdt_category = response['merchant']['productCategory']
            logger.info(f"Value of merchant_pdt_category obtained from Merchant Update : {merchant_pdt_category}")
            merchant_status = response['merchant']['status']
            logger.info(f"Value of status obtained from Merchant Update : {merchant_status}")
            merchant_opt_comm = response['merchant']['optedForCommunication']
            logger.info(f"Value of merchant opted communication obtained from Merchant Update : {merchant_opt_comm}")

            query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from user table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of user table : {result}")
            expected_user_db = result['user'].values[0]
            logger.info(f"Value of user obtained from user table : {expected_user_db}")

            query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from otp table for actual values : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result for actual values from otp table : {result}")
            actual_otp_db = result['otp'].values[0]
            logger.info(f"Value of actual otp obtained from otp table : {actual_otp_db}")
            otp_created_time = result['created_time'].values[0]
            logger.info(f"Value of otp_created_time obtained from otp table : {otp_created_time}")

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

            query = "select id from product_category where name = 'APPAREL';"
            logger.debug(f"Query to fetch id from product_category table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result from product_category table : {result}")
            id_db = result['id'].values[0]
            logger.info(f"Fetching id from product_category table : {id_db}")

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

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "app_key": application_Key,
                    "new_merchant": True,
                    "otp": generate_otp_response,
                    "resend_count_left": 2,
                    "success": True,
                    "user": validate_otp_user,
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "mobile_no": mobile_number,
                    "check_status_after": 30,
                    "check_status_interval": 15,
                    "check_status_count": 8,
                    "min_agent_bal": 100,
                    "min_amt": 100,
                    "max_amt": 49000,
                    "max_agent_bal": 100000,
                    "customer_version": 0,
                    "review_version": 0,
                    "order_version": 0,
                    "status" : "ACTIVE",
                    "opted_for_communication" : True,
                    "store_name": store_name,
                    "pdt_category": pd_category,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "app_key": generate_otp_application_key,
                    "new_merchant": generate_otp_new_merchant,
                    "otp": actual_otp_db,
                    "resend_count_left": generate_otp_resend_count_left,
                    "success": generate_otp_success,
                    "user": expected_user_db,
                    "device_identifier": validate_otp_device_identifier,
                    "device_identifier_type": validate_otp_device_identifier_type,
                    "mobile_no": validate_otp_mobile_number,
                    "check_status_after": validate_otp_check_status_after,
                    "check_status_interval": validate_otp_check_status_interval,
                    "check_status_count": validate_otp_check_status_count,
                    "min_agent_bal": validate_otp_min_agent_balance,
                    "min_amt": validate_otp_min_amount,
                    "max_amt": validate_otp_max_amount,
                    "max_agent_bal": validate_otp_max_agent_balance,
                    "customer_version": int(validate_otp_customer_version),
                    "review_version": int(validate_otp_review_version),
                    "order_version": int(validate_otp_order_version),
                    "status": merchant_status,
                    "opted_for_communication": merchant_opt_comm,
                    "store_name": merchant_store_name,
                    "pdt_category": merchant_pdt_category,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                created_time = datetime.strptime(str(otp_created_time),'%Y-%m-%dT%H:%M:%S.%f000')
                jwt_created_time = datetime.strptime(str(jwt_created_time_db),'%Y-%m-%dT%H:%M:%S.%f000')

                expected_db_values = {
                    "otp_created_by": "ezetap",
                    "otp_mobile_number": mobile_number,
                    "otp_expiry": created_time + timedelta(minutes=5),
                    "otp": actual_otp_db,
                    "otp_resend_count_left":2,
                    "otp_attempts_left": 3,
                    "otp_status": "EXPIRED",
                    "app_key": application_Key,
                    "app_name": "ezegro",
                    "app_key_status": "ACTIVE",
                    "jwt_key_expiry": jwt_created_time + timedelta(days=45),
                    "jwt_key_renew_interval": jwt_created_time + timedelta(days=30),
                    "jwt_key_user": validate_otp_user,
                    "jwt_key_status": "ACTIVE",
                    "push_mobile_number": mobile_number,
                    "push_status": "ACTIVE",
                    "push_token": push_token ,
                    "user_device_identifier": device_identifier,
                    "user_device_identifier_type": device_identifier_type,
                    "user_mobile_number": mobile_number,
                    "user": validate_otp_user,
                    "agent_id": mobile_number,
                    "agent_bal": 0.000,
                    "agent_store_name": store_name,
                    "agent_status":"ACTIVE",
                    "pdt_sub_category": "NULL",
                    "merchant_status" : "ACTIVE",
                    "merchant_store_name" :store_name,
                    "category_id" : id_db
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from otp where mobile_number ='"+str(mobile_number)+"' order by created_time desc limit 1;"
                logger.debug(f"Query to fetch data for actual db values from otp table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from otp table : {result}")
                otp_created_by_db = result['created_by'].values[0]
                logger.info(f"Fetching actual db created_by value from the otp table : {otp_created_by_db}")
                otp_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the otp table : {otp_mobile_number_db}")
                otp_expiry_db = result['otp_expiry'].values[0]
                logger.info(f"Fetching actual db otp_expiry value from the otp table : {otp_expiry_db}")
                otp_db = result['otp'].values[0]
                logger.info(f"Fetching actual db otp value from the otp table : {otp_db}")
                otp_resend_count_left_db = result['resend_count_left'].values[0]
                logger.info(f"Fetching actual db resend_count_left value from the otp table : {otp_resend_count_left_db}")
                otp_attempts_left_db = result['otp_attempts_left'].values[0]
                logger.info(f"Fetching actual db otp_attempts_left value from the otp table : {otp_attempts_left_db}")
                otp_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the otp table : {otp_status_db}")

                query = "select * from application_key where status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from application_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from application_key table : {result}")
                application_key_db = result['application_key'].values[0]
                logger.info(f"Fetching actual db application_key value from the application_key table : {application_key_db}")
                application_name_db = result['application_name'].values[0]
                logger.info(f"Fetching actual db application_name value from the application_key table : {application_name_db}")
                application_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {application_key_status_db}")

                query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from jwt_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from jwt_key table : {result}")
                jwt_key_expiry_db = result['expiry'].values[0]
                logger.info(f"Fetching actual db expiry value from the application_key table : {jwt_key_expiry_db}")
                jwt_key_renew_interval_db = result['renew_interval'].values[0]
                logger.info(f"Fetching actual db renew_interval value from the application_key table : {jwt_key_renew_interval_db}")
                jwt_key_user_db = result['user'].values[0]
                logger.info(f"Fetching actual db user value from the application_key table : {jwt_key_user_db}")
                jwt_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {jwt_key_status_db}")

                query = "select * from push where mobile_number ='"+str(mobile_number)+ "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from push table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from push table : {result}")
                push_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the push table : {push_mobile_number_db}")
                push_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the push table : {push_status_db}")
                push_token_db = result['token'].values[0]
                logger.info(f"Fetching actual db token value from the push table : {push_token_db}")

                query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from user table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from user table : {result}")
                user_db = result['user'].values[0]
                logger.info(f"Value of user obtained from user table : {user_db}")
                user_device_identifier_db = result['device_identifier'].values[0]
                logger.info(f"Fetching actual db device_identifier value from the user table : {user_device_identifier_db}")
                user_device_identifier_type_db = result['device_identifier_type'].values[0]
                logger.info(f"Fetching actual db device_identifier_type value from the user table : {user_device_identifier_type_db}")
                user_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the user table : {user_mobile_number_db}")

                query = "select * from agent where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from agent table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from agent table : {result}")
                agent_id_db = result['agent_id'].values[0]
                logger.info(f"Value of agent id obtained from agent table : {agent_id_db}")
                mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching mobile_number value from the agent table : {mobile_number_db}")
                name_db = result['name'].values[0]
                logger.info(f"Fetching name value from the agent table : {name_db}")
                balance_db = result['balance'].values[0]
                logger.info(f"Fetching balance value from the agent table : {balance_db}")
                agent_status_db = result['status'].values[0]
                logger.info(f"Fetching agent_status_db value from the agent table : {agent_status_db}")

                query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from merchant table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                result = result.replace(np.nan,'NULL',regex=True)
                logger.info(f"Query result for actual db values from merchant table : {result}")
                mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained from merchant table : {mobile_number_db}")
                product_sub_category_db = result['product_sub_category'].values[0]
                logger.info(f"Fetching product_sub_category value from the merchant table : {product_sub_category_db}")
                mer_store_name_db = result['store_name'].values[0]
                logger.info(f"Fetching store name value from the merchant table : {mer_store_name_db}")
                category_id_db = result['category_id'].values[0]
                logger.info(f"Fetching category_id value from the merchant table : {category_id_db}")
                merchant_status_db = result['status'].values[0]
                logger.info(f"Fetching merchant_status_db value from the merchant table : {merchant_status_db}")

                actual_db_values = {
                    "otp_created_by": otp_created_by_db,
                    "otp_mobile_number": otp_mobile_number_db,
                    "otp_expiry": datetime.strptime(str(otp_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "otp": otp_db,
                    "otp_resend_count_left": otp_resend_count_left_db,
                    "otp_attempts_left": otp_attempts_left_db,
                    "otp_status": otp_status_db,
                    "app_key": application_key_db,
                    "app_name": application_name_db,
                    "app_key_status": application_key_status_db,
                    "jwt_key_expiry": datetime.strptime(str(jwt_key_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_renew_interval": datetime.strptime(str(jwt_key_renew_interval_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_user": jwt_key_user_db,
                    "jwt_key_status": jwt_key_status_db,
                    "push_mobile_number": push_mobile_number_db,
                    "push_status": push_status_db,
                    "push_token": push_token_db,
                    "user_device_identifier": user_device_identifier_db,
                    "user_device_identifier_type": user_device_identifier_type_db,
                    "user_mobile_number": user_mobile_number_db,
                    "user": user_db,
                    "agent_id": agent_id_db,
                    "agent_bal": balance_db,
                    "agent_store_name": name_db,
                    "agent_status": agent_status_db,
                    "pdt_sub_category": product_sub_category_db,
                    "merchant_status": merchant_status_db,
                    "merchant_store_name": mer_store_name_db,
                    "category_id": category_id_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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
def test_common_600_601_002():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Generate_and_Validate_OTP_For_ExistingUser
    Sub Feature Description: API: Validate for existing user by hitting generate_otp and validate_otp api
    TC naming code description: 600: EzeGro functions, 601: Sale, 002: TC002
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        mobile_number = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["MobileNumber"]
        logger.info(f"Fetching the mobile_number from EzeGro sheet : {mobile_number}")
        application_Key = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["ApplicationKey"]
        logger.info(f"Fetching the application_Key from EzeGro sheet : {application_Key}")
        device_identifier = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifier"]
        logger.info(f"Fetching the device_identifier from EzeGro sheet : {device_identifier}")
        device_identifier_type = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifierType"]
        logger.debug(f"Fetching the device_identifier_type from EzeGro sheet : {device_identifier_type}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generate the otp
            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                    "mobileNumber": mobile_number,
                    "applicationKey": application_Key,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")
            generate_otp_application_key = response['applicationKey']
            logger.info(f"Value of applicationKey obtained from generate otp : {generate_otp_application_key}")
            generate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from generate otp : {generate_otp_device_identifier}")
            generate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from generate otp : {generate_otp_device_identifier_type}")
            generate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from generate otp : {generate_otp_mobile_number}")
            generate_otp_new_merchant = response['newMerchant']
            logger.info(f"Value of newMerchant obtained from generate otp : {generate_otp_new_merchant}")
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")
            generate_otp_resend_count_left = response['resendCountLeft']
            logger.info(f"Value of resendCountLeft obtained from generate otp : {generate_otp_resend_count_left}")
            generate_otp_success = response['success']
            logger.info(f"Value of success obtained from generate otp : {generate_otp_success}")

            query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from otp table for actual values : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result for actual values from otp table : {result}")
            actual_otp_db = result['otp'].values[0]
            logger.info(f"Value of actual otp obtained from otp table : {actual_otp_db}")
            otp_created_time = result['created_time'].values[0]
            logger.info(f"Value of otp_created_time obtained from otp table : {otp_created_time}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token is : {push_token}")

            # validate the otp
            api_details = DBProcessor.get_api_details('validate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "otp": generate_otp_response,
                "pushToken": push_token,
                "customerVersion": "0",
                "orderVersion": "0",
                "reviewVersion": "0",
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for validate otp is: {response}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from validate otp : {validate_otp_device_identifier}")
            validate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from validate otp : {validate_otp_device_identifier_type}")
            validate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from validate otp : {validate_otp_mobile_number}")
            validate_otp_customer_version = response['customerVersion']
            logger.info(f"Value of customerVersion obtained from validate otp : {validate_otp_customer_version}")
            validate_otp_order_version = response['orderVersion']
            logger.info(f"Value of orderVersion obtained from validate otp : {validate_otp_order_version}")
            validate_otp_review_version = response['reviewVersion']
            logger.info(f"Value of reviewVersion obtained from validate otp : {validate_otp_review_version}")
            validate_otp_check_status_after = response['settings']['checkStatusAfter']
            logger.info(f"Value of checkStatusAfter obtained from validate otp : {validate_otp_check_status_after}")
            validate_otp_check_status_interval = response['settings']['checkStatusInterval']
            logger.info(f"Value of checkStatusInterval obtained from validate otp : {validate_otp_check_status_interval}")
            validate_otp_check_status_count = response['settings']['checkStatusCount']
            logger.info(f"Value of checkStatusCount obtained from validate otp : {validate_otp_check_status_count}")
            validate_otp_min_agent_balance = response['settings']['minAgentBalance']
            logger.info(f"Value of minAgentBalance obtained from validate otp : {validate_otp_min_agent_balance}")
            validate_otp_min_amount = response['settings']['minAmount']
            logger.info(f"Value of minAmount obtained from validate otp : {validate_otp_min_amount}")
            validate_otp_max_amount = response['settings']['maxAmount']
            logger.info(f"Value of maxAmount obtained from validate otp : {validate_otp_max_amount}")
            validate_otp_max_agent_balance = response['settings']['maxAgentBalance']
            logger.info(f"Value of maxAgentBalance obtained from validate otp : {validate_otp_max_agent_balance}")

            query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from user table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of user table : {result}")
            expected_user_db = result['user'].values[0]
            logger.info(f"Value of user obtained from user table : {expected_user_db}")

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

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

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "app_key": application_Key,
                    "new_merchant": False,
                    "otp": generate_otp_response,
                    "resend_count_left": 2,
                    "success": True,
                    "user": validate_otp_user,
                    "customer_version": 0,
                    "review_version": 0,
                    "order_version": 0,
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "mobile_no": mobile_number,
                    "check_status_after": 30,
                    "check_status_interval": 15,
                    "check_status_count": 8,
                    "min_agent_bal": 100,
                    "min_amt": 100,
                    "max_amt": 49000,
                    "max_agent_bal": 100000
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "app_key": generate_otp_application_key,
                    "new_merchant": generate_otp_new_merchant,
                    "otp": actual_otp_db,
                    "resend_count_left": generate_otp_resend_count_left,
                    "success": generate_otp_success,
                    "user": expected_user_db,
                    "customer_version": int(validate_otp_customer_version),
                    "review_version": int(validate_otp_review_version),
                    "order_version": int(validate_otp_order_version),
                    "device_identifier": validate_otp_device_identifier,
                    "device_identifier_type": validate_otp_device_identifier_type,
                    "mobile_no": validate_otp_mobile_number,
                    "check_status_after": validate_otp_check_status_after,
                    "check_status_interval": validate_otp_check_status_interval,
                    "check_status_count": validate_otp_check_status_count,
                    "min_agent_bal": validate_otp_min_agent_balance,
                    "min_amt": validate_otp_min_amount,
                    "max_amt": validate_otp_max_amount,
                    "max_agent_bal": validate_otp_max_agent_balance,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                created_time = datetime.strptime(str(otp_created_time),'%Y-%m-%dT%H:%M:%S.%f000')
                jwt_created_time = datetime.strptime(str(jwt_created_time_db),'%Y-%m-%dT%H:%M:%S.%f000')
                expected_db_values = {
                    "otp_created_by": "ezetap",
                    "otp_mobile_no": mobile_number,
                    "otp_expiry": created_time + timedelta(minutes=5),
                    "otp": actual_otp_db,
                    "otp_resend_count_left":2,
                    "otp_attempts_left": 3,
                    "otp_status": "EXPIRED",
                    "app_key": application_Key,
                    "app_key_name": "ezegro",
                    "app_key_status": "ACTIVE",
                    "jwt_key_expiry": jwt_created_time + timedelta(days=45),
                    "jwt_key_renew_interval": jwt_created_time + timedelta(days=30),
                    "jwt_key_user": validate_otp_user,
                    "jwt_key_status": "ACTIVE",
                    "push_mobile_no": mobile_number,
                    "push_status": "ACTIVE",
                    "push_token": push_token,
                    "user_device_identifier": device_identifier,
                    "user_device_identifier_type": device_identifier_type,
                    "user_mobile_no": mobile_number,
                    "user": validate_otp_user
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from otp where mobile_number ='"+str(mobile_number)+"' order by created_time desc limit 1;"
                logger.debug(f"Query to fetch data for actual db values from otp table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from otp table : {result}")
                otp_created_by_db = result['created_by'].values[0]
                logger.info(f"Fetching actual db created_by value from the otp table : {otp_created_by_db}")
                otp_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the otp table : {otp_mobile_number_db}")
                otp_expiry_db = result['otp_expiry'].values[0]
                logger.info(f"Fetching actual db otp_expiry value from the otp table : {otp_expiry_db}")
                otp_db = result['otp'].values[0]
                logger.info(f"Fetching actual db otp value from the otp table : {otp_db}")
                otp_resend_count_left_db = result['resend_count_left'].values[0]
                logger.info(f"Fetching actual db resend_count_left value from the otp table : {otp_resend_count_left_db}")
                otp_attempts_left_db = result['otp_attempts_left'].values[0]
                logger.info(f"Fetching actual db otp_attempts_left value from the otp table : {otp_attempts_left_db}")
                otp_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the otp table : {otp_status_db}")

                query = "select * from application_key where status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from application_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from application_key table : {result}")
                application_key_db = result['application_key'].values[0]
                logger.info(f"Fetching actual db application_key value from the application_key table : {application_key_db}")
                application_name_db = result['application_name'].values[0]
                logger.info(f"Fetching actual db application_name value from the application_key table : {application_name_db}")
                application_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {application_key_status_db}")

                query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from jwt_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from jwt_key table : {result}")
                jwt_key_expiry_db = result['expiry'].values[0]
                logger.info(f"Fetching actual db expiry value from the application_key table : {jwt_key_expiry_db}")
                jwt_key_renew_interval_db = result['renew_interval'].values[0]
                logger.info(f"Fetching actual db renew_interval value from the application_key table : {jwt_key_renew_interval_db}")
                jwt_key_user_db = result['user'].values[0]
                logger.info(f"Fetching actual db user value from the application_key table : {jwt_key_user_db}")
                jwt_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {jwt_key_status_db}")

                query = "select * from push where mobile_number ='"+str(mobile_number)+ "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from push table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from push table : {result}")
                push_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the push table : {push_mobile_number_db}")
                push_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the push table : {push_status_db}")
                push_token_db = result['token'].values[0]
                logger.info(f"Fetching actual db token value from the push table : {push_token_db}")

                query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from user table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from user table : {result}")
                user_db = result['user'].values[0]
                logger.info(f"Value of user obtained from user table : {user_db}")
                user_device_identifier_db = result['device_identifier'].values[0]
                logger.info(f"Fetching actual db device_identifier value from the user table : {user_device_identifier_db}")
                user_device_identifier_type_db = result['device_identifier_type'].values[0]
                logger.info(f"Fetching actual db device_identifier_type value from the user table : {user_device_identifier_type_db}")
                user_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the user table : {user_mobile_number_db}")

                actual_db_values = {
                    "otp_created_by": otp_created_by_db,
                    "otp_mobile_no": otp_mobile_number_db,
                    "otp_expiry": datetime.strptime(str(otp_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "otp": otp_db,
                    "otp_resend_count_left": otp_resend_count_left_db,
                    "otp_attempts_left": otp_attempts_left_db,
                    "otp_status": otp_status_db,
                    "app_key": application_key_db,
                    "app_key_name": application_name_db,
                    "app_key_status": application_key_status_db,
                    "jwt_key_expiry": datetime.strptime(str(jwt_key_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_renew_interval": datetime.strptime(str(jwt_key_renew_interval_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_user": jwt_key_user_db,
                    "jwt_key_status": jwt_key_status_db,
                    "push_mobile_no": push_mobile_number_db,
                    "push_status": push_status_db,
                    "push_token": push_token_db,
                    "user_device_identifier": user_device_identifier_db,
                    "user_device_identifier_type": user_device_identifier_type_db,
                    "user_mobile_no": user_mobile_number_db,
                    "user": user_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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
def test_common_600_601_003():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Generate_Resend_and_Validate_OTP_For_ExistingUser
    Sub Feature Description: API: Validate for existing user by hitting generate_otp,resend_otp and validate_otp api
    TC naming code description: 600: EzeGro functions, 601: Sale, 003: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        mobile_number = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["MobileNumber"]
        logger.info(f"Fetching the mobile_number from EzeGro sheet : {mobile_number}")
        application_Key = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["ApplicationKey"]
        logger.info(f"Fetching the application_Key from EzeGro sheet : {application_Key}")
        device_identifier = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifier"]
        logger.info(f"Fetching the device_identifier from EzeGro sheet : {device_identifier}")
        device_identifier_type = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifierType"]
        logger.debug(f"Fetching the device_identifier_type from EzeGro sheet : {device_identifier_type}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                    "mobileNumber": mobile_number,
                    "applicationKey": application_Key,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")

            api_details = DBProcessor.get_api_details('resend_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for resend otp is: {response}")
            resend_otp_application_key = response['applicationKey']
            logger.info(f"Value of applicationKey obtained from resend otp : {resend_otp_application_key}")
            resend_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from resend otp : {resend_otp_device_identifier}")
            resend_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from resend otp : {resend_otp_device_identifier_type}")
            resend_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from resend otp : {resend_otp_mobile_number}")
            resend_otp_new_merchant = response['newMerchant']
            logger.info(f"Value of newMerchant obtained from resend otp : {resend_otp_new_merchant}")
            resend_otp_resend_count_left = response['resendCountLeft']
            logger.info(f"Value of resendCountLeft obtained from resend otp : { resend_otp_resend_count_left}")
            resend_otp = response['otp']
            logger.info(f"Value of otp obtained from resend otp : {resend_otp}")
            resend_otp_success = response['success']
            logger.info(f"Value of success obtained from resend otp : {resend_otp_success}")

            query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from otp table for actual values : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result for actual values from otp table : {result}")
            # actual_otp_db = result['otp'].values[0]
            # logger.info(f"Value of actual otp obtained from otp table : {actual_otp_db}")
            otp_created_time = result['created_time'].values[0]
            logger.info(f"Value of otp_created_time obtained from otp table : {otp_created_time}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token is : {push_token}")

            api_details = DBProcessor.get_api_details('validate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "otp": resend_otp,
                "pushToken": push_token,
                "customerVersion": "0",
                "orderVersion": "0",
                "reviewVersion": "0",
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for validate otp is: {response}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_otp_customer_version = response['customerVersion']
            logger.info(f"Value of customerVersion obtained from validate otp : {validate_otp_customer_version}")
            validate_otp_order_version = response['orderVersion']
            logger.info(f"Value of orderVersion obtained from validate otp : {validate_otp_order_version}")
            validate_otp_review_version = response['reviewVersion']
            logger.info(f"Value of reviewVersion obtained from validate otp : {validate_otp_review_version}")
            validate_otp_check_status_after = response['settings']['checkStatusAfter']
            logger.info(f"Value of checkStatusAfter obtained from validate otp : {validate_otp_check_status_after}")
            validate_otp_check_status_interval = response['settings']['checkStatusInterval']
            logger.info(f"Value of checkStatusInterval obtained from validate otp : {validate_otp_check_status_interval}")
            validate_otp_check_status_count = response['settings']['checkStatusCount']
            logger.info(f"Value of checkStatusCount obtained from validate otp : {validate_otp_check_status_count}")
            validate_otp_min_agent_balance = response['settings']['minAgentBalance']
            logger.info(f"Value of minAgentBalance obtained from validate otp : {validate_otp_min_agent_balance}")
            validate_otp_min_amount = response['settings']['minAmount']
            logger.info(f"Value of minAmount obtained from validate otp : {validate_otp_min_amount}")
            validate_otp_max_amount = response['settings']['maxAmount']
            logger.info(f"Value of maxAmount obtained from validate otp : {validate_otp_max_amount}")
            validate_otp_max_agent_balance = response['settings']['maxAgentBalance']
            logger.info(f"Value of maxAgentBalance obtained from validate otp : {validate_otp_max_agent_balance}")
            validate_status = response['merchant']['status']
            logger.info(f"Value of status obtained from validate otp : {validate_status}")

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

            query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from user table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of user table : {result}")
            expected_user_db = result['user'].values[0]
            logger.info(f"Value of user obtained from user table : {expected_user_db}")

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

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "app_key": application_Key,
                    "new_merchant": False,
                    "resend_count_left": 2,
                    "success": True,
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "mobile_no": mobile_number,
                    "user": validate_otp_user,
                    "customer_version": 0,
                    "review_version": 0,
                    "order_version": 0,
                    "check_status_after": 30,
                    "check_status_interval": 15,
                    "check_status_count": 8,
                    "min_agent_bal": 100,
                    "min_amt": 100,
                    "max_amt": 49000,
                    "max_agent_bal": 100000
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "app_key": resend_otp_application_key,
                    "new_merchant": resend_otp_new_merchant,
                    "resend_count_left": resend_otp_resend_count_left,
                    "success": resend_otp_success,
                    "device_identifier": resend_otp_device_identifier,
                    "device_identifier_type": resend_otp_device_identifier_type,
                    "mobile_no": resend_otp_mobile_number,
                    "user": expected_user_db,
                    "customer_version": int(validate_otp_customer_version),
                    "review_version": int(validate_otp_review_version),
                    "order_version": int(validate_otp_order_version),
                    "check_status_after": validate_otp_check_status_after,
                    "check_status_interval": validate_otp_check_status_interval,
                    "check_status_count": validate_otp_check_status_count,
                    "min_agent_bal": validate_otp_min_agent_balance,
                    "min_amt": validate_otp_min_amount,
                    "max_amt": validate_otp_max_amount,
                    "max_agent_bal": validate_otp_max_agent_balance
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                created_time = datetime.strptime(str(otp_created_time),'%Y-%m-%dT%H:%M:%S.%f000')
                jwt_created_time = datetime.strptime(str(jwt_created_time_db),'%Y-%m-%dT%H:%M:%S.%f000')

                expected_db_values = {
                    "otp_created_by": "ezetap",
                    "otp_mobile_no": mobile_number,
                    "otp_expiry": created_time + timedelta(minutes=5),
                    "otp": resend_otp,
                    "otp_resend_count_left": 2,
                    "otp_attempts_left": 3,
                    "otp_status": "EXPIRED",
                    "app_key": application_Key,
                    "app_key_name": "ezegro",
                    "app_key_status": "ACTIVE",
                    "jwt_key_expiry": jwt_created_time + timedelta(days=45),
                    "jwt_key_renew_interval": jwt_created_time + timedelta(days=30),
                    "jwt_key_user": validate_otp_user,
                    "jwt_key_status": "ACTIVE",
                    "push_mobile_no": mobile_number,
                    "push_status": "ACTIVE",
                    "push_token": push_token,
                    "user_device_identifier": device_identifier,
                    "user_device_identifier_type": device_identifier_type,
                    "user_mobile_no": mobile_number,
                    "user": expected_user_db
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
                logger.debug(f"Query to fetch data for actual db values from otp table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from otp table : {result}")
                otp_created_by_db = result['created_by'].values[0]
                logger.info(f"Fetching actual db created_by value from the otp table : {otp_created_by_db}")
                otp_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the otp table : {otp_mobile_number_db}")
                otp_expiry_db = result['otp_expiry'].values[0]
                logger.info(f"Fetching actual db otp_expiry value from the otp table : {otp_expiry_db}")
                otp_db = result['otp'].values[0]
                logger.info(f"Fetching actual db otp value from the otp table : {otp_db}")
                otp_resend_count_left_db = result['resend_count_left'].values[0]
                logger.info(f"Fetching actual db resend_count_left value from the otp table : {otp_resend_count_left_db}")
                otp_attempts_left_db = result['otp_attempts_left'].values[0]
                logger.info(f"Fetching actual db otp_attempts_left value from the otp table : {otp_attempts_left_db}")
                otp_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the otp table : {otp_status_db}")

                query = "select * from application_key where application_name = 'ezegro';"
                logger.debug(f"Query to fetch data for actual db values from application_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from application_key table : {result}")
                application_key_db = result['application_key'].values[0]
                logger.info(f"Fetching actual db application_key value from the application_key table : {application_key_db}")
                application_name_db = result['application_name'].values[0]
                logger.info(f"Fetching actual db application_name value from the application_key table : {application_name_db}")
                application_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {application_key_status_db}")

                query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from jwt_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from jwt_key table : {result}")
                jwt_key_expiry_db = result['expiry'].values[0]
                logger.info(f"Fetching actual db expiry value from the application_key table : {jwt_key_expiry_db}")
                jwt_key_renew_interval_db = result['renew_interval'].values[0]
                logger.info(f"Fetching actual db renew_interval value from the application_key table : {jwt_key_renew_interval_db}")
                jwt_key_user_db = result['user'].values[0]
                logger.info(f"Fetching actual db user value from the application_key table : {jwt_key_user_db}")
                jwt_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {jwt_key_status_db}")

                query = "select * from push where mobile_number ='" + str(mobile_number) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data for actual db values from push table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from push table : {result}")
                push_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the push table : {push_mobile_number_db}")
                push_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the push table : {push_status_db}")
                push_token_db = result['token'].values[0]
                logger.info(f"Fetching actual db token value from the push table : {push_token_db}")

                query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from user table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from user table : {result}")
                user_db = result['user'].values[0]
                logger.info(f"Value of user obtained from user table : {user_db}")
                user_device_identifier_db = result['device_identifier'].values[0]
                logger.info(f"Fetching actual db device_identifier value from the user table : {user_device_identifier_db}")
                user_device_identifier_type_db = result['device_identifier_type'].values[0]
                logger.info(f"Fetching actual db device_identifier_type value from the user table : {user_device_identifier_type_db}")
                user_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the user table : {user_mobile_number_db}")

                actual_db_values = {
                    "otp_created_by": otp_created_by_db,
                    "otp_mobile_no": otp_mobile_number_db,
                    "otp_expiry": datetime.strptime(str(otp_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "otp": otp_db,
                    "otp_resend_count_left": otp_resend_count_left_db,
                    "otp_attempts_left": otp_attempts_left_db,
                    "otp_status": otp_status_db,
                    "app_key": application_key_db,
                    "app_key_name": application_name_db,
                    "app_key_status": application_key_status_db,
                    "jwt_key_expiry": datetime.strptime(str(jwt_key_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_renew_interval": datetime.strptime(str(jwt_key_renew_interval_db),'%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_user": jwt_key_user_db,
                    "jwt_key_status": jwt_key_status_db,
                    "push_mobile_no": push_mobile_number_db,
                    "push_status": push_status_db,
                    "push_token": push_token_db,
                    "user_device_identifier": user_device_identifier_db,
                    "user_device_identifier_type": user_device_identifier_type_db,
                    "user_mobile_no": user_mobile_number_db,
                    "user": user_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_004():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Autologin_API_For_ExistingUser
    Sub Feature Description: API: LValidate for existing user by hitting generate_otp, validate_otp and autologin api
    TC naming code description: 600: EzeGro functions, 601: Sale, 004: TC004
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        mobile_number = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["MobileNumber"]
        logger.info(f"Fetching the mobile_number from EzeGro sheet : {mobile_number}")
        application_Key = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["ApplicationKey"]
        logger.info(f"Fetching the application_Key from EzeGro sheet : {application_Key}")
        device_identifier = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifier"]
        logger.info(f"Fetching the device_identifier from EzeGro sheet : {device_identifier}")
        device_identifier_type = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifierType"]
        logger.debug(f"Fetching the device_identifier_type from EzeGro sheet : {device_identifier_type}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            #generate the otp
            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                    "mobileNumber": mobile_number,
                    "applicationKey": application_Key,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")

            # validate the otp
            api_details = DBProcessor.get_api_details('validate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "otp": generate_otp_response,
                "customerVersion": "0",
                "orderVersion": "0",
                "reviewVersion": "0",
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for validate otp is: {response}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_otp_status = response['merchant']['status']
            logger.info(f"Value of status obtained from validate otp : {validate_otp_status}")
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")
            validate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from validate otp : {validate_otp_mobile_number}")

            #autologin
            api_details = DBProcessor.get_api_details('ezegro_autologin', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customerVersion": "0",
                "orderVersion": "0",
                "pushToken": "0",
                "reviewVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for autologin {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Autologin is: {response}")
            autologin_check_status_after = response['settings']['checkStatusAfter']
            logger.info(f"Value of checkStatusAfter obtained from Autologin : {autologin_check_status_after}")
            autologin_check_status_interval = response['settings']['checkStatusInterval']
            logger.info(f"Value of checkStatusInterval obtained from Autologin : { autologin_check_status_interval}")
            autologin_check_status_count = response['settings']['checkStatusCount']
            logger.info(f"Value of checkStatusCount obtained from Autologin : {autologin_check_status_count}")
            autologin_min_agent_balance = response['settings']['minAgentBalance']
            logger.info(f"Value of minAgentBalance obtained from Autologin : {autologin_min_agent_balance}")
            autologin_min_amount = response['settings']['minAmount']
            logger.info(f"Value of minAmount obtained from Autologin : {autologin_min_amount}")
            autologin_max_amount = response['settings']['maxAmount']
            logger.info(f"Value of maxAmount obtained from Autologin : {autologin_max_amount}")
            autologin_max_agent_balance = response['settings']['maxAgentBalance']
            logger.info(f"Value of maxAgentBalance obtained from Autologin : {autologin_max_agent_balance}")
            autologin_merchant_mobile_no = response['merchant']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from Autologin : {autologin_merchant_mobile_no}")
            autologin_merchant_store_name = response['merchant']['storeName']
            logger.info(f"Value of storeName obtained from Autologin : {autologin_merchant_store_name}")
            autologin_merchant_status = response['merchant']['status']
            logger.info(f"Value of status obtained from Autologin : {autologin_merchant_status}")
            autologin_pdt_category = response['merchant']['productCategory']
            logger.info(f"Value of productCategory obtained from Autologin : {autologin_pdt_category}")

            query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from otp table for actual values : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result for actual values from otp table : {result}")
            actual_otp_db = result['otp'].values[0]
            logger.info(f"Value of actual otp obtained from otp table : {actual_otp_db}")
            otp_created_time = result['created_time'].values[0]
            logger.info(f"Value of otp_created_time obtained from otp table : {otp_created_time}")

            query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from user table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of user table : {result}")
            expected_user_db = result['user'].values[0]
            logger.info(f"Value of user obtained from user table : {expected_user_db}")

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of merchant table : {result}")
            merchant_customer_version_db = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version_db}")
            merchant_order_version_db = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table : {merchant_order_version_db}")
            merchant_review_version_db = result['review_version'].values[0]
            logger.info(f"Value of review_version obtained from merchant table : {merchant_review_version_db}")
            merchant_store_name = result['store_name'].values[0]
            logger.info(f"Value of store_name obtained from merchant table : {merchant_store_name}")
            merchant_category_id = result['category_id'].values[0]
            logger.info(f"Value of store_name obtained from merchant table : {merchant_store_name}")

            query = "select * from product_category where id ='" + str(merchant_category_id) + "';"
            logger.debug(f"Query to fetch data from product_category table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of product_category table : {result}")
            category_name = result['name'].values[0]
            logger.info(f"Value of category_name obtained from product_category table : {category_name}")

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

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "mobile_no": mobile_number,
                    "status": 'ACTIVE',
                    "check_status_after": 30,
                    "check_status_interval": 15,
                    "check_status_count": 8,
                    "min_agent_bal": 100,
                    "min_amt": 100,
                    "max_amt": 49000,
                    "max_agent_bal": 100000,
                    "autologin_mobile_no": mobile_number,
                    "store_name": autologin_merchant_store_name,
                    "product_category": autologin_pdt_category,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "mobile_no": validate_otp_mobile_number,
                    "status": validate_otp_status,
                    "check_status_after": autologin_check_status_after,
                    "check_status_interval": autologin_check_status_interval,
                    "check_status_count": autologin_check_status_count,
                    "min_agent_bal": autologin_min_agent_balance,
                    "min_amt": autologin_min_amount,
                    "max_amt": autologin_max_amount,
                    "max_agent_bal": autologin_max_agent_balance,
                    "autologin_mobile_no": autologin_merchant_mobile_no,
                    "store_name":merchant_store_name ,
                    "product_category": category_name,
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "merchant_customer_version": None,
                    "merchant_order_version": None,
                    "merchant_review_version": None
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "merchant_customer_version": merchant_customer_version_db,
                    "merchant_order_version": merchant_order_version_db,
                    "merchant_review_version": merchant_review_version_db
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_005():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Logout_for_ExistingUser
    Sub Feature Description: API: Validate for existing user by hitting generate_otp,validate_otp and logout api
    TC naming code description: 600: EzeGro, 601: Sale, 005: TC005
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        mobile_number = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["MobileNumber"]
        logger.info(f"mobile_number is {mobile_number}")
        application_Key = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["ApplicationKey"]
        logger.info(f"application_Key is {application_Key}")
        device_identifier = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifier"]
        logger.info(f"device_identifier is {device_identifier}")
        device_identifier_type = EzeGro_processor.get_ezegro_details_from_excel("Ezegrow_user")["DeviceIdentifierType"]
        logger.info(f"device_identifier_type is {device_identifier_type}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            # generate the otp
            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                    "mobileNumber": mobile_number,
                    "applicationKey": application_Key,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")
            generate_otp_application_key = response['applicationKey']
            logger.info(f"Value of applicationKey obtained from generate otp : {generate_otp_application_key}")
            generate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from generate otp : {generate_otp_device_identifier}")
            generate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from generate otp : {generate_otp_device_identifier_type}")
            generate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from generate otp : {generate_otp_mobile_number}")
            generate_otp_new_merchant = response['newMerchant']
            logger.info(f"Value of newMerchant obtained from generate otp : {generate_otp_new_merchant}")
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")
            generate_otp_resend_count_left = response['resendCountLeft']
            logger.info(f"Value of resendCountLeft obtained from generate otp : {generate_otp_resend_count_left}")
            generate_otp_success = response['success']
            logger.info(f"Value of success obtained from generate otp : {generate_otp_success}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated Random push token is : {push_token}")

            # validate the otp
            api_details = DBProcessor.get_api_details('validate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "otp": generate_otp_response,
                "languagePreference": "english",
                "pushToken": push_token,
                "customerVersion": "0",
                "orderVersion": "0",
                "addressVersion": "0",
                "reviewVersion": "0"
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for validate otp is: {response}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_otp_success = response['success']
            logger.info(f"Value of success obtained from validate otp : {validate_otp_success}")
            validate_otp_status = response['merchant']['status']
            logger.info(f"Value of status obtained from generate otp : {validate_otp_status}")
            validate_otp_opted_for_communication = response['merchant']['optedForCommunication']
            logger.info(f"Value of status obtained from generate otp : {validate_otp_opted_for_communication}")
            validate_otp_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from validate otp : {validate_otp_device_identifier}")
            validate_otp_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from validate otp : {validate_otp_device_identifier_type}")
            validate_otp_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from validate otp : {validate_otp_mobile_number}")
            validate_otp_customer_version = response['customerVersion']
            logger.info(f"Value of customerVersion obtained from validate otp : {validate_otp_customer_version}")
            validate_otp_order_version = response['orderVersion']
            logger.info(f"Value of orderVersion obtained from validate otp : {validate_otp_order_version}")
            validate_otp_review_version = response['reviewVersion']
            logger.info(f"Value of reviewVersion obtained from validate otp : {validate_otp_review_version}")
            validate_otp_check_status_after = response['settings']['checkStatusAfter']
            logger.info(f"Value of checkStatusAfter obtained from validate otp : {validate_otp_check_status_after}")
            validate_otp_check_status_interval = response['settings']['checkStatusInterval']
            logger.info(f"Value of checkStatusInterval obtained from validate otp : {validate_otp_check_status_interval}")
            validate_otp_check_status_count = response['settings']['checkStatusCount']
            logger.info(f"Value of checkStatusCount obtained from validate otp : {validate_otp_check_status_count}")
            validate_otp_min_agent_balance = response['settings']['minAgentBalance']
            logger.info(f"Value of minAgentBalance obtained from validate otp : {validate_otp_min_agent_balance}")
            validate_otp_min_amount = response['settings']['minAmount']
            logger.info(f"Value of minAmount obtained from validate otp : {validate_otp_min_amount}")
            validate_otp_max_amount = response['settings']['maxAmount']
            logger.info(f"Value of maxAmount obtained from validate otp : {validate_otp_max_amount}")
            validate_otp_max_agent_balance = response['settings']['maxAgentBalance']
            logger.info(f"Value of maxAgentBalance obtained from validate otp : {validate_otp_max_agent_balance}")
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of validate_auth_token obtained from validate otp : {validate_auth_token}")

            #logout
            api_details = DBProcessor.get_api_details('ezegro_logout', request_body={
                "user": validate_otp_user,
                "mobileNumber" : mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for logout {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Logout is: {response}")
            logout_success = response['success']
            logger.info(f"Value of success obtained from logout : {logout_success}")

            query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from user table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of user table : {result}")
            expected_user_db = result['user'].values[0]
            logger.info(f"Value of user obtained from user table : {expected_user_db}")

            query = "select * from otp where mobile_number ='" + str(mobile_number) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from otp table for actual values : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result for actual values from otp table : {result}")
            actual_otp_db = result['otp'].values[0]
            logger.info(f"Value of actual otp obtained from otp table : {actual_otp_db}")
            otp_created_time = result['created_time'].values[0]
            logger.info(f"Value of otp_created_time obtained from otp table : {otp_created_time}")

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

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

        # -----------------------------------------Start of API Validation----------------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": True,
                    "user": validate_otp_user,
                    "mobile_no": mobile_number,
                    "check_status_after": 30,
                    "check_status_interval": 15,
                    "check_status_count": 8,
                    "min_agent_bal": 100,
                    "min_amt": 100,
                    "max_amt": 49000,
                    "max_agent_bal": 100000,
                    "new_merchant": False,
                    "status": 'ACTIVE',
                    "opted_for_communication": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": logout_success,
                    "user": expected_user_db,
                    "mobile_no": validate_otp_mobile_number,
                    "check_status_after": validate_otp_check_status_after,
                    "check_status_interval": validate_otp_check_status_interval,
                    "check_status_count": validate_otp_check_status_count,
                    "min_agent_bal": validate_otp_min_agent_balance,
                    "min_amt": validate_otp_min_amount,
                    "max_amt": validate_otp_max_amount,
                    "max_agent_bal": validate_otp_max_agent_balance,
                    "new_merchant": generate_otp_new_merchant,
                    "status": validate_otp_status,
                    "opted_for_communication": validate_otp_opted_for_communication
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                jwt_created_time = datetime.strptime(str(jwt_created_time_db),'%Y-%m-%dT%H:%M:%S.%f000')
                expected_db_values = {
                    "jwt_key_expiry": jwt_created_time + timedelta(days=45),
                    "jwt_key_renew_interval": jwt_created_time + timedelta(days=30),
                    "jwt_key_user": validate_otp_user,
                    "jwt_key_status": "EXPIRED",
                    "push_mobile_number": mobile_number,
                    "push_status": "EXPIRED",
                    "push_token": push_token,
                    "user_device_identifier": device_identifier,
                    "user_device_identifier_type": device_identifier_type,
                    "user_mobile_number": mobile_number,
                    "user": validate_otp_user,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' order by created_time desc limit 1;"
                logger.debug(f"Query to fetch data for actual db values from jwt_key table : {query}")
                result = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from jwt_key table : {result}")
                jwt_key_expiry_db = result['expiry'].values[0]
                logger.info(f"Fetching actual db expiry value from the application_key table : {jwt_key_expiry_db}")
                jwt_key_renew_interval_db = result['renew_interval'].values[0]
                logger.info(f"Fetching actual db renew_interval value from the application_key table : {jwt_key_renew_interval_db}")
                jwt_key_user_db = result['user'].values[0]
                logger.info(f"Fetching actual db user value from the application_key table : {jwt_key_user_db}")
                jwt_key_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the application_key table : {jwt_key_status_db}")

                query = "select * from push where mobile_number ='"+str(mobile_number)+ "' order by created_time desc limit 1;"
                logger.debug(f"Query to fetch data for actual db values from push table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from push table : {result}")
                push_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the push table : {push_mobile_number_db}")
                push_status_db = result['status'].values[0]
                logger.info(f"Fetching actual db status value from the push table : {push_status_db}")
                push_token_db = result['token'].values[0]
                logger.info(f"Fetching actual db token value from the push table : {push_token_db}")

                query = "select * from user where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from user table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result for actual db values from user table : {result}")
                user_db = result['user'].values[0]
                logger.info(f"Value of user obtained from user table : {user_db}")
                user_device_identifier_db = result['device_identifier'].values[0]
                logger.info(f"Fetching actual db device_identifier value from the user table : {user_device_identifier_db}")
                user_device_identifier_type_db = result['device_identifier_type'].values[0]
                logger.info(f"Fetching actual db device_identifier_type value from the user table : {user_device_identifier_type_db}")
                user_mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Fetching actual db mobile_number value from the user table : {user_mobile_number_db}")

                actual_db_values = {
                    "jwt_key_expiry": datetime.strptime(str(jwt_key_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_renew_interval": datetime.strptime(str(jwt_key_renew_interval_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "jwt_key_user": jwt_key_user_db,
                    "jwt_key_status": jwt_key_status_db,
                    "push_mobile_number": push_mobile_number_db,
                    "push_status": push_status_db,
                    "push_token": push_token_db,
                    "user_device_identifier": user_device_identifier_db,
                    "user_device_identifier_type": user_device_identifier_type_db,
                    "user_mobile_number": user_mobile_number_db,
                    "user": user_db,
                }

                logger.debug(f"actual_db_values: {actual_db_values}")

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