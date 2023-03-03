import sys
import string
import pytest
import random
import numpy as np
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, EzeGro_processor

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_006():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Update_Merchant_API_For_ExistingUser
    Sub Feature Description: API: Validate for existing user by hitting update_merchant api
    TC naming code description: 600: EzeGro functions, 601: Sale, 006: TC006
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
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            #validate the otp
            push_token = str(random.randint(0, 5))
            logger.info(f"Value of push_token is : {push_token}")

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
            logger.info(f"Value of validate_auth_token obtained from validate otp : {validate_auth_token}")

            email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated email is :{email}")
            gstin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
            logger.debug(f"Randomly generated gstin is : {gstin}")
            pan_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            logger.debug(f"Randomly generated pan_number is : {pan_number}")
            language_preference = "english"
            logger.debug(f"language_preference is : {language_preference}")
            gender = "male"
            logger.debug(f"gender is : {gender}")
            generate_random_merchant_name = "Shubhash " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated merchant_name is : {generate_random_merchant_name}")
            product_category = "OTHERS"
            logger.debug(f"product_category is : {product_category}")
            product_sub_category = "Miscellaneous"
            logger.debug(f"product_sub_category is : {product_sub_category}")
            store_name = "Amith " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated store_name is : {store_name}")
            social_connect_instagram = "www.instagram.com" + "/" + ''.join(random.choices(string.ascii_lowercase, k=5))
            logger.debug(f"Randomly generated social_connect_instagram is : {social_connect_instagram}")
            social_connect_facebook = "www.facebook.com" + "/" + ''.join(random.choices(string.ascii_lowercase, k=5))
            logger.debug(f"Randomly generated social_connect_facebook is : {social_connect_facebook}")
            name = store_name.replace(" ", "")
            logger.debug(f"Removing the whitespaces from store_name to pass to digit store: {name}")
            social_connect_digital_store = "www." + format(name.lower()) + ".com" + "/" + ''.join(random.choices(string.ascii_lowercase, k=5))
            logger.debug(f"Randomly generated social_connect_digital_store is : {social_connect_digital_store}")
            date_of_birth = "1947-01-22"

            #update merchant details
            api_details = DBProcessor.get_api_details('updateMerchant', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "merchant": {
                    "name": generate_random_merchant_name,
                    "mobileNumber": mobile_number,
                    "storeName": store_name,
                    "email": email,
                    "gstin": gstin,
                    "panNumber": pan_number,
                    "productCategory": product_category,
                    "productSubCategory": product_sub_category,
                    "languagePreference": language_preference,
                    "gender": gender,
                    "socialConnect": {
                        "instagram": social_connect_instagram,
                        "facebook": social_connect_facebook,
                        "digitalStore": social_connect_digital_store
                    },
                    "dateOfBirth": date_of_birth,
                    "optedForCommunication": True
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for update merchant {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for update merchant is: {response}")
            update_merchant_success = response['success']
            logger.info(f"Value of success obtained from update merchant : {update_merchant_success}")
            update_merchant_user = response['user']
            logger.info(f"Value of user obtained from update merchant : {update_merchant_user}")
            update_merchant_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from update merchant : {update_merchant_device_identifier}")
            update_merchant_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType type obtained from update merchant : {update_merchant_device_identifier_type}")
            update_merchant_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from update merchant : {update_merchant_mobile_no}")
            update_merchant_name = response['merchant']['name']
            logger.info(f"Value of merchant name obtained from update merchant : {update_merchant_name}")
            update_merchant_email = response['merchant']['email']
            logger.info(f"Value of merchant email obtained from update merchant : {update_merchant_email}")
            update_merchant_store_name = response['merchant']['storeName']
            logger.info(f"Value of merchant storename obtained from update merchant : {update_merchant_store_name}")
            update_merchant_gstin = response['merchant']['gstin']
            logger.info(f"Value of merchant gstin obtained from update merchant : {update_merchant_gstin}")
            update_merchant_pan = response['merchant']['panNumber']
            logger.info(f"Value of merchant panNumber obtained from update merchant : {update_merchant_pan}")
            update_merchant_gender = response['merchant']['gender']
            logger.info(f"Value of merchant gender obtained from update merchant : {update_merchant_gender}")
            update_merchant_dob = response['merchant']['dateOfBirth']
            logger.info(f"Value of merchant dateOfBirth obtained from update merchant : {update_merchant_dob}")
            update_merchant_instagram = response['merchant']['socialConnect']['instagram']
            logger.info(f"Value of merchant socialConnect instagram obtained from update merchant : {update_merchant_instagram}")
            update_merchant_facebook = response['merchant']['socialConnect']['facebook']
            logger.info(f"Value of merchant socialConnect facebook obtained from update merchant : {update_merchant_facebook}")
            update_merchant_digitalstore = response['merchant']['socialConnect']['digitalStore']
            logger.info(f"Value of merchant socialConnect digitalStore obtained from update merchant : {update_merchant_digitalstore}")
            update_merchant_product_category = response['merchant']['productCategory']
            logger.info(f"Value of merchant productCategory obtained from update merchant : {update_merchant_product_category}")
            update_merchant_product_sub_category = response['merchant']['productSubCategory']
            logger.info(f"Value of merchant productSubCategory obtained from update merchant : {update_merchant_product_sub_category}")
            update_merchant_status = response['merchant']['status']
            logger.info(f"Value of merchant status obtained from update merchant : {update_merchant_status}")
            update_merchant_language_preference = response['merchant']['languagePreference']
            logger.info(f"Value of merchant languagePreference obtained from update merchant : {update_merchant_language_preference}")
            update_merchant_opted_for_communication = response['merchant']['optedForCommunication']
            logger.info(f"Value of merchant optedForCommunication obtained from update merchant : {update_merchant_opted_for_communication}")

            query = "select * from product_category where name = '"+product_category+"';"
            logger.debug(f"Query to fetch data from product_category table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of product_category table : {result}")
            product_category_id = result['id'].values[0]
            logger.info(f"Value of id obtained from product_category table : {product_category_id}")

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
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "mobile_no": mobile_number,
                    "merchant_name": generate_random_merchant_name,
                    "email": email,
                    "store_name": store_name,
                    "gstin": gstin,
                    "pan_no": pan_number,
                    "gender": gender,
                    "dob": date_of_birth,
                    "instagram": social_connect_instagram,
                    "facebook": social_connect_facebook,
                    "digital_store": social_connect_digital_store,
                    "product_category": product_category,
                    "product_sub_category": product_sub_category,
                    "status": "ACTIVE",
                    "lang_preference": language_preference,
                    "opted_for_communication": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": update_merchant_success,
                    "user": update_merchant_user,
                    "device_identifier": update_merchant_device_identifier,
                    "device_identifier_type": update_merchant_device_identifier_type,
                    "mobile_no": update_merchant_mobile_no,
                    "merchant_name": update_merchant_name,
                    "email": update_merchant_email,
                    "store_name": update_merchant_store_name,
                    "gstin": update_merchant_gstin,
                    "pan_no": update_merchant_pan,
                    "gender": update_merchant_gender,
                    "dob": update_merchant_dob,
                    "instagram": update_merchant_instagram,
                    "facebook": update_merchant_facebook,
                    "digital_store": update_merchant_digitalstore,
                    "product_category": update_merchant_product_category,
                    "product_sub_category": update_merchant_product_sub_category,
                    "status": update_merchant_status,
                    "lang_preference": update_merchant_language_preference,
                    "opted_for_communication": update_merchant_opted_for_communication
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
                    "merchant_email": email,
                    "merchant_gstin": gstin,
                    "merchant_lang_preference": language_preference,
                    "merchant_mobile_no": mobile_number,
                    "merchant_name": generate_random_merchant_name,
                    "merchant_pan": pan_number,
                    "product_sub_category": product_sub_category,
                    "merchant_birth_date": date_of_birth,
                    "merchant_gender": gender,
                    "merchant_instagram": social_connect_instagram,
                    "merchant_facebook": social_connect_facebook,
                    "merchant_digital_store": social_connect_digital_store,
                    "merchant_status": "ACTIVE",
                    "merchant_store_name": store_name,
                    "merchant_category_id": product_category_id,
                    "opted_for_communication": True
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from merchant where mobile_number ='" + str(mobile_number) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data from merchant table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of merchant table : {result}")
                merchant_email = result['email'].values[0]
                logger.info(f"Value of email obtained from merchant table : {merchant_email}")
                merchant_name = result['name'].values[0]
                logger.info(f"Value of name obtained from merchant table : {merchant_name}")
                merchant_gstin = result['gstin'].values[0]
                logger.info(f"Value of gstin obtained from merchant table : {merchant_gstin}")
                merchant_lang_preference = result['language_preference'].values[0]
                logger.info(f"Value of language_preference obtained from merchant table : {merchant_lang_preference}")
                merchant_mobile_no = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained from merchant table : {merchant_mobile_no}")
                merchant_pan = result['pan_number'].values[0]
                logger.info(f"Value of pan_number obtained from merchant table : {merchant_pan}")
                merchant_product_sub_category = result['product_sub_category'].values[0]
                logger.info(f"Value of product_sub_category obtained from merchant table : {merchant_product_sub_category}")
                merchant_birth_date = result['birth_date'].values[0]
                logger.info(f"Value of birth_date obtained from merchant table : {merchant_birth_date}")
                merchant_gender = result['gender'].values[0]
                logger.info(f"Value of gender obtained from merchant table : {merchant_gender}")
                merchant_social_connect = result['social_connect'].values[0].replace('{','').replace('}','')
                logger.info(f"Value of social_connect obtained from merchant table : {merchant_social_connect}")
                merchant_instagram = merchant_social_connect.split(",")[0].split(":")[1].replace('"','')
                logger.info(f"Value of instagram url obtained from merchant table : {merchant_instagram}")
                merchant_facebook = merchant_social_connect.split(",")[1].split(":")[1].replace('"','')
                logger.info(f"Value of facebook url obtained from merchant table : {merchant_facebook}")
                merchant_digital_store = merchant_social_connect.split(",")[2].split(":")[1].replace('"','')
                logger.info(f"Value of digital_store url obtained from merchant table : {merchant_digital_store}")
                merchant_status = result['status'].values[0]
                logger.info(f"Value of status obtained from merchant table : {merchant_status}")
                merchant_store_name = result['store_name'].values[0]
                logger.info(f"Value of store_name obtained from merchant table : {merchant_store_name}")
                merchant_category_id = result['category_id'].values[0]
                logger.info(f"Value of category_id obtained from merchant table : {merchant_category_id}")

                query = "select cast(opted_for_communication as UNSIGNED) as opt_for_comm from merchant where mobile_number ='" + str(
                    mobile_number) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data from merchant table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of merchant table : {result}")
                merchant_opted_for_communication = result['opt_for_comm'].values[0]
                logger.info(f"Value of opted_for_communication obtained from merchant table : {merchant_opted_for_communication}")
                if merchant_opted_for_communication == 1:
                    opt_for_comm_db = True
                else:
                    opt_for_comm_db = False

                actual_db_values = {
                    "merchant_email": merchant_email,
                    "merchant_gstin": merchant_gstin,
                    "merchant_lang_preference": merchant_lang_preference,
                    "merchant_mobile_no": merchant_mobile_no,
                    "merchant_name": merchant_name,
                    "merchant_pan": merchant_pan,
                    "product_sub_category": merchant_product_sub_category,
                    "merchant_birth_date": merchant_birth_date,
                    "merchant_gender": merchant_gender,
                    "merchant_instagram": merchant_instagram,
                    "merchant_facebook": merchant_facebook,
                    "merchant_digital_store": merchant_digital_store,
                    "merchant_status": merchant_status,
                    "merchant_store_name": merchant_store_name,
                    "merchant_category_id": merchant_category_id,
                    "opted_for_communication": opt_for_comm_db
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
def test_common_600_601_007():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Update_Merchant_Address_For_ExistingUser
    Sub Feature Description: API: Validate for existing user by hitting update_merchant_address api
    TC naming code description: 600: EzeGro functions, 601: Sale, 007: TC007
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
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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
            logger.info(f"Value of push_token is : {push_token}")

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
            logger.info(f"Value of validate_auth_token obtained from validate otp : {validate_auth_token}")

            pin_code = ''.join(random.choices(string.digits, k=6))
            logger.debug(f"Randomly generated pincode is :{pin_code}")
            city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{city}")
            address_line_1 = "123 abc street" " " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{address_line_1}")
            address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{address_line_2}")
            state = "Karnataka"
            logger.debug(f"state is :{state}")
            country = "India"
            logger.debug(f"country is :{country}")

            #update merchant address
            api_details = DBProcessor.get_api_details('update_merchant_address', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "address": {
                    "pincode": pin_code,
                    "city": city,
                    "addressLine1": address_line_1,
                    "addressLine2": address_line_2,
                    "state": state,
                    "country": country
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for update merchant address {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for update merchant address is: {response}")
            update_merchant_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from update merchant address is : {update_merchant_mobile_no}")
            update_merchant_state = response['address']['state']
            logger.info(f"Value of state obtained from update merchant address is : {update_merchant_state}")
            update_merchant_country = response['address']['country']
            logger.info(f"Value of country obtained from update merchant address is : {update_merchant_country}")
            update_merchant_address_line_1 = response['address']['addressLine1']
            logger.info(f"Value of addressLine1 obtained from update merchant address is : {update_merchant_address_line_1}")
            update_merchant_address_line_2 = response['address']['addressLine2']
            logger.info(f"Value of addressLine2 obtained from update merchant address is : {update_merchant_address_line_2}")
            update_merchant_pincode = response['address']['pincode']
            logger.info(f"Value of pincode obtained from update merchant address is : {update_merchant_pincode}")
            update_merchant_city = response['address']['city']
            logger.info(f"Value of city obtained from update merchant address is : {update_merchant_city}")

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

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of merchant table : {result}")
            expected_merchant_store_name = result['store_name'].values[0]
            logger.info(f"Value of store_name obtained from merchant table : {expected_merchant_store_name}")
            expected_merchant_address_id = result['address_id'].values[0]
            logger.info(f"Value of address_id obtained from merchant table : {expected_merchant_address_id}")
            expected_merchant_address_version = result['address_version'].values[0]
            logger.info(f"Value of address_version obtained from merchant table : {expected_merchant_address_version}")

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
                    "state": state,
                    "country": country,
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "pincode": pin_code,
                    "city": city
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "mobile_no": update_merchant_mobile_no,
                    "state": update_merchant_state,
                    "country": update_merchant_country,
                    "address_line_1": update_merchant_address_line_1,
                    "address_line_2": update_merchant_address_line_2,
                    "pincode": update_merchant_pincode,
                    "city": update_merchant_city
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
                    "merchant_store_name": expected_merchant_store_name,
                    "merchant_address_id": expected_merchant_address_id,
                    "merchant_address_line_1": address_line_1,
                    "merchant_address_line_2": address_line_2,
                    "city": city,
                    "country": country,
                    "entity": "MERCHANT",
                    "pincode": pin_code,
                    "state": state,
                    "address_version": expected_merchant_address_version
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select mer.store_name, mer.address_id, addr.address_line_1, addr.address_line_2, addr.city, addr.state , addr.country, addr.entity, addr.pincode, mer.address_version" \
                        " from merchant AS mer INNER JOIN address as addr ON mer.address_id = addr.id " \
                        "where mer.mobile_number ='" + str(mobile_number) + "';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result obtained after inner join : {result}")
                store_name_db = result['store_name'].values[0]
                logger.info(f"Value of store_name obtained after inner joins is : {store_name_db}")
                address_id_db = result['address_id'].values[0]
                logger.info(f"Value of address_id obtained after inner joins is : {address_id_db}")
                address_line_1_db = result['address_line_1'].values[0]
                logger.info(f"Value of address_line_1 obtained after inner joins is : {address_line_1_db}")
                address_line_2_db = result['address_line_2'].values[0]
                logger.info(f"Value of address_line_2 obtained after inner joins is : {address_line_2_db}")
                city_db = result['city'].values[0]
                logger.info(f"Value of city obtained after inner joins is : {city_db}")
                state_db = result['state'].values[0]
                logger.info(f"Value of state obtained after inner joins is : {state_db}")
                country_db = result['country'].values[0]
                logger.info(f"Value of country obtained after inner joins is : {country_db}")
                entity_db = result['entity'].values[0]
                logger.info(f"Value of entity obtained after inner joins is : {entity_db}")
                pincode_db = result['pincode'].values[0]
                logger.info(f"Value of pincode obtained after inner joins is : {pincode_db}")
                address_version_db = result['address_version'].values[0]
                logger.info(f"Value of address_version obtained after inner joins is : {address_version_db}")

                actual_db_values = {
                    "merchant_store_name": store_name_db,
                    "merchant_address_id": address_id_db,
                    "merchant_address_line_1": address_line_1_db,
                    "merchant_address_line_2": address_line_2_db,
                    "city": city_db,
                    "country": country_db,
                    "entity": entity_db,
                    "pincode": pincode_db,
                    "state": state_db,
                    "address_version": address_version_db
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
def test_common_600_601_008():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_To_Update_Merchant_Profile_Image
    Sub Feature Description: API:Validate the functionality of update merchant image API
    TC naming code description: 600: EzeGro, 601: Sale, 008: TC008
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
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            file_name = "Image" + str(random.choice(string.ascii_uppercase))
            api_details = DBProcessor.get_api_details('updateMerchantProfileImage', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "contentType": "png",
                "fileName": file_name
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for autologin {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Update Merchant profile image is: {response}")
            image_upload_success = response['success']
            logger.info(f"Value of success obtained from Update Merchant profile image : {image_upload_success}")
            res_user = response['user']
            logger.info(f"Value of user obtained from Update Merchant profile image : {res_user}")
            res_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from Update Merchant profile image : {res_device_identifier}")
            res_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from Update Merchant profile image : {res_device_identifier_type}")
            res_mobile_number = response['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from Update Merchant profile image : {res_mobile_number}")

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
                    "success": True,
                    "user": validate_otp_user,
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "mobile_no": mobile_number,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": image_upload_success,
                    "user": expected_user_db,
                    "device_identifier": res_device_identifier,
                    "device_identifier_type": res_device_identifier_type,
                    "mobile_no": res_mobile_number,
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
                    "user_mobile_number": mobile_number,
                    "merchant_img" : file_name + ".png"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
                logger.debug(f"Query to fetch data for actual db values from merchant table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                result = result.replace(np.nan,'NULL',regex=True)
                logger.info(f"Query result for actual db values from merchant table : {result}")
                mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained from merchant table : {mobile_number_db}")
                merchant_image = result['merchant_image'].values[0]
                logger.info(f"Fetching merchant_image value from the merchant table : {merchant_image}")
                img_name = merchant_image.split('_')[1]

                actual_db_values = {
                    "user_mobile_number": mobile_number_db,
                    "merchant_img": img_name
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
def test_common_600_601_009():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Customer_For_ExistingUser
    Sub Feature Description: API: Validate create customer by hitting create_customer api
    TC naming code description: 600: EzeGro functions, 601: Sale, 009: TC009
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

        # deleting the customer
        delete_customer_mobile_no = '666666666%'
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{pincode}")
            city = "Bengaluru "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{city}")
            address_line_1 = "123 abc street "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{address_line_1}")
            address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{address_line_2}")
            state = "Karnataka"
            logger.debug(f"state is :{state}")
            country = "India"
            logger.debug(f"country is :{country}")

            #create a customer
            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no,
                    "address": {
                        "pincode": pincode,
                        "state": state,
                        "city": city,
                        "country": country,
                        "addressLine1": address_line_1,
                        "addressLine2": address_line_2
                    }
                },
                "customerVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")
            create_customers_response = list(response['customers'])
            logger.info(f"Converting customers to list format: {create_customers_response}")
            create_customers_name = create_customers_response[0]['name']
            logger.info(f"Value of customer name obtained from create customer is : {create_customers_name}")
            create_customers_mobile_no = create_customers_response[0]['mobileNumber']
            logger.info(f"Value of customer mobile number obtained from create customer is : {create_customers_mobile_no}")
            create_customers_state = create_customers_response[0]['address']['state']
            logger.info(f"Value of customer state obtained from create customer is : {create_customers_state}")
            create_customers_country = create_customers_response[0]['address']['country']
            logger.info(f"Value of customer country obtained from create customer is : {create_customers_country}")
            create_customers_address_line_1 = create_customers_response[0]['address']['addressLine1']
            logger.info(f"Value of customer addressLine1 obtained from create customer is : {create_customers_address_line_1}")
            create_customers_address_line_2 = create_customers_response[0]['address']['addressLine2']
            logger.info(f"Value of customer addressLine2 obtained from create customer is : {create_customers_address_line_2}")
            create_customers_pincode = create_customers_response[0]['address']['pincode']
            logger.info(f"Value of customer pincode obtained from create customer is : {create_customers_pincode}")
            create_customers_city = create_customers_response[0]['address']['city']
            logger.info(f"Value of customer city obtained from create customer is : {create_customers_city}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version_db = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version_db}")

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
                    "name": customer_name,
                    "mobile_no": customer_mobile_no,
                    "state": state,
                    "country": country,
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "pincode": str(pincode),
                    "city": city
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "name": create_customers_name,
                    "mobile_no": create_customers_mobile_no,
                    "state": create_customers_state,
                    "country": create_customers_country,
                    "address_line_1": create_customers_address_line_1,
                    "address_line_2": create_customers_address_line_2,
                    "pincode": create_customers_pincode,
                    "city": create_customers_city
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
                    "customer_version": merchant_customer_version_db,
                    "name": customer_name,
                    "mobile_no": customer_mobile_no,
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "city": city,
                    "state": state,
                    "pincode": str(pincode),
                    "country": country,
                    "entity": "CUSTOMER",
                    "address_type": "DELIVERY"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select C.merchant_id, M.customer_version, A.entity_id, C.name, C.mobile_number, C.notes,C.address_id, A.address_line_1, " \
                        "A.address_line_2, A.city, A.state, A.pincode, A.country, A.entity, A.address_type " \
                        "from merchant AS M INNER JOIN customer AS C ON M.id = C.merchant_id INNER JOIN address AS A ON C.address_id = A.id " \
                        "where C.mobile_number = '" + str(customer_mobile_no) + "' and M.mobile_number = '" + str(mobile_number) + "';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                customer_version_db = result['customer_version'].values[0]
                logger.info(f"Value of customer_version obtained after inner join is : {customer_version_db}")
                name_db = result['name'].values[0]
                logger.info(f"Value of name obtained after inner join is : {name_db}")
                mobile_no_db = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained after inner join is : {mobile_no_db}")
                address_line_1_db = result['address_line_1'].values[0]
                logger.info(f"Value of address_line_1 obtained after inner join is : {address_line_1_db}")
                address_line_2_db = result['address_line_2'].values[0]
                logger.info(f"Value of address_line_2 obtained after inner join is : {address_line_2_db}")
                city_db = result['city'].values[0]
                logger.info(f"Value of city obtained after inner join is : {city_db}")
                state_db = result['state'].values[0]
                logger.info(f"Value of state obtained after inner join is : {state_db}")
                pincode_db = result['pincode'].values[0]
                logger.info(f"Value of pincode obtained after inner join is : {pincode_db}")
                country_db = result['country'].values[0]
                logger.info(f"Value of country obtained after inner join is : {country_db}")
                entity_db = result['entity'].values[0]
                logger.info(f"Value of entity obtained after inner join is : {entity_db}")
                address_type_db = result['address_type'].values[0]
                logger.info(f"Value of address_type obtained after inner join is : {address_type_db}")

                actual_db_values = {
                    "customer_version": customer_version_db,
                    "name": name_db,
                    "mobile_no": mobile_no_db,
                    "address_line_1": address_line_1_db,
                    "address_line_2": address_line_2_db,
                    "city": city_db,
                    "state": state_db,
                    "pincode": pincode_db,
                    "country": country_db,
                    "entity": entity_db,
                    "address_type": address_type_db
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
def test_common_600_601_010():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Order_For_ExistingUser
    Sub Feature Description: API: Validate create order by hitting create_order api
    TC naming code description: 600: EzeGro functions, 601: Sale, 010: TC010
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

        # deleting the customer
        delete_customer_mobile_no = "666666666%"
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False,
                                                   middlewareLog=False, config_log=False)

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

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{pincode}")
            city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{city}")
            address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{address_line_1}")
            address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{address_line_2}")
            state = "Karnataka"
            logger.debug(f"state is :{state}")
            country = "India"
            logger.debug(f"country is :{country}")

            #create a customer
            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no,
                    "address": {
                        "pincode": pincode,
                        "state": state,
                        "city": city,
                        "country": country,
                        "addressLine1": address_line_1,
                        "addressLine2": address_line_2
                    }
                },
                "customerVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")

            prod_name = "t-shits " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100,1500))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1,5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")

            #create order
            api_details = DBProcessor.get_api_details('create_order', request_body={
                    "user": validate_otp_user,
                    "mobileNumber": mobile_number,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type,
                    "order": {
                        "customer": {
                            "name": customer_name,
                            "mobileNumber": customer_mobile_no
                        },
                        "products": [
                            {
                                "name": prod_name,
                                "price": price,
                                "quantity": quantity
                            }
                        ]
                    },
                    "customerVersion": merchant_customer_version,
                    "orderVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order is: {response}")
            create_orders = list(response['orders'])
            logger.info(f"Converting orders to list format: {create_orders}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")
            create_order_name = create_orders[-1]['customer']['name']
            logger.info(f"Value of name obtained from create order : {create_order_name}")
            create_order_mobile_no = create_orders[-1]['customer']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from create order : {create_order_mobile_no}")
            create_order_status = create_orders[-1]['status']
            logger.info(f"Value of status obtained from create order : {create_order_status}")
            create_order_ref_id = create_orders[-1]['refId']
            logger.info(f"Value of refId obtained from create order : {create_order_ref_id}")
            create_order_amount = create_orders[-1]['amount']
            logger.info(f"Value of amount obtained from create order : {create_order_amount}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version_db = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version_db}")

            query = "select * from order_details where id ='" + str(create_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from order_details table : {order_details_id_db}")
            order_details_amt_db = result['amount'].values[0]
            logger.info(f"Value of amount obtained from order_details table : {order_details_amt_db}")
            order_details_ref_id_db = result['ref_id'].values[0]
            logger.info(f"Value of ref_id obtained from order_details table : {order_details_ref_id_db}")

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
                    "id": create_order_id,
                    "name": customer_name,
                    "mobile_no": customer_mobile_no,
                    "status": 'INCOMPLETE',
                    "ref_id": create_order_ref_id,
                    "amt": price*quantity,
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "id": order_details_id_db,
                    "name": create_order_name ,
                    "mobile_no": create_order_mobile_no ,
                    "status": create_order_status,
                    "ref_id": order_details_ref_id_db,
                    "amt": create_order_amount,
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
                    "mobile_no": mobile_number,
                    "customer_name": customer_name,
                    "customer_mobile_no": customer_mobile_no,
                    "order_id": order_details_id_db,
                    "ref_id": order_details_ref_id_db,
                    "amt": price*quantity,
                    "status": 'ACTIVE',
                    "dimensions": None,
                    "pick_up_address": None,
                    "weight": None
                }

                logger.debug(f"expected_db_values: {expected_db_values}")


                query = "select OD.merchant_id, M.mobile_number,OD.customer_id, C.name AS Customer_name, C.mobile_number AS CUST_MOB, OD.id AS ORDER_ID, " \
                        "OD.ref_id, OD.notes, OD.amount, OD.status, OD.dimensions, OD.pick_up_address, OD.weight " \
                        "from merchant AS M INNER JOIN order_details AS OD ON M.id = OD.merchant_id INNER JOIN customer as C ON OD.customer_id = C.id " \
                        "where OD.id = '" + str(create_order_id) + "';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                mobile_no_db = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained after inner join is : {mobile_no_db}")
                customer_name_db = result['Customer_name'].values[0]
                logger.info(f"Value of customer_name obtained after inner join is : {customer_name_db}")
                customer_mobile_no_db = result['CUST_MOB'].values[0]
                logger.info(f"Value of customer mobile number obtained after inner join is : {customer_mobile_no_db}")
                customer_order_id_db = result['ORDER_ID'].values[0]
                logger.info(f"Value of customer order_id obtained after inner join is : {customer_order_id_db}")
                customer_ref_id_db = result['ref_id'].values[0]
                logger.info(f"Value of customer ref_id obtained after inner join is : {customer_ref_id_db}")
                amt_db = result['amount'].values[0]
                logger.info(f"Value of amount obtained after inner join is : {amt_db}")
                status_db = result['status'].values[0]
                logger.info(f"Value of status obtained after inner join is : {status_db}")
                dimensions_db = result['dimensions'].values[0]
                logger.info(f"Value of dimensions obtained after inner join is : {dimensions_db}")
                pickup_address_db = result['pick_up_address'].values[0]
                logger.info(f"Value of pickup_address obtained after inner join is : {pickup_address_db}")
                weight_db = result['weight'].values[0]
                logger.info(f"Value of weight obtained after inner join is : {weight_db}")

                actual_db_values = {
                    "mobile_no": mobile_no_db,
                    "customer_name": customer_name_db,
                    "customer_mobile_no": customer_mobile_no_db,
                    "order_id": customer_order_id_db,
                    "ref_id": customer_ref_id_db,
                    "amt": amt_db,
                    "status": status_db,
                    "dimensions": dimensions_db,
                    "pick_up_address": pickup_address_db,
                    "weight": weight_db
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