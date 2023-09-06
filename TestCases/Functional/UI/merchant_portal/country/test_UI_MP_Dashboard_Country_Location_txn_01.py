from datetime import datetime
import random
import sys
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
def test_mp_700_701_006():
    """
    Sub Feature Code: UI_MP_Calender_txn_for_specific_location_using_dropdown_values_as_country_head
    Sub Feature Description: Verifying txn details on dashboard  for specific location using dropdown values when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    006: TC006
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE1')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        login_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
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

            amount = random.randint(200, 600)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "order_id": order_id,
                "amount": str(amount)
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cash txn via api : {response}")

            query = "select org_employee_username from org_structure where node_name = 'India'" \
                    " and org_code = '" + org_code + "' and org_employee_username is NOT NULL;"
            logger.debug(f"query to fetch username from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            username_db = str(result.values[0]).strip("[]/'")
            logger.debug(f"username from db : {username_db}")

            query = "select node_name from org_structure where org_employee_username = '" + txn_username + "';"
            logger.debug(f"query to fetch node_name id from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            node_name = str(result).split()[-1]
            logger.debug(f"node name from db : {node_name}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            location_hierarchy = ["India", "West", "Maharastra", "Mumbai_City_District", "Akole", "Mumbai1", "Hub1",
                                  str(node_name)]
            logger.info(f"list of hierarchy level of particular location")
            portal_dashboard_page.select_location_by_values(location_hierarchy)

            current_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"current sales date and amount from portal : {current_sales_amount}")
            current_sales = " ".join([ele for ele in current_sales_amount.split()[2:] if ele != "-"]).split()

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_sales[1], '%b').month
            end_month = datetime.strptime(current_sales[3], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_sales[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            logger.info(f"current start date_1 : {current_start_date_1}")
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"
            logger.info(f"current end date : {current_end_date_1}")

            # Fetching total sales of current from DB
            query = "select sum(amount) from txn where id between '" + current_start_date_1 + "' AND '" \
                    + current_end_date_1 + "' and org_code='" + org_code + "' and username = '" + txn_username + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of current : {query}")
            result = DBProcessor.getValueFromDB(query)
            current_total_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.debug(f"current total sales from DB : {current_total_sales_db}")

            query = "select count(*) from txn where id between '" + current_start_date_1 + "' AND '" \
                    + current_end_date_1 + "' and org_code='" + org_code + "' and username = '" + txn_username + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of current : {query}")
            result = DBProcessor.getValueFromDB(query)
            current_total_txns_db = str(result.values[0]).strip("[]")
            logger.debug(f"current total txns from DB : {current_total_txns_db}")

            query = "select parent_node_id from org_structure where " \
                    "org_code = '" + org_code + "' and org_employee_username = '" + txn_username + "' and node_name = '" + node_name + "';"
            logger.debug(f"query to fetch parent node id from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            parent_node_id = str(result).split()[-1]
            logger.debug(f"parent node from db is : {parent_node_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            current_start_date_1 = current_start_date.format('YYYY-MM-DD')
            current_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": current_start_date_1,
                "endDate": current_end_date_1,
                "nodeIds": [parent_node_id]
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")

            current_total_amount_api = sum([float(element['amount']) for element in response['aggregatedTxnResults']])
            logger.info(f"current total sale from api  :{current_total_amount_api}")
            total_number_of_txns_api = 0
            txn_by_type = ['bqr', 'cash', 'cheque', 'cnp', 'nbfc', 'upi', 'wallet']
            txn_by_type_cards = ['credit', 'debit', 'others']
            for by_type in txn_by_type:
                total_number_of_txns_api += sum([ele[by_type]['count'] for ele in response['aggregatedTxnResults']])
            for card_type in txn_by_type_cards:
                total_number_of_txns_api += sum(
                    [ele['cards'][card_type]['count'] for ele in response['aggregatedTxnResults']])
            logger.info(f"total number of txns of {node_name} : {total_number_of_txns_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")

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
                    "total_sale": current_total_sales_db[0],
                    "total_txns": current_total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "total_sale": str(current_total_amount_api),
                    "total_txns": str(total_number_of_txns_api),
                    "org_code": org_code_api_1,
                    "username": username_api_1
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
                    "total_sale": str(current_total_amount_api),
                    "total_txns": str(total_number_of_txns_api),
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "total_sale": current_total_sales_db[0],
                    "total_txns": current_total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {
                    "total_sales": current_total_sales_db[0] + "0",
                    "total_txns": current_total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }

                total_sales = portal_dashboard_page.fetch_total_sales()
                portal_total_sales = "".join([i for i in total_sales.split()[1] if i != ","])
                logger.info(f"total sales from portal : {portal_total_sales}")
                portal_total_txns = portal_dashboard_page.fetch_total_number_of_txns()
                logger.info(f"total txns from portal : {portal_total_txns}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")

                actual_portal_values = {
                    "total_sales": portal_total_sales,
                    "total_txns": portal_total_txns,
                    "org_code": portal_merchant_details[0],
                    "username": portal_merchant_details[-1]
                }
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

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
def test_mp_700_701_007():
    """
    Sub Feature Code: UI_MP_Calender_txn_for_specific_location_using_search_option_as_country_head
    Sub Feature Description: Verifying txn details on dashboard  for specific location using search option when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    007: TC007
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE5')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        login_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
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

            amount = random.randint(50, 250)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "order_id": order_id,
                "amount": str(amount)
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cash txn via api : {response}")

            query = "select org_employee_username from org_structure where node_name = 'India'" \
                    " and org_code = '" + org_code + "' and org_employee_username is NOT NULL;"
            logger.debug(f"query to fetch username from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            username_db = str(result.values[0]).strip("[]/'")
            logger.debug(f"username from db : {username_db}")

            query = "select node_name from org_structure where org_employee_username = '" + txn_username + "';"
            logger.debug(f"query to fetch node name from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            node_name = str(result).split()[-1]
            logger.debug(f"node name from db : {node_name}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            logger.info(f"list of hierarchy level of particular location")
            portal_dashboard_page.select_location_by_search_box(node_name)

            current_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"current sales date and amount from portal : {current_sales_amount}")
            current_sales = " ".join([ele for ele in current_sales_amount.split()[2:] if ele != "-"]).split()

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_sales[1], '%b').month
            end_month = datetime.strptime(current_sales[3], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_sales[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            logger.info(f"current start date_1 : {current_start_date_1}")
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"
            logger.info(f"current end date : {current_end_date_1}")

            query = "select sum(amount) from txn where username  = '" + txn_username + "' and status = 'AUTHORIZED';"
            logger.debug(f"query to fetch total sales from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_sales_db = str(result).split()[-1]
            logger.debug(f"total sales from db : {total_sales_db}")

            query = "select count(*) from txn where username  = '" + txn_username + "' and status = 'AUTHORIZED';"
            logger.debug(f"query to fetch total number of txns from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_txns_db = str(result).split()[-1]
            logger.debug(f"total number of txns : {total_txns_db}")

            query = "select parent_node_id from org_structure where " \
                    "org_code = '" + org_code + "' and org_employee_username = '" + txn_username + "' and node_name = '" + node_name + "';"
            logger.debug(f"query to fetch parent node id from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            parent_node_id = str(result).split()[-1]
            logger.debug(f"parent node from db is : {parent_node_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            current_start_date_1 = current_start_date.format('YYYY-MM-DD')
            current_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": current_start_date_1,
                "endDate": current_end_date_1,
                "nodeIds": [parent_node_id]
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")

            current_total_amount_api = sum(
                [float(element['amount']) for element in response['aggregatedTxnResults']])
            logger.info(f"current total sale from api  :{current_total_amount_api}")
            total_number_of_txns = 0
            txn_by_type = ['bqr', 'cash', 'cheque', 'cnp', 'nbfc', 'upi', 'wallet']
            txn_by_type_cards = ['credit', 'debit', 'others']
            for by_type in txn_by_type:
                total_number_of_txns += sum([ele[by_type]['count'] for ele in response['aggregatedTxnResults']])
            for card_type in txn_by_type_cards:
                total_number_of_txns += sum(
                    [ele['cards'][card_type]['count'] for ele in response['aggregatedTxnResults']])
            logger.info(f"total number of txns of {node_name} : {total_number_of_txns}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")

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
                    "total_sale": total_sales_db,
                    "total_txns": total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "total_sale": str(current_total_amount_api),
                    "total_txns": str(total_number_of_txns),
                    "org_code": org_code_api_1,
                    "username": username_api_1
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
                    "total_sale": str(current_total_amount_api),
                    "total_txns": str(total_number_of_txns),
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "total_sale": total_sales_db,
                    "total_txns": total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                expected_portal_values = {
                    "total_sales": total_sales_db + "0",
                    "total_txns": total_txns_db,
                    "org_code": org_code,
                    "username": username_db
                }

                total_sales = portal_dashboard_page.fetch_total_sales()
                portal_total_sales = "".join([i for i in total_sales.split()[1] if i != ","])
                logger.info(f"total sales from portal : {portal_total_sales}")
                portal_total_txns = portal_dashboard_page.fetch_total_number_of_txns()
                logger.info(f"total txns from portal : {portal_total_txns}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")

                actual_portal_values = {
                    "total_sales": portal_total_sales,
                    "total_txns": portal_total_txns,
                    "org_code": portal_merchant_details[0],
                    "username": portal_merchant_details[-1]
                }
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
                                                actualPortal=actual_portal_values)
            except Exception as e:
                Configuration.perform_portal_val_exception(testcase_id, e)
            logger.info(f"Completed Portal validation for the test case : {testcase_id}")
        # -----------------------------------------End of Portal Validation---------------------------------------

        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


