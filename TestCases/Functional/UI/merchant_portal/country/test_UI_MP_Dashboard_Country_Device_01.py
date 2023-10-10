from datetime import datetime
import random
import sys
import pendulum
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_DashboardPage import PortalDashboardPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    merchant_creator, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger
import pytz

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
def test_mp_700_701_018():
    """
    Sub Feature Code: UI_MP_Device_Usage_as_country_head
    Sub Feature Description: Verifying device usage details on dashboard for payment done thru device when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    018: TC018
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE13')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        cred_dict = ResourceAssigner.get_org_users_using_category(txn_org_code)
        logger.debug(f"Fetched all category credentials from the ezeauto db : {cred_dict}")
        login_username = cred_dict['COUNTRY']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['COUNTRY']['password']

        query = "select org_code from org_employee where username='" + str(login_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(10, 500)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api', request_body={
                                                    "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                     org_code=org_code, acquisition="HDFC",
                                                     payment_gateway="HDFC"),
                                                     "username": txn_username,
                                                     "password": txn_password,
                                                     "amount": str(amount),
                                                     "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                     "nonce": card_details['Nonce'],
                                                     "externalRefNumber": str(card_details['External Ref'])
                                                     + str(random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                logger.info(f"confirm response from api : {confirm_response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"current sales date and amount from portal : {current_sales_amount}")
            current_sales = " ".join([ele for ele in current_sales_amount.split()[2:] if ele != "-"]).split()

            # Converting merchant portal current sale and dates into full date format to fetch txn details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_sales[1], '%b').month
            end_month = datetime.strptime(current_sales[3], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_sales[0]))
            current_start_date_actual = current_start_date.format('YYYYMMDD')
            logger.info(f"current start date actual: {current_start_date_actual}")
            current_start_date_as_db = current_start_date.subtract(days=1)
            current_start_date_1 = current_start_date_as_db.format('YYYYMMDD') + "1830"
            logger.info(f"current start date : {current_start_date_1}")

            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_date_1 = current_end_date.subtract(days=1)
            current_date_2 = current_date_1.format('YYYYMMDD') + "1830"
            logger.info(f"current date date_1: {current_date_2}")
            current_date_actual = current_end_date.format('YYYYMMDD') + "1829"
            logger.info(f"current date date_2: {current_date_actual}")

            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')

            query = "select sum(amount) as SUM, org_code from txn where (id between '" + current_date_2[2:] + "' AND '" + \
                    current_date_actual[2:] + "') and org_code =" \
                    " '" + org_code + "' and payment_mode = 'CARD' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total card sale and org_code from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            card_sale_amt_db = result['SUM'].values[0]
            logger.info(f"card total sales from db : {float(card_sale_amt_db)}")
            org_code_db = result['org_code'].values[0]
            logger.info(f"org code from db : {org_code_db}")

            query = "select device_serial, count(*) from txn where (id between '" + current_date_2[2:] + "' AND '" + \
                    current_date_actual[2:] + "') and org_code =" \
                    " '" + org_code + "' and payment_mode = 'CARD' and status = 'AUTHORIZED' group by device_serial;"
            logger.info(f"query to fetch count of devices used from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            count_of_devices_used_db = 0
            for device_serial_value in result['device_serial']:
                logger.info(f"devices used: {device_serial_value} ")
                count_of_devices_used_db += 1
            logger.info(f"No of devices used from db : {len(result['device_serial'])}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")

            api_details = DBProcessor.get_api_details('mp_devicesusage', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1,
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for devicesUsage : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Device Usage api is: {response}")
            start_date_api = response['startDate']
            end_date_api = response['endDate']
            org_code_api = response['orgCode']
            username_api = response['username']
            stats_api = sorted(response["stats"], key=lambda x: x["date"], reverse=True)[0]
            stats_date_api = stats_api['date']
            stats_sales_volume_api = stats_api['salesVolume']
            stats_devices_used_api = stats_api['devicesUsed']

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
                    "org_code": org_code,
                    "username": login_username,
                    "start_date": this_start_date_1,
                    "end_date": this_end_date_1,
                    "stats_date": this_end_date_1,
                    "stats_sales_volume": format(card_sale_amt_db, ".2f"),
                    "stats_devices_used": str(count_of_devices_used_db)
                }

                actual_api_values = {
                    "org_code": org_code_api,
                    "username": username_api,
                    "start_date": start_date_api,
                    "end_date": end_date_api,
                    "stats_date": stats_date_api,
                    "stats_sales_volume": stats_sales_volume_api,
                    "stats_devices_used": str(stats_devices_used_api)

                }
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
                    "org_code": org_code_api,
                    "username": username_api,
                    "start_date": start_date_api,
                    "end_date": end_date_api,
                    "stats_date": stats_date_api,
                    "stats_sales_volume": stats_sales_volume_api,
                    "stats_devices_used": str(stats_devices_used_api)
                }

                actual_db_values = {
                    "org_code": org_code_db,
                    "username": login_username,
                    "start_date": this_start_date_1,
                    "end_date": this_end_date_1,
                    "stats_date": this_end_date_1,
                    "stats_sales_volume": format(card_sale_amt_db, ".2f"),
                    "stats_devices_used": str(count_of_devices_used_db)
                }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation--------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
def test_mp_700_701_019():
    """
    Sub Feature Code: UI_MP_Devices_as_country_head
    Sub Feature Description: Verifying devices details on dashboard for payment done thru device when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    019: TC019
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")

        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE14')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_username},{txn_password},{txn_org_code}")

        cred_dict = ResourceAssigner.get_org_users_using_category(txn_org_code)
        logger.debug(f"Fetched all category credentials from the ezeauto db : {cred_dict}")
        login_username = cred_dict['COUNTRY']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['COUNTRY']['password']

        query = "select org_code from org_employee where username='" + str(login_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        TestSuiteSetup.launch_browser_and_context_initialize()
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(10, 500)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api', request_body={
                                                    "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                     org_code=org_code, acquisition="HDFC",
                                                     payment_gateway="HDFC"),
                                                     "username": txn_username,
                                                     "password": txn_password,
                                                     "amount": str(amount),
                                                     "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                     "nonce": card_details['Nonce'],
                                                     "externalRefNumber": str(card_details['External Ref'])
                                                     + str(random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                logger.info(f"confirm response from api : {confirm_response}")

            txn_id = response['txnId']
            logger.debug(f"txn id from api : {txn_id}")
            status_api = confirm_response["status"]
            logger.debug(f"status from api : {status_api}")
            amount_api = float(confirm_response["amount"])
            logger.debug(f"amount from api : {amount_api}")
            payment_mode_api = confirm_response["paymentMode"]
            logger.debug(f"payment_mode from api : {payment_mode_api}")
            state_api = confirm_response["states"][0]
            logger.debug(f"state from api : {state_api}")
            settle_status_api = confirm_response['settlementStatus']
            logger.debug(f"settle_status from api : {settle_status_api}")
            org_code_api = confirm_response["orgCode"]
            logger.debug(f"org_code from api : {org_code_api}")
            date_api = confirm_response["createdTime"]
            logger.debug(f"date from api : {date_api}")
            external_ref_api = confirm_response["externalRefNumber"]
            logger.debug(f"externalRefNumber from api : {external_ref_api}")
            txn_type_api = confirm_response['txnType']
            logger.info(f"txn_type from api: {txn_type_api}")
            username_api = confirm_response['username']
            logger.debug(f"username from api : {username_api}")
            issuer_code_api = confirm_response['issuerCode']
            logger.debug(f"issuer code from api : {issuer_code_api}")
            acquirer_code_api = confirm_response['acquirerCode']
            logger.debug(f"acquirer_code from api : {acquirer_code_api}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            created_time_db = result['created_time'].values[0]
            logger.debug(f"created time from db : {created_time_db}")
            amount_db = result['amount'].values[0]
            logger.debug(f"amount from db : {amount_db}")
            external_ref_db = result['external_ref'].values[0]
            logger.debug(f"external_ref from db : {external_ref_db}")
            status_db = result['status'].values[0]
            logger.debug(f"status from db : {status_db}")
            settle_status_db = result['settlement_status'].values[0]
            logger.debug(f"settle_status from db : {settle_status_db}")
            state_db = result['state'].values[0]
            logger.debug(f"state from db : {state_db}")
            txn_type_db = result['txn_type'].values[0]
            logger.debug(f"txn_type from db : {txn_type_db}")
            org_code_db = result['org_code'].values[0]
            logger.debug(f"org_code fro  db : {org_code_db}")
            payment_mode_db = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db {payment_mode_db}")
            username_db = result['username'].values[0]
            logger.debug(f"username from db : {username_db}")
            acquirer_code_db = result['acquirer_code'].values[0]
            logger.debug(f"acquirer_code_db from db : {acquirer_code_db}")
            issuer_code_db = result['issuer_code'].values[0]
            logger.debug(f"issuer_code_db from db :{issuer_code_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")

            api_details = DBProcessor.get_api_details('mp_devices', request_body={
                "isReportingOrg": False,
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for devices: {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Devices api is: {response}")
            org_code_api = response['orgCode']
            logger.info(f"Response obtained for org_code from api is: {org_code_api}")
            username_api = response['username']
            logger.info(f"Response obtained for username from api is: {username_api}")
            total_devices_api = response['totalDevices']
            logger.info(f"Response obtained for total_devices from api is: {total_devices_api}")
            active_devices_api = response['activeDevices']
            logger.info(f"Response obtained for active_devices from api is: {active_devices_api}")
            inactive_devices_api = response['inactiveDevices']
            logger.info(f"Response obtained for inactiveDevices from api is: {inactive_devices_api}")
            # last_activity_api = response['deviceActivityDetails']['Akole']['activeDeviceDetails'][-1]['lastActivity']
            # logger.info(f"Response obtained for last_activity from api is: {last_activity_api}")
            # device_id_api = response['deviceActivityDetails']['Akole']['activeDeviceDetails'][-1]['deviceId']
            # logger.info(f"Response obtained for device_id from api is: {device_id_api}")
            # location_api = response['deviceActivityDetails']['Akole']['activeDeviceDetails'][-1]['location']
            # logger.info(f"Response obtained for location from api is: {location_api}")
            # node_id_api = response['deviceActivityDetails']['Akole']['nodeId']
            # logger.info(f"Response obtained for nodeid from api is: {node_id_api}")

            query = "select device_serial, modified_time from last_device_activity where org_code = '" + org_code + "' order by modified_time desc;"
            logger.info(f"query to fetch device_serial from last_device_activity table: {query}")
            result = DBProcessor.getValueFromDB(query)
            last_device_id_db = result['device_serial'].values[0]
            logger.info(f"latest device from db : {last_device_id_db}")
            modified_time = result['modified_time'].values[0]
            logger.info(f"latest device modified time from db : {modified_time}")
            modified_dt_object_utc = datetime.strptime(str(modified_time), "%Y-%m-%dT%H:%M:%S.%f000")
            ist_timezone = pytz.timezone("Asia/Kolkata")
            # Convert UTC datetime to IST
            modified_dt_object_utc_ist = modified_dt_object_utc.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
            # Convert to 12-hour format with AM/PM
            modified_dttime_db = modified_dt_object_utc_ist.strftime("%Y-%m-%d %I:%M:%S %p")
            logger.info(f"latest device modified time after conversion from db : {modified_dttime_db}")
            logger.info(f"count of devices fetched from db : {len(result['device_serial'])}")
            count_of_devices_used_db = 0
            for device_serial_value in result['device_serial']:
                logger.info(f"devices used: {device_serial_value} ")
                count_of_devices_used_db += 1
            logger.info(f"Total no of devices from db : {count_of_devices_used_db}")

            query = "select lda.device_serial as device from last_device_activity lda inner join device d " \
                    "on lda.device_serial=d.device_serial where lda.org_code = '" + org_code + "' and d.status = 'ACTIVE' order by lda.modified_time desc;"
            logger.info(f"query to fetch no of active devices for the org_code from db: {query}")
            result = DBProcessor.getValueFromDB(query)
            active_devices_db = len(result['device'])
            logger.info(f"No of active devices from db : {active_devices_db}")

            query = "select count(lda.device_serial) as count from last_device_activity lda inner join device d " \
                    "on lda.device_serial=d.device_serial where lda.org_code = '" + org_code + "' and d.status = 'INACTIVE' order by lda.modified_time;"
            logger.info(f"query to fetch no of active devices for the org_code from db: {query}")
            result = DBProcessor.getValueFromDB(query)
            inactive_devices_db = result['count'].values[0]
            logger.info(f"No of inactive devices from db : {inactive_devices_db}")

            query = "select id from org_structure where label_id = (select id from org_structure_label where org_code = '" + org_code + "' and label_name = 'TALUK') and org_employee_username IS NULL;"
            logger.info(f"query to fetch label_id for the org_code from db: {query}")
            result = DBProcessor.getValueFromDB(query)
            cat_node_id_db = result['id'].values[0]
            logger.info(f"node_id_db for the org_code from db: {cat_node_id_db}")

            query = "select lda.device_serial, d.node_id, d.status from last_device_activity lda inner join device d " \
                    "on lda.device_serial=d.device_serial where lda.org_code = '" + org_code + "' and d.status = 'ACTIVE' order by lda.modified_time desc;"
            logger.info(f"query to fetch device_serial,node_id,status for the org_code from db: {query}")
            result = DBProcessor.getValueFromDB(query)
            node_id_db = result['node_id'].values[0]
            logger.info(f"node id of active devices from db : {node_id_db}")

            query = "select node_name from org_structure where org_code = '" + org_code + "' and id = '" + str(node_id_db) + "';"
            logger.info(f"query to fetch node-name for the org_code from db: {query}")
            result = DBProcessor.getValueFromDB(query)
            location_db = result['node_name'].values[0]
            logger.info(f"node name of active devices from db : {location_db}")

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
                    "org_code": org_code,
                    "username": login_username,
                    "total_devices": count_of_devices_used_db,
                    "active_devices": active_devices_db,
                    "inactive_devices": inactive_devices_db,
                    # "last_activity": modified_dttime_db,
                    # "device_id": last_device_id_db,
                    # "location": location_db,
                    # "node_id" : cat_node_id_db
                }

                actual_api_values = {
                    "org_code": org_code_api,
                    "username": username_api,
                    "total_devices": total_devices_api,
                    "active_devices": active_devices_api,
                    "inactive_devices": inactive_devices_api,
                    # "last_activity": last_activity_api,
                    # "device_id": device_id_api,
                    # "location": location_api,
                    # "node_id" : node_id_api

                }
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # # -----------------------------------------End of API Validation---------------------------------------
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "org_code": org_code_api,
                    "username": username_api,
                    "total_devices": total_devices_api,
                    "active_devices": active_devices_api,
                    "inactive_devices": inactive_devices_api,
                    # "last_activity": last_activity_api,
                    # "device_id": device_id_api,
                    # "location": location_api,
                    # "node_id": node_id_api
                }

                actual_db_values = {
                    "org_code": org_code_db,
                    "username": login_username,
                    "total_devices": count_of_devices_used_db,
                    "active_devices": active_devices_db,
                    "inactive_devices": inactive_devices_db,
                    # "last_activity": modified_dttime_db,
                    # "device_id": last_device_id_db,
                    # "location": location_db,
                    # "node_id": cat_node_id_db

                }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation--------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


