from datetime import datetime
import random
import sys
import pendulum
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_DashboardPage import PortalDashboardPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    merchant_creator, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
def test_mp_700_701_008():
    """
    Sub Feature Code: UI_MP_Payment_using_Card_as_country_head
    Sub Feature Description: Verifying txn details on dashboard for payment done using card when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    008: TC008
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE6')
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
            logger.info(f"card payment initiated response from api : {response}")
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

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total card sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            card_total_sale_db = str(result).split()[-1]
            logger.info(f"card total sale from db : {card_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            card_total_txns_db = str(result).split()[-1]
            logger.info(f"card total txns from db : {card_total_txns_db}")

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_card_sale_percent = float(card_total_sale_db)/float(overall_sale)*100
            overall_card_sale_percentage_db = f"{overall_card_sale_percent:.2f}"
            logger.info(f"overall card sale percentage db :{overall_card_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"total sale from api  :{total_amount_api}")
            card_total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']
                                         if element['paymentMode'] == 'CARD'])
            logger.info(f"card total sale from api  :{card_total_amount_api}")
            total_number_of_txns_api = sum([element['count'] for element in response['paymentModeSegregation']
                                            if element['paymentMode'] == 'CARD'])
            logger.info(f"card total number of txns from api  :{total_number_of_txns_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username_1 from api :{username_api_1}")

            card_sale_percent_api = float(card_total_amount_api) / float(total_amount_api) * 100
            card_sale_percentage_api = f"{card_sale_percent_api:.2f}"
            logger.info(f"overall card sale percentage api :{card_sale_percentage_api}")

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
                    "card_txn_amount": card_total_sale_db,
                    "card_total_txns": card_total_txns_db,
                    "card_sale_percentage": overall_card_sale_percentage_db,
                    "org_code": org_code,
                    "username": username_db
                }

                actual_api_values = {
                    "card_txn_amount": str(card_total_amount_api),
                    "card_total_txns": str(total_number_of_txns_api),
                    "card_sale_percentage": card_sale_percentage_api,
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
                    "card_txn_amount": str(card_total_amount_api),
                    "card_total_txns": str(total_number_of_txns_api),
                    "card_sale_percentage": card_sale_percentage_api,
                    "org_code": org_code_api_1,
                    "username": username_api_1
                }

                actual_db_values = {
                    "card_txn_amount": card_total_sale_db,
                    "card_total_txns": card_total_txns_db,
                    "card_sale_percentage": overall_card_sale_percentage_db,
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
                    "card_txn_amount": card_total_sale_db + "0",
                    "card_total_txns": card_total_txns_db,
                    "card_sale_percentage": overall_card_sale_percentage_db,
                    "org_code": org_code,
                    "username": username_db
                }

                card_txn_details = portal_dashboard_page.fetch_txn_details_by_type("Card").split()
                logger.info(f"card overall txn detail from portal :{card_txn_details}")
                portal_dashboard_page.click_merchant_name()
                portal_merchant_details = portal_dashboard_page.fetch_merchant_details().split()
                logger.info(f"fetched org_code and username from portal : {portal_merchant_details}")
                card_txn_amount = card_txn_details[3].replace(",", "")
                card_txns = card_txn_details[1].replace(",", "")
                portal_card_sale_percentage = f"{float(card_txn_details[4]):.2f}"

                actual_portal_values = {
                    "card_txn_amount": card_txn_amount,
                    "card_total_txns": card_txns,
                    "card_sale_percentage": str(portal_card_sale_percentage),
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
def test_mp_700_701_009():
    """
    Sub Feature Code: UI_MP_Payment_using_Cash_as_country_head
    Sub Feature Description: Verifying txn details on dashboard for payment done using Cash when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    009: TC009
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE7')
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

            amount = random.randint(50, 200)
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
                    " org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CASH' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total cash sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cash_total_sale_db = str(result).split()[-1]
            logger.info(f"cash total sale from db : {cash_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CASH'and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cash_total_txns_db = str(result).split()[-1]
            logger.info(f"cash total txns from db : {cash_total_txns_db}")

            query = "select sum(amount) from txn where org_code = '" + org_code + \
                    "' and status = 'AUTHORIZED'" \
                    " and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_cash_sale_percent = float(cash_total_sale_db) / float(overall_sale) * 100
            overall_cash_sale_percentage_db = f"{overall_cash_sale_percent:.2f}"
            logger.info(f"overall card sale percentage db :{overall_cash_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"total sale from api  :{total_amount_api}")
            cash_total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']
                                         if element['paymentMode'] == 'CASH'])
            logger.info(f"cash total sale from api  :{cash_total_amount_api}")
            total_number_of_txns_api = sum([element['count'] for element in response['paymentModeSegregation']
                                            if element['paymentMode'] == 'CASH'])
            logger.info(f"cash total number of txns from api  :{total_number_of_txns_api}")

            cash_sale_percent_api = float(cash_total_amount_api) / float(total_amount_api) * 100
            cash_sale_percentage_api = f"{cash_sale_percent_api:.2f}"
            logger.info(f"overall cash sale percentage api :{cash_sale_percentage_api}")

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
                    "cash_txn_amount": cash_total_sale_db,
                    "cash_total_txns": cash_total_txns_db,
                    "cash_sale_percentage": overall_cash_sale_percentage_db
                }

                actual_api_values = {
                    "cash_txn_amount": str(cash_total_amount_api),
                    "cash_total_txns": str(total_number_of_txns_api),
                    "cash_sale_percentage": cash_sale_percentage_api
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
                    "cash_txn_amount": str(cash_total_amount_api),
                    "cash_total_txns": str(total_number_of_txns_api),
                    "cash_sale_percentage": cash_sale_percentage_api
                }

                actual_db_values = {
                    "cash_txn_amount": cash_total_sale_db,
                    "cash_total_txns": cash_total_txns_db,
                    "cash_sale_percentage": overall_cash_sale_percentage_db
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
                    "cash_txn_amount": cash_total_sale_db + "0",
                    "cash_total_txns": cash_total_txns_db,
                    "cash_sale_percentage": overall_cash_sale_percentage_db,
                }

                cash_txn_details = portal_dashboard_page.fetch_txn_details_by_type("Cash").split()
                logger.info(f"cash overall txn detail from portal :{cash_txn_details}")
                cash_txn_amount = cash_txn_details[3].replace(",", "")
                cash_txns = cash_txn_details[1].replace(",", "")
                portal_cash_sale_percentage = f"{float(cash_txn_details[4]):.2f}"

                actual_portal_values = {
                    "cash_txn_amount": cash_txn_amount,
                    "cash_total_txns": cash_txns,
                    "cash_sale_percentage": str(portal_cash_sale_percentage),
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
def test_mp_700_701_010():
    """
    Sub Feature Code: UI_MP_Payment_using_UPI_as_country_head
    Sub Feature Description: Verifying txn details on dashboard for payment done using UPI when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    010: TC010
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE8')
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

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

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

            amount = random.randint(300, 600)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('upiqrGenerate', request_body={
                "amount": amount,
                "username": txn_username,
                "password": txn_password,
                "orderNumber": order_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi txn via api : {response}")
            txn_id = response['txnId']
            logger.debug(f"upi txn id : {txn_id}")

            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "password": txn_password,
                "username": txn_username,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for upi txn via api : {response}")

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

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'UPI' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total upi sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_total_sale_db = str(result).split()[-1]
            logger.info(f"upi total sale from db : {upi_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'UPI' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total upi txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            upi_total_txns_db = str(result).split()[-1]
            logger.info(f"upi total txns from db : {upi_total_txns_db}")

            query = "select sum(amount) from txn where" \
                    " org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_upi_sale_percent = float(upi_total_sale_db) / float(overall_sale) * 100
            overall_upi_sale_percentage_db = f"{overall_upi_sale_percent:.2f}"
            logger.info(f"overall upi sale percentage db :{overall_upi_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"total sale amount from api  :{total_amount_api}")
            upi_total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']
                                         if element['paymentMode'] == 'UPI'])
            logger.info(f"upi total sale from api  :{upi_total_amount_api}")
            upi_total_number_of_txns_api = sum([element['count'] for element in response['paymentModeSegregation']
                                                if element['paymentMode'] == 'UPI'])
            logger.info(f"upi total number of txns from api  :{upi_total_number_of_txns_api}")

            upi_sale_percent_api = float(upi_total_amount_api) / float(total_amount_api) * 100
            upi_sale_percentage_api = f"{upi_sale_percent_api:.2f}"
            logger.info(f"overall upi sale percentage api :{upi_sale_percentage_api}")

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
                    "upi_txn_amount": upi_total_sale_db,
                    "upi_total_txns": upi_total_txns_db,
                    "upi_sale_percentage": overall_upi_sale_percentage_db
                }

                actual_api_values = {
                    "upi_txn_amount": str(upi_total_amount_api),
                    "upi_total_txns": str(upi_total_number_of_txns_api),
                    "upi_sale_percentage": upi_sale_percentage_api
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
                    "upi_txn_amount": str(upi_total_amount_api),
                    "upi_total_txns": str(upi_total_number_of_txns_api),
                    "upi_sale_percentage": upi_sale_percentage_api
                }

                actual_db_values = {
                    "upi_txn_amount": upi_total_sale_db,
                    "upi_total_txns": upi_total_txns_db,
                    "upi_sale_percentage": overall_upi_sale_percentage_db
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
                    "upi_txn_amount": upi_total_sale_db + "0",
                    "upi_total_txns": upi_total_txns_db,
                    "upi_sale_percentage": overall_upi_sale_percentage_db,
                }

                upi_txn_details = portal_dashboard_page.fetch_txn_details_by_type("UPI").split()
                logger.info(f"upi overall txn detail from portal :{upi_txn_details}")
                upi_txn_amount = upi_txn_details[3].replace(",", "")
                upi_txns = upi_txn_details[1].replace(",", "")
                portal_upi_sale_percentage = f"{float(upi_txn_details[4]):.2f}"

                actual_portal_values = {
                    "upi_txn_amount": upi_txn_amount,
                    "upi_total_txns": upi_txns,
                    "upi_sale_percentage": str(portal_upi_sale_percentage),
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
def test_mp_700_701_011():
    """
    Sub Feature Code: UI_MP_Payment_using_BQR_as_country_head
    Sub Feature Description: Verifying txn details on dashboard for payment done using BQR when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    011: TC011
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE9')
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

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='HDFC', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='BQRV4')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        api_details = DBProcessor.get_api_details('UPI_Enabled', request_body={"username": portal_username,
                                                                               "password": portal_password,
                                                                               "settingForOrgCode": org_code})
        api_details["RequestBody"]["settings"]["upiEnabled"] = "false"
        logger.debug(f"API details  : {api_details} ")
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting preconditions is : {response}")

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

            amount = random.randint(300, 600)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('bqrGenerate', request_body={
                "amount": amount,
                "password": txn_password,
                "qrCodeType": "BHARAT",
                "username": txn_username,
                "qrCodeFormat": "string",
                "orderNumber": order_id
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for bqr txn via api : {response}")
            txn_id = response['txnId']
            logger.debug(f"bqr txn id : {txn_id}")
            api_details = DBProcessor.get_api_details('stopPayment', request_body={
                "password": txn_password,
                "username": txn_username,
                "txnId": txn_id
            })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for bqr txn via api : {response}")

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

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'BHARATQR' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total bqr sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            bqr_total_sale_db = str(result).split()[-1]
            logger.info(f"bqr total sale from db : {bqr_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'BHARATQR' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total bqr txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            bqr_total_txns_db = str(result).split()[-1]
            logger.info(f"bqr total txns from db : {bqr_total_txns_db}")

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_bqr_sale_percent = float(bqr_total_sale_db) / float(overall_sale) * 100
            overall_bqr_sale_percentage_db = f"{overall_bqr_sale_percent:.2f}"
            logger.info(f"overall bqr sale percentage db :{overall_bqr_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"bqr details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"total sale amount of bqr  :{total_amount_api}")
            bqr_total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']
                                         if element['paymentMode'] == 'BHARATQR'])
            logger.info(f"bqr total sale from api  :{bqr_total_amount_api}")
            bqr_total_number_of_txns_api = sum([element['count'] for element in response['paymentModeSegregation']
                                            if element['paymentMode'] == 'BHARATQR'])
            logger.info(f"bqr total number of txns from api  :{bqr_total_number_of_txns_api}")

            bqr_sale_percent_api = float(bqr_total_amount_api) / float(total_amount_api) * 100
            bqr_sale_percentage_api = f"{bqr_sale_percent_api:.2f}"
            logger.info(f"overall bqr sale percentage api :{bqr_sale_percentage_api}")

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
                    "bqr_txn_amount": bqr_total_sale_db,
                    "bqr_total_txns": bqr_total_txns_db,
                    "bqr_sale_percentage": overall_bqr_sale_percentage_db
                }

                actual_api_values = {
                    "bqr_txn_amount": str(bqr_total_amount_api),
                    "bqr_total_txns": str(bqr_total_number_of_txns_api),
                    "bqr_sale_percentage": bqr_sale_percentage_api
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
                    "bqr_txn_amount": str(bqr_total_amount_api),
                    "bqr_total_txns": str(bqr_total_number_of_txns_api),
                    "bqr_sale_percentage": bqr_sale_percentage_api
                }

                actual_db_values = {
                    "bqr_txn_amount": bqr_total_sale_db,
                    "bqr_total_txns": bqr_total_txns_db,
                    "bqr_sale_percentage": overall_bqr_sale_percentage_db
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
                    "bqr_txn_amount": bqr_total_sale_db + "0",
                    "bqr_total_txns": bqr_total_txns_db,
                    "bqr_sale_percentage": overall_bqr_sale_percentage_db,
                }

                bqr_txn_details = portal_dashboard_page.fetch_txn_details_by_type("BQR").split()
                logger.info(f"bqr overall txn detail from portal :{bqr_txn_details}")
                bqr_txn_amount = bqr_txn_details[3].replace(",", "")
                bqr_txns = bqr_txn_details[1].replace(",", "")
                portal_bqr_sale_percentage = f"{float(bqr_txn_details[4]):.2f}"

                actual_portal_values = {
                    "bqr_txn_amount": bqr_txn_amount,
                    "bqr_total_txns": bqr_txns,
                    "bqr_sale_percentage": str(portal_bqr_sale_percentage),
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
def test_mp_700_701_012():
    """
    Sub Feature Code: UI_MP_Payment_using_CNP_as_country_head_as_country_head
    Sub Feature Description: Verifying txn details on dashboard for payment done using CNP when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    012: TC012
    """
    expectedSuccessMessage = "Your payment is successfully completed! You may close the browser now."
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        txn_cred = ResourceAssigner.get_org_users_credentials(testcase_id, 'STORE10')
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

            amount = random.randint(300, 400)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount,
                                                                    "externalRefNumber": order_id,
                                                                    "username": txn_username,
                                                                    "password": txn_password})
            response = APIProcessor.send_request(api_details)
            if response['success'] == False:
                raise Exception("Api could not initate a cnp txn.")
            else:
                paymentLinkUrl = response.get('paymentLink')
                page = TestSuiteSetup.initialize_ui_browser()
                page.goto(paymentLinkUrl)
                remotePayTxn = RemotePayTxnPage(page)
                remotePayTxn.clickOnDebitCardToExpand()
                remotePayTxn.enterNameOnTheCard("Sandeep")
                remotePayTxn.enterCreditCardNumber("4000 0000 0000 0119")
                remotePayTxn.enterDebitCardExpiryMonth("3")
                remotePayTxn.enterDebitCardExpiryYear("2048")
                remotePayTxn.enterCreditCardCvv("111")
                remotePayTxn.clickOnProceedToPay()
                remotePayTxn.wait_for_success_message()
                success_message = str(remotePayTxn.succcessScreenMessage())
                logger.info(f"Your success message is:  {success_message}")
                logger.info(f"Your expected success message is:  {expectedSuccessMessage}")
                assert success_message == expectedSuccessMessage, "Success messages are not matching."
            logger.debug(f"Response received for bqr txn via api : {response}")

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

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CNP' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total cnp sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_total_sale_db = str(result).split()[-1]
            logger.info(f"bqr total sale from db : {cnp_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CNP' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total cnp txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cnp_total_txns_db = str(result).split()[-1]
            logger.info(f"cnp total txns from db : {cnp_total_txns_db}")

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_cnp_sale_percent = float(cnp_total_sale_db) / float(overall_sale) * 100
            overall_cnp_sale_percentage_db = f"{overall_cnp_sale_percent:.2f}"
            logger.info(f"overall cnp sale percentage db :{overall_cnp_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            logger.info(f"mp login response from api : {response}")
            bearer_token = response['token']
            logger.info(f"bearer token from api : {bearer_token}")
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            api_details['Header'] = {'Authorization': 'Bearer ' + bearer_token, 'Content-Type': 'application/json'}
            logger.debug(f"cnp details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum(
                [float(element['amount']) for element in response['paymentModeSegregation']])
            logger.info(f"total sale amount of cnp  :{total_amount_api}")
            cnp_total_amount_api = sum([float(element['amount']) for element in response['paymentModeSegregation']
                                        if element['paymentMode'] == 'CNP'])
            logger.info(f"cnp total sale from api  :{cnp_total_amount_api}")
            cnp_total_number_of_txns_api = sum([element['count'] for element in response['paymentModeSegregation']
                                                if element['paymentMode'] == 'CNP'])
            logger.info(f"cnp total number of txns from api  :{cnp_total_number_of_txns_api}")

            cnp_sale_percent_api = float(cnp_total_amount_api) / float(total_amount_api) * 100
            cnp_sale_percentage_api = f"{cnp_sale_percent_api:.2f}"
            logger.info(f"overall cnp sale percentage api :{cnp_sale_percentage_api}")

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
                    "cnp_txn_amount": cnp_total_sale_db,
                    "cnp_total_txns": cnp_total_txns_db,
                    "cnp_sale_percentage": overall_cnp_sale_percentage_db
                }

                actual_api_values = {
                    "cnp_txn_amount": str(cnp_total_amount_api),
                    "cnp_total_txns": str(cnp_total_number_of_txns_api),
                    "cnp_sale_percentage": cnp_sale_percentage_api
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
                    "cnp_txn_amount": str(cnp_total_amount_api),
                    "cnp_total_txns": str(cnp_total_number_of_txns_api),
                    "cnp_sale_percentage": cnp_sale_percentage_api
                }

                actual_db_values = {
                    "cnp_txn_amount": cnp_total_sale_db,
                    "cnp_total_txns": cnp_total_txns_db,
                    "cnp_sale_percentage": overall_cnp_sale_percentage_db
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
                    "cnp_txn_amount": cnp_total_sale_db + "0",
                    "cnp_total_txns": cnp_total_txns_db,
                    "cnp_sale_percentage": overall_cnp_sale_percentage_db,
                }

                cnp_txn_details = portal_dashboard_page.fetch_txn_details_by_type("CNP").split()
                logger.info(f"cnp overall txn detail from portal :{cnp_txn_details}")
                cnp_txn_amount = cnp_txn_details[3].replace(",", "")
                cnp_txns = cnp_txn_details[1].replace(",", "")
                portal_cnp_sale_percentage = f"{float(cnp_txn_details[4]):.2f}"

                actual_portal_values = {
                    "cnp_txn_amount": cnp_txn_amount,
                    "cnp_total_txns": cnp_txns,
                    "cnp_sale_percentage": str(portal_cnp_sale_percentage),
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
