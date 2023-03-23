import sys
import pytest
import string
import random
import json
from datetime import datetime
from datetime import timedelta
import requests
from bson import ObjectId
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, EzeGro_processor

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_603_001():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Generate_Review_to_User
    Sub Feature Description: Validate generate review functionality of Ezegrow Product
    TC naming code description: 600: EzeGro functions, 603: Feedback, 001: TC001
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

        delete_customer_mobile_no = '666666666%'
        customer_mobile_no = "666666666" + str(random.randint(0, 9))
        logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # deleting the customer
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

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
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token value is : {push_token}")

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")
            merchant_id = result['id'].values[0]
            logger.info(f"Value of merchant_id obtained from merchant table : {merchant_id}")
            merchant_store_name = result['store_name'].values[0]
            logger.info(f"Value of store name obtained from merchant table : {merchant_store_name}")

            customer_name = "John "+''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")

            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                },
                "customerVersion": merchant_customer_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create_customer is: {response}")

            query = "select * from customer where mobile_number ='" + str(customer_mobile_no) + "';"
            logger.debug(f"Query to fetch data from customer table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for customer table : {result}")
            customer_id = result['id'].values[0]
            logger.info(f"Value of customer id obtained from merchant table : {customer_id}")

            api_details = DBProcessor.get_api_details('Generate_Review', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for Generate Review {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Generate Review is: {response}")
            review_success = response['success']
            logger.info(f"Value of success obtained: {review_success}")
            review_link = str(response['reviewLink'])
            logger.info(f"Value of review link obtained : {review_link}")
            testimonial_temp = str(response['testimonialTemplate'])
            logger.info(f"Value of testimonial template obtained : {testimonial_temp}")
            review_id =  str(response['reviewId'])
            logger.info(f"Value of review id obtained: {review_id}")
            cust_name = response['customer']['name']
            logger.info(f"Value of customer name obtained: {cust_name}")
            cust_mobile_num = response['customer']['mobileNumber']
            logger.info(f"Value of customer name obtained: {cust_mobile_num}")

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
                    "review_link": review_link,
                    "review_id": review_id,
                    "cust_name": customer_name,
                    "cust_mobile": customer_mobile_no,
                    "testimonial_template" : f"Dear {customer_name}, We at {merchant_store_name} are happy to serve you & would love to get your review on your recent purchase from us. Share your Review by clicking on the link below: {review_link} - EzeGro"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                mongo_query = {"_id" : ObjectId(f"{review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore","review",mongo_query)

                review_url_db = str(result["reviewUrl"].iloc[0])
                logger.info(f"Value of review url obtained from mongodb : {review_url_db}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")
                created_time_db = str(result["createdTime"].iloc[0])
                logger.info(f"Value of createdTime obtained from mongodb : {created_time_db}")

                actual_api_values = {
                    "review_link": review_url_db,
                    "review_id": reviewid_db,
                    "cust_name": cust_name,
                    "cust_mobile": cust_mobile_num,
                    "testimonial_template" : testimonial_temp
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
                created_time = datetime.strptime(str(created_time_db),'%Y-%m-%d %H:%M:%S.%f')
                expiry_time = datetime.strptime(str(created_time + timedelta(days=90)),'%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
                expected_db_values = {
                    "review_id": review_id,
                    "review_url": review_link,
                    "merchant_id": merchant_id,
                    "customer_id": customer_id,
                    "customer_mobile_no": customer_mobile_no,
                    "status": 'ACTIVE',
                    "expiry_time": expiry_time

                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                mongo_query = {"_id": ObjectId(f"{review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore", "review", mongo_query)

                review_url_db = str(result["reviewUrl"].iloc[0])
                logger.info(f"Value of review url obtained from mongodb : {review_url_db}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")
                merchant_id_db = str(result["merchantId"].iloc[0])
                logger.info(f"Value of merchantId obtained from mongodb : {merchant_id_db}")
                cust_id_db = str(result["customerId"].iloc[0])
                logger.info(f"Value of customer id obtained from mongodb : {cust_id_db}")
                cust_mobile_no_db = str(result["customerMobileNumber"].iloc[0])
                logger.info(f"Value of customer mobile number obtained from mongodb : {cust_mobile_no_db}")
                review_status_db = str(result["status"].iloc[0])
                logger.info(f"Value of review status obtained from mongodb : {review_status_db}")
                expiry_db = str(result["expiry"].iloc[0])
                logger.info(f"Value of expiry time obtained from mongodb : {expiry_db}")

                actual_db_values = {
                    "review_id": reviewid_db,
                    "review_url": review_url_db,
                    "merchant_id": merchant_id_db,
                    "customer_id": cust_id_db,
                    "customer_mobile_no": cust_mobile_no_db,
                    "status": review_status_db,
                    "expiry_time": datetime.strptime(str(expiry_db), '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
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
def test_common_600_603_002():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Generate_Review_to_User
    Sub Feature Description: API: Validate the positive flow for generateReview endpoint and validate the auth table in mysql
    TC naming code description: 600: EzeGro functions, 603: Feedback, 002: TC002
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

        delete_customer_mobile_no = '666666666%'
        customer_mobile_no = "666666666" + str(random.randint(0, 9))
        logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # deleting the customer
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

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
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token value is : {push_token}")

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")

            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                },
                "customerVersion": merchant_customer_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create_customer is: {response}")

            api_details = DBProcessor.get_api_details('Generate_Review', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for generate review : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate review is: {response}")
            generate_review_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobile number obtained from generate review : {generate_review_mobile_no}")
            generate_review_link = response['reviewLink']
            logger.info(f"Value of reviewLink obtained from generate review : {generate_review_link}")
            generate_review_id = response['reviewId']
            logger.info(f"Value of reviewId obtained from generate review : {generate_review_id}")
            generate_review_name = response['customer']['name']
            logger.info(f"Value of customer name obtained from generate review : {generate_review_name}")
            generate_review_cust_mobile_no = response['customer']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from generate review : {generate_review_cust_mobile_no}")

            query = "select * from auth_token where entity_id ='" + str(generate_review_id) + "';"
            logger.debug(f"Query to fetch data from auth_token table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of auth_token table : {result}")
            auth_token_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from auth_token table : {auth_token_created_time_db}")

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
                    "review_link": generate_review_link,
                    "review_id": generate_review_id,
                    "cust_name": customer_name,
                    "cust_mobile_no": customer_mobile_no
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                mongo_query = {"_id" : ObjectId(f"{generate_review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore","review",mongo_query)

                review_url_db = str(result["reviewUrl"].iloc[0])
                logger.info(f"Value of review url obtained from mongodb : {review_url_db}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")
                created_time_db = str(result["createdTime"].iloc[0])
                logger.info(f"Value of createdTime obtained from mongodb : {created_time_db}")

                actual_api_values = {
                    "mobile_no": generate_review_mobile_no,
                    "review_link": review_url_db,
                    "review_id": reviewid_db,
                    "cust_name": generate_review_name,
                    "cust_mobile_no": generate_review_cust_mobile_no
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

            auth_token_created_time = datetime.strptime(str(auth_token_created_time_db), '%Y-%m-%dT%H:%M:%S.%f000')

            try:
                expected_db_values = {
                    "requester_username": validate_otp_user,
                    "status": 'ACTIVE',
                    "token_expiry": auth_token_created_time + timedelta(days=90),
                    "username": validate_otp_user,
                    "entity_type": "review",
                    "entity_id": generate_review_id
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from auth_token where entity_id ='"+str(generate_review_id)+"';"
                logger.debug(f"Query to fetch data for actual db values from auth_token table : {query}")
                response = DBProcessor.getValueFromDB(query, "auth")
                logger.info(f"Query result for actual db values from auth_token table : {result}")
                auth_token_requester_username_db = response['requester_username'].values[0]
                logger.info(f"Fetching actual db requester_username value from the auth_token table : {auth_token_requester_username_db}")
                auth_token_status_db = response['status'].values[0]
                logger.info(f"Fetching actual db status value from the auth_token table : {auth_token_status_db}")
                auth_token_token_expiry_db = response['token_expiry'].values[0]
                logger.info(f"Fetching actual db token_expiry value from the auth_token table : {auth_token_token_expiry_db}")
                auth_token_username_db = response['username'].values[0]
                logger.info(f"Fetching actual db username value from the auth_token table : {auth_token_username_db}")
                auth_token_entity_type_db = response['entity_type'].values[0]
                logger.info(f"Fetching actual db entity_type value from the auth_token table : {auth_token_entity_type_db}")
                auth_token_entity_id_db = response['entity_id'].values[0]
                logger.info(f"Fetching actual db entity_id value from the auth_token table : {auth_token_entity_id_db}")

                actual_db_values = {
                    "requester_username": auth_token_requester_username_db,
                    "status": auth_token_status_db,
                    "token_expiry": datetime.strptime(str(auth_token_token_expiry_db), '%Y-%m-%dT%H:%M:%S.%f000'),
                    "username": auth_token_username_db,
                    "entity_type": auth_token_entity_type_db,
                    "entity_id": auth_token_entity_id_db
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
def test_common_600_603_003():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Generate_Review_and_submit_feedback
    Sub Feature Description: Validate generate review functionality and submitting the review from the user
    TC naming code description: 600: EzeGro functions, 603: Feedback, 002: TC002
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

        delete_customer_mobile_no = '666666666%'
        customer_mobile_no = "666666666" + str(random.randint(0, 9))
        logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # deleting the customer
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

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
            generate_otp_response = response['otp']
            logger.info(f"Value of otp obtained from generate otp : {generate_otp_response}")

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token value is : {push_token}")

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")
            merchant_id = result['id'].values[0]
            logger.info(f"Value of merchant_id obtained from merchant table : {merchant_id}")
            merchant_store_name = result['store_name'].values[0]
            logger.info(f"Value of store name obtained from merchant table : {merchant_store_name}")
            category_id = str(result['category_id'].values[0])
            logger.info(f"Value of category_id obtained from merchant table : {category_id}")
            pdt_sub_category = result['product_sub_category'].values[0]
            logger.info(f"Value of pdt_sub_category obtained from merchant table : {pdt_sub_category}")

            query = "select * from product_category where id ='" + str(category_id) + "';"
            logger.debug(f"Query to fetch data from product_category table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for product_category table : {result}")
            category_name = result['name'].values[0]
            logger.info(f"Value of category_name obtained from product_category table : {category_name}")
            if category_id == '3':
                category_name = pdt_sub_category
            else:
                category_name = category_name

            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")

            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                },
                "customerVersion": merchant_customer_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create_customer is: {response}")

            query = "select * from customer where mobile_number ='" + str(customer_mobile_no) + "';"
            logger.debug(f"Query to fetch data from customer table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for customer table : {result}")
            customer_id = result['id'].values[0]
            logger.info(f"Value of customer id obtained from merchant table : {customer_id}")
            customer_name = result['name'].values[0]
            logger.info(f"Value of customer name obtained from merchant table : {customer_name}")

            api_details = DBProcessor.get_api_details('Generate_Review', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for Generate Review {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Generate Review is: {response}")
            review_success = response['success']
            logger.info(f"Value of success obtained: {review_success}")
            review_link = str(response['reviewLink'])
            logger.info(f"Value of review link obtained : {review_link}")
            testimonial_temp = str(response['testimonialTemplate'])
            logger.info(f"Value of testimonial template obtained : {testimonial_temp}")
            review_id =  str(response['reviewId'])
            logger.info(f"Value of review id obtained: {review_id}")
            cust_name = response['customer']['name']
            logger.info(f"Value of customer name obtained: {cust_name}")
            cust_mobile_num = response['customer']['mobileNumber']
            logger.info(f"Value of customer name obtained: {cust_mobile_num}")

            review_token = review_link.split('=')[1]
            rating_given = random.randint(0,5)
            suggestion_given = "Wohh!! Good Product, can improve on ==> " +''.join(random.choices(string.ascii_uppercase, k=4))
            feedback_given = "Comfortable Fabric, Value for Money, Quick Delivery, Good Quality"
            form_data = {'rating': rating_given, 'feedback':feedback_given,'suggestion':suggestion_given,'token':review_token}

            api_details = DBProcessor.get_api_details('Submit_review', request_body=form_data)
            logger.debug(f"api details for submit Review {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for submit Review is: {response}")
            submit_success = response['success']
            logger.info(f"Value of success obtained: {submit_success}")

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
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                mongo_query = {"_id" : ObjectId(f"{review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore","review",mongo_query)

                review_url_db = str(result["reviewUrl"].iloc[0])
                logger.info(f"Value of review url obtained from mongodb : {review_url_db}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")
                created_time_db = str(result["createdTime"].iloc[0])
                logger.info(f"Value of createdTime obtained from mongodb : {created_time_db}")

                actual_api_values = {
                    "success": submit_success
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # # -----------------------------------------End of API Validation------------------------------------------------
        # # -----------------------------------------Start of DB Validation-----------------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                created_time = datetime.strptime(str(created_time_db), '%Y-%m-%d %H:%M:%S.%f')
                expiry_time = datetime.strptime(str(created_time + timedelta(days=90)),'%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
                expected_db_values = {
                    "review_id": review_id,
                    "review_url": review_link,
                    "merchant_id": merchant_id,
                    "category_name" : category_name,
                    "customer_id": customer_id,
                    "customer_name" :customer_name,
                    "customer_mobile_no": customer_mobile_no,
                    "status": 'SUBMITTED',
                    "suggestion" : suggestion_given,
                    "feedback" : feedback_given,
                    "expiry_time": expiry_time,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                mongo_query = {"_id": ObjectId(f"{review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore", "review", mongo_query)

                review_url_db = str(result["reviewUrl"].iloc[0])
                logger.info(f"Value of review url obtained from mongodb : {review_url_db}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")
                merchant_id_db = str(result["merchantId"].iloc[0])
                logger.info(f"Value of merchantId obtained from mongodb : {merchant_id_db}")
                cust_id_db = str(result["customerId"].iloc[0])
                logger.info(f"Value of customer id obtained from mongodb : {cust_id_db}")
                cust_mobile_no_db = str(result["customerMobileNumber"].iloc[0])
                logger.info(f"Value of customer mobile number obtained from mongodb : {cust_mobile_no_db}")
                review_status_db = str(result["status"].iloc[0])
                logger.info(f"Value of review status obtained from mongodb : {review_status_db}")
                category_db = str(result["category"].iloc[0])
                logger.info(f"Value of category obtained from mongodb : {category_db}")
                cust_name_db = str(result["customerName"].iloc[0])
                logger.info(f"Value of customerName obtained from mongodb : {cust_name_db}")
                suggestion_db = str(result["suggestion"].iloc[0])
                logger.info(f"Value of suggestion obtained from mongodb : {suggestion_db}")
                feedback_db = str(result["feedback"].iloc[0])
                logger.info(f"Value of feedback obtained from mongodb : {feedback_db}")
                expiry_db = str(result["expiry"].iloc[0])
                logger.info(f"Value of expiry time obtained from mongodb : {expiry_db}")

                actual_db_values = {
                    "review_id": reviewid_db,
                    "review_url": review_url_db,
                    "merchant_id": merchant_id_db,
                    "category_name" : category_db,
                    "customer_id": cust_id_db,
                    "customer_name" :cust_name_db,
                    "customer_mobile_no": cust_mobile_no_db,
                    "status": review_status_db,
                    "suggestion" : suggestion_db,
                    "feedback" : feedback_db,
                    "expiry_time": datetime.strptime(str(expiry_db), '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
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
def test_common_600_603_004():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Add_Visuals
    Sub Feature Description: API: Validate the positive flow for the addVisual
    TC naming code description: 600: EzeGro functions, 603: Feedback, 004: TC004
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

        delete_customer_mobile_no = '666666666%'
        customer_mobile_no = "666666666" + str(random.randint(0, 9))
        logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # deleting the customer
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

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

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token value is : {push_token}")

            #validate the otp
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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")
            merchant_id = result['id'].values[0]
            logger.info(f"Value of merchant_id obtained from merchant table : {merchant_id}")

            customer_name = "John "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")

            #create customer
            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                },
                "customerVersion": merchant_customer_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create_customer is: {response}")

            #generate the review
            api_details = DBProcessor.get_api_details('Generate_Review', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for generate review : {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate review is: {response}")
            generate_review_id = str(response['reviewId'])
            logger.info(f"Value of reviewId obtained from generate review : {generate_review_id}")
            generate_review_link = str(response['reviewLink'])
            logger.info(f"Value of review link obtained from generate review : {generate_review_link}")

            review_token = generate_review_link.split('=')[1]
            rating_given = random.randint(0, 5)
            feedback_given = "Comfortable Fabric, Value for Money, Quick Delivery, Good Quality"

            form_data = {'rating': rating_given, 'feedback': feedback_given,'token': review_token}
            api_details = DBProcessor.get_api_details('Submit_review', request_body=form_data)
            logger.debug(f"api details for submit Review {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for submit Review is: {response}")
            submit_success = response['success']
            logger.info(f"Value of success obtained: {submit_success}")

            template_id = "VT03DNLD"
            logger.info(f"Value of template id is : {template_id}")

            api_details = DBProcessor.get_api_details('add_visual', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "visual": {
                    "reviewIds": [f"{generate_review_id}"],
                    "templateId": template_id,
                    "visualImage": [-1, -40, -1, -32, 0, 16, 74, 70, 73, 70, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, -1, -30, 2,
                                    40, 73, 67, 67, 95, 80, 82, 79, 70, 73, 76, 69,
                                    -64, -61, -1, -39]
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for Add Visual : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Add Visual is: {response}")
            add_visual_success = response['success']
            logger.info(f"Value of success obtained from Add Visual API: {add_visual_success}")

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
                    "review_id": generate_review_id,
                    "add_visual_success" : True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                mongo_query = {"_id": ObjectId(f"{generate_review_id}")}
                result = DBProcessor.getvaluefromMongo("ezestore", "review", mongo_query)
                logger.info(f"Result from mongodb : {result}")
                reviewid_db = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb : {reviewid_db}")

                actual_api_values = {
                    "review_id": reviewid_db,
                    "add_visual_success" : add_visual_success
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
                    "template_id": template_id,
                    "review_id": generate_review_id,
                    "merchant_id": merchant_id,
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                mongo_query = {"reviewIds": f"{generate_review_id}"}
                result = DBProcessor.getvaluefromMongo("ezestore","visual",mongo_query)
                logger.info(f"Result from mongodb : {result}")

                template_id_db = str(result["templateId"].iloc[0])
                logger.info(f"Value of templateId obtained from mongodb : {template_id_db}")
                review_ids_db = list(result["reviewIds"].iloc[0])[0]
                logger.info(f"Value of reviewIds obtained from mongodb : {review_ids_db}")
                merchant_id_db = str(result["merchantId"].iloc[0])
                logger.info(f"Value of merchantId obtained from mongodb : {merchant_id_db}")

                actual_db_values = {
                    "template_id": template_id_db,
                    "review_id": review_ids_db,
                    "merchant_id": merchant_id_db,
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
def test_common_600_603_005():
    """
    Sub Feature Code: NonUI_Common_EzeGro_getAll_Reviews
    Sub Feature Description: API: Validate the positive flow for the getAll Reviews
    TC naming code description: 600: EzeGro functions, 603: Feedback, 005: TC005
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

        delete_customer_mobile_no = '666666666%'
        customer_mobile_no = "666666666" + str(random.randint(0, 9))
        logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        # deleting the customer
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

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

            push_token = str(random.randint(0, 5))
            logger.info(f"Generated random push token value is : {push_token}")

            #validate the otp
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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_id = result['id'].values[0]
            logger.info(f"Value of merchant_id obtained from merchant table : {merchant_id}")
            merchant_review_version = result['review_version'].values[0]
            logger.info(f"Value of review_version obtained from merchant table : {merchant_review_version}")

            api_details = DBProcessor.get_api_details('get_all_reviews', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "reviewVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get all reviews : {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get all reviews is : {response}")
            get_all_avg_reviews = response['avgRating']
            logger.info(f"Value of avgRating obtained from get all reviews is : {get_all_avg_reviews}")
            get_all_total_reviews = response['totalReviews']
            logger.info(f"Value of totalReviews obtained from get all reviews is : {get_all_total_reviews}")
            get_all_reviews_reaction = response['reaction']
            logger.info(f"Value of reaction obtained from get all reviews is : {get_all_reviews_reaction}")

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
                    "avg_rating": str(f'{get_all_avg_reviews:.2f}'),
                    "total_reviews": get_all_total_reviews,
                    "reaction": str(get_all_reviews_reaction)
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                mongo_query = [{"$match": {"$and": [{"merchantId": f"{merchant_id}"},{"status": "SUBMITTED"}]}},{"$count":'totals'}]
                result = DBProcessor.getAggregateValueFromMongo("ezestore", "review", mongo_query)
                logger.info(f"Result from mongodb for total feedback received: {result}")
                feedback_total = result['totals'].iloc[0]
                logger.info(f"Value of total feedback received from mongodb : {feedback_total}")

                mongo_query = [{"$match": {"$and": [{"merchantId" : f"{merchant_id}"},{"status" : "SUBMITTED"}]}},{"$group":{"_id" : "_id",
                "AverageValue": { "$avg": "$rating" }}}]
                result = DBProcessor.getAggregateValueFromMongo("ezestore", "review", mongo_query)
                logger.info(f"Result from mongodb for average feedback received: {result}")
                average_id = str(result["_id"].iloc[0])
                logger.info(f"Value of reviewid_db obtained from mongodb for average feedback received : {average_id}")
                average_value = result["AverageValue"].iloc[0]
                logger.info(f"Value of AverageValue obtained from mongodb for average feedback received : {average_value}")

                if (average_value>=0 and average_value<3):
                    reaction = "Needs Improvement"
                elif (average_value>=3 and average_value<4):
                    reaction = "Good going "
                elif (average_value>=4 and average_value<=5):
                    reaction = "Awesome"

                actual_api_values = {
                    "avg_rating": str(f'{average_value:.2f}'),
                    "total_reviews": feedback_total,
                    "reaction": str(reaction)
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
                    "total_feedback": get_all_total_reviews,
                    "avg_value": str(f'{get_all_avg_reviews:.2f}')
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "total_feedback": feedback_total,
                    "avg_value": str(f'{average_value:.2f}')
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