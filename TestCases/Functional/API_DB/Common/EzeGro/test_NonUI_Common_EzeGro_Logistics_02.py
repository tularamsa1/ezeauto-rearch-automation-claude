import string
from datetime import datetime
from datetime import timedelta
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
def test_common_600_602_006():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Create_Order_Logistics_Address_Validation
    Sub Feature Description: Create_Order_Logistics_Address_Validation
    TC naming code description: 600: EzeGro functions, 602: Logistics, 006: TC006
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
            randomly_generated_create_order_ref_id = "EZE" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            logger.info(f"Randomly Generated ref id for create order endpoint : {randomly_generated_create_order_ref_id}")

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
            create_logistics_orders = list(response['orders'])
            logger.info(f"Converting orders to list format from create order logistics : {create_logistics_orders}")
            create_logistics_order_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of id obtained from create order logistics : {create_logistics_order_id}")
            create_logistics_email = create_logistics_orders[-1]['customer']['email']
            logger.info(f"Value of email obtained from create order logistics : {create_logistics_email}")
            create_logistics_state = create_logistics_orders[-1]['customer']['address']['state']
            logger.info(f"Value of state obtained from create order logistics : {create_logistics_state}")
            create_logistics_country = create_logistics_orders[-1]['customer']['address']['country']
            logger.info(f"Value of country obtained from create order logistics : {create_logistics_country}")
            create_logistics_address_line_1 = create_logistics_orders[-1]['customer']['address']['addressLine1']
            logger.info(f"Value of addressLine1 obtained from create order logistics : {create_logistics_address_line_1}")
            create_logistics_address_line_2 = create_logistics_orders[-1]['customer']['address']['addressLine2']
            logger.info(f"Value of addressLine2 obtained from create order logistics : {create_logistics_address_line_2}")
            create_logistics_pincode = create_logistics_orders[-1]['customer']['address']['pincode']
            logger.info(f"Value of pincode obtained from create order logistics : {create_logistics_pincode}")
            create_logistics_city = create_logistics_orders[-1]['customer']['address']['city']
            logger.info(f"Value of city obtained from create order logistics : {create_logistics_city}")

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
                    "email": customer_email,
                    "state": customer_state,
                    "country": customer_country,
                    "address_line_1": customer_address_line_1,
                    "address_line_2": customer_address_line_2,
                    "pincode": str(customer_pincode),
                    "city": customer_city
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "email": create_logistics_email,
                    "state": create_logistics_state,
                    "country": create_logistics_country,
                    "address_line_1": create_logistics_address_line_1,
                    "address_line_2": create_logistics_address_line_2,
                    "pincode": create_logistics_pincode,
                    "city": create_logistics_city
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
                    "address_line_1": customer_address_line_1,
                    "address_line_2": customer_address_line_2,
                    "country": customer_country,
                    "pincode": str(customer_pincode),
                    "state": customer_state,
                    "city": customer_city,
                    "email": customer_email,
                    "entity": 'CUSTOMER'
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.order_customer_id, OA.address_line_1, OA.address_line_2, OA.country, OA.pincode, OA.state,OA.city,OC.email, OA.entity from order_details as OD " \
                        "INNER JOIN order_address AS OA ON OD.order_customer_id = OA.entity_id INNER JOIN order_customer AS OC ON OD.order_customer_id =OC.id " \
                        "where OD.id = '" + str(create_logistics_order_id) + "';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                address_line_1_db = result['address_line_1'].values[0]
                logger.info(f"Value of address_line_1 obtained after inner join is : {address_line_1_db}")
                address_line_2_db = result['address_line_2'].values[0]
                logger.info(f"Value of address_line_2 obtained after inner join is : {address_line_2_db}")
                country_db = result['country'].values[0]
                logger.info(f"Value of country obtained after inner join is : {country_db}")
                pincode_db = result['pincode'].values[0]
                logger.info(f"Value of pincode obtained after inner join is : {pincode_db}")
                state_db = result['state'].values[0]
                logger.info(f"Value of state obtained after inner join is : {state_db}")
                city_db = result['city'].values[0]
                logger.info(f"Value of city obtained after inner join is : {city_db}")
                email_db = result['email'].values[0]
                logger.info(f"Value of email obtained after inner join is : {email_db}")
                entity_db = result['entity'].values[0]
                logger.info(f"Value of entity obtained after inner join is : {entity_db}")


                actual_db_values = {
                    "address_line_1": address_line_1_db,
                    "address_line_2": address_line_2_db,
                    "country": country_db,
                    "pincode": pincode_db,
                    "state": state_db,
                    "city": city_db,
                    "email": email_db,
                    "entity": entity_db
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
def test_common_600_602_007():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_validate_recharge_wallet
    Sub Feature Description: To validate the success flow of recharge Wallet
    TC naming code description: 600: EzeGro functions, 602: Logistics, 007: TC007
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

            # generate the otp
            api_details = DBProcessor.get_api_details('generate_otp', request_body={
                "mobileNumber": mobile_number,
                "applicationKey": application_Key,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type
            })

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate otp is: {response}")
            generate_otp_success = response['success']
            logger.info(f"Value of success obtained from generate otp : {generate_otp_success}")
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
            validate_otp_success = response['success']
            logger.info(f"Value of success obtained from validate otp : {validate_otp_success}")
            validate_otp_user = response['user']
            logger.info(f"Value of user obtained from validate otp : {validate_otp_user}")
            validate_auth_token = str(response['authenticationToken'])
            logger.info(f"Value of authenticationToken obtained from validate otp : {validate_auth_token}")

            amt_to_recharge = random.randint(50,500)
            api_details = DBProcessor.get_api_details('recharge_wallet', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "amount":amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for recharge_wallet is: {response}")
            recharge_wallet_success = response['success']
            logger.info(f"Value of success obtained from recharge_wallet : {recharge_wallet_success}")
            external_ref_no= response['externalRefNumber']
            logger.info(f"Value of external ref no obtained from recharge_wallet : {external_ref_no}")
            pay_link = response['paymentLink']
            logger.info(f"Value of payment link obtained from recharge_wallet : {pay_link}")
            mobile_no = response['mobileNumber']
            logger.info(f"Value of Mobile Number obtained from recharge_wallet : {pay_link}")


            api_details = DBProcessor.get_api_details('cybersource_success_callback', request_body={
                "success": True,
                "paymentMode": "CNP",
                "externalRefNumber": external_ref_no,
                "status": "AUTHORIZED",
                "amount":amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Basic RVpFR1JPXzEyMzQ1NjpFemV0YXBAMTIzNDU2',
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for cnp callback from cybersource {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Status Code obtained cybersource callback api is: {response.status_code}")

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
                    "callback_status_code" : 200,
                    "mobile_no" : mobile_number
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": recharge_wallet_success,
                    "callback_status_code" : response.status_code,
                    "mobile_no" : mobile_no
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
                    "payment_mode" : "CNP",
                    "payment_status" : "SUCCESS",
                    "transfer_mode": "ADD_FUND",
                    "agent_id" : mobile_number,
                    "txn_amt": amt_to_recharge,
                    "external_ref": external_ref_no,
                    "txn_status": "SUCCESS" }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select P.payment_mode,P.status AS payment_status, P.auth_code, P.payment_card_bin, P.payment_gateway, WT.transfer_mode, WT.agent_id , WT.balance AS wallet_balance, WT.amount AS txn_amount, WT.error_code, WT.error_message, WT.external_ref, WT.status AS transation_status FROM payment AS P INNER JOIN wallet_txn as WT ON P.external_ref= WT.external_ref WHERE P.mobile_number ='" + mobile_number +"' AND WT.external_ref ='" +external_ref_no + "';"
                logger.info(f"Query to fetch from payment and wallet_txn tables: {query}")

                result = DBProcessor.getValueFromDB(query, 'ezestore')
                logger.info(f"Query result from payment and wallet_txn table : {result}")
                pay_mode_db = result['payment_mode'].values[0]
                logger.info(f"Value of payment_mode obtained after inner join is : {pay_mode_db}")
                pay_status_db = result['payment_status'].values[0]
                logger.info(f"Value of payment_status obtained after inner join is : {pay_status_db}")
                transfer_mode_db = result['transfer_mode'].values[0]
                logger.info(f"Value of transfer_mode obtained after inner join is : {transfer_mode_db}")
                agent_id_db = result['agent_id'].values[0]
                logger.info(f"Value of agent_id obtained after inner join is : {agent_id_db}")
                txn_amount_db = result['txn_amount'].values[0]
                logger.info(f"Value of txn_amount obtained after inner join is : {txn_amount_db}")
                external_ref_db = result['external_ref'].values[0]
                logger.info(f"Value of external_ref obtained after inner join is : {external_ref_db}")
                txn_status_db = result['transation_status'].values[0]
                logger.info(f"Value of transation_status obtained after inner join is : {txn_status_db}")

                actual_db_values = {
                    "payment_mode": pay_mode_db,
                    "payment_status": pay_status_db,
                    "transfer_mode":transfer_mode_db,
                    "agent_id": agent_id_db,
                    "txn_amt": txn_amount_db,
                    "external_ref": external_ref_db,
                    "txn_status": txn_status_db
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
def test_common_600_602_008():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Get_Courier_Service
    Sub Feature Description: API : Get_Courier_Service weight greather than 5 kg
    TC naming code description: 600: EzeGro functions, 602: Logistics, 008: TC008
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

            weight = round(random.uniform(5.0, 10.0), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            pickup_postal_code = random.randint(560001,560055)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            delivery_postal_code = random.randint(560056,560112)
            logger.info(f"Value of delivery postal code generated is : {delivery_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": delivery_postal_code,
                "weight": weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_success = response['success']
            logger.info(f"Value of success obtained from get courier service is : {get_courier_service_success}")
            get_courier_service_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobile number obtained from get courier service is : {get_courier_service_mobile_no}")
            get_courier_service_pickup_postal_code = response['pickUpPostalCode']
            logger.info(f"Value of pickUpPostalCode obtained from get courier service is : {get_courier_service_pickup_postal_code}")
            get_courier_service_delivery_postal_code = response['deliveryPostalCode']
            logger.info(f"Value of deliveryPostalCode obtained from get courier service is : {get_courier_service_delivery_postal_code}")
            get_courier_service_weight = response['weight']
            logger.info(f"Value of weight obtained from get courier service is : {get_courier_service_weight}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")

            if len(get_courier_service_available_courier_companies) > 0:
                get_courier_service_available_courier_companies = True
            else:
                get_courier_service_available_courier_companies = False

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
                    "mobile_no": mobile_number,
                    "pickup_postal_code": str(pickup_postal_code),
                    "pickup_delivery_postal_code": str(delivery_postal_code),
                    "weight": weight,
                    "available_courier_companies": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": get_courier_service_success,
                    "mobile_no": get_courier_service_mobile_no,
                    "pickup_postal_code": get_courier_service_pickup_postal_code,
                    "pickup_delivery_postal_code": get_courier_service_delivery_postal_code,
                    "weight": get_courier_service_weight,
                    "available_courier_companies": get_courier_service_available_courier_companies
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_600_602_009():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Get_Courier_Service
    Sub Feature Description: API : Get_Courier_Service weight less than 5 kg
    TC naming code description: 600: EzeGro functions, 602: Logistics, 009: TC009
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

            weight = round(random.uniform(0.25, 4.5), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            pickup_postal_code = random.randint(400001,400030)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            delivery_postal_code = random.randint(560056,560112)
            logger.info(f"Value of delivery postal code generated is : {delivery_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": delivery_postal_code,
                "weight": weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_success = response['success']
            logger.info(f"Value of success obtained from get courier service is : {get_courier_service_success}")
            get_courier_service_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobile number obtained from get courier service is : {get_courier_service_mobile_no}")
            get_courier_service_pickup_postal_code = response['pickUpPostalCode']
            logger.info(f"Value of pickUpPostalCode obtained from get courier service is : {get_courier_service_pickup_postal_code}")
            get_courier_service_delivery_postal_code = response['deliveryPostalCode']
            logger.info(f"Value of deliveryPostalCode obtained from get courier service is : {get_courier_service_delivery_postal_code}")
            get_courier_service_weight = response['weight']
            logger.info(f"Value of weight obtained from get courier service is : {get_courier_service_weight}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")

            if len(get_courier_service_available_courier_companies) > 0:
                get_courier_service_available_courier_companies = True
            else:
                get_courier_service_available_courier_companies = False

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
                    "mobile_no": mobile_number,
                    "pickup_postal_code": str(pickup_postal_code),
                    "pickup_delivery_postal_code": str(delivery_postal_code),
                    "weight": weight,
                    "available_courier_companies": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": get_courier_service_success,
                    "mobile_no": get_courier_service_mobile_no,
                    "pickup_postal_code": get_courier_service_pickup_postal_code,
                    "pickup_delivery_postal_code": get_courier_service_delivery_postal_code,
                    "weight": get_courier_service_weight,
                    "available_courier_companies": get_courier_service_available_courier_companies
                }

                logger.debug(f"actual_api_values: {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation------------------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_602_010():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_Get_Courier_Service
    Sub Feature Description: API : Get_Courier_Service weight less than or equal 5 kg and pickup pincode is equal to bangalore
    TC naming code description: 600: EzeGro functions, 602: Logistics, 010: TC010
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

            weight = round(random.uniform(0.25, 5.0), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            pickup_postal_code = random.randint(560001, 560055)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            delivery_postal_code = random.randint(560056, 560112)
            logger.info(f"Value of delivery postal code generated is : {delivery_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": delivery_postal_code,
                "weight": weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_pickup_postal_code = response['pickUpPostalCode']
            logger.info(f"Value of pickUpPostalCode obtained from get courier service is : {get_courier_service_pickup_postal_code}")
            get_courier_service_weight = response['weight']
            logger.info(f"Value of weight obtained from get courier service is : {get_courier_service_weight}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")
            get_courier_service_courier_name = get_courier_service_available_courier_companies[-1]['courierName']
            logger.info(f"Value of courierName obtained from get courier service is : {get_courier_service_courier_name}")
            get_courier_service_rating = get_courier_service_available_courier_companies[-1]['rating']
            logger.info(f"Value of rating obtained from get courier service is : {get_courier_service_rating}")
            get_courier_service_etd = get_courier_service_available_courier_companies[-1]['etd']
            logger.info(f"Value of etd obtained from get courier service is : {get_courier_service_etd}")
            get_courier_service_rate = get_courier_service_available_courier_companies[-1]['rate']
            logger.info(f"Value of rate obtained from get courier service is : {get_courier_service_rate}")
            get_courier_service_estimate_pickup_date = get_courier_service_available_courier_companies[-1]['estimatedPickupDate']
            logger.info(f"Value of estimatedPickupDate obtained from get courier service is : {get_courier_service_estimate_pickup_date}")

            if len(get_courier_service_available_courier_companies) > 0:
                get_courier_service_available_courier_companies = True
            else:
                get_courier_service_available_courier_companies = False

            query = "select * from jwt_key where user ='" + str(validate_otp_user) + "' AND status = 'ACTIVE';"
            logger.debug(f"Query to fetch data from jwt_key table : {query}")
            result = DBProcessor.getValueFromDB(query, "auth")
            logger.info(f"Query result of jwt_key table : {result}")
            jwt_created_time_db = result['created_time'].values[0]
            logger.info(f"Value of created_time obtained from jwt_key table : {jwt_created_time_db}")

            if weight >= 0.099 and weight <0.5:
                price = 25
            elif weight >= 0.5 and weight <1:
                price = 45
            elif weight >= 1 and weight < 2:
                price = 80
            elif weight >= 2 and weight < 3:
                price = 110
            elif weight >= 3 and weight < 4:
                price = 150
            elif weight >= 4 and weight <= 5:
                price = 180

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
                jwt_created_time = (datetime.strptime(str(jwt_created_time_db), '%Y-%m-%dT%H:%M:%S.%f000'))
                expected_api_values = {
                    "pickup_postal_code": str(pickup_postal_code),
                    "weight": weight,
                    "available_courier_companies": True,
                    "courier_name": 'India Post',
                    "rating": '3.9',
                    "etd": (jwt_created_time + timedelta(days=9)).strftime("%b %d %Y"),
                    "rate": str(price),
                    "estimated_pickup_date": (jwt_created_time + timedelta(days=2)).strftime("%b %d %Y")
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "pickup_postal_code": get_courier_service_pickup_postal_code,
                    "weight": get_courier_service_weight,
                    "available_courier_companies": get_courier_service_available_courier_companies,
                    "courier_name": get_courier_service_courier_name,
                    "rating": get_courier_service_rating,
                    "etd": get_courier_service_etd.replace(',',''),
                    "rate": get_courier_service_rate,
                    "estimated_pickup_date": get_courier_service_estimate_pickup_date.replace(',','')
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
                    "setting_name_pincode": "INDIA_POST_SERVICEABLE_SOURCE_PIN_CODES",
                    "setting_value_pincode":  str([560001,560002,560003,560004,560005,560006,560007,560008,560009,560010,560011,560012,560013,560014,
                                              560015,560016,560017,560018,560019,560020,560021,560022,560023,560024,560025,560026,560027,560028,
                                              560029,560030,560031,560032,560033,560034,560035,560036,560037,560038,560039,560040,560041,560042,
                                              560043,560044,560045,560046,560047,560048,560049,560050,560051,560052,560053,560054,560055,560056,
                                              560057,560058,560059,560060,560061,560062,560063,560064,560065,560066,560067,560068,560069,560070,
                                              560071,560072,560073,560074,560075,560076,560077,560078,560079,560080,560081,560082,560083,560084,
                                              560085,560086,560087,560088,560089,560090,560091,560092,560093,560094,560095,560096,560097,560098,
                                              560099,560100,560101,560102,560103,560104,560105,560106,560107,560108,560109,560110,560111,560112,
                                              560114,560116,560119,560122,560125,560149,560203,560204,562125,562127,562129,562130,562131,562132,
                                              562135,562145,562148,562149,562152,562157,562158,562162,562163,562300,565657,565658,573114,575114,
                                              575550,575810,576653,578661]).replace('[','').replace(']','').replace(' ',''),
                    "setting_name_courier_service_enabled": "INDIA_POST_COURIER_SERVICE_ENABLED",
                    "setting_value_courier_service_enabled": india_post_supported,
                    "setting_name_india_post_courier_rating": "INDIA_POST_COURIER_RATING",
                    "setting_value_india_post_courier_rating": "3.9",
                    "setting_name_india_post_pickup_date": "INDIA_POST_PICKUP_DATE",
                    "setting_value_india_post_pickup_date": '2',
                    "setting_name_estimated_delivery_date": 'INDIA_POST_ESTIMATED_DELIVERY_DATE',
                    "setting_value_estimated_delivery_date": '9',
                    "setting_name_india_post_min_weight": "INDIA_POST_MIN_WEIGHT",
                    "setting_value_india_post_min_weight": '0.1',
                    "setting_name_india_post_max_weight": 'INDIA_POST_MAX_WEIGHT',
                    "setting_value_india_post_max_weight": '5'
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from setting where category ='INDIA_POST';"
                logger.debug(f"Query to fetch data from settings table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result from settings table : {result}")
                setting_name_pincodes = result['setting_name'].values[1]
                logger.info(f"Fetching setting_name value from the settings table : {setting_name_pincodes}")
                setting_value_pincodes = result['setting_value'].values[1]
                logger.info(f"Fetching setting_value value from the settings table : {setting_value_pincodes}")
                setting_name_courier_service_enabled = result['setting_name'].values[2]
                logger.info(f"Fetching setting_name courier service enabled value from the settings table : {setting_name_courier_service_enabled}")
                setting_value_courier_service_enabled = result['setting_value'].values[2]
                logger.info(f"Fetching setting_value courier service value from the settings table : {setting_value_courier_service_enabled}")
                setting_name_india_post_courier_rating = result['setting_name'].values[3]
                logger.info(f"Fetching setting_name india post courier rating value from the settings table : {setting_name_india_post_courier_rating}")
                setting_value_india_post_courier_rating = result['setting_value'].values[3]
                logger.info(f"Fetching setting_value india post courier rating value from the settings table : {setting_value_india_post_courier_rating}")
                setting_name_india_post_pickup_date = result['setting_name'].values[4]
                logger.info(f"Fetching setting_name india post pickup date value from the settings table : {setting_name_india_post_pickup_date}")
                setting_value_india_post_pickup_date = result['setting_value'].values[4]
                logger.info(f"Fetching setting_value india post pickup date value from the settings table : {setting_value_india_post_pickup_date}")
                setting_name_estimated_delivery_date = result['setting_name'].values[5]
                logger.info(f"Fetching setting_name estimated delivery value from the settings table : {setting_name_estimated_delivery_date}")
                setting_value_estimated_delivery_date = result['setting_value'].values[5]
                logger.info(f"Fetching setting_value estimated delivery value from the settings table : {setting_value_estimated_delivery_date}")
                setting_name_india_post_min_weight = result['setting_name'].values[6]
                logger.info(f"Fetching setting_name india post minimum weight from the settings table : {setting_name_india_post_min_weight}")
                setting_value_india_post_min_weight = result['setting_value'].values[6]
                logger.info(f"Fetching setting_value india post minimum weight from the settings table : {setting_value_india_post_min_weight}")
                setting_name_india_post_max_weight = result['setting_name'].values[7]
                logger.info(f"Fetching setting_name india post maximum weight from the settings table : {setting_name_india_post_max_weight}")
                setting_value_india_post_max_weight = result['setting_value'].values[7]
                logger.info(f"Fetching setting_value india post maximum weight from the settings table : {setting_value_india_post_max_weight}")

                actual_db_values = {
                    "setting_name_pincode": setting_name_pincodes,
                    "setting_value_pincode": setting_value_pincodes,
                    "setting_name_courier_service_enabled": setting_name_courier_service_enabled,
                    "setting_value_courier_service_enabled": setting_value_courier_service_enabled,
                    "setting_name_india_post_courier_rating": setting_name_india_post_courier_rating,
                    "setting_value_india_post_courier_rating": setting_value_india_post_courier_rating,
                    "setting_name_india_post_pickup_date": setting_name_india_post_pickup_date,
                    "setting_value_india_post_pickup_date": setting_value_india_post_pickup_date,
                    "setting_name_estimated_delivery_date": setting_name_estimated_delivery_date,
                    "setting_value_estimated_delivery_date": setting_value_estimated_delivery_date,
                    "setting_name_india_post_min_weight": setting_name_india_post_min_weight,
                    "setting_value_india_post_min_weight": setting_value_india_post_min_weight,
                    "setting_name_india_post_max_weight": setting_name_india_post_max_weight,
                    "setting_value_india_post_max_weight": setting_value_india_post_max_weight
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




























