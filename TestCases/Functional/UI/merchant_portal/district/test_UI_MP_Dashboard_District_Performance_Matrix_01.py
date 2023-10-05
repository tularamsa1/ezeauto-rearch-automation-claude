import operator
import random
import re
import sys
from datetime import datetime
import pendulum
import pytest
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_DashboardPage import PortalDashboardPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
def test_mp_700_704_062():
    """
    Sub Feature Code: UI_MP_Performance_Matrix_for_Top_10_as_District_head
    Sub Feature Description: Verifying Performance Matrix for TOP 10 performers when District head has logged in for all lower level hierarchies having less than 20 nodes
    TC naming code description:
    700: Merchant Portal
    704: District
    062: TC062
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE16')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        login_cred = ResourceAssigner.get_org_users_login_Credentials('DISTRICT', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

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

            amount = random.randint(50, 150)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "order_id": order_id,
                "amount": str(amount)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cash txn via api : {response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"current sales date and amount from portal : {current_sales_amount}")
            current_sales = " ".join([ele for ele in current_sales_amount.split()[2:] if ele != "-"]).split()

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_sales[1], '%b').month
            end_month = datetime.strptime(current_sales[3], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_sales[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format("YYMMDD") + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_end_date_1 = current_end_date.format("YYMMDD") + "1829"

            query = "select org_employee_username from org_structure where org_code = '" + org_code + "';"
            logger.debug(f"Query to txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            usernames = [str(result.values[i]).strip("[]") for i in range(58) if result.values[i] != None]

            node_names = []
            for username in usernames:
                query = "select node_name from org_structure where org_employee_username = " + username + ";"
                result = DBProcessor.getValueFromDB(query)
                node_names.append(str(result.values[0]))

            total_amount_all_performer = []
            for username in usernames:
                query = "select sum(amount) from txn where" \
                        " id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and org_code = '" + org_code + "' and username = " + username + " and status = 'AUTHORIZED';"
                logger.debug(f"Query to txn details from database : {query}")
                result = DBProcessor.getValueFromDB(query)
                amount = ["0.0" if result.values[0][0] == None else result.values[0][0]]
                total_amount_all_performer.append(str(amount[0]))

            names_and_volumes = {}
            for name, values in zip(node_names, total_amount_all_performer):
                names_and_volumes[str(name).strip('[]')] = float(values)
            categories = ["'India'", "'West'", "'Maharastra'", "'Mumbai_City_District'"]
            for category in categories:
                del names_and_volumes[category]
            top_performer_db = sum(names_and_volumes.values())
            top_performer_db_1 = "name :" + 'Akole' + " , volume :" + str(top_performer_db)
            logger.debug(f"top performer name and volume from db : {top_performer_db_1}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_performance_matrix', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1,
                "labelId": "0"})
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for profile is: {response}")

            names = []
            amounts = []
            len1 = len(response['graphDetails'][0]['dataPoints'])
            for i in range(len1):
                for _ in response['graphDetails'][0]['dataPoints']:
                    name = response['graphDetails'][0]['dataPoints'][i]['name']
                    names.append(name)
                    amount = response['graphDetails'][0]['dataPoints'][i]['volume']
                    amounts.append(amount)
                    break

            top_performer_api = "name :" + names[0] + " , volume :" + amount
            logger.debug(f"top performer name and volume from api : {top_performer_api}")
            color_code_api = response['graphDetails'][0]['colorCode']
            logger.debug(f"color code of top performer from api : {color_code_api}")

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
                    "colorCode": '#BBE1BB',
                    "top_performer": top_performer_db_1
                }

                actual_api_values = {
                    "colorCode": color_code_api,
                    "top_performer": top_performer_api
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
                    "colorCode": color_code_api,
                    "top_performer": top_performer_api
                }

                actual_db_values = {
                    "colorCode": '#BBE1BB',
                    "top_performer": top_performer_db_1
                }
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
@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
def test_mp_700_704_063():
    """
    Sub Feature Code: UI_MP_Performance_Matrix_for_Top_10_and_Bottom_10_as_District_head
    Sub Feature Description: Verifying Performance Matrix for TOP 10  and BOTTOM 10 performers when District head has logged in for all lower level hierarchies having only more than 20 nodes
    TC naming code description:
    700: Merchant Portal
    704: District
    063: TC063
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE17')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        login_cred = ResourceAssigner.get_org_users_login_Credentials('DISTRICT', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

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

            amount = random.randint(50, 150)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "order_id": order_id,
                "amount": str(amount)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cash txn via api : {response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"current sales date and amount from portal : {current_sales_amount}")
            current_sales = " ".join([ele for ele in current_sales_amount.split()[2:] if ele != "-"]).split()

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_sales[1], '%b').month
            end_month = datetime.strptime(current_sales[3], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_sales[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format("YYMMDD") + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_end_date_1 = current_end_date.format("YYMMDD") + "1829"

            query = "select org_employee_username from org_structure where org_code = '" + org_code + "';"
            logger.debug(f"Query to txn details from database : {query}")
            result = DBProcessor.getValueFromDB(query)
            usernames = [str(result.values[i]).strip("[]") for i in range(58) if result.values[i] != None]

            node_names = []
            for username in usernames:
                query = "select node_name from org_structure where org_employee_username = " + username + ";"
                result = DBProcessor.getValueFromDB(query)
                node_names.append(str(result.values[0]))

            total_amount_all_performer = []
            for username in usernames:
                query = "select sum(amount) from txn where" \
                        " id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and org_code = '" + org_code + "' and username = " + username + " and status = 'AUTHORIZED';"
                logger.debug(f"Query to txn details from database : {query}")
                result = DBProcessor.getValueFromDB(query)
                amount = ["0.0" if result.values[0][0] == None else result.values[0][0]]
                total_amount_all_performer.append(str(amount[0]))

            names_and_volumes = {}
            for name, values in zip(node_names, total_amount_all_performer):
                names_and_volumes[str(name).strip('[]')] = float(values)
            pattern = r"""[\[\]"']+"""
            top_to_bottom_all_performers_1 = {}
            for name, volume in names_and_volumes.items():
                formatted_key = re.sub(pattern, "", name)
                if formatted_key.title().startswith("Store"):
                    top_to_bottom_all_performers_1[formatted_key] = volume
            top_to_bottom_all_performers = dict(
                sorted(top_to_bottom_all_performers_1.items(), key=operator.itemgetter(1), reverse=True))

            node_names_db = []
            volumes_db = []
            for name, volume in top_to_bottom_all_performers.items():
                node_names_db.append(name)
                volumes_db.append(volume)

            top_performer_db_1 = "name :" + node_names_db[0] + " , volume :" + str(volumes_db[0])
            logger.debug(f"top_1 performer name and volume from db : {top_performer_db_1}")
            top_performer_db_2 = "name :" + node_names_db[1] + " , volume :" + str(volumes_db[1])
            logger.debug(f"top_2 performer name and volume from db : {top_performer_db_2}")
            top_performer_db_3 = "name :" + node_names_db[2] + " , volume :" + str(volumes_db[2])
            logger.debug(f"top_3 performer name and volume from db : {top_performer_db_3}")
            top_performer_db_4 = "name :" + node_names_db[3] + " , volume :" + str(volumes_db[3])
            logger.debug(f"top_4 performer name and volume from db : {top_performer_db_4}")
            top_performer_db_5 = "name :" + node_names_db[4] + " , volume :" + str(volumes_db[4])
            logger.debug(f"top_5 performer name and volume from db : {top_performer_db_5}")
            top_performer_db_6 = "name :" + node_names_db[5] + " , volume :" + str(volumes_db[5])
            logger.debug(f"top_6 performer name and volume from db : {top_performer_db_6}")
            top_performer_db_7 = "name :" + node_names_db[6] + " , volume :" + str(volumes_db[6])
            logger.debug(f"top_7 performer name and volume from db : {top_performer_db_7}")
            top_performer_db_8 = "name :" + node_names_db[7] + " , volume :" + str(volumes_db[7])
            logger.debug(f"top_8 performer name and volume from db : {top_performer_db_8}")
            top_performer_db_9 = "name :" + node_names_db[8] + " , volume :" + str(volumes_db[8])
            logger.debug(f"top_9 performer name and volume from db : {top_performer_db_9}")
            top_performer_db_10 = "name :" + node_names_db[9] + " , volume :" + str(volumes_db[9])
            logger.debug(f"top_10 performer name and volume from db : {top_performer_db_10}")

            bottom_performer_db_1 = "name :" + node_names_db[-1] + " , volume :" + str(volumes_db[-1])
            logger.debug(f"bottom_1 performer name and volume from db : {bottom_performer_db_1}")
            bottom_performer_db_2 = "name :" + node_names_db[-2] + " , volume :" + str(volumes_db[-2])
            logger.debug(f"bottom_2 performer name and volume from db : {bottom_performer_db_2}")
            bottom_performer_db_3 = "name :" + node_names_db[-3] + " , volume :" + str(volumes_db[-3])
            logger.debug(f"bottom_3 performer name and volume from db : {bottom_performer_db_3}")
            bottom_performer_db_4 = "name :" + node_names_db[-4] + " , volume :" + str(volumes_db[-4])
            logger.debug(f"bottom_4 performer name and volume from db : {bottom_performer_db_4}")
            bottom_performer_db_5 = "name :" + node_names_db[-5] + " , volume :" + str(volumes_db[-5])
            logger.debug(f"bottom_5 performer name and volume from db : {bottom_performer_db_5}")
            bottom_performer_db_6 = "name :" + node_names_db[-6] + " , volume :" + str(volumes_db[-6])
            logger.debug(f"bottom_6 performer name and volume from db : {bottom_performer_db_6}")
            bottom_performer_db_7 = "name :" + node_names_db[-7] + " , volume :" + str(volumes_db[-7])
            logger.debug(f"bottom_7 performer name and volume from db : {bottom_performer_db_7}")
            bottom_performer_db_8 = "name :" + node_names_db[-8] + " , volume :" + str(volumes_db[-8])
            logger.debug(f"bottom_8 performer name and volume from db : {bottom_performer_db_8}")
            bottom_performer_db_9 = "name :" + node_names_db[-9] + " , volume :" + str(volumes_db[-9])
            logger.debug(f"bottom_9 performer name and volume from db : {bottom_performer_db_9}")
            bottom_performer_db_10 = "name :" + node_names_db[-10] + " , volume :" + str(volumes_db[-10])
            logger.debug(f"bottom_10 performer name and volume from db : {bottom_performer_db_10}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_performance_matrix', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1,
                "labelId": "3"})
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for performer is: {response}")

            top_performer_names = []
            top_performer_volumes = []
            len1 = len(response['graphDetails'][0]['dataPoints'])
            for i in range(len1):
                for _ in response['graphDetails'][0]['dataPoints']:
                    name = response['graphDetails'][0]['dataPoints'][i]['name']
                    top_performer_names.append(name)
                    amount = response['graphDetails'][0]['dataPoints'][i]['volume']
                    top_performer_volumes.append(amount)
                    break

            bottom_performer_names = []
            bottom_performer_volumes = []
            len1 = len(response['graphDetails'][1]['dataPoints'])
            for i in range(len1):
                for _ in response['graphDetails'][1]['dataPoints']:
                    name = response['graphDetails'][1]['dataPoints'][i]['name']
                    bottom_performer_names.append(name)
                    amount = response['graphDetails'][1]['dataPoints'][i]['volume']
                    bottom_performer_volumes.append(amount)
                    break

            top_performer_color_code_api = response['graphDetails'][0]['colorCode']
            logger.debug(f"top performer color code of top performer from api : {top_performer_color_code_api}")
            top_performer_api_1 = "name :" + top_performer_names[0] + " , volume :" + top_performer_volumes[0]
            logger.debug(f"top_1 performer name and volume from api : {top_performer_api_1}")
            top_performer_api_2 = "name :" + top_performer_names[1] + " , volume :" + top_performer_volumes[1]
            logger.debug(f"top_2 performer name and volume from api : {top_performer_api_2}")
            top_performer_api_3 = "name :" + top_performer_names[2] + " , volume :" + top_performer_volumes[2]
            logger.debug(f"top_3 performer name and volume from api : {top_performer_api_3}")
            top_performer_api_4 = "name :" + top_performer_names[3] + " , volume :" + top_performer_volumes[3]
            logger.debug(f"top_4 performer name and volume from api : {top_performer_api_4}")
            top_performer_api_5 = "name :" + top_performer_names[4] + " , volume :" + top_performer_volumes[4]
            logger.debug(f"top_5 performer name and volume from api : {top_performer_api_5}")
            top_performer_api_6 = "name :" + top_performer_names[5] + " , volume :" + top_performer_volumes[5]
            logger.debug(f"top_6 performer name and volume from api : {top_performer_api_6}")
            top_performer_api_7 = "name :" + top_performer_names[6] + " , volume :" + top_performer_volumes[6]
            logger.debug(f"top_7 performer name and volume from api : {top_performer_api_7}")
            top_performer_api_8 = "name :" + top_performer_names[7] + " , volume :" + top_performer_volumes[7]
            logger.debug(f"top_8 performer name and volume from api : {top_performer_api_8}")
            top_performer_api_9 = "name :" + top_performer_names[8] + " , volume :" + top_performer_volumes[8]
            logger.debug(f"top_9 performer name and volume from api : {top_performer_api_9}")
            top_performer_api_10 = "name :" + top_performer_names[9] + " , volume :" + top_performer_volumes[9]
            logger.debug(f"top_10 performer name and volume from api : {top_performer_api_10}")

            bottom_performer_color_code_api = response['graphDetails'][1]['colorCode']
            logger.debug(f"bottom performer color code of top performer from api : {bottom_performer_color_code_api}")
            bottom_performer_api_1 = "name :" + bottom_performer_names[0] + " , volume :" + bottom_performer_volumes[0]
            logger.debug(f"bottom_1 performer name and volume from api : {bottom_performer_api_1}")
            bottom_performer_api_2 = "name :" + bottom_performer_names[1] + " , volume :" + bottom_performer_volumes[1]
            logger.debug(f"bottom_2 performer name and volume from api : {bottom_performer_api_2}")
            bottom_performer_api_3 = "name :" + bottom_performer_names[2] + " , volume :" + bottom_performer_volumes[2]
            logger.debug(f"bottom_3 performer name and volume from api : {bottom_performer_api_3}")
            bottom_performer_api_4 = "name :" + bottom_performer_names[3] + " , volume :" + bottom_performer_volumes[3]
            logger.debug(f"tbottom_4 performer name and volume from api : {bottom_performer_api_4}")
            bottom_performer_api_5 = "name :" + bottom_performer_names[4] + " , volume :" + bottom_performer_volumes[4]
            logger.debug(f"bottom_5 performer name and volume from api : {bottom_performer_api_5}")
            bottom_performer_api_6 = "name :" + bottom_performer_names[5] + " , volume :" + bottom_performer_volumes[5]
            logger.debug(f"bottom_6 performer name and volume from api : {bottom_performer_api_6}")
            bottom_performer_api_7 = "name :" + bottom_performer_names[6] + " , volume :" + bottom_performer_volumes[6]
            logger.debug(f"bottom_7 performer name and volume from api : {bottom_performer_api_7}")
            bottom_performer_api_8 = "name :" + bottom_performer_names[7] + " , volume :" + bottom_performer_volumes[7]
            logger.debug(f"bottom_8 performer name and volume from api : {bottom_performer_api_8}")
            bottom_performer_api_9 = "name :" + bottom_performer_names[8] + " , volume :" + bottom_performer_volumes[8]
            logger.debug(f"bottom_9 performer name and volume from api : {bottom_performer_api_9}")
            bottom_performer_api_10 = "name :" + bottom_performer_names[9] + " , volume :" + bottom_performer_volumes[9]
            logger.debug(f"bottom_10 performer name and volume from api : {bottom_performer_api_10}")

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
                    "top_colorCode": '#BBE1BB',
                    "top_performer_1": top_performer_db_1,
                    "top_performer_2": top_performer_db_2,
                    "top_performer_3": top_performer_db_3,
                    "top_performer_4": top_performer_db_4,
                    "top_performer_5": top_performer_db_5,
                    "top_performer_6": top_performer_db_6,
                    "top_performer_7": top_performer_db_7,
                    "top_performer_8": top_performer_db_8,
                    "top_performer_9": top_performer_db_9,
                    "top_performer_10": top_performer_db_10,
                    'bottom_colorCode': '#FFC8C8',
                    "bottom_performer_1": bottom_performer_db_1,
                    "bottom_performer_2": bottom_performer_db_2,
                    "bottom_performer_3": bottom_performer_db_3,
                    "bottom_performer_4": bottom_performer_db_4,
                    "bottom_performer_5": bottom_performer_db_5,
                    "bottom_performer_6": bottom_performer_db_6,
                    "bottom_performer_7": bottom_performer_db_7,
                    "bottom_performer_8": bottom_performer_db_8,
                    "bottom_performer_9": bottom_performer_db_9,
                    "bottom_performer_10": bottom_performer_db_10
                }

                actual_api_values = {
                    "top_colorCode": top_performer_color_code_api,
                    "top_performer_1": top_performer_api_1,
                    "top_performer_2": top_performer_api_2,
                    "top_performer_3": top_performer_api_3,
                    "top_performer_4": top_performer_api_4,
                    "top_performer_5": top_performer_api_5,
                    "top_performer_6": top_performer_api_6,
                    "top_performer_7": top_performer_api_7,
                    "top_performer_8": top_performer_api_8,
                    "top_performer_9": top_performer_api_9,
                    "top_performer_10": top_performer_api_10,
                    'bottom_colorCode': bottom_performer_color_code_api,
                    "bottom_performer_1": bottom_performer_api_1,
                    "bottom_performer_2": bottom_performer_api_2,
                    "bottom_performer_3": bottom_performer_api_3,
                    "bottom_performer_4": bottom_performer_api_4,
                    "bottom_performer_5": bottom_performer_api_5,
                    "bottom_performer_6": bottom_performer_api_6,
                    "bottom_performer_7": bottom_performer_api_7,
                    "bottom_performer_8": bottom_performer_api_8,
                    "bottom_performer_9": bottom_performer_api_9,
                    "bottom_performer_10": bottom_performer_api_10,
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
                    "top_colorCode": top_performer_color_code_api,
                    "top_performer_1": top_performer_api_1,
                    "top_performer_2": top_performer_api_2,
                    "top_performer_3": top_performer_api_3,
                    "top_performer_4": top_performer_api_4,
                    "top_performer_5": top_performer_api_5,
                    "top_performer_6": top_performer_api_6,
                    "top_performer_7": top_performer_api_7,
                    "top_performer_8": top_performer_api_8,
                    "top_performer_9": top_performer_api_9,
                    "top_performer_10": top_performer_api_10,
                    'bottom_colorCode': bottom_performer_color_code_api,
                    "bottom_performer_1": bottom_performer_api_1,
                    "bottom_performer_2": bottom_performer_api_2,
                    "bottom_performer_3": bottom_performer_api_3,
                    "bottom_performer_4": bottom_performer_api_4,
                    "bottom_performer_5": bottom_performer_api_5,
                    "bottom_performer_6": bottom_performer_api_6,
                    "bottom_performer_7": bottom_performer_api_7,
                    "bottom_performer_8": bottom_performer_api_8,
                    "bottom_performer_9": bottom_performer_api_9,
                    "bottom_performer_10": bottom_performer_api_10,
                }

                actual_db_values = {
                    "top_colorCode": '#BBE1BB',
                    "top_performer_1": top_performer_db_1,
                    "top_performer_2": top_performer_db_2,
                    "top_performer_3": top_performer_db_3,
                    "top_performer_4": top_performer_db_4,
                    "top_performer_5": top_performer_db_5,
                    "top_performer_6": top_performer_db_6,
                    "top_performer_7": top_performer_db_7,
                    "top_performer_8": top_performer_db_8,
                    "top_performer_9": top_performer_db_9,
                    "top_performer_10": top_performer_db_10,
                    'bottom_colorCode': '#FFC8C8',
                    "bottom_performer_1": bottom_performer_db_1,
                    "bottom_performer_2": bottom_performer_db_2,
                    "bottom_performer_3": bottom_performer_db_3,
                    "bottom_performer_4": bottom_performer_db_4,
                    "bottom_performer_5": bottom_performer_db_5,
                    "bottom_performer_6": bottom_performer_db_6,
                    "bottom_performer_7": bottom_performer_db_7,
                    "bottom_performer_8": bottom_performer_db_8,
                    "bottom_performer_9": bottom_performer_db_9,
                    "bottom_performer_10": bottom_performer_db_10
                }
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
