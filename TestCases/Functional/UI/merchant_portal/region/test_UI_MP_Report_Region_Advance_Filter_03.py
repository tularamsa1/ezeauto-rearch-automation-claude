from datetime import datetime, timedelta
import random
import sys
import pytest
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.merchant_portal.Portal_ReportsPage import TransHistoryPage
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ConfigReader, ResourceAssigner, DBProcessor, APIProcessor, \
    date_time_converter, card_processor, merchant_creator
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
def test_mp_700_702_051():
    """
    Sub Feature Code: UI_MP_Report_based_on_Advance_filter_VISACardBrand_as_Regional_Head
    Sub Feature Description: Verifying txn details on Report Page using Advance Filter VISACardBrand when logging in as Regional Head
    TC naming code description:
    700: Merchant Portal
    702: Region
    051: TC051
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

        login_cred = ResourceAssigner.get_org_users_login_Credentials('REGION', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

        country_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
        logger.debug(f"Fetched country_cred credentials from the ezeauto db : {country_cred}")
        country_username = country_cred['Username']

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

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                logger.debug(f"txn_id for card transaction is : {txn_id}")
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            card_brand_search_value = "VISA"

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response
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
                "usersList": [],
                "cardType": [],
                "cardBrand": [card_brand_search_value],
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
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [card_brand_search_value],
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
            trans_history_page.click_on_advance_filter()
            trans_history_page.search_based_on_card_brand(card_brand_search_value)
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

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and payment_card_brand='" + card_brand_search_value + "' and username NOT IN ('"+country_username+"') order by created_time asc limit 1;"
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
            logger.debug(f"Query to fetch first txn from database is: {query}")
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
            db_hierarchy_original = result['flat_hierarchy'].values[0]
            db_hierarchy = "|".join(db_hierarchy_original.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_original_last = result['flat_hierarchy'].values[0]
            db_hierarchy_last = "|".join(db_hierarchy_original_last.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

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
        #
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": str(db_amount) + "0",
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
                    "txn_amt_2": str(db_amount_last) + "0",
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
                total_amount = txn_details[0]['Total Amount'].split()
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
                total_amount_last = txn_details[-1]['Total Amount'].split()
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
                    "txn_amt": total_amount[1].replace(',',''),
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
                    "txn_amt_2": total_amount_last[1].replace(',',''),
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
def test_mp_700_702_052():
    """
    Sub Feature Code: UI_MP_Report_based_on_Advance_filter_MASTERCardBrand_as_Regional_Head
    Sub Feature Description: Verifying txn details on Report Page using Advance Filter MASTERCardBrand when logging in as Regional Head
    TC naming code description:
    700: Merchant Portal
    702: Region
    052: TC052
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

        login_cred = ResourceAssigner.get_org_users_login_Credentials('REGION', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

        country_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
        logger.debug(f"Fetched country_cred credentials from the ezeauto db : {country_cred}")
        country_username = country_cred['Username']

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

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response from Card_api is : {response}")
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                logger.debug(f"txn_id for card transaction is : {txn_id}")
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            card_brand_search_value = "MASTER_CARD"

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response
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
                "usersList": [],
                "cardType": [],
                "cardBrand": [card_brand_search_value],
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
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [card_brand_search_value],
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
            trans_history_page.click_on_advance_filter()
            trans_history_page.search_based_on_card_brand(card_brand_search_value)
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

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and payment_card_brand='" + card_brand_search_value + "' and username NOT IN ('"+country_username+"') order by created_time asc limit 1;"
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
            logger.debug(f"Query to fetch first txn from database is: {query}")
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
            db_hierarchy_original = result['flat_hierarchy'].values[0]
            db_hierarchy = "|".join(db_hierarchy_original.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_original_last = result['flat_hierarchy'].values[0]
            db_hierarchy_last = "|".join(db_hierarchy_original_last.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

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
        #
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": str(db_amount) + "0",
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
                    "txn_amt_2": str(db_amount_last) + "0",
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
                total_amount = txn_details[0]['Total Amount'].split()
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
                total_amount_last = txn_details[-1]['Total Amount'].split()
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
                    "txn_amt": total_amount[1].replace(',',''),
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
                    "txn_amt_2": total_amount_last[1].replace(',',''),
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
def test_mp_700_702_053():
    """
    Sub Feature Code: UI_MP_Report_based_on_Advance_filter_RUPAYCardBrand_as_Regional_Head
    Sub Feature Description: Verifying txn details on Report Page using Advance Filter RUPAYCardBrand when logging in as Regional Head
    TC naming code description:
    700: Merchant Portal
    702: Region
    053: TC053
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

        login_cred = ResourceAssigner.get_org_users_login_Credentials('REGION', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

        country_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
        logger.debug(f"Fetched country_cred credentials from the ezeauto db : {country_cred}")
        country_username = country_cred['Username']

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

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            if card_payment_success == True:
                txn_id = response['txnId']
                logger.debug(f"txn_id for card transaction is : {txn_id}")
                confirm_data = card_processor.get_card_details_from_excel("CONFIRM_DATA")

                api_details = DBProcessor.get_api_details('Confirm_Card_Txn',
                                                          request_body={"username": txn_username,
                                                                        "password": txn_password,
                                                                        "ezetapDeviceData": confirm_data[
                                                                            "Ezetap Device Data"],
                                                                        "txnId": txn_id,
                                                                        })
                confirm_response = APIProcessor.send_request(api_details)
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            card_brand_search_value = "RUPAY"

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response
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
                "usersList": [],
                "cardType": [],
                "cardBrand": [card_brand_search_value],
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
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [card_brand_search_value],
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
            trans_history_page.click_on_advance_filter()
            trans_history_page.search_based_on_card_brand(card_brand_search_value)
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

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and payment_card_brand='" + card_brand_search_value + "' and username NOT IN ('"+country_username+"') order by created_time asc limit 1;"
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
            logger.debug(f"Query to fetch first txn from database is: {query}")
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
            db_hierarchy_original = result['flat_hierarchy'].values[0]
            db_hierarchy = "|".join(db_hierarchy_original.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_original_last = result['flat_hierarchy'].values[0]
            db_hierarchy_last = "|".join(db_hierarchy_original_last.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

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
        #
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": str(db_amount) + "0",
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
                    "txn_amt_2": str(db_amount_last) + "0",
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
                total_amount = txn_details[0]['Total Amount'].split()
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
                total_amount_last = txn_details[-1]['Total Amount'].split()
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
                    "txn_amt": total_amount[1].replace(',',''),
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
                    "txn_amt_2": total_amount_last[1].replace(',',''),
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
def test_mp_700_702_054():
    """
    Sub Feature Code: UI_MP_Report_based_on_Advance_filter_ALL_CardBrand_as_Regional_Head
    Sub Feature Description: Verifying txn details on Report Page using Advance Filter for ALL CardBrand  when logging in as Regional Head
    TC naming code description:
    700: Merchant Portal
    702: Region
    054: TC054
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

        login_cred = ResourceAssigner.get_org_users_login_Credentials('REGION', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

        country_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
        logger.debug(f"Fetched country_cred credentials from the ezeauto db : {country_cred}")
        country_username = country_cred['Username']

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

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_RUPAY")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

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
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_MASTER")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

            response = APIProcessor.send_request(api_details)
            logger.debug(f"response from Card_api is : {response}")
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
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            original_amount = random.randint(10, 1000)
            card_details = card_processor.get_card_details_from_excel("HDFC_EMV_DEBIT_VISA")
            api_details = DBProcessor.get_api_details('Card_api',
                                                      request_body={
                                                          "deviceSerial": merchant_creator.get_device_serial_of_merchant(
                                                              org_code=org_code, acquisition="HDFC",
                                                              payment_gateway="HDFC"),
                                                          "username": txn_username,
                                                          "password": txn_password,
                                                          "amount": str(original_amount),
                                                          "ezetapDeviceData": card_details['Ezetap Device Data'],
                                                          "nonce": card_details['Nonce'],
                                                          "externalRefNumber": str(card_details['External Ref']) + str(
                                                              random.randint(0, 9))})

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
                logger.debug(f"confirm response from api is: {confirm_response}")
                confirm_success = confirm_response['success']
            else:
                logger.error("Card payment Failed")

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
            payment_card_type_api = confirm_response['paymentCardType']
            logger.debug(f"Payment Card Type from api : {payment_card_type_api}")

            card_brand_search_value = ["VISA", "MASTER_CARD", "DISCOVER", "DINERS", "AMEX", "MICROPENSION", "JCB",
                                       "MAESTRO", "RUPAY", "LOYALTY", "CUP", "SODEXO"]
            search_value = "Select All"

            api_details = DBProcessor.get_api_details('mp_login', request_body={
                "username": login_username,
                "password": login_password
            })
            response = APIProcessor.send_request(api_details)
            validate_auth_token = response
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
                "usersList": [],
                "cardType": [],
                "cardBrand": card_brand_search_value,
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
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": card_brand_search_value,
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
            trans_history_page.click_on_advance_filter()
            trans_history_page.search_based_on_card_brand(search_value)
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

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and (payment_card_brand='VISA' OR payment_card_brand='MASTER_CARD' OR payment_card_brand='DISCOVER' OR payment_card_brand='DINERS' OR payment_card_brand='AMEX' OR payment_card_brand='MICROPENSION' OR payment_card_brand='JCB' OR payment_card_brand='MAESTRO' OR payment_card_brand='RUPAY' OR payment_card_brand='LOYALTY' OR payment_card_brand='CUP' OR payment_card_brand='SODEXO') and username NOT IN ('"+country_username+"')  order by created_time asc limit 1;"
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
            logger.debug(f"Query to fetch first txn from database is: {query}")
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
            db_hierarchy_original = result['flat_hierarchy'].values[0]
            db_hierarchy = "|".join(db_hierarchy_original.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_original_last = result['flat_hierarchy'].values[0]
            db_hierarchy_last = "|".join(db_hierarchy_original_last.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy_last}")

            db_date_first = date_time_converter.to_portal_format(db_created_time)
            logger.debug(f"db_date_first in portal format : {db_date_first}")
            db_date_last = date_time_converter.to_portal_format(db_created_time_last)
            logger.debug(f"db_date_last in portal format : {db_date_last}")

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
        #
        # -----------------------------------------Start of Portal Validation---------------------------------
        if (ConfigReader.read_config("Validations", "portal_validation")) == "True":
            logger.info(f"Started Portal validation for the test case : {testcase_id}")
            try:
                # --------------------------------------------------------------------------------------------
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": str(db_amount) + "0",
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
                    "txn_amt_2": str(db_amount_last) + "0",
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
                total_amount = txn_details[0]['Total Amount'].split()
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
                total_amount_last = txn_details[-1]['Total Amount'].split()
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
                    "txn_amt": total_amount[1].replace(',',''),
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
                    "txn_amt_2": total_amount_last[1].replace(',',''),
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
def test_mp_700_702_055():
    """
    Sub Feature Code: UI_MP_Report_based_on_Advance_filter_Payment_mode_Cash_as_Regional_Head
    Sub Feature Description: Verifying txn details on Report Page using Advance Filter for payment mode Cash when logging in as Regional Head
    TC naming code description:
    700: Merchant Portal
    702: Region
    055: TC055
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

        login_cred = ResourceAssigner.get_org_users_login_Credentials('REGION', txn_org_code)
        logger.debug(f"Fetched login credentials from the ezeauto db : {login_cred}")
        login_username = login_cred['Username']
        login_password = login_cred['Password']

        country_cred = ResourceAssigner.get_org_users_login_Credentials('COUNTRY', txn_org_code)
        logger.debug(f"Fetched country_cred credentials from the ezeauto db : {country_cred}")
        country_username = country_cred['Username']

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
            validate_auth_token = response
            logger.debug(f"validate_auth_token after hitting userlogin API is : {validate_auth_token}")

            current_date = datetime.now()
            logger.debug(f"current_date for TxnReport API : {current_date}")
            current_date = current_date.strftime('%Y-%m-%d')
            logger.debug(f"current_date in Y/M/D format : {current_date}")

            pmt_mode_search_value = "CASH"

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
                "paymentMode": [pmt_mode_search_value],
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
                    "usersList": [],
                    "cardType": [],
                    "cardBrand": [],
                    "transactionStatus": [],
                    "selectSearchOptions": [],
                    "paymentMode": [pmt_mode_search_value],
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
            trans_history_page.click_on_advance_filter()
            trans_history_page.search_based_on_payment_mode(pmt_mode_search_value)
            trans_history_page.click_on_search_btn()
            txn_details = trans_history_page.get_transaction_details_first_last_page()

            current_date = datetime.now()
            logger.debug(f"current_date for UTC converison: {current_date}")
            # now we are taking the previous day of the current_date for UTC conversion
            prev_day = current_date - timedelta(days=1)
            logger.debug(f"prev_day for UTC converison: {prev_day}")
            current_date = current_date.strftime('%y%m%d')
            logger.debug(f"current_date in Y/M/D format for UTC conversion: {current_date}")
            prev_day = prev_day.strftime('%y%m%d')
            logger.debug(f"prev_day in Y/M/D format for UTC conversion: {prev_day}")
            start_date_time_utc = prev_day + "1830"
            logger.debug(f"start_date_time_utc : {start_date_time_utc}")
            end_date_time_utc = current_date + "1829"
            logger.debug(f"end_date_time_utc : {end_date_time_utc}")

            query = "SELECT * from txn where id BETWEEN '" + start_date_time_utc + "' AND '" + end_date_time_utc + "' and org_code='" + org_code + "' and payment_mode ='" + pmt_mode_search_value + "' and username NOT IN ('"+country_username+"') order by created_time asc limit 1;"
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
            db_hierarchy_original = result['flat_hierarchy'].values[0]
            db_hierarchy = "|".join(db_hierarchy_original.split("|")[1:])
            logger.debug(f"hierarchy from db : {db_hierarchy}")

            query = "select * from org_flat_hierarchy where org_code = '" + org_code + "' and username = '" + db_username_last + "';"
            logger.debug(f"Query to Org Flat Hierarchy from database is: {query}")
            result = DBProcessor.getValueFromDB(query)
            db_hierarchy_original_last = result['flat_hierarchy'].values[0]
            db_hierarchy_last = "|".join(db_hierarchy_original_last.split("|")[1:])
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
                expected_portal_values = {
                    "date_time": db_date_first,
                    "pmt_status": db_status,
                    "pmt_type": db_pmt_mode,
                    "txn_amt": str(db_amount) + "0",
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
                    "txn_amt_2": str(db_amount_last) + "0",
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
                total_amount = txn_details[0]['Total Amount'].split()
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
                total_amount_last = txn_details[-1]['Total Amount'].split()
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
                    "txn_amt": total_amount[1].replace(',',''),
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
                    "txn_amt_2": total_amount_last[1].replace(',',''),
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
