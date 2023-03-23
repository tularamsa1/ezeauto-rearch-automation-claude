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
def test_common_600_602_011():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_InitiateShipment
    Sub Feature Description: API: Validate positive flow for initiateShipment
    TC naming code description: 600: EzeGro functions, 602: Logistics, 011: TC011
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
            customer_pincode = random.randint(560021, 560041)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

            # create a customer
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

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create customer is: {response}")

            pickup_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + "@gamil.com"
            logger.debug(f"Randomly generated pick up email is :{pickup_email}")
            pickup_mobile_no = "777777777" + str(random.randint(0, 9))
            logger.info(f"Randomly generated pick up mobile number is : {pickup_mobile_no}")
            pickup_pincode = random.randint(560001, 560020)
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

            weight = round(random.uniform(0.25, 1.0), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            length = random.randint(1, 2)
            logger.info(f"Randomly Generated length is : {length}")
            breadth = random.randint(2, 4)
            logger.info(f"Randomly Generated breadth is : {breadth}")
            height = random.randint(4, 6)
            logger.info(f"Randomly Generated height is : {height}")
            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100, 1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1, 5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            # create order logistics for existing order id
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

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create order logistics {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for create order logistics is: {response}")
            create_logistics_orders = list(response['orders'])
            logger.info(f"Converting orders to list format from create order logistics : {create_logistics_orders}")
            create_logistics_order_id = create_logistics_orders[-1]['id']
            logger.info(f"Value of id obtained from create order logistics : {create_logistics_order_id}")

            get_courier_service_weight = round(random.uniform(0.25,2.0), 2)
            logger.info(f"Randomly Generated get_courier_service_weight is : {get_courier_service_weight}")
            pickup_postal_code = random.randint(560001, 560055)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": customer_pincode,
                "weight": get_courier_service_weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")

            for i in range(len(get_courier_service_available_courier_companies)):
                if get_courier_service_available_courier_companies[i]['courierName'] == "Ekart Logistics":
                    courier_id = get_courier_service_available_courier_companies[i]['courierCompanyId']
                    logger.info(f"Value of courier company id obtained from get courier service is : {courier_id}")
                    rate = get_courier_service_available_courier_companies[i]['rate']
                    logger.info(f"Value of courier company rate obtained from get courier service is : {rate}")
                    courier_name = get_courier_service_available_courier_companies[i]['courierName']
                    logger.info(f"Value of courier name obtained from get courier service is : {courier_name}")
                    break
                else:
                    logger.error("Courier Name is not found")

            # recharge wallet
            amt_to_recharge = random.randint(50, 500)
            api_details = DBProcessor.get_api_details('recharge_wallet', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for recharge_wallet is: {response}")
            recharge_wallet_success = response['success']
            logger.info(f"Value of success obtained from recharge_wallet : {recharge_wallet_success}")
            external_ref_no = response['externalRefNumber']
            logger.info(f"Value of external ref no obtained from recharge_wallet : {external_ref_no}")

            # cybersource callback
            api_details = DBProcessor.get_api_details('cybersource_success_callback', request_body={
                "success": True,
                "paymentMode": "CNP",
                "externalRefNumber": external_ref_no,
                "status": "AUTHORIZED",
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Basic RVpFR1JPXzEyMzQ1NjpFemV0YXBAMTIzNDU2',
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for cnp callback from cybersource {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Status Code obtained cybersource callback api is: {response.status_code}")

            # checking the wallet_txn after success callback
            query = "select * from wallet_txn where external_ref ='" + str(external_ref_no) + "';"
            logger.debug(f"Query to fetch data after cyber_callback from wallet_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result after cyber_callback from wallet_txn table : {result}")
            wallet_txn_agent_id = result['agent_id'].values[0]
            logger.info(f"Value of agent_id obtained after cyber_callback from wallet_txn table : {wallet_txn_agent_id}")
            wallet_txn_amt = result['amount'].values[0]
            logger.info(f"Value of amount obtained after cyber_callback from wallet_txn table : {wallet_txn_amt}")
            wallet_txn_bal = result['balance'].values[0]
            logger.info(f"Value of balance obtained after cyber_callback from wallet_txn table : {wallet_txn_bal}")
            wallet_txn_status = result['status'].values[0]
            logger.info(f"Value of status obtained after cyber_callback from wallet_txn table : {wallet_txn_status}")
            wallet_txn_transfer_mode = result['transfer_mode'].values[0]
            logger.info(f"Value of transfer_mode obtained after cyber_callback from wallet_txn table : {wallet_txn_transfer_mode}")

            # initiate_shipment
            api_details = DBProcessor.get_api_details('initiate_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id,
                "courierId": courier_id,
                "amount": rate,
                "courierName": courier_name
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for initiate shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for initiate shipment is: {response}")
            initiate_shipment_success = response['success']
            logger.info(f"Value of success obtained for initiate shipment is : {initiate_shipment_success}")
            initiate_shipment_mobile_no = response['mobileNumber']
            logger.info(f"Value of mobile number obtained for initiate shipment is : {initiate_shipment_mobile_no}")
            initiate_shipment_id = response['shipment']['id']
            logger.info(f"Value of shipment id obtained for initiate shipment is : {initiate_shipment_id}")
            initiate_shipment_courier_name = response['shipment']['courierName']
            logger.info(f"Value of shipment courier name obtained for initiate shipment is : {initiate_shipment_courier_name}")
            initiate_shipment_awb = response['shipment']['awb']
            logger.info(f"Value of shipment awb obtained for initiate shipment is : {initiate_shipment_awb}")
            initiate_shipment_status = response['shipment']['status']
            logger.info(f"Value of shipment status obtained for initiate shipment is : {initiate_shipment_status}")
            initiate_shipment_courier_id = response['shipment']['courierId']
            logger.info(f"Value of shipment courier id obtained for initiate shipment is : {initiate_shipment_courier_id}")
            initiate_shipment_amt = response['shipment']['shipmentAmount']
            logger.info(f"Value of shipment amount obtained for initiate shipment is : {initiate_shipment_amt}")

            query = "select * from shipment_details where order_id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from shipment_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of shipment_details table : {result}")
            shipment_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from shipment_details table : {shipment_details_id_db}")
            shipment_details_awb_no_db = result['awb_number'].values[0]
            logger.info(f"Value of awb_number obtained from shipment_details table : {shipment_details_awb_no_db}")
            shipment_details_courier_id_db = result['courier_id'].values[0]
            logger.info(f"Value of courier_id obtained from shipment_details table : {shipment_details_courier_id_db}")
            shipment_details_courier_name_db = result['courier_name'].values[0]
            logger.info(f"Value of courier_name obtained from shipment_details table : {shipment_details_courier_name_db}")
            shipment_details_order_id_db = result['order_id'].values[0]
            logger.info(f"Value of order_id obtained from shipment_details table : {shipment_details_order_id_db}")
            shipment_details_pickup_scheduled_date_db = result['pickup_scheduled_date'].values[0]
            logger.info(f"Value of pickup_scheduled_date obtained from shipment_details table : {shipment_details_pickup_scheduled_date_db}")
            shipment_details_shipment_status_db = result['shipment_status'].values[0]
            logger.info(f"Value of shipment_status obtained from shipment_details table : {shipment_details_shipment_status_db}")
            status_db = result['status'].values[0]
            logger.info(f"Value of status obtained from shipment_details table : {status_db}")
            shipment_details_amt_db = result['amount'].values[0]
            logger.info(f"Value of amount obtained from shipment_details table : {shipment_details_amt_db}")

            query = "select * from order_status_audit where order_id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from order_status_audit table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of order_status_audit table : {result}")
            from_status_db = result['from_status'].values[0]
            logger.info(f"Value of from_status obtained from order_status_audit table : {from_status_db}")
            order_status_order_id_db = result['order_id'].values[0]
            logger.info(f"Value of order_id obtained from order_status_audit table : {order_status_order_id_db}")
            to_status_db = result['to_status'].values[0]
            logger.info(f"Value of to_status obtained from order_status_audit table : {to_status_db}")

            query = "select * from wallet_txn where awb_number ='" + str(initiate_shipment_awb) + "';"
            logger.debug(f"Query to fetch data from wallet_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of wallet_txn table : {result}")
            wallet_txn_agent_id_db = result['agent_id'].values[0]
            logger.info(f"Value of agent_id obtained from wallet_txn table : {wallet_txn_agent_id_db}")
            wallet_txn_amt_db = result['amount'].values[0]
            logger.info(f"Value of amount obtained from wallet_txn table : {wallet_txn_amt_db}")
            wallet_txn_status_db = result['status'].values[0]
            logger.info(f"Value of status obtained from wallet_txn table : {wallet_txn_status_db}")
            wallet_txn_transfer_mode_db = result['transfer_mode'].values[0]
            logger.info(f"Value of transfer_mode obtained from wallet_txn table : {wallet_txn_transfer_mode_db}")
            wallet_txn_shipment_id_db = result['shipment_id'].values[0]
            logger.info(f"Value of shipment_id obtained from wallet_txn table : {wallet_txn_shipment_id_db}")
            wallet_txn_awb_no_db = result['awb_number'].values[0]
            logger.info(f"Value of awb_number obtained from wallet_txn table : {wallet_txn_awb_no_db}")
            wallet_txn_courier_name_db = result['courier_name'].values[0]
            logger.info(f"Value of courier_name obtained from wallet_txn table : {wallet_txn_courier_name_db}")

            #cancel shipment
            api_details = DBProcessor.get_api_details('cancel_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for cancel shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for cancel shipment is : {response}")
            cancel_shipment_success = response['success']
            logger.info(f"Value of success obtained for cancel shipment is : {cancel_shipment_success}")
            cancel_shipment_status = response['shipment']['status']
            logger.info(f"Value of shipment status obtained for cancel shipment is : {cancel_shipment_status}")

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
                    "order_id": create_logistics_order_id,
                    "initiate_shipment_mobile_no": mobile_number,
                    "initiate_shipment_success":True,
                    "cancel_success": True,
                    "cancel_status": 'NEW'
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "order_id": order_details_id_db,
                    "initiate_shipment_mobile_no": initiate_shipment_mobile_no,
                    "initiate_shipment_success": initiate_shipment_success,
                    "cancel_success": cancel_shipment_success,
                    "cancel_status": cancel_shipment_status
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
                    "shipment_id": initiate_shipment_id,
                    "shipment_awb_no": initiate_shipment_awb,
                    "shipment_courier_id": initiate_shipment_courier_id,
                    "shipment_courier_name": initiate_shipment_courier_name,
                    "shipment_order_id": create_logistics_order_id,
                    "pickup_scheduled_date": None,
                    "shipment_status": "AWB_ASSIGNED",
                    "status": "READY_TO_SHIP",
                    "shipment_amount": initiate_shipment_amt,
                    "order_from_status": 'NEW',
                    "order_id": create_logistics_order_id,
                    "order_to_status": "READY_TO_SHIP",
                    "wallet_agent_id": mobile_number,
                    # "wallet_amount": initiate_shipment_amt,
                    "wallet_status": "SUCCESS",
                    "wallet_transfer_mode": "WITHDRAW",
                    "wallet_shipment_id": initiate_shipment_id,
                    "wallet_courier_name": initiate_shipment_courier_name
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "shipment_id": shipment_details_id_db,
                    "shipment_awb_no": shipment_details_awb_no_db,
                    "shipment_courier_id": shipment_details_courier_id_db,
                    "shipment_courier_name": shipment_details_courier_name_db,
                    "shipment_order_id": shipment_details_order_id_db,
                    "pickup_scheduled_date": shipment_details_pickup_scheduled_date_db,
                    "shipment_status": shipment_details_shipment_status_db,
                    "status": status_db,
                    "shipment_amount": shipment_details_amt_db,
                    "order_from_status": from_status_db,
                    "order_id": order_status_order_id_db,
                    "order_to_status": to_status_db,
                    "wallet_agent_id": wallet_txn_agent_id_db,
                    # "wallet_amount": wallet_txn_amt_db,
                    "wallet_status": wallet_txn_status_db,
                    "wallet_transfer_mode": wallet_txn_transfer_mode_db,
                    "wallet_shipment_id": wallet_txn_shipment_id_db,
                    "wallet_courier_name": wallet_txn_courier_name_db
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
def test_common_600_602_012():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_InitiateShipment_generateLabel
    Sub Feature Description: API: Validate postive flow for initiateShipment and generating a Label
    TC naming code description: 600: EzeGro functions, 602: Logistics, 012: TC012
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
            customer_pincode = random.randint(560021, 560041)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

            # create a customer
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
            pickup_pincode = random.randint(560001, 560020)
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

            weight = round(random.uniform(0.25, 1.0), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            length = random.randint(1, 2)
            logger.info(f"Randomly Generated length is : {length}")
            breadth = random.randint(2, 4)
            logger.info(f"Randomly Generated breadth is : {breadth}")
            height = random.randint(4, 6)
            logger.info(f"Randomly Generated height is : {height}")
            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100, 1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1, 5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            # create order logistics for existing order id
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

            get_courier_service_weight = round(random.uniform(0.25,2.0), 2)
            logger.info(f"Randomly Generated get_courier_service_weight is : {get_courier_service_weight}")
            pickup_postal_code = random.randint(560001, 560055)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": customer_pincode,
                "weight": get_courier_service_weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")

            for i in range(len(get_courier_service_available_courier_companies)):
                if get_courier_service_available_courier_companies[i]['courierName'] == "Delhivery":
                    courier_id = get_courier_service_available_courier_companies[i]['courierCompanyId']
                    logger.info(f"Value of courier company id obtained from get courier service is : {courier_id}")
                    rate = get_courier_service_available_courier_companies[i]['rate']
                    logger.info(f"Value of courier company rate obtained from get courier service is : {rate}")
                    courier_name = get_courier_service_available_courier_companies[i]['courierName']
                    logger.info(f"Value of courier name obtained from get courier service is : {courier_name}")
                    break
                else:
                    logger.error("Courier Name is not found")

            # recharge wallet
            amt_to_recharge = random.randint(50, 500)
            api_details = DBProcessor.get_api_details('recharge_wallet', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for recharge_wallet is: {response}")
            recharge_wallet_success = response['success']
            logger.info(f"Value of success obtained from recharge_wallet : {recharge_wallet_success}")
            external_ref_no = response['externalRefNumber']
            logger.info(f"Value of external ref no obtained from recharge_wallet : {external_ref_no}")

            # cybersource callback
            api_details = DBProcessor.get_api_details('cybersource_success_callback', request_body={
                "success": True,
                "paymentMode": "CNP",
                "externalRefNumber": external_ref_no,
                "status": "AUTHORIZED",
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Basic RVpFR1JPXzEyMzQ1NjpFemV0YXBAMTIzNDU2',
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for cnp callback from cybersource {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Status Code obtained cybersource callback api is: {response.status_code}")

            # checking the wallet_txn after success callback
            query = "select * from wallet_txn where external_ref ='" + str(external_ref_no) + "';"
            logger.debug(f"Query to fetch data after cyber_callback from wallet_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result after cyber_callback from wallet_txn table : {result}")
            wallet_txn_agent_id = result['agent_id'].values[0]
            logger.info(f"Value of agent_id obtained after cyber_callback from wallet_txn table : {wallet_txn_agent_id}")
            wallet_txn_amt = result['amount'].values[0]
            logger.info(f"Value of amount obtained after cyber_callback from wallet_txn table : {wallet_txn_amt}")
            wallet_txn_bal = result['balance'].values[0]
            logger.info(f"Value of balance obtained after cyber_callback from wallet_txn table : {wallet_txn_bal}")
            wallet_txn_status = result['status'].values[0]
            logger.info(f"Value of status obtained after cyber_callback from wallet_txn table : {wallet_txn_status}")
            wallet_txn_transfer_mode = result['transfer_mode'].values[0]
            logger.info(f"Value of transfer_mode obtained after cyber_callback from wallet_txn table : {wallet_txn_transfer_mode}")

            # initiate_shipment
            api_details = DBProcessor.get_api_details('initiate_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id,
                "courierId": courier_id,
                "amount": rate,
                "courierName": courier_name
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for initiate shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for initiate shipment is: {response}")
            initiate_shipment_id = response['shipment']['id']
            logger.info(f"Value of shipment id obtained for initiate shipment is : {initiate_shipment_id}")
            initiate_shipment_courier_name = response['shipment']['courierName']
            logger.info(f"Value of shipment courier name obtained for initiate shipment is : {initiate_shipment_courier_name}")
            initiate_shipment_awb = response['shipment']['awb']
            logger.info(f"Value of shipment awb obtained for initiate shipment is : {initiate_shipment_awb}")
            initiate_shipment_courier_id = response['shipment']['courierId']
            logger.info(f"Value of shipment courier id obtained for initiate shipment is : {initiate_shipment_courier_id}")
            initiate_shipment_amt = response['shipment']['shipmentAmount']
            logger.info(f"Value of shipment amount obtained for initiate shipment is : {initiate_shipment_amt}")

            # generate_label
            api_details = DBProcessor.get_api_details('generate_label', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for generate label is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate label is: {response}")
            generate_label_url = response['shipment']['labelUrl']
            logger.info(f"Value of labelUrl obtained for generate label is : {generate_label_url}")
            generate_label_id = response['orderId']
            logger.info(f"Value of orderId obtained for generate label is : {generate_label_id}")

            query = "select * from shipment_details where order_id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from shipment_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of shipment_details table : {result}")
            shipment_details_id_db = result['id'].values[0]
            logger.info(f"Value of id obtained from shipment_details table : {shipment_details_id_db}")
            shipment_details_awb_no_db = result['awb_number'].values[0]
            logger.info(f"Value of awb_number obtained from shipment_details table : {shipment_details_awb_no_db}")
            shipment_details_courier_id_db = result['courier_id'].values[0]
            logger.info(f"Value of courier_id obtained from shipment_details table : {shipment_details_courier_id_db}")
            shipment_details_courier_name_db = result['courier_name'].values[0]
            logger.info(f"Value of courier_name obtained from shipment_details table : {shipment_details_courier_name_db}")
            shipment_details_label_url_db = result['label_url'].values[0]
            logger.info(f"Value of label url obtained from shipment_details table : {shipment_details_label_url_db}")
            shipment_details_order_id_db = result['order_id'].values[0]
            logger.info(f"Value of order_id obtained from shipment_details table : {shipment_details_order_id_db}")
            shipment_details_amt_db = result['amount'].values[0]
            logger.info(f"Value of amount obtained from shipment_details table : {shipment_details_amt_db}")

            #cancel shipment
            api_details = DBProcessor.get_api_details('cancel_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for cancel shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for cancel shipment is : {response}")
            cancel_shipment_status = response['shipment']['status']
            logger.info(f"Value of shipment status obtained for cancel shipment is : {cancel_shipment_status}")

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
                    "create_order_id": create_logistics_order_id,
                    "generate_label_url": generate_label_url,
                    "generate_order_id": generate_label_id,
                    "cancel_status": 'NEW'
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "create_order_id": order_details_id_db,
                    "generate_label_url": shipment_details_label_url_db,
                    "generate_order_id": order_details_id_db,
                    "cancel_status": cancel_shipment_status
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
                    "shipment_id": initiate_shipment_id,
                    "shipment_awb_no": initiate_shipment_awb,
                    "shipment_courier_id": initiate_shipment_courier_id,
                    "shipment_courier_name": initiate_shipment_courier_name,
                    "shipment_label_url": generate_label_url,
                    "shipment_order_id": create_logistics_order_id,
                    "shipment_amt": str(f'{float(initiate_shipment_amt):.2f}')
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                actual_db_values = {
                    "shipment_id": shipment_details_id_db,
                    "shipment_awb_no": shipment_details_awb_no_db,
                    "shipment_courier_id": shipment_details_courier_id_db,
                    "shipment_courier_name": shipment_details_courier_name_db,
                    "shipment_label_url": shipment_details_label_url_db,
                    "shipment_order_id": shipment_details_order_id_db,
                    "shipment_amt": str(f'{float(shipment_details_amt_db):.2f}')
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
def test_common_600_602_013():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_InitiateShipment_generateInvoice
    Sub Feature Description: API: Validate postive flow for initiateShipment and generating a Invoice
    TC naming code description: 600: EzeGro functions, 602: Logistics, 013: TC013
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
            customer_pincode = random.randint(560021, 560041)
            logger.debug(f"Randomly generated pincode is :{customer_pincode}")
            customer_city = "Bengaluru " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated city is :{customer_city}")
            customer_address_line_1 = "123 abc street " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_1 is :{customer_address_line_1}")
            customer_address_line_2 = ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.debug(f"Randomly generated address_line_2 is :{customer_address_line_2}")
            customer_state = "Karnataka"
            logger.debug(f"state is :{customer_state}")
            customer_country = "India"
            logger.debug(f"country is :{customer_country}")

            # create a customer
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
            pickup_pincode = random.randint(560001, 560020)
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

            weight = round(random.uniform(0.25, 1.0), 2)
            logger.info(f"Randomly Generated weight is : {weight}")
            length = random.randint(1, 2)
            logger.info(f"Randomly Generated length is : {length}")
            breadth = random.randint(2, 4)
            logger.info(f"Randomly Generated breadth is : {breadth}")
            height = random.randint(4, 6)
            logger.info(f"Randomly Generated height is : {height}")
            prod_name = "blue t-shirts " + ''.join(random.choices(string.ascii_lowercase, k=4))
            logger.info(f"Randomly generated customer product name is : {prod_name}")
            price = float(random.randint(100, 1000))
            logger.info(f"Randomly generated price is : {price}")
            quantity = random.randint(1, 5)
            logger.info(f"Randomly generated quantity is : {quantity}")

            # create order logistics for existing order id
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

            get_courier_service_weight = round(random.uniform(0.25,2.0), 2)
            logger.info(f"Randomly Generated get_courier_service_weight is : {get_courier_service_weight}")
            pickup_postal_code = random.randint(560001, 560055)
            logger.info(f"Value of pickup postal code generated is : {pickup_postal_code}")
            india_post_supported = "true"

            #get courier service
            api_details = DBProcessor.get_api_details('get_courier_service', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "pickUpPostalCode": pickup_postal_code,
                "deliveryPostalCode": customer_pincode,
                "weight": get_courier_service_weight,
                "indiaPostSupported": india_post_supported
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get courier service is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get courier service is: {response}")
            get_courier_service_available_courier_companies = list(response['availableCourierCompanies'])
            logger.info(f"Value of availableCourierCompanies obtained from get courier service is : {get_courier_service_available_courier_companies}")

            for i in range(len(get_courier_service_available_courier_companies)):
                if get_courier_service_available_courier_companies[i]['courierName'] == "Ekart Logistics Surface":
                    courier_id = get_courier_service_available_courier_companies[i]['courierCompanyId']
                    logger.info(f"Value of courier company id obtained from get courier service is : {courier_id}")
                    rate = get_courier_service_available_courier_companies[i]['rate']
                    logger.info(f"Value of courier company rate obtained from get courier service is : {rate}")
                    courier_name = get_courier_service_available_courier_companies[i]['courierName']
                    logger.info(f"Value of courier name obtained from get courier service is : {courier_name}")
                    break
                else:
                    logger.error("Courier Name is not found")

            # recharge wallet
            amt_to_recharge = random.randint(50, 500)
            api_details = DBProcessor.get_api_details('recharge_wallet', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for create customer {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for recharge_wallet is: {response}")
            recharge_wallet_success = response['success']
            logger.info(f"Value of success obtained from recharge_wallet : {recharge_wallet_success}")
            external_ref_no = response['externalRefNumber']
            logger.info(f"Value of external ref no obtained from recharge_wallet : {external_ref_no}")

            # cybersource callback
            api_details = DBProcessor.get_api_details('cybersource_success_callback', request_body={
                "success": True,
                "paymentMode": "CNP",
                "externalRefNumber": external_ref_no,
                "status": "AUTHORIZED",
                "amount": amt_to_recharge
            })
            api_details['Header'] = {'Authorization': 'Basic RVpFR1JPXzEyMzQ1NjpFemV0YXBAMTIzNDU2',
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for cnp callback from cybersource {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Status Code obtained cybersource callback api is: {response.status_code}")

            # checking the wallet_txn after success callback
            query = "select * from wallet_txn where external_ref ='" + str(external_ref_no) + "';"
            logger.debug(f"Query to fetch data after cyber_callback from wallet_txn table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result after cyber_callback from wallet_txn table : {result}")
            wallet_txn_agent_id = result['agent_id'].values[0]
            logger.info(f"Value of agent_id obtained after cyber_callback from wallet_txn table : {wallet_txn_agent_id}")
            wallet_txn_amt = result['amount'].values[0]
            logger.info(f"Value of amount obtained after cyber_callback from wallet_txn table : {wallet_txn_amt}")
            wallet_txn_bal = result['balance'].values[0]
            logger.info(f"Value of balance obtained after cyber_callback from wallet_txn table : {wallet_txn_bal}")
            wallet_txn_status = result['status'].values[0]
            logger.info(f"Value of status obtained after cyber_callback from wallet_txn table : {wallet_txn_status}")
            wallet_txn_transfer_mode = result['transfer_mode'].values[0]
            logger.info(f"Value of transfer_mode obtained after cyber_callback from wallet_txn table : {wallet_txn_transfer_mode}")

            # initiate_shipment
            api_details = DBProcessor.get_api_details('initiate_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id,
                "courierId": courier_id,
                "amount": rate,
                "courierName": courier_name
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for initiate shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for initiate shipment is: {response}")
            initiate_shipment_id = response['shipment']['id']
            logger.info(f"Value of shipment id obtained for initiate shipment is : {initiate_shipment_id}")
            initiate_shipment_courier_name = response['shipment']['courierName']
            logger.info(f"Value of shipment courier name obtained for initiate shipment is : {initiate_shipment_courier_name}")
            initiate_shipment_awb = response['shipment']['awb']
            logger.info(f"Value of shipment awb obtained for initiate shipment is : {initiate_shipment_awb}")
            initiate_shipment_courier_id = response['shipment']['courierId']
            logger.info(f"Value of shipment courier id obtained for initiate shipment is : {initiate_shipment_courier_id}")
            initiate_shipment_amt = response['shipment']['shipmentAmount']
            logger.info(f"Value of shipment amount obtained for initiate shipment is : {initiate_shipment_amt}")

            # generate_label
            api_details = DBProcessor.get_api_details('generate_invoice', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for generate label is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for generate invoice is: {response}")
            generate_invoice_url = response['shipment']['invoiceUrl']
            logger.info(f"Value of invoiceUrl obtained form generate invoice is : {generate_invoice_url}")

            query = "select * from shipment_details where order_id ='" + str(create_logistics_order_id) + "';"
            logger.debug(f"Query to fetch data from shipment_details table : {query}")
            result = DBProcessor.getValueFromDB(query, "ezestore")
            logger.info(f"Query result of shipment_details table : {result}")
            shipment_details_awb_no_db = result['awb_number'].values[0]
            logger.info(f"Value of awb_number obtained from shipment_details table : {shipment_details_awb_no_db}")
            shipment_details_courier_id_db = result['courier_id'].values[0]
            logger.info(f"Value of courier_id obtained from shipment_details table : {shipment_details_courier_id_db}")
            shipment_details_courier_name_db = result['courier_name'].values[0]
            logger.info(f"Value of courier_name obtained from shipment_details table : {shipment_details_courier_name_db}")
            shipment_details_invoice_url_db = result['invoice_url'].values[0]
            logger.info(f"Value of invoice url obtained from shipment_details table : {shipment_details_invoice_url_db}")
            shipment_details_order_id_db = result['order_id'].values[0]
            logger.info(f"Value of order_id obtained from shipment_details table : {shipment_details_order_id_db}")
            shipment_details_amt_db = result['amount'].values[0]
            logger.info(f"Value of amount obtained from shipment_details table : {shipment_details_amt_db}")

            #cancel shipment
            api_details = DBProcessor.get_api_details('cancel_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "orderId": create_logistics_order_id
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for cancel shipment is {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for cancel shipment is : {response}")
            cancel_shipment_status = response['shipment']['status']
            logger.info(f"Value of shipment status obtained for cancel shipment is : {cancel_shipment_status}")

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
                    "create_order_id": create_logistics_order_id,
                    "generate_invoice_url": generate_invoice_url,
                    "cancel_status": 'NEW'
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "create_order_id": order_details_id_db,
                    "generate_invoice_url": shipment_details_invoice_url_db,
                    "cancel_status": cancel_shipment_status
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
                    "shipment_awb_no": initiate_shipment_awb,
                    "shipment_courier_id": initiate_shipment_courier_id,
                    "shipment_courier_name": initiate_shipment_courier_name,
                    "shipment_invoice_url": generate_invoice_url,
                    "shipment_order_id": create_logistics_order_id,
                    "shipment_amt": str(f'{float(initiate_shipment_amt):.2f}'),
                    "shipment_awb_no_2": None,
                    "shipment_courier_i_d_2": None,
                    "shipment_courier_name_2": None,
                    "shipment_invoice_url_2": None,
                    "status": 'NEW',
                    "order_from_status": 'READY_TO_SHIP',
                    "order_id": create_logistics_order_id,
                    "order_to_status": 'NEW',
                    "wallet_agent_id": mobile_number,
                    "wallet_amount": str(f'{float(rate):.2f}'),
                    "wallet_status": "REFUNDED",
                    "wallet_transfer_mode": "WITHDRAW",
                    "wallet_awb_no": initiate_shipment_awb,
                    "wallet_agent_id_2": mobile_number,
                    "wallet_amount_2": str(f'{float(rate):.2f}'),
                    "wallet_status_2": "SUCCESS",
                    "wallet_transfer_mode_2": "REFUND",
                    "wallet_awb_no_2": initiate_shipment_awb
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from shipment_details where order_id ='" + str(create_logistics_order_id) + "';"
                logger.debug(f"Query to fetch data after cancel shipment from shipment_details table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result after cancel shipment from shipment_details table : {result}")
                shipment_details_awb_no = result['awb_number'].values[0]
                logger.info(f"Value of awb_number obtained after cancel shipment from shipment_details table : {shipment_details_awb_no}")
                shipment_details_courier_id = result['courier_id'].values[0]
                logger.info(f"Value of courier_id obtained after cancel shipment  from shipment_details table : {shipment_details_courier_id}")
                shipment_details_courier_name = result['courier_name'].values[0]
                logger.info(f"Value of courier_name obtained after cancel shipment  from shipment_details table : {shipment_details_courier_name}")
                shipment_details_invoice_url = result['invoice_url'].values[0]
                logger.info(f"Value of invoice url obtained after cancel shipment  from shipment_details table : {shipment_details_invoice_url}")
                shipment_details_order_id = result['order_id'].values[0]
                logger.info(f"Value of order_id obtained after cancel shipment from shipment_details table : {shipment_details_order_id}")
                shipment_details_status = result['status'].values[0]
                logger.info(f"Value of status obtained after cancel shipment  from shipment_details table : {shipment_details_status}")

                query = "select * from order_status_audit where order_id ='" + str(create_logistics_order_id) + "';"
                logger.debug(f"Query to fetch data from order_status_audit table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of order_status_audit table : {result}")
                order_status_audit_from_status_db = result['from_status'].values[-1]
                logger.info(f"Value of from_status obtained from order_status_audit table : {order_status_audit_from_status_db}")
                order_status_audit_order_id_db = result['order_id'].values[-1]
                logger.info(f"Value of order_id obtained from order_status_audit table : {order_status_audit_order_id_db}")
                order_status_audit_to_status_db = result['to_status'].values[-1]
                logger.info(f"Value of to_status obtained from order_status_audit table : {order_status_audit_to_status_db}")

                query = "select * from wallet_txn where awb_number ='" + str(initiate_shipment_awb) + "';"
                logger.debug(f"Query to fetch data from wallet_txn table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of wallet_txn table : {result}")
                wallet_txn_agent_id_db = result['agent_id'].values[0]
                logger.info(f"Value of agent_id from row 1 obtained from wallet_txn table : {wallet_txn_agent_id_db}")
                wallet_txn_amt_db = result['amount'].values[0]
                logger.info(f"Value of amount from row 1 obtained from wallet_txn table : {wallet_txn_amt_db}")
                wallet_txn_status_db = result['status'].values[0]
                logger.info(f"Value of status from row 1 obtained from wallet_txn table : {wallet_txn_status_db}")
                wallet_txn_transfer_mode_db = result['transfer_mode'].values[0]
                logger.info(f"Value of transfer_mode from row 1  obtained from wallet_txn table : {wallet_txn_transfer_mode_db}")
                wallet_txn_awb_no_db = result['awb_number'].values[0]
                logger.info(f"Value of awb_number from row 1  obtained from wallet_txn table : {wallet_txn_awb_no_db}")
                wallet_txn_agent_id_2_db = result['agent_id'].values[-1]
                logger.info(f"Value of agent_id from row 2 obtained from wallet_txn table : {wallet_txn_agent_id_2_db}")
                wallet_txn_amt_2_db = result['amount'].values[-1]
                logger.info(f"Value of amount from row 2 obtained from wallet_txn table : {wallet_txn_amt_2_db}")
                wallet_txn_status_2_db = result['status'].values[-1]
                logger.info(f"Value of status from row 2 obtained from wallet_txn table : {wallet_txn_status_2_db}")
                wallet_txn_transfer_mode_2_db = result['transfer_mode'].values[-1]
                logger.info(f"Value of transfer_mode from row 2 obtained from wallet_txn table : {wallet_txn_transfer_mode_2_db}")
                wallet_txn_awb_no_2_db = result['awb_number'].values[-1]
                logger.info(f"Value of awb_number from row 2 obtained from wallet_txn table : {wallet_txn_awb_no_2_db}")

                actual_db_values = {
                    "shipment_awb_no": shipment_details_awb_no_db,
                    "shipment_courier_id": shipment_details_courier_id_db,
                    "shipment_courier_name": shipment_details_courier_name_db,
                    "shipment_invoice_url": shipment_details_invoice_url_db,
                    "shipment_order_id": shipment_details_order_id_db,
                    "shipment_amt": str(f'{float(shipment_details_amt_db):.2f}'),
                    "shipment_awb_no_2": shipment_details_awb_no,
                    "shipment_courier_i_d_2": shipment_details_courier_id,
                    "shipment_courier_name_2": shipment_details_courier_name,
                    "shipment_invoice_url_2": shipment_details_invoice_url,
                    "status": shipment_details_status,
                    "order_from_status": order_status_audit_from_status_db,
                    "order_id": order_status_audit_order_id_db,
                    "order_to_status": order_status_audit_to_status_db,
                    "wallet_agent_id": wallet_txn_agent_id_db,
                    "wallet_amount": str(f'{float(wallet_txn_amt_db):.2f}'),
                    "wallet_status": wallet_txn_status_db,
                    "wallet_transfer_mode": wallet_txn_transfer_mode_db,
                    "wallet_awb_no": wallet_txn_awb_no_db,
                    "wallet_agent_id_2": wallet_txn_agent_id_2_db,
                    "wallet_amount_2": str(f'{float(wallet_txn_amt_2_db):.2f}'),
                    "wallet_status_2": wallet_txn_status_2_db,
                    "wallet_transfer_mode_2": wallet_txn_transfer_mode_2_db,
                    "wallet_awb_no_2": wallet_txn_awb_no_2_db
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
def test_common_600_602_014():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_getAllshipment
    Sub Feature Description: API: Validate positive flow for getAllShipment
    TC naming code description: 600: EzeGro functions, 602: Logistics, 014: TC014
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

            # get_all_shipment
            api_details = DBProcessor.get_api_details('get_all_shipment', request_body={
                "user": validate_otp_user,
                "mobileNumber": mobile_number,
                "deviceIdentifier": device_identifier,
                "deviceIdentifierType": device_identifier_type,
                "shipmentVersion": "0"
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,'Content-Type': 'application/json'}
            logger.debug(f"api details for get all shipment {api_details}")

            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for get all shipment : {response}")
            get_all_shipment_success = response['success']
            logger.info(f"Value of success obtained from get all shipment : {get_all_shipment_success}")
            get_all_shipments = len(response['shipments'])
            logger.info(f"Value of shipments obtained from get all shipment : {get_all_shipments}")

            if get_all_shipments > 0:
                get_all_shipment = True
            else:
                get_all_shipment = False

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
                    "shipments": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": get_all_shipment_success,
                    "shipments": get_all_shipment
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
                    "count_id": get_all_shipments
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from merchant where mobile_number ='" + str(mobile_number) + "' AND status = 'ACTIVE';"
                logger.debug(f"Query to fetch data from merchant table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of merchant table : {result}")
                merchant_id = result['id'].values[0]
                logger.info(f"Value of merchant id obtained from merchant table : {merchant_id}")

                query = "select count(id) from shipment_details where merchant_id ='" + str(merchant_id) + "';"
                logger.debug(f"Query to fetch data from shipment_details table : {query}")
                result = DBProcessor.getValueFromDB(query, "ezestore")
                logger.info(f"Query result of shipment_details table : {result}")
                shipment_details_count_id = result['count(id)'].values[0]
                logger.info(f"Value of count of id obtained from shipment_details table : {shipment_details_count_id}")

                actual_db_values = {
                    "count_id": shipment_details_count_id
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
def test_common_600_602_015():
    """
    Sub Feature Code: NonUI_Common_EzeGro_Logistics_validate_wallet_settings
    Sub Feature Description: To validate the wallet settings populating in the response of validate OTP
    TC naming code description: 600: EzeGro functions, 602: Logistics, 015: TC015
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
            validate_otp_support_no = response['settings']['supportNumber']
            logger.info(f"Value of supportNumber obtained from validate otp : {validate_otp_support_no}")

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
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": validate_otp_success
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
                    "wallet_creation_enable" : "true",
                    "check_status_after": str(validate_otp_check_status_after),
                    "check_status_interval": str(validate_otp_check_status_interval),
                    "check_status_count": str(validate_otp_check_status_count),
                    "min_agent_bal": str(validate_otp_min_agent_balance),
                    "min_amt": str(validate_otp_min_amount),
                    "max_amt": str(validate_otp_max_amount),
                    "max_agent_bal": str(validate_otp_max_agent_balance),
                    "support_no": str(validate_otp_support_no)
                }

                logger.debug(f"expected_db_values: {expected_db_values}")

                query = "select * from setting where category ='WALLET' OR  category=  'CHECK_STATUS' OR setting_name ='EZEGRO_SUPPORT_NUMBER';"
                result = DBProcessor.getValueFromDB(query, 'ezestore')
                logger.info(f"Query result for wallet/check status settings from setting table : {result}")

                for ind in result.index:
                    if result['setting_name'][ind] == 'EZEGRO_SUPPORT_NUMBER':
                        eze_support_no_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db ezetap_support_no value from the setting table : {eze_support_no_db}")
                    elif result['setting_name'][ind] == 'WALLET_CREATION_ENABLE':
                        wallet_enable_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db wallet_enable value from the setting table : {wallet_enable_db}")
                    elif result['setting_name'][ind] == 'WALLET_MINIMUM_AMOUNT':
                        wallet_min_amt_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db wallet_min_amt value from the setting table : {wallet_min_amt_db}")
                    elif result['setting_name'][ind] == 'WALLET_MAXIMUM_AMOUNT':
                        wallet_max_amt_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db wallet_max_amt value from the setting table : {wallet_max_amt_db}")
                    elif result['setting_name'][ind] == 'WALLET_MIN_AGENT_BALANCE':
                        wallet_min_agent_bal_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db wallet_min_agent_balance value from the setting table : {wallet_min_agent_bal_db}")
                    elif result['setting_name'][ind] == 'WALLET_MAX_AGENT_BALANCE':
                        wallet_max_agent_bal_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db wallet_max_agent_balance value from the setting table : {wallet_max_agent_bal_db}")
                    elif result['setting_name'][ind] == 'CHECK_STATUS_AFTER':
                        check_status_after_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db check_status_after value from the setting table : {check_status_after_db}")
                    elif result['setting_name'][ind] == 'CHECK_STATUS_INTERVAL':
                        check_status_interval_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db check_status_interval value from the setting table : {check_status_interval_db}")
                    elif result['setting_name'][ind] == 'CHECK_STATUS_COUNT':
                        check_status_count_db = result['setting_value'][ind]
                        logger.info(f"Fetching actual db check_status_count value from the setting table : {check_status_count_db}")
                    else:
                        logger.error(f"No Wallet/Check status settings associated in settings table")

                actual_db_values = {
                    "wallet_creation_enable" : str(wallet_enable_db),
                    "check_status_after": str(check_status_after_db),
                    "check_status_interval": str(check_status_interval_db),
                    "check_status_count": str(check_status_count_db),
                    "min_agent_bal": str(wallet_min_agent_bal_db),
                    "min_amt": str(wallet_min_amt_db),
                    "max_amt": str(wallet_max_amt_db),
                    "max_agent_bal": str(wallet_max_agent_bal_db),
                    "support_no": eze_support_no_db
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























