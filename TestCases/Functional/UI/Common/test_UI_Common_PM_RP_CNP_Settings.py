import random
import shutil
import sys
import time
from datetime import datetime

import pandas as pd
import pytest
from termcolor import colored
from Configuration import Configuration, TestSuiteSetup, testsuite_teardown
from DataProvider import GlobalVariables
from PageFactory.App_HomePage import HomePage
from PageFactory.App_LoginPage import LoginPage
from PageFactory.App_TransHistoryPage import TransHistoryPage
from PageFactory.Portal_HomePage import PortalHomePage
from PageFactory.Portal_LoginPage import PortalLoginPage
from PageFactory.Portal_TransHistoryPage import PortalTransHistoryPage
from PageFactory.portal_remotePayPage import RemotePayTxnPage
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, receipt_validator, \
    ResourceAssigner, date_time_converter
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)

from datetime import datetime, timedelta


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
@pytest.mark.portalVal
@pytest.mark.appVal
@pytest.mark.chargeSlipVal
def test_common_100_103_077():
    """
    Sub Feature Code: UI_Common_PM_CNP_Cyber_bumpCount_CnpSettigs
    Sub Feature Description: Verification of the bump count via cnp link
    TC naming code description:
    100: Payment Method
    103: RemotePay
    077: TC_077
    """
    expectedExpiryMessage = "Remote payment link has expired, Use a different mode or request for a new remote pay link to complete payment"
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        query = "update remotepay_setting set setting_value= '1' where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.debug(f"Result for remote pay setting is: {result}")

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        query = "update remotepay_setting set setting_value=2 where setting_name='rmpayBumpTime' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)-----------------------------

        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')
            ui_driver = TestSuiteSetup.initialize_portal_driver()
            logger.info("Initiating a Remote pay Link")

            query = "select * from payment_intent where org_code='" + org_code + "' and id ='" + payment_intent_id + "'"
            logger.debug(f"Query to fetch bumptime from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            intent_expiry_time = result['expire_by_time'].values[0]
            logger.debug(f"Query result, bumptime : {intent_expiry_time}")


            query = "select * from remotepay_setting where setting_name='rmpayBumpTime' and org_code='" + org_code + "'"
            logger.debug(f"Query to fetch bumptime from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bump_time = int(result['setting_value'].values[0])
            logger.debug(f"Query result, bumptime : {bump_time}")

            query = "select * from remotepay_setting where setting_name='remotePayExpTime' and org_code='" + org_code + "'"
            logger.debug(f"Query to fetch expiry time from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_time = int(result['setting_value'].values[0])
            logger.debug(f"Query result, expiry time : {expiry_time}")
            wait_time = (60 * (bump_time - expiry_time))
            time.sleep((wait_time + 2))

            if wait_time < bump_time:
                ui_driver.get(paymentLinkUrl)
                logger.info("Remote pay Link initiation completed and opening in a browser")

            query = "select * from remotepay_setting where setting_name='rmpayBumpTime' and org_code='" + org_code + "'"
            logger.debug(f"Query to fetch bumptime from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            bumptime = result['setting_value'].values[0]
            logger.debug(f"Query result, bumptime : {bumptime}")



            # remote_pay_txn = remotePayTxnPage(ui_driver)
            # remote_pay_txn.waitForExpiryElement()
            # expiryMessage = str(remote_pay_txn.expiryMessage())
            # logger.info(f"Your expiryMessage is:  {expiryMessage}")
            # logger.info(f"Your expiryMessage is:  {expectedExpiryMessage}")
            # if expiryMessage == (expectedExpiryMessage):
            #     pass
            # else:
            #     raise Exception("Expiry Messages are not matching.")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        query = "update remotepay_setting set setting_value=15 where setting_name='rmpayBumpCount' and org_code='" + org_code + "';"
        logger.debug(f"Query to update remote pay settings is : {query}")
        result = DBProcessor.setValueToDB(query)
        logger.info(f"In finally, remote pay setting is: {result}")
        api_details = DBProcessor.get_api_details('DB Refresh', request_body={"username": portal_username,
                                                                              "password": portal_password})
        response = APIProcessor.send_request(api_details)
        logger.debug(f"Response received for setting precondition DB refresh is : {response}")
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_100_103_090():
    """
    Sub Feature Code: UI_Common_PM_CNP_Cyber_bumpTime_CnpSettigs
    Sub Feature Description: Verification the bump time via cnp link.
    TC naming code description:
    100: Payment Method
    103: RemotePay
    090: TC_090
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)--------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
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

        testsuite_teardown.revert_cnp_payment_settings_default(org_code, bank_code='CYBERSOURCE',
                                                               portal_un=portal_username,
                                                               portal_pw=portal_password, payment_gateway='CYBERSOURCE')

        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        # Write the setup code here
        GlobalVariables.setupCompletedSuccessfully = True  # Do not remove this line of code.
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------

        # ---------------------------------------------------------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=False, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            amount = random.randint(300, 399)
            order_id = datetime.now().strftime('%m%d%H%M%S')
            api_details = DBProcessor.get_api_details('Remotepay_Initiate',
                                                      request_body={"amount": amount, "externalRefNumber": order_id,
                                                                    "username": app_username, "password": app_password})

            response = APIProcessor.send_request(api_details)
            paymentLinkUrl = response['paymentLink']
            payment_intent_id = response.get('paymentIntentId')

            query = "select * from payment_intent where org_code='" + org_code + "' and id ='" + payment_intent_id + "'"
            logger.debug(f"Query to fetch expire_by_time from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            intent_expiry_time = str(result['expire_by_time'].values[0])
            logger.debug(f"Query result, expire_by_time : {intent_expiry_time}")

            original_time = date_time_converter.bump_datetime(intent_expiry_time)
            logger.info(f"original time is:{original_time}")

            try:
                query = "select * from remotepay_setting where setting_name='rmpayBumpTime' and org_code='" + str(
                    org_code) + "';"
                logger.debug(f"Query to fetch bumptime from the DB : {query}")
                result = DBProcessor.getValueFromDB(query)
                bump_time = (60 * int(result['setting_value'].values[0]))
                logger.debug(f"Query result, bumptime : {bump_time}")
                bump_time1 = bump_time
                logger.debug(f"Query result, bumptime : {bump_time1}")
            except Exception as e:
                bump_time = None
                print(e)

            logger.info(f"timeout time is :{bump_time} min.")
            query = "select * from remotepay_setting where setting_name='remotePayExpTime' and org_code='" + str(
                org_code) + "';"
            logger.debug(f"Query to fetch expiry time from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_time = (60 * int(result['setting_value'].values[0]))
            logger.debug(f"Query result, expiry time : {expiry_time}")

            logger.info(f"Expiry time is {expiry_time}")
            logger.info(f"bump time is {bump_time}")

            ui_driver = TestSuiteSetup.initialize_portal_driver()
            logger.info("Initiating a Remote pay Link")
            ui_driver.get(paymentLinkUrl)
            logger.info("Remote pay Link initiation completed and opening in a browser")
            query = "select * from payment_intent where org_code='" + org_code + "' and id ='" + payment_intent_id + "'"
            logger.debug(f"Query to fetch expire_by_time from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            modified_time = str(result['modified_time'].values[0])
            logger.debug(f"Query result, modified time : {modified_time}")
            modified_time1 = date_time_converter.bump_datetime(modified_time)
            logger.info(f"expiry with bump time:{modified_time1}")
            created_time = pd.to_datetime(modified_time1)
            print(created_time)
            print(type(created_time))
            date_time_str = str(created_time)
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S').strftime("%H:%M:%S")
            date_time_obj = datetime.strptime(date_time_obj, "%H:%M:%S")
            t = date_time_obj + timedelta(0, bump_time1)
            t2 = t.strftime("%H:%M:%S")
            print(type(t2))
            t1 = datetime.strptime(t2, "%H:%M:%S")
            print(t1)

            query = "select * from payment_intent where org_code='" + org_code + "' and id ='" + payment_intent_id + "'"
            logger.debug(f"Query to fetch expire_by_time from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            expiry_with_bump = str(result['expire_by_time'].values[0])
            expiry_with_bump1 = date_time_converter.bump_datetime(expiry_with_bump)
            time = datetime.strptime(expiry_with_bump1, "%H:%M:%S").strftime("%H:%M:%S")
            time1 = datetime.strptime(time, "%H:%M:%S")
            logger.debug(f"Query result, modified time : {time1}")
            print(t1)
            print(time1)
            print(type(t1))
            print(type(time1))
            if t1 == time1:
                print("time is matching")

            else:
                raise Exception ("modified time is not matching with Expiry time")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")
        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
    # -------------------------------------------End of Validation---------------------------------------------
    finally:
        logger.info(f"In finally, remote pay setting is: {result}")
        Configuration.executeFinallyBlock(testcase_id)
