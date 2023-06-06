import random
import sys
from datetime import datetime

import pytest

from Configuration import Configuration, testsuite_teardown
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, ResourceAssigner
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_d103_103_018():
    """
    Sub Feature Code: NonUI_Common_RP_Link_Initiation_Successful_Via_KOTAK_OLIVE
    Sub Feature Description: Verification of a Successful Remote Pay link generation via KOTAK OLIVE
    TC naming code description: d103: Dev Project[KOTAK_OLIVE_UPI], 103-> RemotePay, 018->TC018
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        app_cred = ResourceAssigner.getAppUserCredentials(testcase_id)
        logger.debug(f"Fetched app credentials from the ezeauto db : {app_cred}")
        app_username = app_cred['Username']
        app_password = app_cred['Password']

        portal_cred = ResourceAssigner.getPortalUserCredentials(testcase_id)
        logger.debug(f"Fetched portal credentials from the ezeauto db : {portal_cred}")
        portal_username = portal_cred['Username']
        portal_password = portal_cred['Password']

        query = "select org_code from org_employee where username='" + str(app_username) + "';"
        logger.debug(f"Query to fetch org_code from the DB : {query}")
        result = DBProcessor.getValueFromDB(query)
        org_code = result['org_code'].values[0]
        logger.debug(f"Query result, org_code : {org_code}")

        testsuite_teardown.revert_payment_settings_default(org_code, bank_code='KOTAK_OLIVE', portal_un=portal_username,
                                                           portal_pw=portal_password, payment_mode='UPI')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------

        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")

        query = "select * from upi_merchant_config where org_code ='" + str(
            org_code) + "' AND status = 'ACTIVE' AND bank_code = 'KOTAK_OLIVE'"
        logger.debug(f"Query to fetch upi config data from the upi_merchant_config for the {org_code} : {query}")
        result = DBProcessor.getValueFromDB(query)
        logger.debug(f"query result for upi_merchant_config table is : {result}")
        vpa = result['vpa'].values[0]
        logger.debug(f"fetched vpa : {vpa}")
        pg_merchant_id = result['pgMerchantId'].values[0]
        logger.debug(f"fetched pg_merchant_id : {pg_merchant_id}")
        upi_mc_id = result['id'].values[0]
        logger.debug(f"fetched upi_mc_id : {upi_mc_id}")
        tid = result['tid'].values[0]
        logger.debug(f"fetched tid : {tid}")
        mid = result['mid'].values[0]
        logger.debug(f"fetched mid : {mid}")

        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog=True, cnpwareLog=True)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(1, 100)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            logger.info(f"You order id is: {order_id}")
            logger.info(f"Entered amount is: {amount}")
            api_details = DBProcessor.get_api_details('Remotepay_Initiate', request_body={
                "amount": amount, "externalRefNumber": order_id, "username": app_username, "password": app_password})
            response = APIProcessor.send_request(api_details)
            logger.debug(f"response received for Remotepay_Initiate : {response}")

            if not response['success']:
                raise Exception("Api could not initiate a cnp txn.")
            else:
                username_api = response['username']
                amount_api = response['amount']
                external_ref_number_api = response['externalRefNumber']
                org_code_api = response['orgCode']
                payment_intent_id_api = response['paymentIntentId']
                maximum_pay_attempts_allowed_api = response['maximumPayAttemptsAllowed']
                maximum_successful_payment_allowed_api = response['maximumSuccessfulPaymentAllowed']
                intent_status_api = response['intentStatus']
                order_number_api = response['orderNumber']
                total_amount_api = response['totalAmount']

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

        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                expected_db_values = {
                    "username": username_api,
                    "amount": float(amount_api),
                    "external_ref_number": external_ref_number_api,
                    "org_code": org_code_api,
                    "payment_intent_id": payment_intent_id_api,
                    "maximum_pay_attempts_allowed": maximum_pay_attempts_allowed_api,
                    "maximum_successful_payment_allowed": maximum_successful_payment_allowed_api,
                    "intent_status": intent_status_api,
                    "intent_type": "CNP",
                    "payment_mode": "CNP",
                    "payment_flow": "REMOTEPAY"
                }
                logger.debug(f"expected_db_values: {expected_db_values}")

                query = f"select * from payment_intent where id='{payment_intent_id_api}'"
                logger.debug(f"query to fetch payment_intent data : {query}")
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result : {result}")
                username_db = result["username"].iloc[0]
                amount_db = result["amount"].iloc[0]
                external_ref_number_db = result["external_ref"].iloc[0]
                org_code_db = result["org_code"].iloc[0]
                payment_intent_id_db = result["id"].iloc[0]
                maximum_pay_attempts_allowed_db = result["maximum_pay_attempts_allowed"].iloc[0]
                maximum_successful_payment_allowed_db = result["max_succesful_payment_allowed"].iloc[0]
                intent_status_db = result["status"].iloc[0]
                intent_type_db = result["intent_type"].iloc[0]
                payment_mode_db = result["payment_mode"].iloc[0]
                payment_flow_db = result["payment_flow"].iloc[0]

                actual_db_values = {
                    "username": username_db,
                    "amount": float(amount_db),
                    "external_ref_number": external_ref_number_db,
                    "org_code": org_code_db,
                    "payment_intent_id": payment_intent_id_db,
                    "maximum_pay_attempts_allowed": maximum_pay_attempts_allowed_db,
                    "maximum_successful_payment_allowed": maximum_successful_payment_allowed_db,
                    "intent_status": intent_status_db,
                    "intent_type": intent_type_db,
                    "payment_mode": payment_mode_db,
                    "payment_flow": payment_flow_db
                }
                logger.debug(f"actual_db_values : {actual_db_values}")

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
