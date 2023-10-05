import random
import pendulum
import sys
import pytest
from datetime import datetime
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
def test_mp_700_701_002():
    """
    Sub Feature Code: UI_MP_Calender_txn_for_This_Week_as_country_head
    Sub Feature Description: Verifying sales over with previous comparision for This Week calender dates when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    002: TC002
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE2')
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

            query = "select org_employee_username from org_structure where node_name = 'India'" \
                    " and org_code = '" + org_code + "' and org_employee_username is NOT NULL;"
            logger.debug(f"query to fetch username from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            username_db = str(result.values[0]).strip("[]/'")
            logger.debug(f"username from db : {username_db}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            portal_dashboard_page.click_calendar()
            portal_dashboard_page.select_txn_period_for_this_week()

            previous_week_sales_date_amount = portal_dashboard_page.fetch_previous_sales_dates_and_amount()
            logger.info(f"last previous week sales date and amount from portal : {previous_week_sales_date_amount}")
            previous_week_sales = " ".join(
                [ele for ele in previous_week_sales_date_amount.split()[2:] if ele != "-"]).split()
            logger.debug(f"list of previous week sale from portal : {previous_week_sales}")
            this_week_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"this week sales date and amount from portal : {this_week_sales_amount}")
            this_week_sales = " ".join([ele for ele in this_week_sales_amount.split()[2:] if ele != "-"]).split()
            logger.debug(f"list of this week sale from portal : {previous_week_sales}")

            # Converting merchant portal this week and previous week dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(this_week_sales[1], '%b').month
            end_month = datetime.strptime(this_week_sales[3], '%b').month
            this_start_date = pendulum.datetime(year=year, month=start_month, day=int(this_week_sales[0]))
            this_week_start_date = this_start_date.subtract(days=1).format('YYMMDD') + "1830"
            logger.info(f"this week start date : {this_week_start_date}")
            this_end_date = pendulum.datetime(year=year, month=end_month, day=int(this_week_sales[2]))
            this_week_end_date = this_end_date.format('YYMMDD') + "1829"
            logger.info(f"this week end date date : {this_week_end_date}")
            this_week_number_of_days = this_start_date.diff(this_end_date).in_days()
            logger.info(f"this week number of days : {this_week_number_of_days}")
            pvs_start_date = this_start_date.subtract(days=this_week_number_of_days + 2)
            previous_week_sale_start_date = pvs_start_date.format('YYMMDD') + "1830"
            logger.info(f"previous week sale start date : {previous_week_sale_start_date}")
            previous_week_sale_end_date = this_start_date.subtract(days=1).format('YYMMDD') + "1829"
            logger.info(f"previous week sale end date : {previous_week_sale_end_date}")

            # Fetching total sales of previous week from DB
            query = "select sum(amount) from txn where id between '" + previous_week_sale_start_date + "' AND '" + \
                    previous_week_sale_end_date + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of previous week : {query}")
            result = DBProcessor.getValueFromDB(query)
            previous_week_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.info(f"previous_week_sales_db : {previous_week_sales_db}")
            previous_week_total_sale_db = ["0.00" if previous_week_sales_db == "None" else previous_week_sales_db]
            logger.debug(f"previous week total sales from DB : {previous_week_total_sale_db}")

            # Fetching total sales of this week from DB
            query = "select sum(amount) from txn where id between '" + this_week_start_date + "' AND '"\
                    + this_week_end_date + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of this week : {query}")
            result = DBProcessor.getValueFromDB(query)
            this_week_total_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.debug(f"this week total sales from DB : {this_week_total_sales_db}")

            # Fetching overall sale from merchant portal
            overall_sales = portal_dashboard_page.fetch_overall_sales_and_amount()
            portal_overall_sale_diff = [None if overall_sales == None else overall_sales.split()[-1].strip("()").replace(",", "")]
            logger.info(f"overall sales between previous week and this week from portal : {portal_overall_sale_diff}")

            # Calculating sale difference between this week and previous week
            sales_difference_db = float(this_week_total_sales_db[0]) - float(*previous_week_total_sale_db[0])
            overall_sale_diff_db = ["0.00" if portal_overall_sale_diff[0] == "0.00" else sales_difference_db]
            logger.info(f"overall sale difference between previous week and this week from db "
                        f": {sales_difference_db}")

            # Calculating sale percentage between this week and previous week
            overall_percentage_db = ["0.00" if previous_week_total_sale_db[0][0] == "0.00" else
                                     str(round((float(sales_difference_db * 100 / float(*previous_week_total_sale_db[0]))), 1))]
            logger.info(f"overall sale percentage of previous week sale and this week sale from db : "
                        f"{overall_percentage_db}")
            overall_status_db = portal_dashboard_page.overall_status_validation_db(str(overall_percentage_db[0]))
            logger.info(f"overall sale status from previous week sale to this week sale :{overall_status_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = this_start_date.format('YYYY-MM-DD')
            this_end_date_1 = this_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            this_week_total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"this week total sale from api  :{this_week_total_amount_api}")
            previous_week_total_amount_api = sum(
                [float(element['amount']) for element in response['prevDurationData']])
            logger.info(f"previous week total sale from api :{previous_week_total_amount_api}")

            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")
            overall_sale_difference_api = this_week_total_amount_api - previous_week_total_amount_api
            overall_sale_difference_api_1 = [
                "0.00" if previous_week_total_amount_api == 0.0 else str(overall_sale_difference_api) + "0"]
            logger.info(f"overall sale difference between this week and previous week from api "
                        f": {overall_sale_difference_api_1}")
            overall_sale_percentage_api = ["0.00" if str(previous_week_total_amount_api) + "0" == "0.00" else round(
                float(overall_sale_difference_api) / float(previous_week_total_amount_api) * 100, 1)]
            overall_sale_percentage_api_1 = [
                str(overall_sale_percentage_api[0])[1:] if "-" in str(overall_sale_percentage_api[0]) else str(
                    overall_sale_percentage_api[0])]
            logger.info(f"overall sale percentage between this week and previous week api"
                        f" : {overall_sale_percentage_api_1}")
            status_api_1 = portal_dashboard_page.overall_status_validation_db(str(overall_sale_percentage_api[0]))
            logger.info(f"overall status between this week and previous week api : {status_api_1}")

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
                previous_week_total_sale_db_2 = ["0.0" if previous_week_total_sale_db[0][0] == "0.00"
                                                 else previous_week_total_sale_db[0][0]]
                overall_sales_diff_1 = ["0.00" if str(overall_sale_diff_db[0]) == "0.00"
                                        else str(overall_sale_diff_db[0]) + "0"]
                overall_percentage_db_1 = [overall_percentage_db[0][1:] if "-" in overall_percentage_db[0]
                                           else overall_percentage_db[0]]
                expected_api_values = {
                    "previous_week_sale": str(previous_week_total_sale_db_2[0]),
                    "this_week_sale": float(this_week_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "previous_week_sale": str(previous_week_total_amount_api),
                    "this_week_sale": float(this_week_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
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
                    "previous_week_sale": str(previous_week_total_amount_api),
                    "this_week_sale": float(this_week_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "previous_week_sale": str(previous_week_total_sale_db_2[0]),
                    "this_week_sale": float(this_week_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
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
                previous_week_total_sale_db_1 = ["₹ 0.00" if previous_week_total_sale_db[0][0] == "0.00"
                                                 else "₹ " + previous_week_total_sale_db[0][0] + "0"]
                expected_portal_values = {
                    "previous_week_sale": previous_week_total_sale_db_1[0],
                    "this_week_sale": "₹ " + this_week_total_sales_db[0] + "0",
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                portal_previous_week_sales_date_amount = previous_week_sales_date_amount.split("-")[-1]\
                    .strip().replace(",", "")
                logger.info(f"previous week sale amount from portal : {portal_previous_week_sales_date_amount}")
                portal_this_week_sales_amount = this_week_sales_amount.split("-")[-1].strip().replace(",", "")
                logger.info(f"this week sale amount from portal : {portal_this_week_sales_amount}")
                portal_overall_percentage = ["0.00" if overall_percentage_db[0] == "0.00"
                                             else str(float(overall_sales.split()[1]))]
                logger.info(f"portal overall percentage from previous week and this week :{portal_overall_percentage}")
                portal_overall_status = portal_dashboard_page.overall_status_validation_db\
                    ("0.00" if overall_status_db == "0.00" else overall_sales.split()[-1].strip(")"))
                logger.info(f"portal overall status from previous week and this week : {portal_overall_status}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")

                actual_portal_values = {
                    "previous_week_sale": portal_previous_week_sales_date_amount,
                    "this_week_sale": portal_this_week_sales_amount,
                    "overall_sale_diff": portal_overall_sale_diff[0],
                    "overall_percentage": portal_overall_percentage[0],
                    "overall_status": portal_overall_status,
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
def test_mp_700_701_003():
    """
    Sub Feature Code: UI_MP_Calender_txn_for_This_Month_as_country_head
    Sub Feature Description: Verifying sales over with previous comparision for This Month calender dates when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    003: TC003
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE3')
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

            amount = random.randint(50, 300)
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

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            portal_dashboard_page.click_calendar()
            portal_dashboard_page.select_txn_period_for_this_month()

            previous_month_sales_date_amount = portal_dashboard_page.fetch_previous_sales_dates_and_amount()
            logger.info(f"last previous month sales date and amount from portal : {previous_month_sales_date_amount}")
            previous_week_sales = " ".join(
                [ele for ele in previous_month_sales_date_amount.split()[2:] if ele != "-"]).split()
            logger.debug(f"list of previous month sale from portal : {previous_week_sales}")
            this_month_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"this month sales date and amount from portal : {this_month_sales_amount}")
            this_month_sales = " ".join([ele for ele in this_month_sales_amount.split()[2:] if ele != "-"]).split()
            logger.debug(f"list of this month sale from portal : {this_month_sales}")

            # Converting merchant portal this month and previous month dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(this_month_sales[1], '%b').month
            end_month = datetime.strptime(this_month_sales[3], '%b').month
            this_start_date = pendulum.datetime(year=year, month=start_month, day=int(this_month_sales[0]))
            this_month_start_date = this_start_date.subtract(days=1).format('YYMMDD') + "1830"
            logger.info(f"this month start date : {this_month_start_date}")
            this_end_date = pendulum.datetime(year=year, month=end_month, day=int(this_month_sales[2]))
            this_month_end_date = this_end_date.format('YYMMDD') + "1829"
            logger.info(f"this month end date date : {this_month_end_date}")
            this_month_number_of_days = this_start_date.diff(this_end_date).in_days()
            logger.info(f"this month number of days : {this_month_number_of_days}")
            pvs_start_date = this_start_date.subtract(days=this_month_number_of_days + 2)
            previous_month_sale_start_date = pvs_start_date.format('YYMMDD') + "1830"
            logger.info(f"previous month sale start date : {previous_month_sale_start_date}")
            previous_month_sale_end_date = this_start_date.subtract(days=1).format('YYMMDD') + "1829"
            logger.info(f"previous month sale end date : {previous_month_sale_end_date}")

            # Fetching total sales of previous month from DB
            query = "select sum(amount) from txn where id between '" + previous_month_sale_start_date + "' AND '" + \
                    previous_month_sale_end_date + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of previous month : {query}")
            result = DBProcessor.getValueFromDB(query)
            previous_month_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.info(f"previous_month_sales_db : {previous_month_sales_db}")
            previous_month_total_sale_db = ["0.00" if previous_month_sales_db == "None" else previous_month_sales_db]
            logger.debug(f"previous month total sales from DB : {previous_month_total_sale_db}")

            # Fetching total sales of this month from DB
            query = "select sum(amount) from txn where id between '" + this_month_start_date + "' AND '" \
                    + this_month_end_date + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of this month : {query}")
            result = DBProcessor.getValueFromDB(query)
            this_month_total_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.debug(f"this month total sales from DB : {this_month_total_sales_db}")

            # Fetching overall sale between previous month and this month from merchant portal
            overall_sales = portal_dashboard_page.fetch_overall_sales_and_amount()
            portal_overall_sale_diff = [
                None if overall_sales == None else overall_sales.split()[-1].strip("()").replace(",", "")]
            logger.info(f"overall sales between previous month and this month from portal : {portal_overall_sale_diff}")

            # Calculating sale difference between this month and previous month
            sales_difference_db = float(this_month_total_sales_db[0]) - float(*previous_month_total_sale_db[0])
            overall_sale_diff_db = ["0.00" if portal_overall_sale_diff[0] == "0.00" else sales_difference_db]
            logger.info(f"overall sale difference between previous month and this month from db "
                        f": {sales_difference_db}")

            # Calculating sale percentage between this month and previous month
            overall_percentage_db = ["0.00" if previous_month_total_sale_db[0][0] == "0.00" else
                                     str(round((float(sales_difference_db * 100 / float(*previous_month_total_sale_db[0]))), 1))]
            logger.info(
                f"overall sale percentage of previous month sale and this month sale from db : {overall_percentage_db}")
            overall_status_db = portal_dashboard_page.overall_status_validation_db(str(overall_percentage_db[0]))
            logger.info(f"overall sale status from previous month sale to this month sale :{overall_status_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = this_start_date.format('YYYY-MM-DD')
            this_end_date_1 = this_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            this_month_total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"this month total sale from api  :{this_month_total_amount_api}")
            previous_month_total_amount_api = sum([float(element['amount']) for element in
                                                   response['prevDurationData']])
            logger.info(f" previous month total sale from api :{previous_month_total_amount_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")

            overall_sale_difference_api = this_month_total_amount_api - previous_month_total_amount_api
            overall_sale_difference_api_1 = [
                "0.00" if previous_month_total_amount_api == 0.0 else str(overall_sale_difference_api) + "0"]
            logger.info(f"overall sale difference between this month and previous month from api "
                        f": {overall_sale_difference_api_1}")
            overall_sale_percentage_api = ["0.00" if previous_month_total_amount_api == 0.0 else round(
                float(overall_sale_difference_api) / float(previous_month_total_amount_api) * 100, 1)]
            overall_sale_percentage_api_1 = [
                str(overall_sale_percentage_api[0])[1:] if "-" in str(overall_sale_percentage_api[0]) else str(
                    overall_sale_percentage_api[0])]
            logger.info(f"overall sale percentage between this month and previous month api"
                        f" : {overall_sale_percentage_api_1}")
            status_api_1 = portal_dashboard_page.overall_status_validation_db(str(overall_sale_percentage_api[0]))
            logger.info(f"overall status between this month and previous month api : {status_api_1}")

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
                previous_month_total_sale_db_2 = [
                    "0.0" if previous_month_total_sale_db[0][0] == "0.00" else previous_month_total_sale_db[0][0]]
                overall_sales_diff_1 = [
                    "0.00" if str(overall_sale_diff_db[0]) == "0.00" else str(overall_sale_diff_db[0]) + "0"]
                overall_percentage_db_1 = [
                    overall_percentage_db[0][1:] if "-" in overall_percentage_db[0] else overall_percentage_db[0]]
                expected_api_values = {
                    "previous_month_sale": str(previous_month_total_sale_db_2[0]),
                    "this_month_sale": float(this_month_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "previous_month_sale": str(previous_month_total_amount_api),
                    "this_month_sale": float(this_month_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
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
                    "previous_month_sale": str(previous_month_total_amount_api),
                    "this_month_sale": float(this_month_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "previous_month_sale": str(previous_month_total_sale_db_2[0]),
                    "this_month_sale": float(this_month_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
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
                previous_month_total_sale_db_1 = ["₹ 0.00" if previous_month_total_sale_db[0][0] == "0.00"
                                                  else "₹ " + previous_month_total_sale_db[0][0] + "0"]
                expected_portal_values = {
                    "previous_month_sale": previous_month_total_sale_db_1[0],
                    "this_month_sale": "₹ " + this_month_total_sales_db[0] + "0",
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                portal_previous_month_sales_date_amount = previous_month_sales_date_amount.split("-")[-1].strip().replace(",", "")
                logger.info(f"previous month sale amount from portal : {portal_previous_month_sales_date_amount}")
                portal_this_month_sales_amount = this_month_sales_amount.split("-")[-1].strip().replace(",", "")
                logger.info(f"this month sale amount from portal : {portal_this_month_sales_amount}")
                portal_overall_percentage = ["0.00" if overall_percentage_db[0] == "0.00"
                                             else str(float(overall_sales.split()[1]))]
                logger.info(f"portal overall percentage from previous month and this month"
                            f" :{portal_overall_percentage}")
                portal_overall_status = portal_dashboard_page.overall_status_validation_db\
                    ("0.00" if overall_status_db == "0.00" else overall_sales.split()[-1].strip(")"))
                logger.info(f"portal overall status from previous month and this month : {portal_overall_status}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")

                actual_portal_values = {
                    "previous_month_sale": portal_previous_month_sales_date_amount,
                    "this_month_sale": portal_this_month_sales_amount,
                    "overall_sale_diff": portal_overall_sale_diff[0],
                    "overall_percentage": portal_overall_percentage[0],
                    "overall_status": portal_overall_status,
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
def test_mp_700_701_004():
    """
    Sub Feature Code: UI_MP_Calender_txn_for_Last_30_days_as_country_head
    Sub Feature Description: Verifying sales over with previous comparision for last 30 days calender dates when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    004: TC004
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE4')
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

            amount = random.randint(50, 300)
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

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            portal_dashboard_page.click_calendar()
            portal_dashboard_page.select_txn_period_for_last_30_days()

            previous_last_30_days_sales_date_amount = portal_dashboard_page.fetch_previous_sales_dates_and_amount()
            logger.info(f"last previous last 30 days sales date and amount from portal :"
                        f" {previous_last_30_days_sales_date_amount}")
            previous_last_30_days_sales = " ".join([ele for ele in previous_last_30_days_sales_date_amount.split()[2:]
                                                    if ele != "-"]).split()
            logger.debug(f"list of previous last 30 days sale from portal : {previous_last_30_days_sales}")
            this_last_30_days_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
            logger.info(f"this last 30 days sales date and amount from portal : {this_last_30_days_sales_amount}")
            last_30_days_sales = " ".join([ele for ele in this_last_30_days_sales_amount.split()[2:] if ele != "-"]).split()
            logger.debug(f"list of last 30 days sale from portal : {last_30_days_sales}")

            # Converting merchant portal last 30 ays and previous last 30 days dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(last_30_days_sales[1], '%b').month
            end_month = datetime.strptime(last_30_days_sales[3], '%b').month
            last_start_date = pendulum.datetime(year=year, month=start_month, day=int(last_30_days_sales[0]))
            last_30_days_start_date = last_start_date.subtract(days=1).format('YYMMDD') + "1830"
            logger.info(f"last 30 days start start date : {last_30_days_start_date}")
            last_30_days_end_date = pendulum.datetime(year=year, month=end_month, day=int(last_30_days_sales[2]))
            last_30_days_end_date_1 = last_30_days_end_date.format('YYMMDD') + "1829"
            logger.info(f"last 30 days_1 end date date : {last_30_days_end_date_1}")
            last_30_days_number_of_days = last_start_date.diff(last_30_days_end_date).in_days()
            logger.info(f"last 30 days number of days : {last_30_days_number_of_days}")
            pvs_start_date = last_start_date.subtract(days=last_30_days_number_of_days + 2)
            previous_last_30_days_sale_start_date = pvs_start_date.format('YYMMDD') + "1830"
            logger.info(f"previous last 30 days sale start date : {previous_last_30_days_sale_start_date}")
            previous_last_30_days_sale_end_date = last_start_date.subtract(days=1).format('YYMMDD') + "1829"
            logger.info(f"previous last 30 days sale end date : {previous_last_30_days_sale_end_date}")

            # Fetching total sales of previous last 30 days from DB
            query = "select sum(amount) from txn where id between '" + previous_last_30_days_sale_start_date + "' AND '" + \
                    previous_last_30_days_sale_end_date + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of previous last 30 days : {query}")
            result = DBProcessor.getValueFromDB(query)
            previous_last_30_days_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.info(f"previous_last_30_days_sales_db : {previous_last_30_days_sales_db}")
            previous_last_30_days_total_sale_db = ["0.00" if previous_last_30_days_sales_db == "None"
                                                   else previous_last_30_days_sales_db]
            logger.debug(f"previous last 30 days total sales from DB : {previous_last_30_days_total_sale_db}")

            # Fetching total sales of last 30 days from DB
            query = "select sum(amount) from txn where id between '" + last_30_days_start_date + "' AND '" \
                    + last_30_days_end_date_1 + "' and org_code='" + org_code + "' and status = 'AUTHORIZED';"
            logger.info(f"query to fetch total sales of last 30 days : {query}")
            result = DBProcessor.getValueFromDB(query)
            last_30_days_total_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
            logger.debug(f"last 30 days total sales from DB : {last_30_days_total_sales_db}")

            # Fetching overall sale between previous last 30 days and last 30 days from merchant portal
            overall_sales = portal_dashboard_page.fetch_overall_sales_and_amount()
            portal_overall_sale_diff = [
                None if overall_sales == None else overall_sales.split()[-1].strip("()").replace(",", "")]
            logger.info(f"overall sales between previous last 30 days and last 30 days from portal :"
                        f" {portal_overall_sale_diff}")

            # Calculating sale difference between last 30 days and previous last 30 days
            sales_difference_db = float(last_30_days_total_sales_db[0]) - float(*previous_last_30_days_total_sale_db[0])
            overall_sale_diff_db = ["0.00" if portal_overall_sale_diff[0] == "0.00" else sales_difference_db]
            logger.info(f"overall sale difference between previous last 30 days and last 30 days from db "
                        f": {sales_difference_db}")

            # Calculating sale percentage between last 30 days and previous last 30 days
            overall_percentage_db = ["0.00" if previous_last_30_days_total_sale_db[0][0] == "0.00"
                                     else str(round((float(sales_difference_db * 100 /
                                                           float(*previous_last_30_days_total_sale_db[0]))), 1))]
            logger.info(
                f"overall sale percentage of previous last 30 days sale and last 30 days sale from db : "
                f"{overall_percentage_db}")
            overall_status_db = portal_dashboard_page.overall_status_validation_db(str(overall_percentage_db[0]))
            logger.info(f"overall sale status from previous last 30 days sale to last 30 days sale :"
                        f"{overall_status_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = last_start_date.format('YYYY-MM-DD')
            this_end_date_1 = last_30_days_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")

            last_30_days_total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"last 30 days total sale from api  :{last_30_days_total_amount_api}")
            previous_last_30_days_total_amount_api = sum([float(element['amount'])
                                                          for element in response['prevDurationData']])
            logger.info(f"previous last 30 days total sale from api :{previous_last_30_days_total_amount_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username from api :{username_api_1}")

            overall_sale_difference_api = last_30_days_total_amount_api - previous_last_30_days_total_amount_api
            overall_sale_difference_api_1 = [
                "0.00" if previous_last_30_days_total_amount_api == 0.0 else str(overall_sale_difference_api) + "0"]
            logger.info(f"overall sale difference between last 30 days and previous last 30 days from api "
                        f": {overall_sale_difference_api_1}")
            overall_sale_percentage_api = ["0.00" if previous_last_30_days_total_amount_api == 0.0 else
                                           round(float(overall_sale_difference_api) / float(
                                               previous_last_30_days_total_amount_api) * 100, 1)]
            overall_sale_percentage_api_1 = [
                str(overall_sale_percentage_api[0])[1:] if "-" in str(overall_sale_percentage_api[0]) else str(
                    overall_sale_percentage_api[0])]
            logger.info(f"overall sale percentage between last 30 days and previous last 30 days api"
                        f" : {overall_sale_percentage_api_1}")
            status_api_1 = portal_dashboard_page.overall_status_validation_db(str(overall_sale_percentage_api[0]))
            logger.info(f"overall status between last 30 days and previous last 30 days api : {status_api_1}")

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
                previous_last_30_days_total_sale_db_2 = [
                    "0.0" if previous_last_30_days_total_sale_db[0][0] == "0.00"
                    else previous_last_30_days_total_sale_db[0][0]]
                overall_sales_diff_1 = [
                    "0.00" if str(overall_sale_diff_db[0]) == "0.00" else str(overall_sale_diff_db[0]) + "0"]
                overall_percentage_db_1 = [
                    overall_percentage_db[0][1:] if "-" in overall_percentage_db[0] else overall_percentage_db[0]]
                expected_api_values = {
                    "previous_last_30_days_sale": str(previous_last_30_days_total_sale_db_2[0]),
                    "last_30_days_sale": float(last_30_days_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "previous_last_30_days_sale": str(previous_last_30_days_total_amount_api),
                    "last_30_days_sale": float(last_30_days_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
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
                    "previous_last_30_days_sale": str(previous_last_30_days_total_amount_api),
                    "last_30_days_sale": float(last_30_days_total_amount_api),
                    "overall_sale_diff": str(overall_sale_difference_api_1[0]),
                    "overall_percentage": str(overall_sale_percentage_api_1[0]),
                    "overall_status": status_api_1,
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "previous_last_30_days_sale": str(previous_last_30_days_total_sale_db_2[0]),
                    "last_30_days_sale": float(last_30_days_total_sales_db[0]),
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
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
                previous_last_30_days_total_sale_db_1 = \
                    ["₹ 0.00" if previous_last_30_days_total_sale_db[0][0] == "0.00"
                     else "₹ " + previous_last_30_days_total_sale_db[0][0] + "0"]
                expected_portal_values = {
                    "previous_last_30_days_sale": previous_last_30_days_total_sale_db_1[0],
                    "last_30_days_sale": "₹ " + last_30_days_total_sales_db[0] + "0",
                    "overall_sale_diff": overall_sales_diff_1[0],
                    "overall_percentage": overall_percentage_db_1[0],
                    "overall_status": overall_status_db,
                    "org_code": org_code,
                    "username": username_db
                }

                portal_previous_last_30_days_sales_date_amount = previous_last_30_days_sales_date_amount.split("-")[-1].strip().replace(",", "")
                logger.info(f"previous last 30 days sale amount from portal : "
                            f"{portal_previous_last_30_days_sales_date_amount}")
                last_30_days_month_sales_amount = this_last_30_days_sales_amount.split("-")[-1].strip().replace(",", "")
                logger.info(f"last 30 days sale amount from portal : {last_30_days_month_sales_amount}")
                portal_overall_percentage = ["0.00" if overall_percentage_db[0] == "0.00" else str(float(overall_sales.split()[1]))]
                logger.info(f"portal overall percentage from previous last 30 days and last 30 days :"
                            f"{portal_overall_percentage}")
                portal_overall_status = portal_dashboard_page.overall_status_validation_db\
                    ("0.00" if overall_status_db == "0.00" else overall_sales.split()[-1].strip(")"))
                logger.info(f"portal overall status from previous last 30 days and last 30 days : "
                            f"{portal_overall_status}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")

                actual_portal_values = {
                    "previous_last_30_days_sale": portal_previous_last_30_days_sales_date_amount,
                    "last_30_days_sale": last_30_days_month_sales_amount,
                    "overall_sale_diff": portal_overall_sale_diff[0],
                    "overall_percentage": portal_overall_percentage[0],
                    "overall_status": portal_overall_status,
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


# @pytest.mark.usefixtures("log_on_success", "method_setup")
# @pytest.mark.dbVal
# @pytest.mark.apiVal
# @pytest.mark.portalVal
# def test_mp_700_701_005():
#     """
#     Sub Feature Code: UI_MP_Calender_txn_for_Last_90_days_as_country_head
#     Sub Feature Description: Verifying sales over with previous comparision converting to weeks  for last 90 days calender dates when logging in  as Country Head
#     calender dates  as Country Head
#     TC naming code description:
#     700: Merchant Portal
#     701: Country
#     005: TC005
#     """
#     try:
#         testcase_id = sys._getframe().f_code.co_name
#         GlobalVariables.time_calc.setup.resume()
#         logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")
#
#         # -------------------------------Reset Settings to default(started)--------------------------------------------
#         logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
#         txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE4')
#         logger.debug(f"Fetched txn credentials from the ezeauto db : {txn_cred}")
#         txn_username = txn_cred['Username']
#         txn_password = txn_cred['Password']
#         txn_org_code = txn_cred['Merchant_Code']
#
#         cred_dict = ResourceAssigner.get_org_users_using_category(txn_org_code)
#         logger.debug(f"Fetched all category credentials from the ezeauto db : {cred_dict}")
#         login_username = cred_dict['COUNTRY']['username']
#         logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
#         login_password = cred_dict['COUNTRY']['password']
#
#         query = "select org_code from org_employee where username='" + str(login_username) + "';"
#         logger.debug(f"Query to fetch org_code from the DB : {query}")
#         result = DBProcessor.getValueFromDB(query)
#         org_code = result['org_code'].values[0]
#         logger.debug(f"Query result, org_code : {org_code}")
#
#         logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
#         # -------------------------------Reset Settings to default(completed)-------------------------------------------
#
#         # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
#         logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
#
#         TestSuiteSetup.launch_browser_and_context_initialize()
#         GlobalVariables.setupCompletedSuccessfully = True
#         logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
#         # -----------------------------PreConditions(Completed)-----------------------------
#
#         Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False,
#                                                    config_log=False)
#
#         GlobalVariables.time_calc.setup.end()
#         logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")
#
#         # -----------------------------------------Start of Test Execution-------------------------------------
#         try:
#             logger.info(f"Starting execution for the test case : {testcase_id}")
#             GlobalVariables.time_calc.execution.start()
#             logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
#
#             amount = random.randint(50, 300)
#             order_id = datetime.now().strftime('%m%d%H%M%S')
#
#             api_details = DBProcessor.get_api_details('cash_payment', request_body={
#                 "username": txn_username,
#                 "password": txn_password,
#                 "order_id": order_id,
#                 "amount": str(amount)
#             })
#
#             response = APIProcessor.send_request(api_details)
#             logger.debug(f"Response received for cash txn via api : {response}")
#
#             query = "select org_employee_username from org_structure where node_name = 'India'" \
#                     " and org_code = '" + org_code + "' and org_employee_username is NOT NULL;"
#             logger.debug(f"query to fetch username from db : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             username_db = str(result.values[0]).strip("[]/'")
#             logger.debug(f"username from db : {username_db}")
#
#             GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
#             login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
#             login_page_portal.perform_login_to_portal(login_username, login_password)
#             portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
#             portal_dashboard_page.click_calendar()
#             portal_dashboard_page.select_txn_period_for_last_90_days()
#
#             previous_last_90_days_sales_date_amount = portal_dashboard_page.fetch_previous_sales_dates_and_amount()
#             logger.info(f"last previous last 90 days sales date and amount from portal :"
#                         f" {previous_last_90_days_sales_date_amount}")
#             previous_last_90_days_sales = " ".join([ele for ele in previous_last_90_days_sales_date_amount.split()[2:]
#                                                     if ele != "-"]).split()
#             logger.debug(f"list of previous last 90 days sale from portal : {previous_last_90_days_sales}")
#             this_last_90_days_sales_amount = portal_dashboard_page.fetch_current_sales_dates_and_amount()
#             logger.info(f"this last 90 days sales date and amount from portal : {this_last_90_days_sales_amount}")
#             last_90_days_sales = " ".join([ele for ele in this_last_90_days_sales_amount.split()[2:]
#                                            if ele != "-"]).split()
#             logger.debug(f"list of last 90 days sale from portal : {last_90_days_sales}")
#
#             # Converting merchant portal last 90 days and previous last 30 days dates into full date format to fetch details from DB
#             year = int(pendulum.now().format("YYYY"))
#             start_month = datetime.strptime(last_90_days_sales[1], '%b').month
#             end_month = datetime.strptime(last_90_days_sales[3], '%b').month
#             last_start_date = pendulum.datetime(year=year, month=start_month, day=int(last_90_days_sales[0]))
#             last_90_days_start_date = last_start_date.subtract(days=1).format('YYMMDD') + "1830"
#             logger.info(f"last 90 days start start date : {last_90_days_start_date}")
#             last_90_days_end_date = pendulum.datetime(year=year, month=end_month, day=int(last_90_days_sales[2]))
#             last_90_days_end_date_1 = last_90_days_end_date.format('YYMMDD') + "1829"
#             logger.info(f"last 90 days_1 end date date : {last_90_days_end_date_1}")
#             last_90_days_number_of_days = last_start_date.diff(last_90_days_end_date).in_days()
#             logger.info(f"last 90 days number of days : {last_90_days_number_of_days}")
#             pvs_start_date = last_start_date.subtract(days=last_90_days_number_of_days + 2)
#             previous_last_90_days_sale_start_date = pvs_start_date.format('YYMMDD') + "1830"
#             logger.info(f"previous last 90 days sale start date : {previous_last_90_days_sale_start_date}")
#             previous_last_90_days_sale_end_date = last_start_date.subtract(days=1).format('YYMMDD') + "1829"
#             logger.info(f"previous last 90 days sale end date : {previous_last_90_days_sale_end_date}")
#
#             # Fetching total sales of previous last 90 days from DB
#             query = "select sum(amount) from txn where (id between '" + previous_last_90_days_sale_start_date + "' AND '" + \
#                     last_90_days_start_date + "') and org_code='" + org_code + "'and status = 'AUTHORIZED';"
#             logger.info(f"query to fetch total sales of previous last 90 days : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             previous_last_90_days_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
#             logger.info(f"previous_last_90_days_sales_db : {previous_last_90_days_sales_db}")
#             previous_last_90_days_total_sale_db = ["0.00" if previous_last_90_days_sales_db == "None"
#                                                    else previous_last_90_days_sales_db]
#             logger.debug(f"previous last 90 days total sales from DB : {previous_last_90_days_total_sale_db}")
#
#             # Fetching total sales of last 90 days from DB
#             query = "select sum(amount) from txn where (id between '" + last_90_days_start_date + "' AND '" \
#                     + last_90_days_end_date_1 + "') and org_code='" + org_code + "' and status = 'AUTHORIZED';"
#             logger.info(f"query to fetch total sales of last 90 days : {query}")
#             result = DBProcessor.getValueFromDB(query)
#             last_90_days_total_sales_db = ["0.00" if str(result).split()[-1] == "None" else str(result).split()[-1]]
#             logger.debug(f"last 90 days total sales from DB : {last_90_days_total_sales_db}")
#
#             # Fetching overall sale between previous last 90 days and last 90 days from merchant portal
#             overall_sales = portal_dashboard_page.fetch_overall_sales_and_amount()
#             portal_overall_sale_diff = [
#                 None if overall_sales == None else overall_sales.split()[-1].strip("()").replace(",", "")]
#             logger.info(f"overall sales between previous last 90 days and last 90 days from portal :"
#                         f" {portal_overall_sale_diff}")
#
#             # Calculating sale difference between last 90 days and previous last 90 days
#             sales_difference_db = float(last_90_days_total_sales_db[0]) - float(*previous_last_90_days_total_sale_db[0])
#             overall_sale_diff_db = ["0.00" if portal_overall_sale_diff[0] == "0.00" else sales_difference_db]
#             logger.info(f"overall sale difference between previous last 90 days and last 90 days from db "
#                         f": {sales_difference_db}")
#
#             # Calculating sale percentage between last 90 days and previous last 90 days
#             overall_percentage_db = ["0.00" if previous_last_90_days_total_sale_db[0][0] == "0.00"
#                                      else str(round((float(sales_difference_db * 100 /
#                                                            float(*previous_last_90_days_total_sale_db[0]))), 1))]
#             logger.info(
#                 f"overall sale percentage of previous last 90 days sale and last 90 days sale from db : "
#                 f"{overall_percentage_db}")
#             overall_status_db = portal_dashboard_page.overall_status_validation_db(str(overall_percentage_db[0]))
#             logger.info(f"overall sale status from previous last 90 days sale to last 90 days sale :"
#                         f"{overall_status_db}")
#
#             api_details = DBProcessor.get_api_details('mp_login', request_body={
#                 "username": login_username,
#                 "password": login_password
#             })
#             response = APIProcessor.send_request(api_details)
#             logger.info(f"mp login response from api : {response}")
#             bearer_token = response['token']
#             logger.info(f"bearer token from api : {bearer_token}")
#             this_start_date_1 = last_start_date.format('YYYY-MM-DD')
#             this_end_date_1 = last_90_days_end_date.format('YYYY-MM-DD')
#             api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
#                 "startDate": this_start_date_1,
#                 "endDate": this_end_date_1
#             })
#             api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
#             logger.debug(f"api details for TxnReport : {api_details}")
#             response = APIProcessor.send_request(api_details)
#             logger.info(f"Response obtained for Txn Dashboard is: {response}")
#
#             last_90_days_total_amount_api = sum(
#                 [float(element['amount']) for element in response['paymentModeSegregation']])
#             logger.info(f"last 90 days total sale from api  :{last_90_days_total_amount_api}")
#             previous_last_90_days_total_amount_api = sum(
#                 [float(element['amount']) for element in response['prevDurationData']])
#             logger.info(f"previous last 90 days total sale from api :{previous_last_90_days_total_amount_api}")
#             org_code_api_1 = response['orgCode']
#             logger.info(f"org code from api :{org_code_api_1}")
#             username_api_1 = response['username']
#             logger.info(f"username from api :{username_api_1}")
#
#             overall_sale_difference_api = last_90_days_total_amount_api - previous_last_90_days_total_amount_api
#             overall_sale_difference_api_1 = [
#                 "0.00" if previous_last_90_days_total_amount_api == 0.0 else str(overall_sale_difference_api) + "0"]
#             logger.info(f"overall sale difference between last 90 days and previous last 90 days from api "
#                         f": {overall_sale_difference_api_1}")
#             overall_sale_percentage_api = ["0.00" if previous_last_90_days_total_amount_api == 0.0 else
#                                            round(float(overall_sale_difference_api) / float(
#                                                previous_last_90_days_total_amount_api) * 100, 1)]
#             overall_sale_percentage_api_1 = [
#                 str(overall_sale_percentage_api[0])[1:] if "-" in str(overall_sale_percentage_api[0]) else str(
#                     overall_sale_percentage_api[0])]
#             logger.info(f"overall sale percentage between last 90 days and previous last 90 days api"
#                         f" : {overall_sale_percentage_api_1}")
#             status_api_1 = portal_dashboard_page.overall_status_validation_db(str(overall_sale_percentage_api[0]))
#             logger.info(f"overall status between last 90 days and previous last 90 days api : {status_api_1}")
#
#             GlobalVariables.EXCEL_TC_Execution = "Pass"
#             GlobalVariables.time_calc.execution.pause()
#             logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
#             logger.info(f"Execution is completed for the test case : {testcase_id}")
#         except Exception as e:
#             Configuration.perform_exe_exception(testcase_id)
#             pytest.fail("Test case execution failed due to the exception -" + str(e))
#         # -----------------------------------------End of Test Execution--------------------------------------
#
#         # -----------------------------------------Start of Validation----------------------------------------
#         logger.info(f"Starting Validation for the test case : {testcase_id}")
#         GlobalVariables.time_calc.validation.start()
#         logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
#
#         # -----------------------------------------Start of API Validation------------------------------------
#         if (ConfigReader.read_config("Validations", "api_validation")) == "True":
#             logger.info(f"Started API validation for the test case : {testcase_id}")
#             try:
#                 previous_last_90_days_total_sale_db_2 = ["0.0" if previous_last_90_days_total_sale_db[0][0] == "0.00"
#                                                          else previous_last_90_days_total_sale_db[0][0]]
#                 overall_sales_diff_1 = [
#                     "0.00" if str(overall_sale_diff_db[0]) == "0.00" else str(overall_sale_diff_db[0]) + "0"]
#                 overall_percentage_db_1 = [
#                     overall_percentage_db[0][1:] if "-" in overall_percentage_db[0] else overall_percentage_db[0]]
#                 expected_api_values = {
#                     "previous_last_90_days_sale": str(previous_last_90_days_total_sale_db_2[0]),
#                     "last_90_days_sale": float(last_90_days_total_sales_db[0]),
#                     "overall_sale_diff": overall_sales_diff_1[0],
#                     "overall_percentage": overall_percentage_db_1[0],
#                     "overall_status": overall_status_db,
#                     "org_code": org_code,
#                     "username": username_db
#                 }
#
#                 actual_api_values = {
#                     "previous_last_90_days_sale": str(previous_last_90_days_total_amount_api),
#                     "last_90_days_sale": float(last_90_days_total_amount_api),
#                     "overall_sale_diff": str(overall_sale_difference_api_1[0]),
#                     "overall_percentage": str(overall_sale_percentage_api_1[0]),
#                     "overall_status": status_api_1,
#                     "org_code": org_code_api_1,
#                     "username": username_api_1
#                 }
#                 Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
#             except Exception as e:
#                 Configuration.perform_api_val_exception(testcase_id, e)
#             logger.info(f"Completed API validation for the test case : {testcase_id}")
#         # -----------------------------------------End of API Validation---------------------------------------
#
#         # -----------------------------------------Start of DB Validation--------------------------------------
#         if (ConfigReader.read_config("Validations", "db_validation")) == "True":
#             logger.info(f"Started DB validation for the test case : {testcase_id}")
#             try:
#                 expected_db_values = {
#                     "previous_last_90_days_sale": str(previous_last_90_days_total_amount_api),
#                     "last_90_days_sale": float(last_90_days_total_amount_api),
#                     "overall_sale_diff": str(overall_sale_difference_api_1[0]),
#                     "overall_percentage": str(overall_sale_percentage_api_1[0]),
#                     "overall_status": status_api_1,
#                     "org_code": org_code_api_1,
#                     "username": username_api_1
#                 }
#
#                 actual_db_values = {
#                     "previous_last_90_days_sale": str(previous_last_90_days_total_sale_db_2[0]),
#                     "last_90_days_sale": float(last_90_days_total_sales_db[0]),
#                     "overall_sale_diff": overall_sales_diff_1[0],
#                     "overall_percentage": overall_percentage_db_1[0],
#                     "overall_status": overall_status_db,
#                     "org_code": org_code,
#                     "username": username_db
#                 }
#                 Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
#             except Exception as e:
#                 Configuration.perform_db_val_exception(testcase_id, e)
#             logger.info(f"Completed DB validation for the test case : {testcase_id}")
#         # -----------------------------------------End of DB Validation---------------------------------------
#
#         # -----------------------------------------Start of Portal Validation---------------------------------
#         if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
#             logger.info(f"Started Portal validation for the test case : {testcase_id}")
#             try:
#                 previous_last_90_days_total_sale_db_1 = ["₹ 0.00" if previous_last_90_days_total_sale_db[0][0] == "0.00"
#                                                          else "₹ " + previous_last_90_days_total_sale_db[0][0] + "0"]
#                 expected_portal_values = {
#                     "previous_last_90_days_sale": previous_last_90_days_total_sale_db_1[0],
#                     "last_90_days_sale": "₹ " + last_90_days_total_sales_db[0] + "0",
#                     "overall_sale_diff": overall_sales_diff_1[0],
#                     "overall_percentage": overall_percentage_db_1[0],
#                     "overall_status": overall_status_db,
#                     "org_code": org_code,
#                     "username": username_db
#                 }
#
#                 portal_previous_last_90_days_sales_date_amount = previous_last_90_days_sales_date_amount.split("-")[-1].strip().replace(",", "")
#                 logger.info(f"previous last 90 days sale amount from portal : "
#                             f"{portal_previous_last_90_days_sales_date_amount}")
#                 last_90_days_month_sales_amount = this_last_90_days_sales_amount.split("-")[-1].strip().replace(",", "")
#                 logger.info(f"last 30 days sale amount from portal : {last_90_days_month_sales_amount}")
#                 portal_overall_percentage = ["0.00" if overall_percentage_db[0] == "0.00"
#                                              else str(float(overall_sales.split()[1]))]
#                 logger.info(f"portal overall percentage from previous last 90 days and last 90 days :"
#                             f"{portal_overall_percentage}")
#                 portal_overall_status = portal_dashboard_page.overall_status_validation_db\
#                     ("0.00" if overall_status_db == "0.00" else overall_sales.split()[-1].strip(")"))
#                 logger.info(f"portal overall status from previous last 90 days and last 90 days : "
#                             f"{portal_overall_status}")
#                 portal_dashboard_page.click_merchant_name()
#                 portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
#                 logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")
#
#                 actual_portal_values = {
#                     "previous_last_90_days_sale": portal_previous_last_90_days_sales_date_amount,
#                     "last_90_days_sale": last_90_days_month_sales_amount,
#                     "overall_sale_diff": portal_overall_sale_diff[0],
#                     "overall_percentage": portal_overall_percentage[0],
#                     "overall_status": portal_overall_status,
#                     "org_code": portal_merchant_details[0],
#                     "username": portal_merchant_details[-1]
#                 }
#                 Validator.validateAgainstPortal(expectedPortal=expected_portal_values,
#                                                 actualPortal=actual_portal_values)
#             except Exception as e:
#                 Configuration.perform_portal_val_exception(testcase_id, e)
#             logger.info(f"Completed Portal validation for the test case : {testcase_id}")
#         # -----------------------------------------End of Portal Validation---------------------------------------
#
#         GlobalVariables.time_calc.validation.end()
#         logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
#         logger.info(f"Completed Validation for the test case : {testcase_id}")
#         # -------------------------------------------End of Validation---------------------------------------------
#     finally:
#         Configuration.executeFinallyBlock(testcase_id)

