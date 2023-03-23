import string
import sys
import pytest
import random
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, EzeGro_processor

logger = EzeAutoLogger(__name__)

@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_602_001():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Add_Pickup_Location
    Sub Feature Description: Add Pickup location
    TC naming code description: 600: EzeGro functions, 602: Logistics, 001: TC001
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
        delete_customer_mobile_no = "666666666%"
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        #deleting add pickup address mobile number
        delete_pickup_address_mobile_no = "777777777%"
        EzeGro_processor.delete_existing_pickup_address(delete_pickup_address_mobile_no)

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pick up pincode is :{pickup_pincode}")
            pickup_name = "Micheal "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated name for pick up is :{pickup_name}")
            pickup_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_1 is :{pickup_address_line_1}")
            pickup_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_2 is :{pickup_address_line_2}")
            pickup_state = "Karnataka"
            logger.debug(f"Value of pick up state is :{pickup_state}")
            pickup_country = "India"
            logger.debug(f"Value of pick up country is :{pickup_country}")
            pickup_city = "Benguluru"
            logger.debug(f"Value of pick up city is :{pickup_city}")
            pickup_is_default = "true"
            logger.debug(f"Value of pick up is_default is :{pickup_is_default}")
            pickup_address_name = "HOME"
            logger.debug(f"Value of pick up address name  is :{pickup_address_name}")

            #add pick location
            api_details = DBProcessor.get_api_details('add_pick_location', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "addressVersion": "0",
                "address": {
                    "email": pickup_email,
                    "mobileNumber": pickup_mobile_no,
                    "pincode": pickup_pincode,
                    "name": pickup_name,
                    "addressLine1": pickup_address_line_1,
                    "addressLine2": pickup_address_line_2,
                    "state": pickup_state,
                    "country": pickup_country,
                    "city": pickup_city,
                    "isDefault": pickup_is_default,
                    "addressName": pickup_address_name
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for add pickup location {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for add pickup location is: {response}")
            pickup_address_version = response['addressVersion']
            logger.info(f"Value of addressVersion obtained from add pickup location is : {pickup_address_version}")
            pickup_add = list(response['addresses'])
            logger.info(f"Converting addresses to list format from from add pickup location is : {pickup_add}")
            pickup_address = pickup_add[-1]['pickUpAddress']
            logger.info(f"Value of pickUpAddress obtained from add pickup location is : {pickup_address}")

            query = "select * from address where mobile_number ='" + str(pickup_mobile_no) + "';"
            logger.debug(f"Query to fetch data from address table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of address table : {result}")
            address_id_db = result['id'].values[-1]
            logger.debug(f"Value of id from address table :{address_id_db}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of merchant table : {result}")
            merchant_address_version_db = result['address_version'].values[0]
            logger.info(f"Value of address_version obtained from merchant table : {merchant_address_version_db}")

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
                    "address_version": pickup_address_version,
                    "pickup_address": pickup_address
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "address_version": merchant_address_version_db,
                    "pickup_address": address_id_db
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
                    "address_line_1": pickup_address_line_1,
                    "address_line_2": pickup_address_line_2,
                    "city": pickup_city,
                    "country": pickup_country,
                    "entity": "MERCHANT",
                    "pincode": str(pickup_pincode),
                    "state": pickup_state,
                    "address_name": pickup_address_name,
                    "address_type": "PICK_UP",
                    "mobile_number": pickup_mobile_no,
                    "address_version": pickup_address_version,
                    "name": pickup_name,
                    "email": pickup_email,
                    "is_default": True
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select A.address_line_1,A.address_line_2,A.city, A.country, A.entity, A.pincode, A.state, A.address_name, A.address_type, " \
                        "A.is_default, A.name,A.mobile_number,A.name, A.email, A.shiprocket_address_id,M.address_version " \
                        "from address AS A INNER JOIN merchant AS M ON A.entity_id = M.id where A.id ='"+str(pickup_address)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                address_line_1_db = result['address_line_1'].values[0]
                logger.info(f"Value of address_line_1 obtained after inner join is : {address_line_1_db}")
                address_line_2_db = result['address_line_2'].values[0]
                logger.info(f"Value of address_line_2 obtained after inner join is : {address_line_2_db}")
                city_db = result['city'].values[0]
                logger.info(f"Value of city obtained after inner join is : {city_db}")
                country_db = result['country'].values[0]
                logger.info(f"Value of country obtained after inner join is : {country_db}")
                entity_db = result['entity'].values[0]
                logger.info(f"Value of entity obtained after inner join is : {entity_db}")
                pincode_db = result['pincode'].values[0]
                logger.info(f"Value of pincode obtained after inner join is : {pincode_db}")
                state_db = result['state'].values[0]
                logger.info(f"Value of state obtained after inner join is : {state_db}")
                address_name_db = result['address_name'].values[0]
                logger.info(f"Value of address_name obtained after inner join is : {address_name_db}")
                address_type_db = result['address_type'].values[0]
                logger.info(f"Value of address_type obtained after inner join is : {address_type_db}")
                mobile_number_db = result['mobile_number'].values[0]
                logger.info(f"Value of mobile_number obtained after inner join is : {mobile_number_db}")
                address_version_db = result['address_version'].values[0]
                logger.info(f"Value of address_version obtained after inner join is : {address_version_db}")
                name_db = result['name'].values[0]
                logger.info(f"Value of name obtained after inner join is : {name_db}")
                email_db = result['email'].values[0]
                logger.info(f"Value of email obtained after inner join is : {email_db}")

                query = "select id,cast(is_default as UNSIGNED) as is_default from address where id ='" + str(pickup_address) + "';"
                logger.debug(f"Query to fetch data from address table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of address table : {result}")
                is_default_db = result['is_default'].values[0]
                logger.info(f"Value of is_default obtained from address table : {is_default_db}")

                if is_default_db == 1:
                    is_default_db = True
                else:
                    is_default_db = False

                actual_db_values = {
                    "address_line_1": address_line_1_db,
                    "address_line_2": address_line_2_db,
                    "city": city_db,
                    "country": country_db,
                    "entity": entity_db,
                    "pincode": pincode_db,
                    "state": state_db,
                    "address_name": address_name_db,
                    "address_type": address_type_db,
                    "mobile_number": mobile_number_db,
                    "address_version": address_version_db,
                    "name": name_db[0],
                    "email": email_db,
                    "is_default": is_default_db
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
def test_common_600_602_002():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Add_Pickup_Location_and_change_default_Pickup_addess
    Sub Feature Description: Add Pickup location and Change_default_pickup_address
    TC naming code description: 600: EzeGro functions, 602: Logistics, 002: TC002
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
        delete_customer_mobile_no = "666666666%"
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        #deleting add pickup address mobile number
        delete_pickup_address_mobile_no = "777777777%"
        EzeGro_processor.delete_existing_pickup_address(delete_pickup_address_mobile_no)

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pick up pincode is :{pickup_pincode}")
            pickup_name = "Micheal "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated name for pick up is :{pickup_name}")
            pickup_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_1 is :{pickup_address_line_1}")
            pickup_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_2 is :{pickup_address_line_2}")
            pickup_state = "Karnataka"
            logger.debug(f"Value of pick up state is :{pickup_state}")
            pickup_country = "India"
            logger.debug(f"Value of pick up country is :{pickup_country}")
            pickup_city = "Benguluru"
            logger.debug(f"Value of pick up city is :{pickup_city}")
            pickup_is_default = "false"
            logger.debug(f"Value of pick up is_default is :{pickup_is_default}")
            pickup_address_name = "HOME"
            logger.debug(f"Value of pick up address name  is :{pickup_address_name}")

            #add pick location
            api_details = DBProcessor.get_api_details('add_pick_location', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "addressVersion": "0",
                "address": {
                    "email": pickup_email,
                    "mobileNumber": pickup_mobile_no,
                    "pincode": pickup_pincode,
                    "name": pickup_name,
                    "addressLine1": pickup_address_line_1,
                    "addressLine2": pickup_address_line_2,
                    "state": pickup_state,
                    "country": pickup_country,
                    "city": pickup_city,
                    "isDefault": pickup_is_default,
                    "addressName": pickup_address_name
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for add pickup location {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for add pickup location is: {response}")
            pickup_address_version = response['addressVersion']
            logger.info(f"Value of addressVersion obtained from add pickup location is : {pickup_address_version}")
            pickup_add = list(response['addresses'])
            logger.info(f"Converting addresses to list format from from add pickup location is : {pickup_add}")
            pickup_is_default_response = pickup_add[-1]['isDefault']
            logger.info(f"Value of is default obtained from add pickup location is : {pickup_is_default_response}")
            pickup_address = pickup_add[-1]['pickUpAddress']
            logger.info(f"Value of pickUpAddress obtained from add pickup location is : {pickup_address}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of merchant table : {result}")
            merchant_address_version_db = result['address_version'].values[0]
            logger.info(f"Value of address_version obtained from merchant table : {merchant_address_version_db}")

            #change default pick up address
            api_details = DBProcessor.get_api_details('change_default_pickup_add', request_body={
                    "user": validate_otp_user,
                    "mobileNumber": mobile_number,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type,
                    "address": {
                        "pickUpAddress": pickup_address
                    }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for change default pickup address {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for isDefault : {response}")
            change_default_pickup_add = response['address']
            logger.info(f"Converting address to list format from from add pickup location is : {change_default_pickup_add}")
            change_is_default = change_default_pickup_add['isDefault']
            logger.info(f"Value of isDefault obtained from change default pickup addressis : {change_is_default}")

            query = "select * from address where mobile_number ='" + str(pickup_mobile_no) + "';"
            logger.debug(f"Query to fetch data from address table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of address table : {result}")
            address_id_db = result['id'].values[-1]
            logger.debug(f"Value of id from address table :{address_id_db}")

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
                    "address_version": pickup_address_version,
                    "add_pickup_is_default": False,
                    "pickup_address": pickup_address,
                    "change_default_is_default": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "address_version": merchant_address_version_db,
                    "add_pickup_is_default": pickup_is_default_response,
                    "pickup_address": address_id_db,
                    "change_default_is_default": change_is_default
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
                    "is_default": True
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select id,cast(is_default as UNSIGNED) as is_default from address where id ='" + str(pickup_address) + "';"
                logger.debug(f"Query to fetch data from address table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of address table : {result}")
                is_default_db = result['is_default'].values[0]
                logger.info(f"Value of is_default obtained from address table : {is_default_db}")

                if is_default_db == 1:
                    is_default_db = True
                else:
                    is_default_db = False

                actual_db_values = {
                    "is_default": is_default_db
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
def test_common_600_602_003():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Create_order_Add_Pickup_location_and_create_order_logistics_existing_order
    Sub Feature Description: Create_order, Add_Pickup_location and create_order_logistics
    TC naming code description: 600: EzeGro functions, 602: Logistics, 003: TC003
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
        delete_customer_mobile_no = "666666666%"
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        # deleting add pickup address mobile number
        delete_pickup_address_mobile_no = "777777777%"
        EzeGro_processor.delete_existing_pickup_address(delete_pickup_address_mobile_no)

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            customer_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated customer email is :{customer_email}")
            customer_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

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
                        "pincode": customer_pincode,
                        "state": customer_state,
                        "city": customer_city,
                        "country": customer_country,
                        "addressLine1": customer_address_line_1,
                        "addressLine2": customer_address_line_2
                    }
                },
                "customerVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")

            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100,1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1,5)
            logger.info(f"Randomly generated quantity is : {quantity}")
            notes = "Just enjoy our products and live a luxury life !!"
            randomly_generated_create_order_ref_id = "EZE" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order endpoint : {randomly_generated_create_order_ref_id}")

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
                        ],
                        "refId": randomly_generated_create_order_ref_id,
                        "notes": notes,
                    },
                    "customerVersion": "0",
                    "orderVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order is: {response}")
            create_order_version = response['orderVersion']
            logger.info(f"Value of order version obtained from create order : {create_order_version}")
            create_orders = list(response['orders'])
            logger.info(f"Converting orders to list format: {create_orders}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")
            create_order_customer_name = create_orders[-1]['customer']['name']
            logger.info(f"Value of name obtained from create order : {create_order_customer_name}")
            create_order_mobile_no = create_orders[-1]['customer']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from create order : {create_order_mobile_no}")
            create_order_notes = create_orders[-1]['notes']
            logger.info(f"Value of notes obtained from create order : {create_order_notes}")
            create_order_ref_id = create_orders[-1]['refId']
            logger.info(f"Value of refId obtained from create order : {create_order_ref_id}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version_db = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version_db}")
            merchant_order_version_db = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table : {merchant_order_version_db}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pick up pincode is :{pickup_pincode}")
            pickup_name = "Micheal "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated name for pick up is :{pickup_name}")
            pickup_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_1 is :{pickup_address_line_1}")
            pickup_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_2 is :{pickup_address_line_2}")
            pickup_state = "Karnataka"
            logger.debug(f"Value of pick up state is :{pickup_state}")
            pickup_country = "India"
            logger.debug(f"Value of pick up country is :{pickup_country}")
            pickup_city = "Benguluru"
            logger.debug(f"Value of pick up city is :{pickup_city}")
            pickup_is_default = "true"
            logger.debug(f"Value of pick up is_default is :{pickup_is_default}")
            pickup_address_name = "HOME"
            logger.debug(f"Value of pick up address name  is :{pickup_address_name}")

            #add pick location
            api_details = DBProcessor.get_api_details('add_pick_location', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "addressVersion": "0",
                "address": {
                    "email": pickup_email,
                    "mobileNumber": pickup_mobile_no,
                    "pincode": pickup_pincode,
                    "name": pickup_name,
                    "addressLine1": pickup_address_line_1,
                    "addressLine2": pickup_address_line_2,
                    "state": pickup_state,
                    "country": pickup_country,
                    "city": pickup_city,
                    "isDefault": pickup_is_default,
                    "addressName": pickup_address_name
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for add pickup location {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for add pickup location is: {response}")
            pickup_add = list(response['addresses'])
            logger.info(f"Converting addresses to list format from from add pickup location is : {pickup_add}")
            pickup_address = pickup_add[-1]['pickUpAddress']
            logger.info(f"Value of pickUpAddress obtained from add pickup location is : {pickup_address}")

            weight = round(random.uniform(0.25,1.0),2)
            logger.info(f"Randomly Generated weight is : {weight}")
            length = random.randint(1,2)
            logger.info(f"Randomly Generated length is : {length}")
            breadth = random.randint(2,4)
            logger.info(f"Randomly Generated breadth is : {breadth}")
            height = random.randint(4,6)
            logger.info(f"Randomly Generated height is : {height}")
            ref_id = "EZE"+''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order logistics endpoint : {ref_id}")
            create_order_logistics_notes = "This Product is Good and Comfortable"

            #create order logistics for existing order id
            api_details = DBProcessor.get_api_details('create_order_logistics', request_body={
                    "user": validate_otp_user,
                    "mobileNumber": mobile_number,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type,
                    "customerVersion": "0",
                    "orderVersion": "0",
                    "order": {
                        "id": create_order_id,
                        "customer": {
                            "name": customer_name,
                            "email": customer_email,
                            "mobileNumber": customer_mobile_no,
                            "address": {
                                "state": customer_state,
                                "country": customer_country,
                                "addressLine1": customer_address_line_1,
                                "addressLine2": customer_address_line_2,
                                "pincode": customer_pincode,
                                "city": customer_city
                            }
                        },
                        "products": [
                            {
                                "name": prod_name,
                                "price": price,
                                "quantity": quantity
                            }
                        ],
                        "notes": create_order_logistics_notes,
                        "refId": ref_id,
                        "packageDetails": {
                            "weight": weight,
                            "dimension": {
                                "length": length,
                                "breadth": breadth,
                                "height": height
                            }
                        },
                        "pickUpAddress": pickup_address
                    }

            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order logistics {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order logistics is: {response}")
            create_logistics_customer_version = response['customerVersion']
            logger.info(f"Value of customer version obtained from create order logistics : {create_logistics_customer_version}")
            create_logistics_order_version = response['orderVersion']
            logger.info(f"Value of order version obtained from create order logistics : {create_logistics_order_version}")
            create_logistics_orders = list(response['orders'])
            logger.info(f"Converting orders to list format from create order logistics : {create_logistics_orders}")
            create_logistics_order_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of id obtained from create order logistics : {create_logistics_order_id}")
            create_logistics_name = create_logistics_orders[-1]['customer']['name']
            logger.info(f"Value of name obtained from create order logistics : {create_logistics_name}")
            create_logistics_email = create_logistics_orders[-1]['customer']['email']
            logger.info(f"Value of email obtained from create order logistics : {create_logistics_email}")
            create_logistics_mobile_no = create_logistics_orders[-1]['customer']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from create order logistics : {create_logistics_mobile_no}")
            create_logistics_ref_id = create_logistics_orders[-1]['refId']
            logger.info(f"Value of refId obtained from create order logistics : {create_logistics_ref_id}")
            create_logistics_amt = create_logistics_orders[-1]['amount']
            logger.info(f"Value of amount obtained from create order logistics : {create_logistics_amt}")
            create_logistics_pickup_addr = create_logistics_orders[-1]['pickUpAddress']
            logger.info(f"Value of pickup address obtained from create order logistics : {create_logistics_pickup_addr}")
            create_logistics_weight = create_logistics_orders[-1]['packageDetails']['weight']
            logger.info(f"Value of weight address obtained from create order logistics : {create_logistics_weight}")
            create_logistics_length = create_logistics_orders[-1]['packageDetails']['dimension']['length']
            logger.info(f"Value of length address obtained from create order logistics : {create_logistics_length}")
            create_logistics_breadth = create_logistics_orders[-1]['packageDetails']['dimension']['breadth']
            logger.info(f"Value of breadth address obtained from create order logistics : {create_logistics_breadth}")
            create_logistics_height = create_logistics_orders[-1]['packageDetails']['dimension']['height']
            logger.info(f"Value of height address obtained from create order logistics : {create_logistics_height}")

            query = "select * from address where mobile_number ='" + str(pickup_mobile_no) + "';"
            logger.debug(f"Query to fetch data from address table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of address table : {result}")
            address_id_db = result['id'].values[-1]
            logger.debug(f"Value of id from address table :{address_id_db}")

            query = "select * from order_details where id ='" + str(create_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from order_details table : {order_details_id_db}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table after create order logistics : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table after create order logistics : {result}")
            create_order_logistics_order_version_db = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table after create order logistics : {create_order_logistics_order_version_db}")

            query = "select * from shipment_details where order_id ='" + str(create_order_id) + "';"
            logger.debug(f"Query to fetch data from shipment details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for shipment details table : {result}")
            shipment_id = result['shipment_id'].values[0]
            logger.info(f"Value of shipment_id obtained from shipment details : {shipment_id}")

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
                    "order_version": merchant_order_version_db,
                    "id": create_order_id,
                    "name": customer_name,
                    "mobile_no": customer_mobile_no,
                    "notes": notes,
                    "ref_id": randomly_generated_create_order_ref_id,
                    "pick_up_address": pickup_address,
                    "customer_version": merchant_customer_version_db,
                    "create_logistics_order_version": create_order_logistics_order_version_db,
                    "create_logistics_name": customer_name,
                    "create_logistics_email": customer_email,
                    "create_logistics_mobile_no": customer_mobile_no,
                    "create_logistics_ref_id": ref_id,
                    "create_logistics_amount": price * quantity,
                    "create_logistics_pick_up_add": pickup_address,
                    "create_logistics_weight": str(f'{float(weight):.2f}'),
                    "create_logistics_length": str(f'{float(length):.1f}'),
                    "create_logistics_breadth": str(f'{float(breadth):.1f}'),
                    "create_logistics_height": str(f'{float(height):.1f}')
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "order_version": create_order_version,
                    "id": order_details_id_db,
                    "name": create_order_customer_name ,
                    "mobile_no": create_order_mobile_no,
                    "notes": create_order_notes,
                    "ref_id": create_order_ref_id,
                    "pick_up_address": address_id_db,
                    "customer_version": create_logistics_customer_version,
                    "create_logistics_order_version": create_logistics_order_version,
                    "create_logistics_name": create_logistics_name,
                    "create_logistics_email": create_logistics_email,
                    "create_logistics_mobile_no": create_logistics_mobile_no,
                    "create_logistics_ref_id": create_logistics_ref_id,
                    "create_logistics_amount": create_logistics_amt,
                    "create_logistics_pick_up_add": create_logistics_pickup_addr,
                    "create_logistics_weight": str(f'{float(create_logistics_weight):.2f}'),
                    "create_logistics_length": str(f'{float(create_logistics_length):.1f}'),
                    "create_logistics_breadth": str(f'{float(create_logistics_breadth):.1f}'),
                    "create_logistics_height": str(f'{float(create_logistics_height):.1f}')
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
                    "order_version": merchant_order_version_db,
                    "customer_version": merchant_customer_version_db,
                    "customer_name": customer_name,
                    "customer_mobile_no": customer_mobile_no,
                    "order_id": create_order_id,
                    "ref_id": ref_id,
                    "notes": create_order_logistics_notes,
                    "amt": price*quantity,
                    "order_status": 'ACTIVE',
                    "length": str(f'{float(length):.1f}'),
                    "breadth": str(f'{float(breadth):.1f}'),
                    "height": str(f'{float(height):.1f}'),
                    "pickup_address": pickup_address,
                    "weight": str(f'{float(weight):.2f}'),
                    "order_customer_name": customer_name,
                    "order_customer_mobile_no": customer_mobile_no,
                    "shipment_status": "PENDING",
                    "shipment_id": shipment_id,
                    "status": 'NEW'
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.merchant_id, M.store_name,M.order_version,M.customer_version, OD.customer_id, C.name AS Customer_name, " \
                        "C.mobile_number AS CUST_MOB, OD.id AS ORDER_ID, OD.ref_id, OD.notes, OD.amount, OD.status AS order_status,OD.dimensions, " \
                        "OD.pick_up_address, OD.weight, OC.name AS order_customer_name, OC.mobile_number AS Order_cus_mobile_no, " \
                        "SD.shipment_status,SD.shipment_id,SD.status from merchant AS M INNER JOIN order_details AS OD ON M.id = OD.merchant_id " \
                        "INNER JOIN customer as C ON OD.customer_id = C.id INNER JOIN order_customer AS OC ON OD.order_customer_id = OC.id " \
                        "INNER JOIN shipment_details AS SD ON OD.id = SD.order_id where OD.id = '"+str(create_order_id)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                order_version_db = result['order_version'].values[0]
                logger.info(f"Value of order version obtained after inner join is : {order_version_db}")
                customer_version_db = result['customer_version'].values[0]
                logger.info(f"Value of customer version obtained after inner join is : {customer_version_db}")
                customer_name_db = result['Customer_name'].values[0]
                logger.info(f"Value of customer name obtained after inner join is : {customer_name_db}")
                customer_mobile_db = result['CUST_MOB'].values[0]
                logger.info(f"Value of customer mobile number obtained after inner join is : {customer_mobile_db}")
                order_id_db = result['ORDER_ID'].values[0]
                logger.info(f"Value of customer order id obtained after inner join is : {order_id_db}")
                ref_id_db = result['ref_id'].values[0]
                logger.info(f"Value of customer ref id obtained after inner join is : {ref_id_db}")
                notes_db = result['notes'].values[0]
                logger.info(f"Value of customer notes obtained after inner join is : {notes_db}")
                amt_db = result['amount'].values[0]
                logger.info(f"Value of amount obtained after inner join is : {amt_db}")
                order_status_db = result['order_status'].values[0]
                logger.info(f"Value of order_status obtained after inner join is : {order_status_db}")
                dimensions_db = result['dimensions'].values[0].replace('{', '').replace('}', '')
                logger.info(f"Value of dimensions obtained after inner join is : {dimensions_db}")
                length_db = dimensions_db.split(",")[0].split(":")[1].replace('"', '')
                logger.info(f"Value of length obtained after inner join is : {length_db}")
                breadth_db = dimensions_db.split(",")[1].split(":")[1].replace('"', '')
                logger.info(f"Value of breadth obtained after inner join is : {breadth_db}")
                height_db = dimensions_db.split(",")[2].split(":")[1].replace('"', '')
                logger.info(f"Value of height obtained after inner join is : {height_db}")
                pickup_add_db = result['pick_up_address'].values[0]
                logger.info(f"Value of pickup address obtained after inner join is : {pickup_add_db}")
                weight_db = result['weight'].values[0]
                logger.info(f"Value of weight obtained after inner join is : {weight_db}")
                order_customer_name_db = result['order_customer_name'].values[0]
                logger.info(f"Value of customer name obtained after inner join is : {order_customer_name_db}")
                order_customer_mobile_no_db = result['Order_cus_mobile_no'].values[0]
                logger.info(f"Value of customer mobile no obtained after inner join is : {order_customer_mobile_no_db}")
                shipment_status_db = result['shipment_status'].values[0]
                logger.info(f"Value of shipment status obtained after inner join is : {shipment_status_db}")
                shipment_id_db = result['shipment_id'].values[0]
                logger.info(f"Value of shipment id obtained after inner join is : {shipment_id_db}")
                status_db = result['status'].values[0]
                logger.info(f"Value of status obtained after inner join is : {status_db}")

                actual_db_values = {
                    "order_version": merchant_order_version_db,
                    "customer_version": customer_version_db,
                    "customer_name": customer_name_db,
                    "customer_mobile_no": customer_mobile_db,
                    "order_id": order_id_db,
                    "ref_id": ref_id_db,
                    "notes": notes_db,
                    "amt": amt_db,
                    "order_status": order_status_db,
                    "length": str(f'{float(length_db):.1f}'),
                    "breadth": str(f'{float(breadth_db):.1f}'),
                    "height": str(f'{float(height_db):.1f}'),
                    "pickup_address": pickup_add_db,
                    "weight": str(f'{float(weight_db):.2f}'),
                    "order_customer_name": order_customer_name_db,
                    "order_customer_mobile_no": order_customer_mobile_no_db,
                    "shipment_status": shipment_status_db,
                    "shipment_id": shipment_id_db,
                    "status": status_db
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
def test_common_600_602_004():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Create_order_Add_Pickup_location_and_create_order_logistics_new_order
    Sub Feature Description: Create_order, Add_Pickup_location and create_order_logistics
    TC naming code description: 600: EzeGro functions, 602: Logistics, 004: TC004
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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            customer_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated customer email is :{customer_email}")
            customer_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

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
                        "pincode": customer_pincode,
                        "state": customer_state,
                        "city": customer_city,
                        "country": customer_country,
                        "addressLine1": customer_address_line_1,
                        "addressLine2": customer_address_line_2
                    }
                },
                "customerVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version_db = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version_db}")
            merchant_address_version_db = result['address_version'].values[0]
            logger.info(f"Value of address_version obtained from merchant table : {merchant_address_version_db}")
            merchant_order_version_db = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table : {merchant_order_version_db}")

            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100,1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1,5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pick up pincode is :{pickup_pincode}")
            pickup_name = "Micheal "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated name for pick up is :{pickup_name}")
            pickup_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_1 is :{pickup_address_line_1}")
            pickup_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_2 is :{pickup_address_line_2}")
            pickup_state = "Karnataka"
            logger.debug(f"Value of pick up state is :{pickup_state}")
            pickup_country = "India"
            logger.debug(f"Value of pick up country is :{pickup_country}")
            pickup_city = "Benguluru"
            logger.debug(f"Value of pick up city is :{pickup_city}")
            pickup_is_default = "true"
            logger.debug(f"Value of pick up is_default is :{pickup_is_default}")
            pickup_address_name = "HOME"
            logger.debug(f"Value of pick up address name  is :{pickup_address_name}")

            #add pick location
            api_details = DBProcessor.get_api_details('add_pick_location', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "addressVersion": merchant_address_version_db,
                "address": {
                    "email": pickup_email,
                    "mobileNumber": pickup_mobile_no,
                    "pincode": pickup_pincode,
                    "name": pickup_name,
                    "addressLine1": pickup_address_line_1,
                    "addressLine2": pickup_address_line_2,
                    "state": pickup_state,
                    "country": pickup_country,
                    "city": pickup_city,
                    "isDefault": pickup_is_default,
                    "addressName": pickup_address_name
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for add pickup location {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for add pickup location is: {response}")
            pickup_add = list(response['addresses'])
            logger.info(f"Converting addresses to list format from from add pickup location is : {pickup_add}")
            pickup_address = pickup_add[-1]['pickUpAddress']
            logger.info(f"Value of pickUpAddress obtained from add pickup location is : {pickup_address}")

            weight = random.uniform(0.25, 0.95)
            length = random.randint(1, 2)
            breadth = random.randint(2, 3)
            height = random.randint(1, 3)
            ref_id = "EZE"+''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order logistics endpoint : {ref_id}")
            sku = "EZ" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            notes = "This Product is Good!!!!"

            api_details = DBProcessor.get_api_details('create_order_logistics', request_body={
                    "user": validate_otp_user,
                    "mobileNumber": mobile_number,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type,
                    "customerVersion": merchant_customer_version_db,
                    "orderVersion": merchant_order_version_db,
                    "order": {
                        "customer": {
                            "name": customer_name,
                            "email": customer_email,
                            "mobileNumber": customer_mobile_no,
                            "address": {
                                "state": customer_state,
                                "country": customer_country,
                                "addressLine1": customer_address_line_1,
                                "addressLine2": customer_address_line_2,
                                "pincode": customer_pincode,
                                "city": customer_city
                            }
                        },
                        "products": [
                            {
                                "name": prod_name,
                                "price": price,
                                "sku" : sku,
                                "quantity": quantity
                            }
                        ],
                        "notes": notes,
                        "refId": ref_id,
                        "packageDetails": {
                            "weight": weight,
                            "dimension": {
                                "length": length,
                                "breadth": breadth,
                                "height": height
                            }
                        },
                        "pickUpAddress": pickup_address
                    }

            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order logistics {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order logistics is: {response}")
            create_logistics_customer_version = response['customerVersion']
            logger.info(f"Value of customer version obtained from create order logistics : {create_logistics_customer_version}")
            create_logistics_order_version = response['orderVersion']
            logger.info(f"Value of order version obtained from create order logistics : {create_logistics_order_version}")
            create_logistics_orders = list(response['orders'])
            logger.info(f"Converting orders to list format from create order logistics : {create_logistics_orders}")
            create_logistics_order_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of id obtained from create order logistics : {create_logistics_order_id}")
            create_logistics_name = create_logistics_orders[-1]['customer']['name']
            logger.info(f"Value of name obtained from create order logistics : {create_logistics_name}")
            create_logistics_email = create_logistics_orders[-1]['customer']['email']
            logger.info(f"Value of email obtained from create order logistics : {create_logistics_email}")
            create_logistics_mobile_no = create_logistics_orders[-1]['customer']['mobileNumber']
            logger.info(f"Value of mobileNumber obtained from create order logistics : {create_logistics_mobile_no}")
            create_logistics_ref_id = create_logistics_orders[-1]['refId']
            logger.info(f"Value of refId obtained from create order logistics : {create_logistics_ref_id}")
            create_logistics_amt = create_logistics_orders[-1]['amount']
            logger.info(f"Value of amount obtained from create order logistics : {create_logistics_amt}")
            create_logistics_pickup_addr = create_logistics_orders[-1]['pickUpAddress']
            logger.info(f"Value of pickup address obtained from create order logistics : {create_logistics_pickup_addr}")
            create_logistics_weight = create_logistics_orders[-1]['packageDetails']['weight']
            logger.info(f"Value of weight address obtained from create order logistics : {create_logistics_weight}")
            create_logistics_length = create_logistics_orders[-1]['packageDetails']['dimension']['length']
            logger.info(f"Value of length address obtained from create order logistics : {create_logistics_length}")
            create_logistics_breadth = create_logistics_orders[-1]['packageDetails']['dimension']['breadth']
            logger.info(f"Value of breadth address obtained from create order logistics : {create_logistics_breadth}")
            create_logistics_height = create_logistics_orders[-1]['packageDetails']['dimension']['height']
            logger.info(f"Value of height address obtained from create order logistics : {create_logistics_height}")
            create_logistics_status = create_logistics_orders[-1]['status']
            logger.info(f"Value of status obtained from create order logistics : {create_logistics_height}")
            create_logistics_notes = create_logistics_orders[-1]['notes']
            logger.info(f"Value of notes obtained from create order logistics : {create_logistics_notes}")

            query = "select * from address where mobile_number ='" + str(pickup_mobile_no) + "';"
            logger.debug(f"Query to fetch data from address table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of address table : {result}")
            address_id_db = result['id'].values[-1]
            logger.debug(f"Value of id from address table :{address_id_db}")

            query = "select * from order_details where id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from order_details table : {order_details_id_db}")

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table after create order logistics : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table after create order logistics : {result}")
            create_order_logistics_order_version_db = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table after create order logistics : {create_order_logistics_order_version_db}")

            query = "select * from shipment_details where order_id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from shipment details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for shipment details table : {result}")
            shipment_id = result['shipment_id'].values[0]
            logger.info(f"Value of shipment_id obtained from shipment details : {shipment_id}")

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
                    "id": order_details_id_db,
                    "notes": notes,
                    "pick_up_address": address_id_db,
                    "customer_version": merchant_customer_version_db,
                    "create_logistics_order_version": create_order_logistics_order_version_db,
                    "create_logistics_name": customer_name,
                    "create_logistics_email": customer_email,
                    "create_logistics_mobile_no": customer_mobile_no,
                    "create_logistics_ref_id": ref_id,
                    "create_logistics_amount": price * quantity,
                    "create_logistics_pick_up_add": pickup_address,
                    "create_logistics_weight": str(f'{float(weight):.2f}'),
                    "create_logistics_length": str(f'{float(length):.1f}'),
                    "create_logistics_breadth": str(f'{float(breadth):.1f}'),
                    "create_logistics_height": str(f'{float(height):.1f}'),
                    "create_logistics_status" :"NEW"
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "id": create_logistics_order_id,
                    "notes": create_logistics_notes,
                    "pick_up_address": pickup_address,
                    "customer_version": create_logistics_customer_version,
                    "create_logistics_order_version": create_logistics_order_version,
                    "create_logistics_name": create_logistics_name,
                    "create_logistics_email": create_logistics_email,
                    "create_logistics_mobile_no": create_logistics_mobile_no,
                    "create_logistics_ref_id": create_logistics_ref_id,
                    "create_logistics_amount": create_logistics_amt,
                    "create_logistics_pick_up_add": create_logistics_pickup_addr,
                    "create_logistics_weight": str(f'{float(create_logistics_weight):.2f}'),
                    "create_logistics_length": str(f'{float(create_logistics_length):.1f}'),
                    "create_logistics_breadth": str(f'{float(create_logistics_breadth):.1f}'),
                    "create_logistics_height": str(f'{float(create_logistics_height):.1f}'),
                    "create_logistics_status": create_logistics_status
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
                    "order_version": merchant_order_version_db,
                    "customer_version": merchant_customer_version_db,
                    "customer_name": customer_name,
                    "customer_mobile_no": customer_mobile_no,
                    "order_id": create_logistics_order_id,
                    "ref_id": ref_id,
                    "notes": create_logistics_notes,
                    "amt": price*quantity,
                    "order_status": 'ACTIVE',
                    "length": str(f'{float(length):.1f}'),
                    "breadth": str(f'{float(breadth):.1f}'),
                    "height": str(f'{float(height):.1f}'),
                    "pickup_address": pickup_address,
                    "weight": str(f'{float(weight):.2f}'),
                    "order_customer_name": customer_name,
                    "order_customer_mobile_no": customer_mobile_no,
                    "shipment_status": "PENDING",
                    "shipment_id": shipment_id,
                    "status": "NEW"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.merchant_id, M.store_name,M.order_version,M.customer_version, OD.customer_id, C.name AS Customer_name, " \
                        "C.mobile_number AS CUST_MOB, OD.id AS ORDER_ID, OD.ref_id, OD.notes, OD.amount, OD.status AS order_status,OD.dimensions, " \
                        "OD.pick_up_address, OD.weight, OC.name AS order_customer_name, OC.mobile_number AS Order_cus_mobile_no, " \
                        "SD.shipment_status,SD.shipment_id,SD.status from merchant AS M INNER JOIN order_details AS OD ON M.id = OD.merchant_id " \
                        "INNER JOIN customer as C ON OD.customer_id = C.id INNER JOIN order_customer AS OC ON OD.order_customer_id = OC.id " \
                        "INNER JOIN shipment_details AS SD ON OD.id = SD.order_id where OD.id = '"+str(create_logistics_order_id)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                order_version_db = result['order_version'].values[0]
                logger.info(f"Value of order version obtained after inner join is : {order_version_db}")
                customer_version_db = result['customer_version'].values[0]
                logger.info(f"Value of customer version obtained after inner join is : {customer_version_db}")
                customer_name_db = result['Customer_name'].values[0]
                logger.info(f"Value of customer name obtained after inner join is : {customer_name_db}")
                customer_mobile_db = result['CUST_MOB'].values[0]
                logger.info(f"Value of customer mobile number obtained after inner join is : {customer_mobile_db}")
                order_id_db = result['ORDER_ID'].values[0]
                logger.info(f"Value of customer order id obtained after inner join is : {order_id_db}")
                ref_id_db = result['ref_id'].values[0]
                logger.info(f"Value of customer ref id obtained after inner join is : {ref_id_db}")
                notes_db = result['notes'].values[0]
                logger.info(f"Value of customer notes obtained after inner join is : {notes_db}")
                amt_db = result['amount'].values[0]
                logger.info(f"Value of amount obtained after inner join is : {amt_db}")
                order_status_db = result['order_status'].values[0]
                logger.info(f"Value of order_status obtained after inner join is : {order_status_db}")
                dimensions_db = result['dimensions'].values[0].replace('{', '').replace('}', '')
                logger.info(f"Value of dimensions obtained after inner join is : {dimensions_db}")
                length_db = dimensions_db.split(",")[0].split(":")[1].replace('"', '')
                logger.info(f"Value of length obtained after inner join is : {length_db}")
                breadth_db = dimensions_db.split(",")[1].split(":")[1].replace('"', '')
                logger.info(f"Value of breadth obtained after inner join is : {breadth_db}")
                height_db = dimensions_db.split(",")[2].split(":")[1].replace('"', '')
                logger.info(f"Value of height obtained after inner join is : {height_db}")
                pickup_add_db = result['pick_up_address'].values[0]
                logger.info(f"Value of pickup address obtained after inner join is : {pickup_add_db}")
                weight_db = result['weight'].values[0]
                logger.info(f"Value of weight obtained after inner join is : {weight_db}")
                order_customer_name_db = result['order_customer_name'].values[0]
                logger.info(f"Value of customer name obtained after inner join is : {order_customer_name_db}")
                order_customer_mobile_no_db = result['Order_cus_mobile_no'].values[0]
                logger.info(f"Value of customer mobile no obtained after inner join is : {order_customer_mobile_no_db}")
                shipment_status_db = result['shipment_status'].values[0]
                logger.info(f"Value of shipment status obtained after inner join is : {shipment_status_db}")
                shipment_id_db = result['shipment_id'].values[0]
                logger.info(f"Value of shipment id obtained after inner join is : {shipment_id_db}")
                status_db = result['status'].values[0]
                logger.info(f"Value of status obtained after inner join is : {status_db}")

                actual_db_values = {
                    "order_version": merchant_order_version_db,
                    "customer_version": customer_version_db,
                    "customer_name": customer_name_db,
                    "customer_mobile_no": customer_mobile_db,
                    "order_id": order_id_db,
                    "ref_id": ref_id_db,
                    "notes": notes_db,
                    "amt": amt_db,
                    "order_status": order_status_db,
                    "length": str(f'{float(length_db):.1f}'),
                    "breadth": str(f'{float(breadth_db):.1f}'),
                    "height": str(f'{float(height_db):.1f}'),
                    "pickup_address": pickup_add_db,
                    "weight": str(f'{float(weight_db):.2f}'),
                    "order_customer_name": order_customer_name_db,
                    "order_customer_mobile_no": order_customer_mobile_no_db,
                    "shipment_status": shipment_status_db,
                    "shipment_id": shipment_id_db,
                    "status": status_db
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
def test_common_600_602_005():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Create_Order_Logistics_Product_Validation
    Sub Feature Description: API: Create_Order_Logistics_Product_Validation
    TC naming code description: 600: EzeGro functions, 602: Logistics, 005: TC005
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
        delete_customer_mobile_no = "666666666%"
        EzeGro_processor.delete_existing_ezegro_customer(delete_customer_mobile_no)

        # deleting add pickup address mobile number
        delete_pickup_address_mobile_no = "777777777%"
        EzeGro_processor.delete_existing_pickup_address(delete_pickup_address_mobile_no)

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
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            customer_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated customer email is :{customer_email}")
            customer_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

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
                        "pincode": customer_pincode,
                        "state": customer_state,
                        "city": customer_city,
                        "country": customer_country,
                        "addressLine1": customer_address_line_1,
                        "addressLine2": customer_address_line_2
                    }
                },
                "customerVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pick up pincode is :{pickup_pincode}")
            pickup_name = "Micheal "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated name for pick up is :{pickup_name}")
            pickup_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_1 is :{pickup_address_line_1}")
            pickup_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated pick up address_line_2 is :{pickup_address_line_2}")
            pickup_state = "Karnataka"
            logger.debug(f"Value of pick up state is :{pickup_state}")
            pickup_country = "India"
            logger.debug(f"Value of pick up country is :{pickup_country}")
            pickup_city = "Benguluru"
            logger.debug(f"Value of pick up city is :{pickup_city}")
            pickup_is_default = "true"
            logger.debug(f"Value of pick up is_default is :{pickup_is_default}")
            pickup_address_name = "HOME"
            logger.debug(f"Value of pick up address name  is :{pickup_address_name}")

            #add pick location
            api_details = DBProcessor.get_api_details('add_pick_location', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "addressVersion": "0",
                "address": {
                    "email": pickup_email,
                    "mobileNumber": pickup_mobile_no,
                    "pincode": pickup_pincode,
                    "name": pickup_name,
                    "addressLine1": pickup_address_line_1,
                    "addressLine2": pickup_address_line_2,
                    "state": pickup_state,
                    "country": pickup_country,
                    "city": pickup_city,
                    "isDefault": pickup_is_default,
                    "addressName": pickup_address_name
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for add pickup location {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for add pickup location is: {response}")
            pickup_add = list(response['addresses'])
            logger.info(f"Converting addresses to list format from from add pickup location is : {pickup_add}")
            pickup_address = pickup_add[-1]['pickUpAddress']
            logger.info(f"Value of pickUpAddress obtained from add pickup location is : {pickup_address}")

            weight = round(random.uniform(0.25,1.0),2)
            logger.info(f"Randomly Generated weight is : {weight}")
            length = random.randint(1,2)
            logger.info(f"Randomly Generated length is : {length}")
            breadth = random.randint(2,4)
            logger.info(f"Randomly Generated breadth is : {breadth}")
            height = random.randint(4,6)
            logger.info(f"Randomly Generated height is : {height}")
            ref_id = "EZE"+''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order logistics endpoint : {ref_id}")
            create_order_logistics_notes = "This Product is Good and Comfortable"
            sku = "EZv" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated sku for create order endpoint : {sku}")


            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100,1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1,5)
            logger.info(f"Randomly generated quantity is : {quantity}")
            randomly_generated_create_order_ref_id = "EZE" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order endpoint : {randomly_generated_create_order_ref_id}")

            #create order logistics for existing order id
            api_details = DBProcessor.get_api_details('create_order_logistics', request_body={
                    "user": validate_otp_user,
                    "mobileNumber": mobile_number,
                    "deviceIdentifier": device_identifier,
                    "deviceIdentifierType": device_identifier_type,
                    "customerVersion": "0",
                    "orderVersion": "0",
                    "order": {
                        "customer": {
                            "name": customer_name,
                            "email": customer_email,
                            "mobileNumber": customer_mobile_no,
                            "address": {
                                "state": customer_state,
                                "country": customer_country,
                                "addressLine1": customer_address_line_1,
                                "addressLine2": customer_address_line_2,
                                "pincode": customer_pincode,
                                "city": customer_city
                            }
                        },
                        "products": [
                            {
                                "name": prod_name,
                                "price": price,
                                "sku": sku,
                                "quantity": quantity
                            }
                        ],
                        "notes": create_order_logistics_notes,
                        "refId": ref_id,
                        "packageDetails": {
                            "weight": weight,
                            "dimension": {
                                "length": length,
                                "breadth": breadth,
                                "height": height
                            }
                        },
                        "pickUpAddress": pickup_address
                    }

            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create order logistics {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order logistics is: {response}")
            create_logistics_orders = list(response['orders'])
            logger.info(f"Converting orders to list format from create order logistics : {create_logistics_orders}")
            create_logistics_order_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of id obtained from create order logistics : {create_logistics_order_id}")
            create_logistics_product = list(create_logistics_orders[-1]['products'])
            logger.info(f"Converting products to list format from create order logistics : {create_logistics_product}")
            create_logistics_product_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of product id obtained from create order logistics : {create_logistics_product_id}")
            create_logistics_product_name = create_logistics_product[-1]['name']
            logger.info(f"Value of product name obtained from create order logistics : {create_logistics_product_name}")
            create_logistics_product_price = create_logistics_product[-1]['price']
            logger.info(f"Value of product price obtained from create order logistics : {create_logistics_product_price}")
            create_logistics_product_sku = create_logistics_product[-1]['sku']
            logger.info(f"Value of product sku obtained from create order logistics : {create_logistics_product_sku}")
            create_logistics_product_amt = create_logistics_product[-1]['amount']
            logger.info(f"Value of product amount obtained from create order logistics : {create_logistics_product_amt}")
            create_logistics_product_quantity = create_logistics_product[-1]['quantity']
            logger.info(f"Value of product quantity obtained from create order logistics : {create_logistics_product_quantity}")

            query = "select * from order_details where id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from order_details table : {order_details_id_db}")

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
                    "id": create_logistics_order_id,
                    "name": prod_name,
                    "price": price,
                    "sku": sku,
                    "amt": price*quantity,
                    "quantity": quantity
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "id": order_details_id_db,
                    "name": create_logistics_product_name,
                    "price": create_logistics_product_price,
                    "sku": create_logistics_product_sku,
                    "amt": create_logistics_product_amt,
                    "quantity": create_logistics_product_quantity
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
                    "id": create_logistics_order_id,
                    "name": prod_name,
                    "price": price,
                    "sku": sku,
                    "hsn": None,
                    "quantity": quantity,
                    "amt": price*quantity,
                    "status": 'ACTIVE'
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = " select OD.id AS ORDERID, OD.status AS order_status,  OI.id AS Order_Item_ID, OI.order_product_id, OP.name, OP.price, OP.sku," \
                        " OP.hsn, OI.quantity, OI.amount, OI.status from order_details AS OD INNER JOIN order_items AS OI ON OD.id = OI.order_id " \
                        "INNER JOIN order_product AS OP ON OI.order_product_id = OP.id where OD.id = '"+str(create_logistics_order_id)+"' and OD.status = 'ACTIVE' AND OI.status ='ACTIVE';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                order_id_db = result['ORDERID'].values[0]
                logger.info(f"Value of customer order id obtained after inner join is : {order_id_db}")
                name_db = result['name'].values[0]
                logger.info(f"Value of customer name id obtained after inner join is : {name_db}")
                price_db = result['price'].values[0]
                logger.info(f"Value of price obtained after inner join is : {price_db}")
                sku_db = result['sku'].values[0]
                logger.info(f"Value of sku obtained after inner join is : {sku_db}")
                hsn_db = result['hsn'].values[0]
                logger.info(f"Value of hsn obtained after inner join is : {hsn_db}")
                quantity_db = result['quantity'].values[0]
                logger.info(f"Value of quantity obtained after inner join is : {quantity_db}")
                amt_db = result['amount'].values[0]
                logger.info(f"Value of amount obtained after inner join is : {amt_db}")
                status_db = result['status'].values[0]
                logger.info(f"Value of status obtained after inner join is : {amt_db}")

                actual_db_values = {
                    "id": order_id_db,
                    "name": name_db,
                    "price": price_db,
                    "sku": sku_db,
                    "hsn": hsn_db,
                    "quantity": quantity_db,
                    "amt": amt_db,
                    "status": status_db
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
























