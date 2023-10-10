from datetime import datetime
import random
import sys
import pendulum
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.merchant_portal.Portal_DashboardPage import PortalDashboardPage
from PageFactory.Portal_LoginPage import PortalLoginPage
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, card_processor, \
    merchant_creator, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.dbVal
@pytest.mark.apiVal
@pytest.mark.portalVal
def test_mp_700_709_013():
    """
    Sub Feature Code: UI_MP_Payment_using_Cheque_as_Cashier
    Sub Feature Description: Verifying txn details on dashboard for payment done using Cheque when logged in as Cashier
    TC naming code description:
    700: Merchant Portal
    709: Cashier
    013: TC013
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
        login_username = cred_dict['CASHIER']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['CASHIER']['password']
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
        city_username = cred_dict['CITY']['username']
        logger.debug(f"Fetched city_username credentials from the ezeauto db : {city_username}")
        hub_username = cred_dict['HUB']['username']
        logger.debug(f"Fetched hub_username credentials from the ezeauto db : {hub_username}")
        store1_username = cred_dict['STORE1']['username']
        logger.debug(f"Fetched store1_username credentials from the ezeauto db : {store1_username}")

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

            amount = random.randint(500, 900)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            current_date = pendulum.now().format("YYYY-MM-DD")
            api_details = DBProcessor.get_api_details('mp_cheque',
                                                      request_body={"amount": str(amount),
                                                                    "username": txn_username,
                                                                    "password": txn_password,
                                                                    "chequeNumber": order_id,
                                                                    "chequeDate": current_date
                                                                    })
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received for cheque txn via api : {response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_date_range = portal_dashboard_page.fetch_sales_overview_indicators_dates()
            logger.info(f"current sales date range from portal : {current_date_range}")

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_date_range[1], '%b').month
            end_month = datetime.strptime(current_date_range[4], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_date_range[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_date_range[3]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CHEQUE' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "'and username = '" + txn_username + "';"
            logger.info(f"query to fetch total cnp sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cheque_total_sale_db = str(result).split()[-1]
            logger.info(f"cheque total sale from db : {cheque_total_sale_db}")

            query = "select count(*) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CHEQUE' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total cheque txns sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            cheque_total_txns_db = str(result).split()[-1]
            logger.info(f"cheque total txns from db : {cheque_total_txns_db}")

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_sale = result.values[0]
            logger.info(f"overall sale from db : {overall_sale}")

            overall_cheque_sale_percent = float(cheque_total_sale_db) / float(overall_sale) * 100
            overall_cheque_sale_percentage_db = f"{overall_cheque_sale_percent:.2f}"
            logger.info(f"overall cheque sale percentage db :{overall_cheque_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"cnp details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            total_amount_api = sum(
                [float(element['amount']) for element in response['aggregatedTxnResults']])
            logger.info(f"total sale amount of cheque  :{total_amount_api}")
            cheque_total_amount_api = 0
            cheque_total_amount_api += sum([float(element['cheque']['amount'])
                                            for element in response['aggregatedTxnResults']])
            logger.info(f"cheque total sale from api  :{cheque_total_amount_api}")
            cheque_total_number_of_txns_api = 0
            cheque_total_number_of_txns_api += sum([element['cheque']['count']
                                                    for element in response['aggregatedTxnResults']])
            logger.info(f"cheque total number of txns from api  :{cheque_total_number_of_txns_api}")

            cheque_sale_percent_api = float(cheque_total_amount_api) / float(total_amount_api) * 100
            cheque_sale_percentage_api = f"{cheque_sale_percent_api:.2f}"
            logger.info(f"overall cheque sale percentage api :{cheque_sale_percentage_api}")

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
                    "cheque_txn_amount": cheque_total_sale_db,
                    "cheque_total_txns": cheque_total_txns_db,
                    "cheque_sale_percentage": overall_cheque_sale_percentage_db
                }

                actual_api_values = {
                    "cheque_txn_amount": str(cheque_total_amount_api),
                    "cheque_total_txns": str(cheque_total_number_of_txns_api),
                    "cheque_sale_percentage": cheque_sale_percentage_api
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
                    "cheque_txn_amount": str(cheque_total_amount_api),
                    "cheque_total_txns": str(cheque_total_number_of_txns_api),
                    "cheque_sale_percentage": cheque_sale_percentage_api
                }

                actual_db_values = {
                    "cheque_txn_amount": cheque_total_sale_db,
                    "cheque_total_txns": cheque_total_txns_db,
                    "cheque_sale_percentage": overall_cheque_sale_percentage_db
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
                    "cheque_txn_amount": cheque_total_sale_db + "0",
                    "cheque_total_txns": cheque_total_txns_db,
                    "cheque_sale_percentage": overall_cheque_sale_percentage_db,
                }

                cheque_txn_details = portal_dashboard_page.fetch_txn_details_by_type("Cheque").split()
                logger.info(f"cnp overall txn detail from portal :{cheque_txn_details}")
                cheque_txn_amount = cheque_txn_details[3].replace(",", "")
                cheque_txns = cheque_txn_details[1].replace(",", "")
                portal_cheque_sale_percentage = f"{float(cheque_txn_details[4]):.2f}"

                actual_portal_values = {
                    "cheque_txn_amount": cheque_txn_amount,
                    "cheque_total_txns": cheque_txns,
                    "cheque_sale_percentage": str(portal_cheque_sale_percentage),
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
def test_mp_700_709_014():
    """
    Sub Feature Code: UI_MP_Payment_using_Normal_EMI_as_Cashier
    Sub Feature Description: Verifying txn details on dashboard for payment done using Normal_EMI when logged in as Cashier
    TC naming code description:
    700: Merchant Portal
    709: Cashier
    014: TC014
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
        login_username = cred_dict['CASHIER']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['CASHIER']['password']
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
        city_username = cred_dict['CITY']['username']
        logger.debug(f"Fetched city_username credentials from the ezeauto db : {city_username}")
        hub_username = cred_dict['HUB']['username']
        logger.debug(f"Fetched hub_username credentials from the ezeauto db : {hub_username}")
        store1_username = cred_dict['STORE1']['username']
        logger.debug(f"Fetched store1_username credentials from the ezeauto db : {store1_username}")

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

            amount = random.randint(3000, 9000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_CREDIT_VISA")
            api_details = DBProcessor.get_api_details('mp_normal_emi', request_body={
                                                        "username": txn_username,
                                                        "password": txn_password,
                                                        "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                        org_code=org_code, acquisition="HDFC",
                                                        payment_gateway="HDFC"),
                                                        "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                        "emiType": "NORMAL",
                                                        "amount": str(amount),
                                                        "nonce": card_details['Nonce']})

            response = APIProcessor.send_request(api_details)
            logger.info(f"response : {response}")
            emi_id = response['emiOptions'][0]['emiId']
            logger.debug(f"emi id from api : {emi_id}")

            api_details = DBProcessor.get_api_details('mp_card_payment_emi', request_body={
                                                        "username": txn_username,
                                                        "password": txn_password,
                                                        "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                        org_code=org_code, acquisition="HDFC",
                                                        payment_gateway="HDFC"),
                                                        "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                        "amount": str(amount),
                                                        "originalAmount": str(amount),
                                                        "emiId": emi_id,
                                                        "emiType": "NORMAL",
                                                        "nonce": card_details['Nonce']})
            response = APIProcessor.send_request(api_details)
            logger.info(f"response_2 : {response}")

            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                         "Ezetap Device Data"],
                                                                        "txnId": txn_id})
                confirm_response = APIProcessor.send_request(api_details)
                logger.info(f"confirm response from api : {confirm_response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_date_range = portal_dashboard_page.fetch_sales_overview_indicators_dates()
            logger.info(f"current sales date range from portal : {current_date_range}")

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_date_range[1], '%b').month
            end_month = datetime.strptime(current_date_range[4], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_date_range[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_date_range[3]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"

            # query = "select sum(amount) from txn where org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and id between '" + current_start_date_1[2:] + "' and '" + current_end_date_1[2:] + "';"
            query = "SELECT sum(amount) from txn where " \
                    "id BETWEEN '" + current_start_date_1 + "' AND '" + current_end_date_1 + "' and org_code='" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and payment_card_type ='CREDIT' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total credit card sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            credit_card_total_sale_db = str(result).split()[-1]
            logger.info(f"credit card total sale from db : {credit_card_total_sale_db}")

            query = "SELECT count(*) from txn where id " \
                    "BETWEEN '" + current_start_date_1 + "' AND '" + current_end_date_1 + "' and org_code='" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and payment_card_type ='CREDIT' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total credit card txns from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            credit_card_total_txns_db = str(result).split()[-1]
            logger.info(f"credit card total txns from db : {credit_card_total_txns_db}")

            query = "select sum(amount) from txn where " \
                    "org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and payment_mode = 'CARD' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_card_sale = result.values[0]
            logger.info(f"overall card sale from db : {overall_card_sale}")

            overall_credit_card_sale_percent = float(credit_card_total_sale_db)/float(overall_card_sale)*100
            overall_credit_card_sale_percentage_db = f"{overall_credit_card_sale_percent:.2f}"
            logger.info(f"overall credit card sale percentage db :{overall_credit_card_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            txn_by_type_cards = ['credit', "debit", "others"]
            total_card_amount_api = 0
            for card_type in txn_by_type_cards:
                total_card_amount_api += sum([float(element['cards'][card_type]['amount'])
                                              for element in response['aggregatedTxnResults']])
            logger.info(f"total card sale from api  :{total_card_amount_api}")
            credit_card_total_amount_api = 0
            for card_type in txn_by_type_cards:
                if card_type == "credit":
                    credit_card_total_amount_api += sum([float(element['cards'][card_type]['amount'])
                                                         for element in response['aggregatedTxnResults']])
            logger.info(f"credit card total sale from api  :{credit_card_total_amount_api}")
            credit_card_total_number_of_txns_api = 0
            for card_type in txn_by_type_cards:
                if card_type == "credit":
                    credit_card_total_number_of_txns_api += sum([element['cards'][card_type]['count']
                                                                 for element in response['aggregatedTxnResults']])
            logger.info(f"credit card total number of txns from api  :{credit_card_total_number_of_txns_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username_1 from api :{username_api_1}")

            credit_card_sale_percent_api = float(credit_card_total_amount_api) / float(total_card_amount_api) * 100
            credit_card_sale_percentage_api = f"{credit_card_sale_percent_api:.2f}"
            logger.info(f"overall credit card sale percentage api :{credit_card_sale_percentage_api}")

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
                    "card_txn_amount": credit_card_total_sale_db,
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
                }

                actual_api_values = {
                    "card_txn_amount": str(credit_card_total_amount_api),
                    "card_total_txns": str(credit_card_total_number_of_txns_api),
                    "card_sale_percentage": credit_card_sale_percentage_api,
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
                    "card_txn_amount": str(credit_card_total_amount_api),
                    "card_total_txns": str(credit_card_total_number_of_txns_api),
                    "card_sale_percentage": credit_card_sale_percentage_api,
                }

                actual_db_values = {
                    "card_txn_amount": credit_card_total_sale_db,
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
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
                    "card_txn_amount": credit_card_total_sale_db + "0",
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
                }

                credit_card_txn_details = portal_dashboard_page.fetch_txn_details_by_type("Credit Card").split()
                logger.info(f"credit card overall txn detail from portal :{credit_card_txn_details}")
                credit_card_txn_amount = credit_card_txn_details[4].replace(",", "")
                credit_card_txns = credit_card_txn_details[2].replace(",", "")
                portal_credit_card_sale_percentage = f"{float(credit_card_txn_details[5]):.2f}"

                actual_portal_values = {
                    "card_txn_amount": credit_card_txn_amount,
                    "card_total_txns": credit_card_txns,
                    "card_sale_percentage": str(portal_credit_card_sale_percentage),
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
def test_mp_700_709_015():
    """
    Sub Feature Code: UI_MP_Payment_using_Brand_EMI_as_Cashier
    Sub Feature Description: Verifying txn details on dashboard for payment done using BrandEMI when logged in as Cashier
    TC naming code description:
    700: Merchant Portal
    709: Cashier
    015: TC015
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
        login_username = cred_dict['CASHIER']['username']
        logger.debug(f"Fetched login_username credentials from the ezeauto db : {login_username}")
        login_password = cred_dict['CASHIER']['password']
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
        city_username = cred_dict['CITY']['username']
        logger.debug(f"Fetched city_username credentials from the ezeauto db : {city_username}")
        hub_username = cred_dict['HUB']['username']
        logger.debug(f"Fetched hub_username credentials from the ezeauto db : {hub_username}")
        store1_username = cred_dict['STORE1']['username']
        logger.debug(f"Fetched store1_username credentials from the ezeauto db : {store1_username}")

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

            api_details = DBProcessor.get_api_details('mp_brand_details', request_body={"username": txn_username,
                                                                                        "password": txn_password,
                                                                                        "emiType": "BRAND"})
            response = APIProcessor.send_request(api_details)
            brand_id = response['brandDetails'][0]['brandId']
            logger.debug(f"brand id from api : {brand_id}")
            sku_id = response['brandDetails'][0]['productDetails'][0]['skuId']
            logger.debug(f"sku id from api : {sku_id}")

            amount = random.randint(3000, 9000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_CREDIT_VISA")
            api_details = DBProcessor.get_api_details('mp_fetch_emi_options', request_body={
                                                                "amount": amount,
                                                                "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                                org_code=org_code, acquisition="HDFC",
                                                                payment_gateway="HDFC"),
                                                                "emiType": "BRAND",
                                                                "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                "nonce": card_details['Nonce'],
                                                                "username": txn_username,
                                                                "password": txn_password,
                                                                "productBrandId": brand_id,
                                                                "productSkuId": sku_id})

            response = APIProcessor.send_request(api_details)
            logger.info(f"response : {response}")
            emi_id = response['emiOptions'][0]['emiId']
            logger.debug(f"emi_id from api : {emi_id}")

            api_details = DBProcessor.get_api_details('mp_card_payment_brand_emi', request_body={
                                                                   "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                                   "nonce": card_details['Nonce'],
                                                                   "username": txn_username,
                                                                   "password": txn_password,
                                                                   "amount": str(amount),
                                                                   "originalAmount": str(amount),
                                                                   "deviceSerial":  merchant_creator.get_device_serial_of_merchant(
                                                                    org_code=org_code, acquisition="HDFC",
                                                                    payment_gateway="HDFC"),
                                                                   "emiType": "BRAND",
                                                                   "emiId": emi_id})
            response = APIProcessor.send_request(api_details)
            logger.info(f"response for card payment : {response}")

            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                        "Ezetap Device Data"],
                                                                        "txnId": txn_id})
                confirm_response = APIProcessor.send_request(api_details)
                logger.info(f"confirm response from api : {confirm_response}")

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)
            portal_dashboard_page = PortalDashboardPage(GlobalVariables.portal_page)
            current_date_range = portal_dashboard_page.fetch_sales_overview_indicators_dates()
            logger.info(f"current sales date range from portal : {current_date_range}")

            # Converting merchant portal current sale dates into full date format to fetch details from DB
            year = int(pendulum.now().format("YYYY"))
            start_month = datetime.strptime(current_date_range[1], '%b').month
            end_month = datetime.strptime(current_date_range[4], '%b').month
            current_start_date = pendulum.datetime(year=year, month=start_month, day=int(current_date_range[0]))
            current_start_date_1 = current_start_date.subtract(days=1).format('YYMMDD') + "1830"
            current_end_date = pendulum.datetime(year=year, month=end_month, day=int(current_date_range[3]))
            current_end_date_1 = current_end_date.format('YYMMDD') + "1829"

            # query = "select sum(amount) from txn where org_code = '" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and id between '" + current_start_date_1[2:] + "' and '" + current_end_date_1[2:] + "';"
            query = "SELECT sum(amount) from txn where " \
                    "id BETWEEN '" + current_start_date_1 + "' AND '" + current_end_date_1 + "' and org_code='" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and payment_card_type ='CREDIT' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total credit card sale from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            credit_card_total_sale_db = str(result).split()[-1]
            logger.info(f"credit card total sale from db : {credit_card_total_sale_db}")

            query = "SELECT count(*) from txn where " \
                    "id BETWEEN '" + current_start_date_1 + "' AND '" + current_end_date_1 + "' and org_code='" + org_code + "' and status = 'AUTHORIZED' and payment_mode = 'CARD' and payment_card_type ='CREDIT' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total credit card txns from db : {query}")
            result = DBProcessor.getValueFromDB(query)
            credit_card_total_txns_db = str(result).split()[-1]
            logger.info(f"credit card total txns from db : {credit_card_total_txns_db}")

            query = "select sum(amount) from txn where" \
                    " org_code = '" + org_code + "' and status = 'AUTHORIZED' and id between '" + current_start_date_1 + "' and '" + current_end_date_1 + "' and payment_mode = 'CARD' and username = '" + txn_username + "';"
            logger.info(f"query to fetch total overall sale : {query}")
            result = DBProcessor.getValueFromDB(query)
            overall_card_sale = result.values[0]
            logger.info(f"overall card sale from db : {overall_card_sale}")

            overall_credit_card_sale_percent = float(credit_card_total_sale_db)/float(overall_card_sale)*100
            overall_credit_card_sale_percentage_db = f"{overall_credit_card_sale_percent:.2f}"
            logger.info(f"overall credit card sale percentage db :{overall_credit_card_sale_percentage_db}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            this_start_date_1 = current_start_date.format('YYYY-MM-DD')
            this_end_date_1 = current_end_date.format('YYYY-MM-DD')
            api_details = DBProcessor.get_api_details('mp_txn_details', request_body={
                "startDate": this_start_date_1,
                "endDate": this_end_date_1
            })
            logger.info(f"bearer token from api : {response}")
            api_details['Header'] = {'Authorization': 'Bearer ' + response, 'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for Txn Dashboard is: {response}")
            txn_by_type_cards = ['credit', "debit", "others"]
            total_card_amount_api = 0
            for card_type in txn_by_type_cards:
                total_card_amount_api += sum([float(element['cards'][card_type]['amount'])
                                              for element in response['aggregatedTxnResults']])
            logger.info(f"total card sale from api  :{total_card_amount_api}")
            credit_card_total_amount_api = 0
            for card_type in txn_by_type_cards:
                if card_type == "credit":
                    credit_card_total_amount_api += sum([float(element['cards'][card_type]['amount'])
                                                         for element in response['aggregatedTxnResults']])
            logger.info(f"credit card total sale from api  :{credit_card_total_amount_api}")
            credit_card_total_number_of_txns_api = 0
            for card_type in txn_by_type_cards:
                if card_type == "credit":
                    credit_card_total_number_of_txns_api += sum([element['cards'][card_type]['count']
                                                                 for element in response['aggregatedTxnResults']])
            logger.info(f"credit card total number of txns from api  :{credit_card_total_number_of_txns_api}")
            org_code_api_1 = response['orgCode']
            logger.info(f"org code from api :{org_code_api_1}")
            username_api_1 = response['username']
            logger.info(f"username_1 from api :{username_api_1}")

            credit_card_sale_percent_api = float(credit_card_total_amount_api) / float(total_card_amount_api) * 100
            credit_card_sale_percentage_api = f"{credit_card_sale_percent_api:.2f}"
            logger.info(f"overall credit card sale percentage api :{credit_card_sale_percentage_api}")

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
                    "card_txn_amount": credit_card_total_sale_db,
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
                }

                actual_api_values = {
                    "card_txn_amount": str(credit_card_total_amount_api),
                    "card_total_txns": str(credit_card_total_number_of_txns_api),
                    "card_sale_percentage": credit_card_sale_percentage_api,
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
                    "card_txn_amount": credit_card_total_sale_db,
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
                }

                actual_db_values = {
                    "card_txn_amount": str(credit_card_total_amount_api),
                    "card_total_txns": str(credit_card_total_number_of_txns_api),
                    "card_sale_percentage": credit_card_sale_percentage_api,
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
                    "card_txn_amount": credit_card_total_sale_db + "0",
                    "card_total_txns": credit_card_total_txns_db,
                    "card_sale_percentage": overall_credit_card_sale_percentage_db,
                }

                credit_card_txn_details = portal_dashboard_page.fetch_txn_details_by_type("Credit Card").split()
                logger.info(f"credit card overall txn detail from portal :{credit_card_txn_details}")
                credit_card_txn_amount = credit_card_txn_details[4].replace(",", "")
                credit_card_txns = credit_card_txn_details[2].replace(",", "")
                portal_credit_card_sale_percentage = f"{float(credit_card_txn_details[5]):.2f}"

                actual_portal_values = {
                    "card_txn_amount": credit_card_txn_amount,
                    "card_total_txns": credit_card_txns,
                    "card_sale_percentage": str(portal_credit_card_sale_percentage),
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
