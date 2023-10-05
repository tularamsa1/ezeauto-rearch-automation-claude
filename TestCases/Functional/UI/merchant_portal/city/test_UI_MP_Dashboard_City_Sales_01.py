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
def test_mp_700_706_001():
    """
    Sub Feature Code: UI_MP_Dashboard_Sales_as_City_head
    Sub Feature Description: Verifying Total sales, Total Txns and hierarchy details for Upper hierarchy when logged in as City Head
    TC naming code description:
    700: Merchant Portal
    706: City
    001: TC001
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'CASHIER')
        logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
        txn_username = txn_cred['Username']
        txn_password = txn_cred['Password']
        txn_org_code = txn_cred['Merchant_Code']

        cred_dict = ResourceAssigner.get_org_users_using_category(txn_org_code)
        logger.debug(f"Fetched all category credentials from the ezeauto db : {cred_dict}")
        login_username = cred_dict['CITY']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['CITY']['password']
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")
        country_username = cred_dict['COUNTRY']['username']
        logger.debug(f"Fetched country_username credentials from the ezeauto db : {country_username}")
        region_username = cred_dict['REGION']['username']
        logger.debug(f"Fetched region_username credentials from the ezeauto db : {region_username}")
        state_username = cred_dict['STATE']['username']
        logger.debug(f"Fetched state_username credentials from the ezeauto db : {state_username}")
        district_username = cred_dict['DISTRICT']['username']
        logger.debug(f"Fetched district_username credentials from the ezeauto db : {district_username}")
        taluk_username = cred_dict['TALUK']['username']
        logger.debug(f"Fetched taluk_username credentials from the ezeauto db : {taluk_username}")

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
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_sales[2]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"

            query = "select sum(amount) from txn where" \
                    " org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + \
                    "' and '" + current_end_date_1 + "' and username not in ('" + country_username + "', '" + region_username + "', '" + state_username + "', '" + taluk_username + "', '" + district_username + "');"
            logger.debug(f"query to fetch total sales from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_sales_db = str(float(result.values[0]))
            logger.debug(f"total sales from db : {total_sales_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 +\
                    "' and '" + current_end_date_1 + "' and username not in ('" + country_username + "', '" + region_username + "', '" + state_username + "', '" + taluk_username + "', '" + district_username + "');"
            logger.debug(f"query to fetch total number of txns from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            total_txns_db = str(result.values[0]).strip("[]")
            logger.debug(f"total sales from db : {total_sales_db}")

            query = "select parent_node_id from org_structure where " \
                    "org_code = '" + org_code + "' and org_employee_username = '" + login_username + "';"
            logger.debug(f"query to fetch parent node id from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            parent_node_id = result.values[0]
            logger.debug(f"parent node from db is : {parent_node_id}")

            query = "select count(*) from org_structure where org_code = '" + org_code + "'" \
                    " and node_name like 'Store%' and org_employee_username is not NULL;"
            logger.debug(f"query to fetch number of stores from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_store_db = result.values[0]
            logger.debug(f"number of org stores from db  : {org_store_db}")

            query = "select count(*) from org_structure where org_code = '" + org_code + "'" \
                    " and node_name like 'Hub%' and org_employee_username is not NULL;"
            logger.debug(f"query to fetch number of hubs from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_hub_db = result.values[0]
            logger.debug(f"number of org HUB from db  : {org_hub_db}")

            query = "select count(*) from org_structure where org_code = '" + org_code + "'" \
                    " and node_name like 'Cashier%' and org_employee_username is not NULL;"
            logger.debug(f"query to fetch number of cashiers from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            org_cashier_db = result.values[0]
            logger.debug(f"number of org Cashiers from db  : {org_cashier_db}")

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
                "nodeIds": [parent_node_id[0]]
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")

            total_sale_amount_api = sum(
                [float(element['amount']) for element in response['aggregatedTxnResults']])
            logger.info(f"total sale from api  :{total_sale_amount_api}")
            total_number_of_txns_api = 0
            txn_by_type = ['bqr', 'cash', 'cheque', 'cnp', 'nbfc', 'upi', 'wallet']
            txn_by_type_cards = ['credit', 'debit', 'others']
            for by_type in txn_by_type:
                total_number_of_txns_api += sum([ele[by_type]['count'] for ele in response['aggregatedTxnResults']])
            for card_type in txn_by_type_cards:
                total_number_of_txns_api += sum(
                    [ele['cards'][card_type]['count'] for ele in response['aggregatedTxnResults']])
            logger.info(f"total number of txns of : {total_number_of_txns_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")

            org_cashier_api = response['hierarchy']['hierarchy'][0]['count']
            org_store_api = response['hierarchy']['hierarchy'][1]['count']
            org_hub_api = response['hierarchy']['hierarchy'][2]['count']
            logger.info(f"org hierarchy of number of org_cashier_api : {org_cashier_api},"
                        f" org_store_api : {org_store_api}, arg_hub_api : {org_hub_api}")

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
                    "cashier": str(org_cashier_db[0]),
                    "store": str(org_store_db[0]),
                    "hub": str(org_hub_db[0])
                }

                actual_api_values = {
                    "total_sale": str(total_sale_amount_api),
                    "total_txns": str(total_number_of_txns_api),
                    "org_code": org_code_api_1,
                    "cashier": org_cashier_api,
                    "store": org_store_api,
                    "hub": org_hub_api
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
                    "total_sale": str(total_sale_amount_api),
                    "total_txns": str(total_number_of_txns_api),
                    "org_code": org_code_api_1,
                    "cashier": org_cashier_api,
                    "store": org_store_api,
                    "hub": org_hub_api
                }

                actual_db_values = {
                    "total_sale": total_sales_db,
                    "total_txns": total_txns_db,
                    "org_code": org_code,
                    "cashier": str(org_cashier_db[0]),
                    "store": str(org_store_db[0]),
                    "hub": str(org_hub_db[0])
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
                    "cashier": str(org_cashier_db[0]),
                    "store": str(org_store_db[0]),
                    "hub": str(org_hub_db[0])
                }

                total_sales = portal_dashboard_page.fetch_total_sales()
                portal_total_sales = "".join([i for i in total_sales.split()[1] if i != ","])
                logger.info(f"total sales from portal : {portal_total_sales}")
                portal_total_txns = portal_dashboard_page.fetch_total_number_of_txns()
                logger.info(f"total txns from portal : {portal_total_txns}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")
                portal_org_hierarchy = portal_dashboard_page.fetch_org_structure()
                portal_cashier = portal_org_hierarchy[0].split("-")[1]
                portal_store = portal_org_hierarchy[1].split("-")[1]
                portal_hub = portal_org_hierarchy[2].split("-")[1]
                logger.info(f"portal org hierarchy portal_cashier:{portal_cashier}, portal_store : {portal_store},"
                            f"portal_hub: {portal_hub}")

                actual_portal_values = {
                    "total_sales": portal_total_sales,
                    "total_txns": portal_total_txns,
                    "org_code": portal_merchant_details[0],
                    "cashier": portal_cashier,
                    "store": portal_store,
                    "hub": portal_hub
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
