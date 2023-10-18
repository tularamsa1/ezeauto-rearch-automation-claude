from datetime import datetime, timedelta
import random
import sys
import pytest
import locale
from Configuration import Configuration, TestSuiteSetup
from DataProvider import GlobalVariables
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.merchant_portal.Portal_ReportsPage import TransHistoryPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_701_023():
    """
    Sub Feature Code: UI_MP_Report_based_on_username_as_country_head
    Sub Feature Description: Verifying txn details on Report Page using Filter username when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    023: TC023
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
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")

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

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------

            amount = random.randint(10, 500)
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "amount": amount
            })
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received after cash transaction is : {response}")

            txn_id = response['txnId']
            logger.debug(f"txn_id after cash transaction is : {txn_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response['token']
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")

            username_search_value = [{"label": "username", "value": f"{txn_username}"}]

            api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                "startDateAndTime": current_date + " 00:00",
                "endDateAndTime": current_date + " 23:59",
                "maxRecordsPerPage": 100,
                "pageNumber": 0,
                "usersList": [],
                "cardType": [],
                "cardBrand": [],
                "transactionStatus": [],
                "selectSearchOptions": [],
                "paymentMode": [],
                "totalPages": 0,
                "nodeIds": [],
                "totalRecords": 0,
                "selectUniversalSearch": username_search_value
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for TxnReport is: {response}")
            total_pages = response['totalPages']
            logger.debug(
                f"total number of pages from txn report api: {total_pages}, type of total_pages: {type(total_pages)}")
            total_pages = int(total_pages)

            api_first_txn_details = response["transactions"][0]
            logger.debug(f"api_first_txn_details: {api_first_txn_details}")

            api_first_created_time = api_first_txn_details['createdTime']
            api_first_pmt_state = api_first_txn_details['state']
            api_first_pmt_status = api_first_txn_details['status']
            api_first_pmt_settle_status = api_first_txn_details['settlementStatus']
            api_first_pmt_mode = api_first_txn_details['type']
            api_first_amount = api_first_txn_details['amount']
            api_first_txn_type = api_first_txn_details['txnType']
            api_first_order_id = api_first_txn_details['externalRefNumber']
            api_first_username = api_first_txn_details['username']
            api_first_txn_id = api_first_txn_details['id']
            api_first_hierarchy = api_first_txn_details['hierarchy']
            api_first_org_code = api_first_txn_details['merchantCode']

            if total_pages > 1:
                api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                    "startDateAndTime": current_date + " 00:00",
                    "endDateAndTime": current_date + " 23:59",
                    "maxRecordsPerPage": 100,
                    "pageNumber": total_pages - 1,
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [],
                    "totalPages": 0,
                    "nodeIds": [],
                    "totalRecords": 0,
                    "selectUniversalSearch": username_search_value
                })

                api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for TxnReport : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.info(f"Response obtained for TxnReport is: {response}")

                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']
            else:
                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)

            trans_history_page = TransHistoryPage(GlobalVariables.portal_page)
            trans_history_page.click_on_reports()
            trans_history_page.click_on_transactions()
            trans_history_page.search_based_on_username(txn_username)
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            # now we are taking the previous day of the current_date for UTC conversion
            prev_day = current_date - timedelta(days=1)
            logger.debug(f"prev_day for UTC converison: {prev_day}")
            prev_day = prev_day.strftime('%y%m%d')
            logger.debug(f"prev_day in Y/M/D format for UTC conversion: {prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            start_date_time_utc = prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and username='" + txn_username + "' order by created_time asc limit 1;"
            logger.debug(f"Query to fetch last transaction from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id_last = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id_last}")
            db_rrn_last = result['rr_number'].values[0]
            logger.debug(f"rrn number from db : {db_rrn_last}")
            db_auth_code_last = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code_last}")
            db_amount_last = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount_last}")
            db_username_last = result['username'].values[0]
            logger.debug(f"username from db : {db_username_last}")
            db_pmt_mode_last = result['payment_mode'].values[0]
            logger.debug(f"pmt mode from db: {db_pmt_mode_last}")
            db_pmt_status_last = result['status'].values[0]
            logger.debug(f" pmt status from db: {db_pmt_status_last}")
            db_created_time_last = result['created_time'].values[0]
            logger.debug(f" created time from db: {db_created_time_last}")
            db_pmt_state_last = result['state'].values[0]
            logger.debug(f" pmt state from db: {db_pmt_state_last}")
            db_txn_type_last = result['txn_type'].values[0]
            logger.debug(f"txn type from db: {db_txn_type_last}")
            db_pmt_settle_status_last = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db: {db_pmt_settle_status_last}")
            db_org_code_last = result['org_code'].values[0]
            logger.debug(f"org code from db: {db_org_code_last}")
            db_order_id_last = result['external_ref'].values[0]
            logger.debug(f"order id from db: {db_order_id_last}")
            db_cust_mob_last = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob_last}")
            db_labels_last = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels_last}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"rr number from db : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code}")
            db_created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {db_created_time}")
            db_username = result['username'].values[0]
            logger.debug(f"username from db : {db_username}")
            db_amount = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount}")
            db_status = result['status'].values[0]
            logger.debug(f"status from db : {db_status}")
            db_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db : {db_settle_status}")
            db_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db : {db_pmt_mode}")
            db_txn_type = result['txn_type'].values[0]
            logger.debug(f"txn type from db : {db_txn_type}")
            db_org_code = result['org_code'].values[0]
            logger.debug(f"org code from db : {db_org_code}")
            db_pmt_state = result['state'].values[0]
            logger.debug(f"state from db : {db_pmt_state}")
            db_order_id = result['external_ref'].values[0]
            logger.debug(f"order id from db : {db_order_id}")
            db_cust_mob = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob}")
            db_labels = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_last = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                actual_api_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }

                actual_db_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                locale.setlocale(locale.LC_ALL, 'en_IN')
                formatted_amount_first = str(locale.currency(db_amount, grouping=True)).replace('₹', '₹ ')
                formatted_amount_last = str(locale.currency(db_amount_last, grouping=True)).replace('₹', '₹ ')
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": formatted_amount_first,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "rrn": "-" if db_rrn is None else db_rrn,
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "cust_mobile": "-" if db_cust_mob is None else db_cust_mob,
                    "labels": "-" if db_labels is None else db_labels,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_type_2": db_pmt_mode_last,
                    "txn_amt_2": formatted_amount_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "rrn_2": "-" if db_rrn_last is None else db_rrn_last,
                    "auth_code_2": "-" if db_auth_code_last is None else db_auth_code_last,
                    "cust_mobile_2": "-" if db_cust_mob_last is None else db_cust_mob_last,
                    "labels_2": "-" if db_labels_last is None else db_labels_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                date_time = txn_details[0]['Date & Time']
                transaction_id = txn_details[0]['Transaction ID']
                total_amount = txn_details[0]['Total Amount']
                rr_number = txn_details[0]['RR Number']
                transaction_type = txn_details[0]['Type']
                status = txn_details[0]['Status']
                username = txn_details[0]['Username']
                auth_code = txn_details[0]['Auth Code']
                hierarchy = txn_details[0]['Hierarchy']
                cust_mobile = txn_details[0]['Mobile No.']
                labels = txn_details[0]['Labels']

                date_time_last = txn_details[-1]['Date & Time']
                transaction_id_last = txn_details[-1]['Transaction ID']
                total_amount_last = txn_details[-1]['Total Amount']
                rr_number_last = txn_details[-1]['RR Number']
                transaction_type_last = txn_details[-1]['Type']
                status_last = txn_details[-1]['Status']
                username_last = txn_details[-1]['Username']
                auth_code_last = txn_details[-1]['Auth Code']
                hierarchy_last = txn_details[-1]['Hierarchy']
                cust_mobile_last = txn_details[-1]['Mobile No.']
                labels_last = txn_details[-1]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount,
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code,
                    "cust_mobile": cust_mobile,
                    "labels": labels,
                    "hierarchy": hierarchy,

                    "date_time_2": date_time_last,
                    "pmt_status_2": status_last,
                    "pmt_type_2": transaction_type_last,
                    "txn_amt_2": total_amount_last,
                    "username_2": username_last,
                    "txn_id_2": transaction_id_last,
                    "rrn_2": rr_number_last,
                    "auth_code_2": auth_code_last,
                    "cust_mobile_2": cust_mobile_last,
                    "labels_2": labels_last,
                    "hierarchy_2": hierarchy_last,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_701_024():
    """
    Sub Feature Code: UI_MP_Repor_based_on_order_number_as_country_head
    Sub Feature Description: Verifying txn details on Report Page using Filter order number when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    024: TC024
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
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")

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

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(10, 500)
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "amount": amount
            })
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received after cash transaction is : {response}")

            txn_id = response['txnId']
            logger.debug(f"txn_id after cash transaction is : {txn_id}")
            order_number = response['externalRefNumber']
            logger.debug(f"order_number after cash transaction is : {order_number}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response['token']
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")
            order_number_search_value = [{"label": "external_ref", "value": f"{order_number}"}]

            api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                "startDateAndTime": current_date + " 00:00",
                "endDateAndTime": current_date + " 23:59",
                "maxRecordsPerPage": 100,
                "pageNumber": 0,
                "usersList": [],
                "cardType": [],
                "cardBrand": [],
                "transactionStatus": [],
                "selectSearchOptions": [],
                "paymentMode": [],
                "totalPages": 0,
                "nodeIds": [],
                "totalRecords": 0,
                "selectUniversalSearch": order_number_search_value
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for TxnReport is: {response}")
            total_pages = response['totalPages']
            logger.debug(
                f"total number of pages from txn report api: {total_pages}, type of total_pages: {type(total_pages)}")
            total_pages = int(total_pages)

            api_first_txn_details = response["transactions"][0]
            logger.debug(f"api_first_txn_details: {api_first_txn_details}")

            api_first_created_time = api_first_txn_details['createdTime']
            api_first_pmt_state = api_first_txn_details['state']
            api_first_pmt_status = api_first_txn_details['status']
            api_first_pmt_settle_status = api_first_txn_details['settlementStatus']
            api_first_pmt_mode = api_first_txn_details['type']
            api_first_amount = api_first_txn_details['amount']
            api_first_txn_type = api_first_txn_details['txnType']
            api_first_order_id = api_first_txn_details['externalRefNumber']
            api_first_username = api_first_txn_details['username']
            api_first_txn_id = api_first_txn_details['id']
            api_first_hierarchy = api_first_txn_details['hierarchy']
            api_first_org_code = api_first_txn_details['merchantCode']

            if total_pages > 1:
                api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                    "startDateAndTime": current_date + " 00:00",
                    "endDateAndTime": current_date + " 23:59",
                    "maxRecordsPerPage": 100,
                    "pageNumber": total_pages - 1,
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [],
                    "totalPages": 0,
                    "nodeIds": [],
                    "totalRecords": 0,
                    "selectUniversalSearch": order_number_search_value
                })

                api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for TxnReport : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.info(f"Response obtained for TxnReport is: {response}")

                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']
            else:
                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)

            trans_history_page = TransHistoryPage(GlobalVariables.portal_page)
            trans_history_page.click_on_reports()
            trans_history_page.click_on_transactions()
            trans_history_page.search_based_on_order_number(order_number)
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            # now we are taking the previous day of the current_date for UTC conversion
            prev_day = current_date - timedelta(days=1)
            logger.debug(f"prev_day for UTC converison: {prev_day}")
            prev_day = prev_day.strftime('%y%m%d')
            logger.debug(f"prev_day in Y/M/D format for UTC conversion: {prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            start_date_time_utc = prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and external_ref='" + order_number + "' order by created_time asc limit 1;"
            logger.debug(f"Query to fetch last transaction from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id_last = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id_last}")
            db_rrn_last = result['rr_number'].values[0]
            logger.debug(f"rrn number from db : {db_rrn_last}")
            db_auth_code_last = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code_last}")
            db_amount_last = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount_last}")
            db_username_last = result['username'].values[0]
            logger.debug(f"username from db : {db_username_last}")
            db_pmt_mode_last = result['payment_mode'].values[0]
            logger.debug(f"pmt mode from db: {db_pmt_mode_last}")
            db_pmt_status_last = result['status'].values[0]
            logger.debug(f" pmt status from db: {db_pmt_status_last}")
            db_created_time_last = result['created_time'].values[0]
            logger.debug(f" created time from db: {db_created_time_last}")
            db_pmt_state_last = result['state'].values[0]
            logger.debug(f" pmt state from db: {db_pmt_state_last}")
            db_txn_type_last = result['txn_type'].values[0]
            logger.debug(f"txn type from db: {db_txn_type_last}")
            db_pmt_settle_status_last = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db: {db_pmt_settle_status_last}")
            db_org_code_last = result['org_code'].values[0]
            logger.debug(f"org code from db: {db_org_code_last}")
            db_order_id_last = result['external_ref'].values[0]
            logger.debug(f"order id from db: {db_order_id_last}")
            db_cust_mob_last = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob_last}")
            db_labels_last = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels_last}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"rr number from db : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code}")
            db_created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {db_created_time}")
            db_username = result['username'].values[0]
            logger.debug(f"username from db : {db_username}")
            db_amount = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount}")
            db_status = result['status'].values[0]
            logger.debug(f"status from db : {db_status}")
            db_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db : {db_settle_status}")
            db_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db : {db_pmt_mode}")
            db_txn_type = result['txn_type'].values[0]
            logger.debug(f"txn type from db : {db_txn_type}")
            db_org_code = result['org_code'].values[0]
            logger.debug(f"org code from db : {db_org_code}")
            db_pmt_state = result['state'].values[0]
            logger.debug(f"state from db : {db_pmt_state}")
            db_order_id = result['external_ref'].values[0]
            logger.debug(f"order id from db : {db_order_id}")
            db_cust_mob = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob}")
            db_labels = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_last = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                actual_api_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }

                actual_db_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                locale.setlocale(locale.LC_ALL, 'en_IN')
                formatted_amount_first = str(locale.currency(db_amount, grouping=True)).replace('₹', '₹ ')
                formatted_amount_last = str(locale.currency(db_amount_last, grouping=True)).replace('₹', '₹ ')
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": formatted_amount_first,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "rrn": "-" if db_rrn is None else db_rrn,
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "cust_mobile": "-" if db_cust_mob is None else db_cust_mob,
                    "labels": "-" if db_labels is None else db_labels,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_type_2": db_pmt_mode_last,
                    "txn_amt_2": formatted_amount_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "rrn_2": "-" if db_rrn_last is None else db_rrn_last,
                    "auth_code_2": "-" if db_auth_code_last is None else db_auth_code_last,
                    "cust_mobile_2": "-" if db_cust_mob_last is None else db_cust_mob_last,
                    "labels_2": "-" if db_labels_last is None else db_labels_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                date_time = txn_details[0]['Date & Time']
                transaction_id = txn_details[0]['Transaction ID']
                total_amount = txn_details[0]['Total Amount']
                rr_number = txn_details[0]['RR Number']
                transaction_type = txn_details[0]['Type']
                status = txn_details[0]['Status']
                username = txn_details[0]['Username']
                auth_code = txn_details[0]['Auth Code']
                hierarchy = txn_details[0]['Hierarchy']
                cust_mobile = txn_details[0]['Mobile No.']
                labels = txn_details[0]['Labels']

                date_time_last = txn_details[-1]['Date & Time']
                transaction_id_last = txn_details[-1]['Transaction ID']
                total_amount_last = txn_details[-1]['Total Amount']
                rr_number_last = txn_details[-1]['RR Number']
                transaction_type_last = txn_details[-1]['Type']
                status_last = txn_details[-1]['Status']
                username_last = txn_details[-1]['Username']
                auth_code_last = txn_details[-1]['Auth Code']
                hierarchy_last = txn_details[-1]['Hierarchy']
                cust_mobile_last = txn_details[-1]['Mobile No.']
                labels_last = txn_details[-1]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount,
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code,
                    "cust_mobile": cust_mobile,
                    "labels": labels,
                    "hierarchy": hierarchy,

                    "date_time_2": date_time_last,
                    "pmt_status_2": status_last,
                    "pmt_type_2": transaction_type_last,
                    "txn_amt_2": total_amount_last,
                    "username_2": username_last,
                    "txn_id_2": transaction_id_last,
                    "rrn_2": rr_number_last,
                    "auth_code_2": auth_code_last,
                    "cust_mobile_2": cust_mobile_last,
                    "labels_2": labels_last,
                    "hierarchy_2": hierarchy_last,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_701_025():
    """
    Sub Feature Code: UI_MP_Report_based_on_calender_dates_as_country_head
    Sub Feature Description: Verifying txn details on Report Page using Filter calender dates when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    025: TC025
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
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")

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

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(10, 500)
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "amount": amount
            })
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received after cash transaction is : {response}")

            txn_id = response['txnId']
            logger.debug(f"txn_id after cash transaction is : {txn_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response['token']
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            last_30_days = current_date - timedelta(days=29)
            logger.debug(f"last_30_days for TxnReport API : {last_30_days}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")
            last_30_days = last_30_days.strftime('%Y-%m-%d')
            logger.debug(f"last_30_days in Y/M/D format : {last_30_days}")

            api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                "startDateAndTime": last_30_days + " 00:00",
                "endDateAndTime": current_date + " 23:59",
                "maxRecordsPerPage": 100,
                "pageNumber": 0,
                "usersList": [],
                "cardType": [],
                "cardBrand": [],
                "transactionStatus": [],
                "selectSearchOptions": [],
                "paymentMode": [],
                "totalPages": 0,
                "nodeIds": [],
                "totalRecords": 0,
                "selectUniversalSearch": []
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for TxnReport is: {response}")
            total_pages = response['totalPages']
            logger.debug(
                f"total number of pages from txn report api: {total_pages}, type of total_pages: {type(total_pages)}")
            total_pages = int(total_pages)

            api_first_txn_details = response["transactions"][0]
            logger.debug(f"api_first_txn_details: {api_first_txn_details}")

            api_first_created_time = api_first_txn_details['createdTime']
            api_first_pmt_state = api_first_txn_details['state']
            api_first_pmt_status = api_first_txn_details['status']
            api_first_pmt_settle_status = api_first_txn_details['settlementStatus']
            api_first_pmt_mode = api_first_txn_details['type']
            api_first_amount = api_first_txn_details['amount']
            api_first_txn_type = api_first_txn_details['txnType']
            api_first_order_id = api_first_txn_details['externalRefNumber']
            api_first_username = api_first_txn_details['username']
            api_first_txn_id = api_first_txn_details['id']
            api_first_hierarchy = api_first_txn_details['hierarchy']
            api_first_org_code = api_first_txn_details['merchantCode']

            if total_pages > 1:
                api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                    "startDateAndTime": last_30_days + " 00:00",
                    "endDateAndTime": current_date + " 23:59",
                    "maxRecordsPerPage": 100,
                    "pageNumber": total_pages - 1,
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [],
                    "totalPages": 0,
                    "nodeIds": [],
                    "totalRecords": 0,
                    "selectUniversalSearch": []
                })

                api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for TxnReport : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.info(f"Response obtained for TxnReport is: {response}")

                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']
            else:
                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)

            trans_history_page = TransHistoryPage(GlobalVariables.portal_page)
            trans_history_page.click_on_reports()
            trans_history_page.click_on_transactions()
            trans_history_page.select_txn_period_last_30_days()
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            #  here we are finding the end date for last 30 days
            last_30_days = current_date - timedelta(days=29)
            logger.debug(f"last_30_days for UTC converison: {last_30_days}")
            # now we are taking the previous day of the last 30 days for UTC conversion
            last_30_days_prev_day = last_30_days - timedelta(days=1)
            logger.debug(f"last_30_days_prev_day for UTC converison: {last_30_days_prev_day}")
            last_30_days_prev_day = last_30_days_prev_day.strftime('%y%m%d')
            logger.debug(f"last_30_days_prev_day in Y/M/D format for UTC conversion: {last_30_days_prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            start_date_time_utc = last_30_days_prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where (id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "') and org_code='" + org_code + "' order by created_time asc limit 1;"
            logger.debug(f"Query to fetch last transaction from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id_last = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id_last}")
            db_rrn_last = result['rr_number'].values[0]
            logger.debug(f"rrn number from db : {db_rrn_last}")
            db_auth_code_last = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code_last}")
            db_amount_last = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount_last}")
            db_username_last = result['username'].values[0]
            logger.debug(f"username from db : {db_username_last}")
            db_pmt_mode_last = result['payment_mode'].values[0]
            logger.debug(f"pmt mode from db: {db_pmt_mode_last}")
            db_pmt_status_last = result['status'].values[0]
            logger.debug(f" pmt status from db: {db_pmt_status_last}")
            db_created_time_last = result['created_time'].values[0]
            logger.debug(f" created time from db: {db_created_time_last}")
            db_pmt_state_last = result['state'].values[0]
            logger.debug(f" pmt state from db: {db_pmt_state_last}")
            db_txn_type_last = result['txn_type'].values[0]
            logger.debug(f"txn type from db: {db_txn_type_last}")
            db_pmt_settle_status_last = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db: {db_pmt_settle_status_last}")
            db_org_code_last = result['org_code'].values[0]
            logger.debug(f"org code from db: {db_org_code_last}")
            db_order_id_last = result['external_ref'].values[0]
            logger.debug(f"order id from db: {db_order_id_last}")
            db_cust_mob_last = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob_last}")
            db_labels_last = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels_last}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"rr number from db : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code}")
            db_created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {db_created_time}")
            db_username = result['username'].values[0]
            logger.debug(f"username from db : {db_username}")
            db_amount = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount}")
            db_status = result['status'].values[0]
            logger.debug(f"status from db : {db_status}")
            db_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db : {db_settle_status}")
            db_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db : {db_pmt_mode}")
            db_txn_type = result['txn_type'].values[0]
            logger.debug(f"txn type from db : {db_txn_type}")
            db_org_code = result['org_code'].values[0]
            logger.debug(f"org code from db : {db_org_code}")
            db_pmt_state = result['state'].values[0]
            logger.debug(f"state from db : {db_pmt_state}")
            db_order_id = result['external_ref'].values[0]
            logger.debug(f"order id from db : {db_order_id}")
            db_cust_mob = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob}")
            db_labels = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_last = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                actual_api_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }
                # ---------------------------------------------------------------------------------------------
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
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }

                actual_db_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
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
                locale.setlocale(locale.LC_ALL, 'en_IN')
                formatted_amount_first = str(locale.currency(db_amount, grouping=True)).replace('₹', '₹ ')
                formatted_amount_last = str(locale.currency(db_amount_last, grouping=True)).replace('₹', '₹ ')
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": formatted_amount_first,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "rrn": "-" if db_rrn is None else db_rrn,
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "cust_mobile": "-" if db_cust_mob is None else db_cust_mob,
                    "labels": "-" if db_labels is None else db_labels,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_type_2": db_pmt_mode_last,
                    "txn_amt_2": formatted_amount_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "rrn_2": "-" if db_rrn_last is None else db_rrn_last,
                    "auth_code_2": "-" if db_auth_code_last is None else db_auth_code_last,
                    "cust_mobile_2": "-" if db_cust_mob_last is None else db_cust_mob_last,
                    "labels_2": "-" if db_labels_last is None else db_labels_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                date_time = txn_details[0]['Date & Time']
                transaction_id = txn_details[0]['Transaction ID']
                total_amount = txn_details[0]['Total Amount']
                rr_number = txn_details[0]['RR Number']
                transaction_type = txn_details[0]['Type']
                status = txn_details[0]['Status']
                username = txn_details[0]['Username']
                auth_code = txn_details[0]['Auth Code']
                hierarchy = txn_details[0]['Hierarchy']
                cust_mobile = txn_details[0]['Mobile No.']
                labels = txn_details[0]['Labels']

                date_time_last = txn_details[-1]['Date & Time']
                transaction_id_last = txn_details[-1]['Transaction ID']
                total_amount_last = txn_details[-1]['Total Amount']
                rr_number_last = txn_details[-1]['RR Number']
                transaction_type_last = txn_details[-1]['Type']
                status_last = txn_details[-1]['Status']
                username_last = txn_details[-1]['Username']
                auth_code_last = txn_details[-1]['Auth Code']
                hierarchy_last = txn_details[-1]['Hierarchy']
                cust_mobile_last = txn_details[-1]['Mobile No.']
                labels_last = txn_details[-1]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount,
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code,
                    "cust_mobile": cust_mobile,
                    "labels": labels,
                    "hierarchy": hierarchy,

                    "date_time_2": date_time_last,
                    "pmt_status_2": status_last,
                    "pmt_type_2": transaction_type_last,
                    "txn_amt_2": total_amount_last,
                    "username_2": username_last,
                    "txn_id_2": transaction_id_last,
                    "rrn_2": rr_number_last,
                    "auth_code_2": auth_code_last,
                    "cust_mobile_2": cust_mobile_last,
                    "labels_2": labels_last,
                    "hierarchy_2": hierarchy_last,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_701_026():
    """
    Sub Feature Code: UI_MP_Report_based_on_Location_as_country_head
    Sub Feature Description: Verifying txn details on Report Page using Filter All Location when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    026: TC026
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
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")

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

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(10, 500)
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "amount": amount
            })
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received after cash transaction is : {response}")

            txn_id = response['txnId']
            logger.debug(f"txn_id after cash transaction is : {txn_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response['token']
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")

            query = "select node_name from org_structure where org_code = '" + org_code + "' and org_employee_username ='"+ txn_username +"' ;"
            logger.debug(f"Query to fetch location name to be searched for which txn was done: {query}")
            result = DBProcessor.getValueFromDB(query)
            search_location = result['node_name'].values[0]
            logger.debug(f"search_location: {search_location} ")

            query = "select parent_node_id from org_structure where org_code = '" + org_code + "' and org_employee_username ='"+ txn_username +"'  and node_name = '" + search_location + "';"
            logger.debug(f"Query to fetch node_IDs from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            nodeid = int(result['parent_node_id'].values[0])
            logger.debug(f"nodeid: {nodeid} ")

            api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                "startDateAndTime": current_date + " 00:00",
                "endDateAndTime": current_date + " 23:59",
                "maxRecordsPerPage": 100,
                "pageNumber": 0,
                "usersList": [],
                "cardType": [],
                "cardBrand": [],
                "transactionStatus": [],
                "selectSearchOptions": [],
                "paymentMode": [],
                "totalPages": 0,
                "nodeIds": [nodeid],
                "totalRecords": 0,
                "selectUniversalSearch": []
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for TxnReport is: {response}")
            total_pages = response['totalPages']
            logger.debug(
                f"total number of pages from txn report api: {total_pages}, type of total_pages: {type(total_pages)}")

            api_first_txn_details = response["transactions"][0]
            logger.debug(f"api_first_txn_details: {api_first_txn_details}")

            api_first_created_time = api_first_txn_details['createdTime']
            api_first_pmt_state = api_first_txn_details['state']
            api_first_pmt_status = api_first_txn_details['status']
            api_first_pmt_settle_status = api_first_txn_details['settlementStatus']
            api_first_pmt_mode = api_first_txn_details['type']
            api_first_amount = api_first_txn_details['amount']
            api_first_txn_type = api_first_txn_details['txnType']
            api_first_order_id = api_first_txn_details['externalRefNumber']
            api_first_username = api_first_txn_details['username']
            api_first_txn_id = api_first_txn_details['id']
            api_first_hierarchy = api_first_txn_details['hierarchy']
            api_first_org_code = api_first_txn_details['merchantCode']

            if total_pages > 1:
                api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                    "startDateAndTime": current_date + " 00:00",
                    "endDateAndTime": current_date + " 23:59",
                    "maxRecordsPerPage": 100,
                    "pageNumber": total_pages - 1,
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [],
                    "totalPages": 0,
                    "nodeIds": [nodeid],
                    "totalRecords": 0,
                    "selectUniversalSearch": []
                })

                api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for TxnReport : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.info(f"Response obtained for TxnReport is: {response}")

                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']
            else:
                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)

            trans_history_page = TransHistoryPage(GlobalVariables.portal_page)
            trans_history_page.click_on_reports()
            trans_history_page.click_on_transactions()
            trans_history_page.search_based_on_location(search_location)
            trans_history_page.click_on_search_btn()
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            # now we are taking the previous day of the current_date for UTC conversion
            prev_day = current_date - timedelta(days=1)
            logger.debug(f"prev_day for UTC converison: {prev_day}")
            prev_day = prev_day.strftime('%y%m%d')
            logger.debug(f"prev_day in Y/M/D format for UTC conversion: {prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            start_date_time_utc = prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where (id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "') and org_code='" + org_code + "' and username ='" + txn_username + "' order by created_time asc limit 1;"
            logger.debug(f"Query to fetch last transaction from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id_last = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id_last}")
            db_rrn_last = result['rr_number'].values[0]
            logger.debug(f"rrn number from db : {db_rrn_last}")
            db_auth_code_last = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code_last}")
            db_amount_last = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount_last}")
            db_username_last = result['username'].values[0]
            logger.debug(f"username from db : {db_username_last}")
            db_pmt_mode_last = result['payment_mode'].values[0]
            logger.debug(f"pmt mode from db: {db_pmt_mode_last}")
            db_pmt_status_last = result['status'].values[0]
            logger.debug(f" pmt status from db: {db_pmt_status_last}")
            db_created_time_last = result['created_time'].values[0]
            logger.debug(f" created time from db: {db_created_time_last}")
            db_pmt_state_last = result['state'].values[0]
            logger.debug(f" pmt state from db: {db_pmt_state_last}")
            db_txn_type_last = result['txn_type'].values[0]
            logger.debug(f"txn type from db: {db_txn_type_last}")
            db_pmt_settle_status_last = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db: {db_pmt_settle_status_last}")
            db_org_code_last = result['org_code'].values[0]
            logger.debug(f"org code from db: {db_org_code_last}")
            db_order_id_last = result['external_ref'].values[0]
            logger.debug(f"order id from db: {db_order_id_last}")
            db_cust_mob_last = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob_last}")
            db_labels_last = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels_last}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"rr number from db : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code}")
            db_created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {db_created_time}")
            db_username = result['username'].values[0]
            logger.debug(f"username from db : {db_username}")
            db_amount = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount}")
            db_status = result['status'].values[0]
            logger.debug(f"status from db : {db_status}")
            db_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db : {db_settle_status}")
            db_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db : {db_pmt_mode}")
            db_txn_type = result['txn_type'].values[0]
            logger.debug(f"txn type from db : {db_txn_type}")
            db_org_code = result['org_code'].values[0]
            logger.debug(f"org code from db : {db_org_code}")
            db_pmt_state = result['state'].values[0]
            logger.debug(f"state from db : {db_pmt_state}")
            db_order_id = result['external_ref'].values[0]
            logger.debug(f"order id from db : {db_order_id}")
            db_cust_mob = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob}")
            db_labels = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_last = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                actual_api_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }
                # ---------------------------------------------------------------------------------------------
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
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }

                actual_db_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
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
                locale.setlocale(locale.LC_ALL, 'en_IN')
                formatted_amount_first = str(locale.currency(db_amount, grouping=True)).replace('₹', '₹ ')
                formatted_amount_last = str(locale.currency(db_amount_last, grouping=True)).replace('₹', '₹ ')
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": formatted_amount_first,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "rrn": "-" if db_rrn is None else db_rrn,
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "cust_mobile": "-" if db_cust_mob is None else db_cust_mob,
                    "labels": "-" if db_labels is None else db_labels,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_type_2": db_pmt_mode_last,
                    "txn_amt_2": formatted_amount_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "rrn_2": "-" if db_rrn_last is None else db_rrn_last,
                    "auth_code_2": "-" if db_auth_code_last is None else db_auth_code_last,
                    "cust_mobile_2": "-" if db_cust_mob_last is None else db_cust_mob_last,
                    "labels_2": "-" if db_labels_last is None else db_labels_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                date_time = txn_details[0]['Date & Time']
                transaction_id = txn_details[0]['Transaction ID']
                total_amount = txn_details[0]['Total Amount']
                rr_number = txn_details[0]['RR Number']
                transaction_type = txn_details[0]['Type']
                status = txn_details[0]['Status']
                username = txn_details[0]['Username']
                auth_code = txn_details[0]['Auth Code']
                hierarchy = txn_details[0]['Hierarchy']
                cust_mobile = txn_details[0]['Mobile No.']
                labels = txn_details[0]['Labels']

                date_time_last = txn_details[-1]['Date & Time']
                transaction_id_last = txn_details[-1]['Transaction ID']
                total_amount_last = txn_details[-1]['Total Amount']
                rr_number_last = txn_details[-1]['RR Number']
                transaction_type_last = txn_details[-1]['Type']
                status_last = txn_details[-1]['Status']
                username_last = txn_details[-1]['Username']
                auth_code_last = txn_details[-1]['Auth Code']
                hierarchy_last = txn_details[-1]['Hierarchy']
                cust_mobile_last = txn_details[-1]['Mobile No.']
                labels_last = txn_details[-1]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount,
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code,
                    "cust_mobile": cust_mobile,
                    "labels": labels,
                    "hierarchy": hierarchy,

                    "date_time_2": date_time_last,
                    "pmt_status_2": status_last,
                    "pmt_type_2": transaction_type_last,
                    "txn_amt_2": total_amount_last,
                    "username_2": username_last,
                    "txn_id_2": transaction_id_last,
                    "rrn_2": rr_number_last,
                    "auth_code_2": auth_code_last,
                    "cust_mobile_2": cust_mobile_last,
                    "labels_2": labels_last,
                    "hierarchy_2": hierarchy_last,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")

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
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_701_027():
    """
    Sub Feature Code: UI_MP_Report_based_on_User_as_country_head
    Sub Feature Description: Verifying txn details on Report Page using Filter User when logging in as Country Head
    TC naming code description:
    700: Merchant Portal
    701: Country
    027: TC027
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
        logger.debug(f"Fetched login_password credentials from the ezeauto db : {login_password}")

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

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=True, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")
            # ------------------------------------------------------------------------------------------------
            amount = random.randint(10, 500)
            api_details = DBProcessor.get_api_details('cash_payment', request_body={
                "username": txn_username,
                "password": txn_password,
                "amount": amount
            })
            logger.debug(f"API details  : {api_details} ")
            response = APIProcessor.send_request(api_details)
            logger.debug(f"Response received after cash transaction is : {response}")

            txn_id = response['txnId']
            logger.debug(f"txn_id after cash transaction is : {txn_id}")

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response['token']
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")

            api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                "startDateAndTime": current_date + " 00:00",
                "endDateAndTime": current_date + " 23:59",
                "maxRecordsPerPage": 100,
                "pageNumber": 0,
                "usersList": [txn_username],
                "cardType": [],
                "cardBrand": [],
                "transactionStatus": [],
                "selectSearchOptions": [],
                "paymentMode": [],
                "totalPages": 0,
                "nodeIds": [],
                "totalRecords": 0,
                "selectUniversalSearch": []
            })

            api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                     'Content-Type': 'application/json'}
            logger.debug(f"api details for TxnReport : {api_details}")
            response = APIProcessor.send_request(api_details)
            logger.info(f"Response obtained for TxnReport is: {response}")
            total_pages = response['totalPages']
            logger.debug(
                f"total number of pages from txn report api: {total_pages}, type of total_pages: {type(total_pages)}")
            total_pages = int(total_pages)

            api_first_txn_details = response["transactions"][0]
            logger.debug(f"api_first_txn_details: {api_first_txn_details}")

            api_first_created_time = api_first_txn_details['createdTime']
            api_first_pmt_state = api_first_txn_details['state']
            api_first_pmt_status = api_first_txn_details['status']
            api_first_pmt_settle_status = api_first_txn_details['settlementStatus']
            api_first_pmt_mode = api_first_txn_details['type']
            api_first_amount = api_first_txn_details['amount']
            api_first_txn_type = api_first_txn_details['txnType']
            api_first_order_id = api_first_txn_details['externalRefNumber']
            api_first_username = api_first_txn_details['username']
            api_first_txn_id = api_first_txn_details['id']
            api_first_hierarchy = api_first_txn_details['hierarchy']
            api_first_org_code = api_first_txn_details['merchantCode']

            if total_pages > 1:
                api_details = DBProcessor.get_api_details('mp_txn_report', request_body={
                    "startDateAndTime": current_date + " 00:00",
                    "endDateAndTime": current_date + " 23:59",
                    "maxRecordsPerPage": 100,
                    "pageNumber": total_pages - 1,
                    "usersList": [txn_username],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [],
                    "totalPages": 0,
                    "nodeIds": [],
                    "totalRecords": 0,
                    "selectUniversalSearch": []
                })

                api_details['Header'] = {'Authorization': 'Bearer ' + validate_auth_token,
                                         'Content-Type': 'application/json'}
                logger.debug(f"api details for TxnReport : {api_details}")
                response = APIProcessor.send_request(api_details)
                logger.info(f"Response obtained for TxnReport is: {response}")

                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']
            else:
                api_last_txn_details = response["transactions"][-1]
                logger.debug(f"api_last_txn_details: {api_last_txn_details}")

                api_last_created_time = api_last_txn_details['createdTime']
                api_last_pmt_state = api_last_txn_details['state']
                api_last_pmt_mode = api_last_txn_details['type']
                api_last_amount = api_last_txn_details['amount']
                api_last_username = api_last_txn_details['username']
                api_last_txn_id = api_last_txn_details['id']
                api_last_org_code = api_last_txn_details['merchantCode']
                api_last_txn_type = api_last_txn_details['txnType']
                api_last_pmt_settle_status = api_last_txn_details['settlementStatus']
                api_last_pmt_status = api_last_txn_details['status']
                api_last_order_id = api_last_txn_details['externalRefNumber']
                api_last_hierarchy = api_last_txn_details['hierarchy']

            GlobalVariables.portal_page = TestSuiteSetup.initialize_portal_browser()
            login_page_portal = PortalLoginPage(GlobalVariables.portal_page)
            login_page_portal.perform_login_to_portal(login_username, login_password)

            trans_history_page = TransHistoryPage(GlobalVariables.portal_page)
            trans_history_page.click_on_reports()
            trans_history_page.click_on_transactions()
            trans_history_page.search_based_on_user(txn_username)
            trans_history_page.click_on_search_btn()
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            # now we are taking the previous day of the current_date for UTC conversion
            prev_day = current_date - timedelta(days=1)
            logger.debug(f"prev_day for UTC converison: {prev_day}")
            prev_day = prev_day.strftime('%y%m%d')
            logger.debug(f"prev_day in Y/M/D format for UTC conversion: {prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            start_date_time_utc = prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and username='" + txn_username + "' order by created_time asc limit 1;"
            logger.debug(f"Query to fetch last transaction from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id_last = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id_last}")
            db_rrn_last = result['rr_number'].values[0]
            logger.debug(f"rrn number from db : {db_rrn_last}")
            db_auth_code_last = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code_last}")
            db_amount_last = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount_last}")
            db_username_last = result['username'].values[0]
            logger.debug(f"username from db : {db_username_last}")
            db_pmt_mode_last = result['payment_mode'].values[0]
            logger.debug(f"pmt mode from db: {db_pmt_mode_last}")
            db_pmt_status_last = result['status'].values[0]
            logger.debug(f" pmt status from db: {db_pmt_status_last}")
            db_created_time_last = result['created_time'].values[0]
            logger.debug(f" created time from db: {db_created_time_last}")
            db_pmt_state_last = result['state'].values[0]
            logger.debug(f" pmt state from db: {db_pmt_state_last}")
            db_txn_type_last = result['txn_type'].values[0]
            logger.debug(f"txn type from db: {db_txn_type_last}")
            db_pmt_settle_status_last = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db: {db_pmt_settle_status_last}")
            db_org_code_last = result['org_code'].values[0]
            logger.debug(f"org code from db: {db_org_code_last}")
            db_order_id_last = result['external_ref'].values[0]
            logger.debug(f"order id from db: {db_order_id_last}")
            db_cust_mob_last = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob_last}")
            db_labels_last = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels_last}")

            query = "select * from txn where id = '" + txn_id + "';"
            logger.debug(f"Query to fetch transaction id from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_txn_id = result['id'].values[0]
            logger.debug(f"txn_id from db : {db_txn_id}")
            db_rrn = result['rr_number'].values[0]
            logger.debug(f"rr number from db : {db_rrn}")
            db_auth_code = result['auth_code'].values[0]
            logger.debug(f"auth code from db : {db_auth_code}")
            db_created_time = result['created_time'].values[0]
            logger.debug(f"created time from db : {db_created_time}")
            db_username = result['username'].values[0]
            logger.debug(f"username from db : {db_username}")
            db_amount = result['amount'].values[0]
            logger.debug(f"amount from db : {db_amount}")
            db_status = result['status'].values[0]
            logger.debug(f"status from db : {db_status}")
            db_settle_status = result['settlement_status'].values[0]
            logger.debug(f"settlement status from db : {db_settle_status}")
            db_pmt_mode = result['payment_mode'].values[0]
            logger.debug(f"payment mode from db : {db_pmt_mode}")
            db_txn_type = result['txn_type'].values[0]
            logger.debug(f"txn type from db : {db_txn_type}")
            db_org_code = result['org_code'].values[0]
            logger.debug(f"org code from db : {db_org_code}")
            db_pmt_state = result['state'].values[0]
            logger.debug(f"state from db : {db_pmt_state}")
            db_order_id = result['external_ref'].values[0]
            logger.debug(f"order id from db : {db_order_id}")
            db_cust_mob = result['customer_mobile'].values[0]
            logger.debug(f"customer_mobile no from db : {db_cust_mob}")
            db_labels = result['label_ids'].values[0]
            logger.debug(f"labels from db : {db_labels}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_last = result['flat_hierarchy'].values[0]
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

            # ------------------------------------------------------------------------------------------------
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
                # --------------------------------------------------------------------------------------------
                expected_api_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                actual_api_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)
            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_db_values = {
                    "date_time": api_first_created_time,
                    "pmt_state": api_first_pmt_state,
                    "settle_status": api_first_pmt_settle_status,
                    "pmt_status": api_first_pmt_status,
                    "pmt_mode": api_first_pmt_mode,
                    "txn_amt": str(api_first_amount),
                    "txn_type": api_first_txn_type,
                    "order_id": api_first_order_id,
                    "username": api_first_username,
                    "txn_id": api_first_txn_id,
                    "org_code": api_first_org_code,
                    "hierarchy": api_first_hierarchy,

                    "date_time_2": api_last_created_time,
                    "pmt_state_2": api_last_pmt_state,
                    "settle_status_2": api_last_pmt_settle_status,
                    "pmt_status_2": api_last_pmt_status,
                    "pmt_mode_2": api_last_pmt_mode,
                    "txn_amt_2": str(api_last_amount),
                    "txn_type_2": api_last_txn_type,
                    "order_id_2": api_last_order_id,
                    "username_2": api_last_username,
                    "txn_id_2": api_last_txn_id,
                    "org_code_2": api_last_org_code,
                    "hierarchy_2": api_last_hierarchy
                }

                actual_db_values = {
                    "date_time": db_date_first,
                    "pmt_state": db_pmt_state,
                    "settle_status": db_settle_status,
                    "pmt_status": db_status,
                    "pmt_mode": db_pmt_mode,
                    "txn_amt": str(db_amount),
                    "txn_type": db_txn_type,
                    "order_id": db_order_id,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "org_code": db_org_code,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_state_2": db_pmt_state_last,
                    "settle_status_2": db_pmt_settle_status_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_mode_2": db_pmt_mode_last,
                    "txn_amt_2": str(db_amount_last),
                    "txn_type_2": db_txn_type_last,
                    "order_id_2": db_order_id_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "org_code_2": db_org_code_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expected_db_values, actualDB=actual_db_values)
            except Exception as e:
                Configuration.perform_db_val_exception(testcase_id, e)
            logger.info(f"Completed DB validation for the test case : {testcase_id}")
        # -----------------------------------------End of DB Validation---------------------------------------

        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                locale.setlocale(locale.LC_ALL, 'en_IN')
                formatted_amount_first = str(locale.currency(db_amount, grouping=True)).replace('₹', '₹ ')
                formatted_amount_last = str(locale.currency(db_amount_last, grouping=True)).replace('₹', '₹ ')
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": formatted_amount_first,
                    "username": db_username,
                    "txn_id": db_txn_id,
                    "rrn": "-" if db_rrn is None else db_rrn,
                    "auth_code": "-" if db_auth_code is None else db_auth_code,
                    "cust_mobile": "-" if db_cust_mob is None else db_cust_mob,
                    "labels": "-" if db_labels is None else db_labels,
                    "hierarchy": str(db_hierarchy).replace('|', ' | '),

                    "date_time_2": db_date_last,
                    "pmt_status_2": db_pmt_status_last,
                    "pmt_type_2": db_pmt_mode_last,
                    "txn_amt_2": formatted_amount_last,
                    "username_2": db_username_last,
                    "txn_id_2": db_txn_id_last,
                    "rrn_2": "-" if db_rrn_last is None else db_rrn_last,
                    "auth_code_2": "-" if db_auth_code_last is None else db_auth_code_last,
                    "cust_mobile_2": "-" if db_cust_mob_last is None else db_cust_mob_last,
                    "labels_2": "-" if db_labels_last is None else db_labels_last,
                    "hierarchy_2": str(db_hierarchy_last).replace('|', ' | ')
                }

                logger.debug(f"expectedPortalValues : {expected_portal_values}")

                date_time = txn_details[0]['Date & Time']
                transaction_id = txn_details[0]['Transaction ID']
                total_amount = txn_details[0]['Total Amount']
                rr_number = txn_details[0]['RR Number']
                transaction_type = txn_details[0]['Type']
                status = txn_details[0]['Status']
                username = txn_details[0]['Username']
                auth_code = txn_details[0]['Auth Code']
                hierarchy = txn_details[0]['Hierarchy']
                cust_mobile = txn_details[0]['Mobile No.']
                labels = txn_details[0]['Labels']

                date_time_last = txn_details[-1]['Date & Time']
                transaction_id_last = txn_details[-1]['Transaction ID']
                total_amount_last = txn_details[-1]['Total Amount']
                rr_number_last = txn_details[-1]['RR Number']
                transaction_type_last = txn_details[-1]['Type']
                status_last = txn_details[-1]['Status']
                username_last = txn_details[-1]['Username']
                auth_code_last = txn_details[-1]['Auth Code']
                hierarchy_last = txn_details[-1]['Hierarchy']
                cust_mobile_last = txn_details[-1]['Mobile No.']
                labels_last = txn_details[-1]['Labels']

                actual_portal_values = {
                    "date_time": date_time,
                    "pmt_status": str(status),
                    "pmt_type": transaction_type,
                    "txn_amt": total_amount,
                    "username": username,
                    "txn_id": transaction_id,
                    "rrn": rr_number,
                    "auth_code": auth_code,
                    "cust_mobile": cust_mobile,
                    "labels": labels,
                    "hierarchy": hierarchy,

                    "date_time_2": date_time_last,
                    "pmt_status_2": status_last,
                    "pmt_type_2": transaction_type_last,
                    "txn_amt_2": total_amount_last,
                    "username_2": username_last,
                    "txn_id_2": transaction_id_last,
                    "rrn_2": rr_number_last,
                    "auth_code_2": auth_code_last,
                    "cust_mobile_2": cust_mobile_last,
                    "labels_2": labels_last,
                    "hierarchy_2": hierarchy_last,
                }

                logger.debug(f"actual_portal_values : {actual_portal_values}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstPortal(expectedPortal=expected_portal_values, actualPortal=actual_portal_values)
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