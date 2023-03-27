import sys
import pytest
import string
import random

from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities.execution_log_processor import EzeAutoLogger
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, EzeGro_processor

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_011():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Order_Product_Validation_For_ExistingUser
    Sub Feature Description: API: Validate product for existing customer by hitting create_order api
    TC naming code description: 600: EzeGro functions, 601: Sale, 011: TC011
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

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John" " " + ""''.join(random.choices(string.ascii_lowercase, k=4))
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

            prod_name = "t-shits "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(1000,5000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1, 5)
            logger.info(f"Randomly generated quantity is : {quantity}")

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
            logger.info(f"Response obtained for create merchant is: {response}")
            create_orders = list(response['orders'])
            logger.info(f"Converting orders to list format: {create_orders}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")
            create_order_prod = list(create_orders[-1]['products'])
            logger.info(f"Value of product obtained from create order : {create_order_prod}")
            create_order_name = create_order_prod[-1]['name']
            logger.info(f"Value of name obtained from create order : {create_order_name}")
            create_order_price = create_order_prod[-1]['price']
            logger.info(f"Value of price obtained from create order : {create_order_price}")
            create_order_prod_id = create_order_prod[-1]['id']
            logger.info(f"Value of product id obtained from create order : {create_order_prod_id}")

            query = "select * from product where id ='" + str(create_order_prod_id) + "';"
            logger.debug(f"Query to fetch data from product table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of product table : {result}")
            prod_sku = result['sku'].values[0]
            logger.info(f"Value of sku obtained from product table : {prod_sku}")
            prod_hsn = result['hsn'].values[0]
            logger.info(f"Value of hsn obtained from product table : {prod_hsn}")

            query = "select * from order_details where id ='" + str(create_order_id) + "';"
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
                    "id": create_order_id,
                    "name": prod_name,
                    "price": price
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "id": order_details_id_db,
                    "name": create_order_name,
                    "price": create_order_price
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
                    "order_id":create_order_id,
                    "order_status": 'ACTIVE',
                    "name": prod_name,
                    "price": price,
                    "sku": prod_sku,
                    "hsn": prod_hsn,
                    "quantity": quantity,
                    "amt": price*quantity,
                    "status": 'ACTIVE'
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.id AS ORDERID, OD.status AS order_status, OI.id AS Order_Item_ID, OI.order_product_id, OP.name, OP.price, OP.sku," \
                        " OP.hsn, OI.quantity, OI.amount, OI.status " \
                        "from order_details AS OD INNER JOIN order_items AS OI ON OD.id = OI.order_id INNER JOIN order_product AS OP ON OI.order_product_id = OP.id " \
                        "where OD.id = '"+str(create_order_id)+"' and OD.status = 'ACTIVE' AND OI.status = 'ACTIVE' order by OD.created_time desc limit 1 ;"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                order_id_db = result['ORDERID'].values[0]
                logger.info(f"Value of order_id obtained after inner join is : {order_id_db}")
                order_status_db = result['order_status'].values[0]
                logger.info(f"Value of order_status obtained after inner join is : {order_status_db}")
                name_db = result['name'].values[0]
                logger.info(f"Value of name obtained after inner join is : {name_db}")
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
                logger.info(f"Value of status obtained after inner join is : {status_db}")

                actual_db_values = {
                    "order_id":order_id_db,
                    "order_status": order_status_db,
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


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_600_601_012():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Order_Address_Validation_For_ExistingUser
    Sub Feature Description: API:  Validate address for existing customer by hitting create_order api
    TC naming code description: 600: EzeGro functions, 601: Sale, 012: TC012
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

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")

            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            customer_name = "John" " " + ""''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")

            #create a customer
            api_details = DBProcessor.get_api_details('create_customer', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customer": {
                    "name": customer_name,
                    "mobileNumber": customer_mobile_no,
                },
                "customerVersion": merchant_customer_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create_customer is: {response}")

            pincode = random.randint(100000, 900000)
            logger.debug(f"Randomly generated pincode is :{pincode}")
            state = "Karnataka"
            logger.debug(f"state is :{state}")
            city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{city}")
            country = "India"
            logger.debug(f"country is :{country}")
            address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{address_line_1}")
            address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{address_line_2}")
            name = 'RED TAPE Shoes ' + ''.join(random.choices(string.ascii_lowercase, k=3))
            logger.debug(f"Value of name is :{name}")
            price = float(random.randint(1000,5000))
            logger.debug(f"Value of price is :{price}")
            quantity = random.randint(1,5)
            logger.debug(f"Value of quantity is :{quantity}")

            #create order
            api_details = DBProcessor.get_api_details('create_order', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "order": {
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
                    "products": [
                        {
                            "name": name,
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
            create_order_state = create_orders[-1]['customer']['address']['state']
            logger.info(f"Value of state obtained from create order : {create_order_state}")
            create_order_country = create_orders[-1]['customer']['address']['country']
            logger.info(f"Value of country obtained from create order : {create_order_country}")
            create_order_address_line_1 = create_orders[-1]['customer']['address']['addressLine1']
            logger.info(f"Value of addressLine1 obtained from create order : {create_order_address_line_1}")
            create_order_address_line_2 = create_orders[-1]['customer']['address']['addressLine2']
            logger.info(f"Value of addressLine2 obtained from create order : {create_order_address_line_2}")
            create_order_pincode = create_orders[-1]['customer']['address']['pincode']
            logger.info(f"Value of pincode obtained from create order : {create_order_pincode}")
            create_order_city = create_orders[-1]['customer']['address']['city']
            logger.info(f"Value of city obtained from create order : {create_order_city}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")

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
                    "state": state,
                    "country": country,
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "pincode": str(pincode),
                    "city": city
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "state": create_order_state,
                    "country": create_order_country,
                    "address_line_1": create_order_address_line_1,
                    "address_line_2": create_order_address_line_2,
                    "pincode": create_order_pincode,
                    "city": create_order_city
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
                    "address_line_1": address_line_1,
                    "address_line_2": address_line_2,
                    "country": country,
                    "pincode": str(pincode),
                    "state": state,
                    "city": city,
                    "entity": "CUSTOMER"
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.order_customer_id, OA.address_line_1, OA.address_line_2, OA.country, OA.pincode, OA.state,OA.city, OA.entity " \
                        "from order_details as OD INNER JOIN order_address AS OA ON OD.order_customer_id = OA.entity_id " \
                        "where OD.id = '"+ str(create_order_id)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                address_line_1_db = result['address_line_1'].values[0]
                logger.info(f"Value of address_line_1 obtained after inner join is : {address_line_1_db}")
                address_line_2_db = result['address_line_2'].values[0]
                logger.info(f"Value of address_line_2 obtained after inner join is : {address_line_2_db}")
                country_db = result['country'].values[0]
                logger.info(f"Value of country_db obtained after inner join is : {country_db}")
                pincode_db = result['pincode'].values[0]
                logger.info(f"Value of pincode obtained after inner join is : {pincode_db}")
                state_db = result['state'].values[0]
                logger.info(f"Value of state obtained after inner join is : {state_db}")
                city_db = result['city'].values[0]
                logger.info(f"Value of city obtained after inner join is : {city_db}")
                entity_db = result['entity'].values[0]
                logger.info(f"Value of entity obtained after inner join is : {entity_db}")

                actual_db_values = {
                    "address_line_1": address_line_1_db,
                    "address_line_2": address_line_2_db,
                    "country": country_db,
                    "pincode": pincode_db,
                    "state": state_db,
                    "city": city_db,
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
def test_common_600_601_013():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Order_and_update_order_For_ExistingUser
    Sub Feature Description: "API: Validate the positive login flow to update an order for an existing user by hitting the create Prder > update order
    TC naming code description: 600: EzeGro functions, 601: Sale, 013: TC013
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

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")
            merchant_order_version = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table : {merchant_order_version}")

            customer_name = "John "  + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")
            name = "t-shits " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {name}")
            price = random.randint(100,1500)
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1,5)
            logger.info(f"Randomly generated quantity is : {quantity}")
            create_order_sku = "EZU " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated create order sku is : {create_order_sku}")

            #create a customer
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

            #create a order
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
                                "name": name,
                                "price": price,
                                "quantity": quantity,
                                "sku": create_order_sku
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
            create_order_device_identifier = response['deviceIdentifier']
            logger.info(f"Value of deviceIdentifier obtained from create order : {create_order_device_identifier}")
            create_order_device_identifier_type = response['deviceIdentifierType']
            logger.info(f"Value of deviceIdentifierType obtained from create order : {create_order_device_identifier_type}")
            create_orders = list(response['orders'])
            logger.info(f"Converting orders to list format in create order : {create_orders}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")
            create_order_products = list(create_orders[-1]['products'])
            logger.info(f"Converting products to list format in create order : {create_order_products}")
            create_order_name = create_order_products[-1]['name']
            logger.info(f"Value of name obtained from create order : {create_order_name}")
            create_order_price = create_order_products[-1]['price']
            logger.info(f"Value of price obtained from create order : {create_order_price}")

            update_order_prod_name = "t-shits " +''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated update order product name is : {update_order_prod_name}")
            update_order_price = random.randint(100, 1500)
            logger.info(f"Randomly generated update order price is : {update_order_price}")
            update_order_quantity = random.randint(1, 5)
            logger.info(f"Randomly generated update order quantity is : {update_order_quantity}")
            update_order_sku = "EZU " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated update order sku is : {update_order_sku}")

            #update order
            api_details = DBProcessor.get_api_details('update_order', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "customerVersion": merchant_customer_version,
                "orderVersion": merchant_order_version,
                "order": {
                    "id": create_order_id,
                    "customer": {
                        "name": customer_name,
                        "mobileNumber": customer_mobile_no
                    },
                    "products": [
                        {
                            "name": update_order_prod_name,
                            "price": update_order_price,
                            "quantity": update_order_quantity,
                            "sku": update_order_sku
                        }
                    ]
                }
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for update order {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for update order is: {response}")
            update_orders = list(response['orders'])
            logger.info(f"Converting orders to list format in update order : {update_orders}")
            update_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from update order : {update_order_id}")
            update_order_products = list(update_orders[-1]['products'])
            logger.info(f"Converting product to list format in update order : {update_order_products}")
            update_order_name =  update_order_products[-1]['name']
            logger.info(f"Value of name obtained from update order : {update_order_name}")
            update_order_price_response = update_order_products[-1]['price']
            logger.info(f"Value of price obtained from update order : {update_order_price_response}")
            update_order_sku_response = update_order_products[-1]['sku']
            logger.info(f"Value of sku obtained from update order : {update_order_sku_response}")
            update_order_amt = update_order_products[-1]['amount']
            logger.info(f"Value of amount obtained from update order : {update_order_amt}")
            update_order_quantity_response = update_order_products[-1]['quantity']
            logger.info(f"Value of quantity obtained from update order : {update_order_quantity_response}")

            query = "select * from order_details where id ='" + str(create_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of Id obtained from order_details table : {order_details_id_db}")

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
                    "device_identifier": device_identifier,
                    "device_identifier_type": device_identifier_type,
                    "original_order_id": create_order_id,
                    "name": name,
                    "price": price,
                    "updated_order_id": create_order_id,
                    "updated_name": update_order_prod_name,
                    "updated_price": update_order_price,
                    "updated_sku": update_order_sku,
                    "updated_amt": update_order_price*update_order_quantity,
                    "updated_quantity": update_order_quantity
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "device_identifier": create_order_device_identifier,
                    "device_identifier_type": create_order_device_identifier_type,
                    "original_order_id": order_details_id_db,
                    "name": create_order_name,
                    "price": create_order_price,
                    "updated_order_id": update_order_id,
                    "updated_name": update_order_name,
                    "updated_price": update_order_price_response,
                    "updated_sku": update_order_sku_response,
                    "updated_amt": update_order_amt,
                    "updated_quantity": update_order_quantity_response
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
                    "status": "DELETED",
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "sku": create_order_sku,
                    "status_2": "ACTIVE",
                    "name_2": update_order_prod_name,
                    "price_2": update_order_price,
                    "quantity_2": update_order_quantity,
                    "sku_2": update_order_sku
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "SELECT OI.order_id, OI.order_product_id,OI.status, OI.quantity, OP.name, OP.price, OP.sku " \
                        "from order_items AS OI INNER JOIN order_product as OP ON OI.order_product_id = OP.id " \
                        "where order_id ='"+str(update_order_id)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                status_db = result['status'].values[0]
                logger.info(f"Value of status obtained for previous product after inner join is : {status_db}")
                quantity_db = result['quantity'].values[0]
                logger.info(f"Value of quantity obtained for previous product after inner join is : {quantity_db}")
                name_db = result['name'].values[0]
                logger.info(f"Value of name obtained for previous product after inner join is : {name_db}")
                price_db = result['price'].values[0]
                logger.info(f"Value of price obtained for previous product after inner join is : {price_db}")
                sku_db = result['sku'].values[0]
                logger.info(f"Value of sku obtained for previous product after inner join is : {sku_db}")
                status_2_db = result['status'].values[1]
                logger.info(f"Value of status obtained for current product after inner join is : {status_2_db}")
                quantity_2_db = result['quantity'].values[1]
                logger.info(f"Value of quantity obtained for current product after inner join is : {quantity_2_db}")
                name_2_db = result['name'].values[1]
                logger.info(f"Value of name obtained for current product after inner join is : {name_2_db}")
                price_2_db = result['price'].values[1]
                logger.info(f"Value of price obtained for current product after inner join is : {price_2_db}")
                sku_2_db = result['sku'].values[1]
                logger.info(f"Value of sku obtained for current product after inner join is : {sku_2_db}")

                actual_db_values = {
                    "status": status_db,
                    "name": name_db,
                    "price": price_db,
                    "quantity": quantity_db,
                    "sku": sku_db,
                    "status_2": status_2_db,
                    "name_2": name_2_db,
                    "price_2": price_2_db,
                    "quantity_2": quantity_2_db,
                    "sku_2": sku_2_db
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
def test_common_600_601_014():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Sale_Create_Order_and_delete_order_For_ExistingUser
    Sub Feature Description: "API: Validate the positive login flow to delete an order for an existing user by hitting the create order > delete order
    TC naming code description: 600: EzeGro functions, 601: Sale, 014: TC014
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

            query = "select * from merchant where mobile_number ='" + str(mobile_number) + "';"
            logger.debug(f"Query to fetch data from merchant table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result for merchant table : {result}")
            merchant_customer_version = result['customer_version'].values[0]
            logger.info(f"Value of customer_version obtained from merchant table : {merchant_customer_version}")
            merchant_order_version = result['order_version'].values[0]
            logger.info(f"Value of order_version obtained from merchant table : {merchant_order_version}")
            merchant_id = result['id'].values[0]
            logger.info(f"Value of id obtained from merchant table : {merchant_id}")

            customer_name = "John "+ ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated customer name is : {customer_name}")
            customer_mobile_no = "666666666" + str(random.randint(0, 9))
            logger.info(f"Randomly generated customer mobile number is : {customer_mobile_no}")

            #create a customer
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

            prod_name = "t-shits" " " + ""''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = random.randint(100, 1500)
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1, 5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            #create a order
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
            create_order_customer_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobile_number obtained from create order : {create_order_customer_mobile_no}")
            create_orders = list(response['orders'])
            logger.info(f"Converting orders to list format: {create_orders}")
            create_order_id = create_orders[-1]['id']
            logger.info(f"Value of id obtained from create order : {create_order_id}")
            create_order_ref_id = create_orders[-1]['refId']
            logger.info(f"Value of ref_id obtained from create order : {create_order_ref_id}")

            api_details = DBProcessor.get_api_details('delete_order', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_order_id,
                "orderVersion": merchant_order_version
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for delete order {api_details}")
            
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for delete order is: {response}")
            delete_order_id = response['orderId']
            logger.info(f"Value of order id obtained from delete order : {delete_order_id}")

            query = "select * from order_details where id ='" + str(create_order_id) + "';"
            logger.debug(f"Query to fetch data from order_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_details table : {result}")
            order_details_ref_id_db = result['ref_id'].values[0]
            logger.info(f"Value of refId obtained from order_details table : {order_details_ref_id_db}")
            order_details_id_db = result['id'].values[0]
            logger.info(f"Value of Id obtained from order_details table : {order_details_id_db}")
            order_details_customer_id_db = result['order_customer_id'].values[0]
            logger.info(f"Value of order_customer_id obtained from order_details table : {order_details_customer_id_db}")

            query = "select * from order_customer where merchant_id='"+str(merchant_id)+"' order by created_time desc limit 1;"
            logger.debug(f"Query to fetch data from order_customer table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_customer table : {result}")
            order_customer_address_id_db = result['address_id'].values[0]
            logger.info(f"Value of address_id obtained from order_customer table : {order_customer_address_id_db}")

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
                    "id": create_order_id,
                    "ref_id": create_order_ref_id,
                    "deleted_id" : delete_order_id

                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "mobile_no": create_order_customer_mobile_no,
                    "id": order_details_id_db,
                    "ref_id": order_details_ref_id_db,
                    "deleted_id": order_details_id_db
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
                    "order_id": delete_order_id,
                    "ref_id": create_order_ref_id,
                    "order_status": 'CANCELLED',
                    "order_customer_id": order_details_customer_id_db,
                    "customer_mobile_no": customer_mobile_no,
                    "order_address_id": order_customer_address_id_db,
                    "merchant_mobile_no": mobile_number
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select OD.id as order_id, OD.merchant_id, OD.ref_id, OD.status AS order_status, OD.amount, OD.order_customer_id," \
                        "OD.dimensions, OD.pick_up_address, OD.weight, C.name AS Customer_name, C.mobile_number AS customer_mobileNo," \
                        "C.address_id as order_address_id,M.name,M.mobile_number as Merchant_mobile_number, " \
                        "M.store_name from order_details as OD INNER JOIN order_customer AS C ON OD.order_customer_id = C.id INNER JOIN merchant AS M ON OD.merchant_id = M.id " \
                        "where OD.id ='"+str(delete_order_id)+"';"

                logger.debug(f"Query to fetch data after inner join : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after inner join : {result}")
                order_id_db = result['order_id'].values[0]
                logger.info(f"Value of order_id obtained after inner join is : {order_id_db}")
                ref_id_db = result['ref_id'].values[0]
                logger.info(f"Value of ref_id obtained after inner join is : {ref_id_db}")
                order_status_db = result['order_status'].values[0]
                logger.info(f"Value of order_status obtained after inner join is : {order_status_db}")
                order_customer_id_db = result['order_customer_id'].values[0]
                logger.info(f"Value of order_customer_id obtained after inner join is : {order_customer_id_db}")
                customer_mobile_no_db = result['customer_mobileNo'].values[0]
                logger.info(f"Value of customer_mobileNo obtained after inner join is : {customer_mobile_no_db}")
                order_address_id_db = result['order_address_id'].values[0]
                logger.info(f"Value of order_address_id obtained after inner join is : {order_address_id_db}")
                merchant_mobile_no_db = result['Merchant_mobile_number'].values[0]
                logger.info(f"Value of merchant_mobile_no obtained after inner join is : {merchant_mobile_no_db}")

                actual_db_values = {
                    "order_id": order_id_db,
                    "ref_id": ref_id_db,
                    "order_status": order_status_db,
                    "order_customer_id": order_customer_id_db,
                    "customer_mobile_no": customer_mobile_no_db,
                    "order_address_id": order_address_id_db,
                    "merchant_mobile_no": merchant_mobile_no_db
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