import random
import re
import shutil
import time
from datetime import datetime, date
import pytest
import sys
from termcolor import colored

from Configuration import Configuration
from DataProvider import GlobalVariables, GlobalConstants
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger


logger = EzeAutoLogger(__name__)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_006():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Refund_Cash_collected_InValid_TxnID
        Sub Feature Description: API to perform a Refund txn for the cash collected having Invalid TxnID and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "originalTransactionId": "220801073501153E"})
            response = APIProcessor.send_request(api_details)

            original_amount_refunded = float(api_details["RequestBody"]["amount"])
            refund_payment_success = response['success']
            username = response['username']
            error_message = response['errorMessage']
            error_code = response['errorCode']
            real_code = response['realCode']
            logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{error_message},{original_amount_refunded}, {username}, {error_code},{real_code}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored(
                "Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                     "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                    expectedAPIValues = {"success": False, "username": GlobalConstants.AGENT_USER,
                                         "error_message": "Invalid Transaction ID: null", "error_code": "EZETAP_0000025",
                                         "real_code": "PAYMENT_INVALID_TXN_ID",
                                         "balance": agent_balance_before}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_refund = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": refund_payment_success, "username": username, "error_message":error_message ,
                                       "error_code": error_code, "real_code": real_code,
                                         "balance": agentbal_after_refund}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Refund Payment has been failed" + GlobalConstants.AGENT_USER
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Refund Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for Refund  : {original_amount_refunded}")

                expectedDBValues = {"agent_balance": agent_balance_before,
                                    "settlement_balance": settlement_bal_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"agent_balance": agentbal_after_cash_payment,
                                  "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_007():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Partial_Refund_Cash_collected
        Sub Feature Description: API to perform a Partial Refund txn for the cash collected and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            api_details = DBProcessor.get_api_details('Cash_Collection',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD})
            response = APIProcessor.send_request(api_details)

            original_amount_cashpay = float(api_details["RequestBody"]["amount"])
            txn_id = response['txnId']
            cash_payment_success = response['success']
            GlobalVariables.cash_txn_id = txn_id
            GlobalVariables.collection_amt += original_amount_cashpay
            GlobalVariables.collection_count += 1

            if cash_payment_success == True:

                api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD})
                original_amount_refunded = float(api_details["RequestBody"]["amount"])
                api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "amount" :original_amount_refunded - 2,
                                                                    "originalTransactionId": GlobalVariables.cash_txn_id})
                response = APIProcessor.send_request(api_details)


                refund_payment_success = response['success']
                username = response['username']
                error_message = response['errorMessage']
                error_code = response['errorCode']
                real_code = response['realCode']
                logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{error_message},{original_amount_refunded}, {username}, {error_code},{real_code}")

                GlobalVariables.EXCEL_TC_Execution = "Pass"
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                      "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored(
                "Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                     "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                    expectedAPIValues = {"success": False, "username": GlobalConstants.AGENT_USER,
                                         "error_message": "Partial refund is not supported.", "error_code": "EZETAP_0000360",
                                         "real_code": "REFUND_AMOUNT_MISMATCH",
                                         "balance": agent_balance_before - original_amount_cashpay}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_refund = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": refund_payment_success, "username": username, "error_message":error_message ,
                                         "error_code": error_code, "real_code": real_code,
                                         "balance": agentbal_after_refund}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Refund Payment has been failed" + GlobalConstants.AGENT_USER
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Refund Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for Refund  : {original_amount_refunded}")

                expectedDBValues = {"agent_balance": agent_balance_before - original_amount_cashpay,
                                    "settlement_balance": settlement_bal_before + original_amount_cashpay}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"agent_balance": agentbal_after_cash_payment,
                                  "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_008():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Refund_Cash_collected_MoreThan_Actual_Txn_Amount
        Sub Feature Description: API to perform a Refund txn for the cash collected for amount greater than the actual transaction amount and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,
                                                   config_log=False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD})
            original_amount_refunded = float(api_details["RequestBody"]["amount"])
            api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "amount" :original_amount_refunded + 2,
                                                                    "originalTransactionId": GlobalVariables.cash_txn_id})
            response = APIProcessor.send_request(api_details)


            refund_payment_success = response['success']
            username = response['username']
            error_message = response['errorMessage']
            error_code = response['errorCode']
            real_code = response['realCode']
            logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{error_message},{original_amount_refunded}, {username}, {error_code},{real_code}")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored(
                    "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored(
                "Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                     "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                    expectedAPIValues = {"success": False, "username": GlobalConstants.AGENT_USER,
                                         "error_message": "Transaction declined. Amount entered is more than maximum allowed for the transaction. Maximum Allowed: " + str(original_amount_refunded) + "0", "error_code": "EZETAP_0000164",
                                         "real_code": "AMOUNT_MORE_THAN_ALLWD",
                                         "balance": agent_balance_before}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_refund = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": refund_payment_success, "username": username, "error_message":error_message ,
                                          "error_code": error_code,"real_code": real_code,
                                         "balance": agentbal_after_refund}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Refund Payment has been failed" + GlobalConstants.AGENT_USER
                print("API Validation failed due to exception - " + str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")

        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Refund Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for Refund  : {original_amount_refunded}")

                expectedDBValues = {"agent_balance": agent_balance_before,
                                    "settlement_balance": settlement_bal_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"agent_balance": agentbal_after_cash_payment,
                                  "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")

        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                      'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored(
                "Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored(
            "Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                   "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_009():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Cash_collection_Higher_AgentBalance
        Sub Feature Description: API to perform a Cash payment as a BILLPAY more than the Agent balance and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Cash_Collection', request_body={"username": GlobalConstants.AGENT_USER,
                                                                                       "password": GlobalConstants.AGENT_PASSWORD})

            original_amount_cashpay = float(api_details["RequestBody"]["amount"])
            higher_amount = agent_balance_before + (original_amount_cashpay + 1)

            api_details = DBProcessor.get_api_details('Cash_Collection',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "amount": higher_amount})

            response = APIProcessor.send_request(api_details)
            cash_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            settlement_status = response['settlementStatus']
            clw_status = response['clwStatus']
            account_label = response['accountLabel']
            apimessage_title = response['apiMessageTitle']
            closeloop_meta = str(response['closeLoopMeta'])
            logger.info(f"API Result: Fetch Response of Cash Payment - BILLPAY: {cash_payment_success}, {original_amount_cashpay},{higher_amount}, {username}, {amount},{settlement_status}, {clw_status}, {txn_id}, {status}, {account_label}, {closeloop_meta},{apimessage_title}")


            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                    expectedAPIValues = {"success": False, "username": GlobalConstants.AGENT_USER, "txn_amt": higher_amount, "pmt_status":"PENDING",
                                         "settle_status":"PENDING","account_label": "BILLPAY","clw_status": "PENDING",
                                         "api_message_title":"DECLINED","closedloop_meta":"{\"success\":\"false\",\"errorCode\":\"CLOSED_LOOP_000037\",\"errorMessage\":\"Insufficient funds for ' AGENT",
                                         "balance":agent_balance_before}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": cash_payment_success, "username": username, "txn_amt": amount, "pmt_status":status,
                                         "settle_status":settlement_status,"account_label": account_label,"clw_status": clw_status,
                                         "api_message_title":apimessage_title,"closedloop_meta":re.search("{\"success\":\"false\",\"errorCode\":\"CLOSED_LOOP_000037\",\"errorMessage\":\"Insufficient funds for ' AGENT",closeloop_meta).group(),
                                         "balance":agentbal_after_cash_payment}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Cash Payment has been failed" + GlobalConstants.AGENT_USER
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Cash Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for BILLPAY  : {higher_amount}")

                expectedDBValues = {"agent_balance": agent_balance_before,
                                    "settlement_balance": settlement_bal_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"agent_balance": agentbal_after_cash_payment,
                                    "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_202_010():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Cash_collection_with_decimal
        Sub Feature Description: API to perform a Cash payment as a BILLPAY with decimal and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Cash_Collection', request_body={"username": GlobalConstants.AGENT_USER,
                                                                                       "password": GlobalConstants.AGENT_PASSWORD})
            original_amount_cashpay = float(api_details["RequestBody"]["amount"])
            api_details = DBProcessor.get_api_details('Cash_Collection',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "amount": original_amount_cashpay + 0.25})
            response = APIProcessor.send_request(api_details)


            cash_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            settlement_status = response['settlementStatus']
            clw_status = response['clwStatus']
            account_label = response['accountLabel']
            payment_mode = response['paymentMode']
            logger.info(f"API Result: Fetch Response of Cash Payment - BILLPAY: {cash_payment_success}, {original_amount_cashpay},{payment_mode}, {username}, {amount},{settlement_status}, {clw_status}, {txn_id}, {status}, {account_label}")

            GlobalVariables.collection_amt += (original_amount_cashpay+0.25)
            GlobalVariables.collection_count += 1

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":

            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                if cash_payment_success == True:
                    expectedAPIValues = {"success": True, "username": GlobalConstants.AGENT_USER, "txn_amt": (original_amount_cashpay+0.25), "pmt_status":"AUTHORIZED",
                                         "settle_status":"SETTLED","account_label": "BILLPAY","clw_status": "SUCCESS",
                                         "balance":agent_balance_before - (original_amount_cashpay+0.25)}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                    result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                    agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])

                    actualAPIValues = {"success": cash_payment_success, "username": username, "txn_amt": amount, "pmt_status":status,
                                        "settle_status":settlement_status,"account_label": account_label,"clw_status":clw_status,
                                        "balance":agentbal_after_cash_payment}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Cash Payment is not successfull")

            except Exception as e:
                msg = "Cash Payment has been failed" + GlobalConstants.AGENT_USER
                print("API Validation failed due to exception - "+str(e))
                logger.exception(f"API Validation failed due to exception - {e}")
                msg = msg + "\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"
            logger.info(f"Completed API validation for the test case : {testcase_id}")


        # -----------------------------------------End of API Validation---------------------------------------
        # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            logger.info(f"Started DB validation for the test case : {testcase_id}")
            try:
                logger.debug(f"Agent Balance before Cash Payment : {agent_balance_before}")
                logger.debug(f"Actual amount for BILLPAY  : {original_amount_cashpay + 0.25}")

                expectedDBValues = {"txn_amt":original_amount_cashpay+0.25,"pmt_mode":payment_mode, "settle_status":settlement_status,
                                    "pmt_status":status,"agent_balance": agent_balance_before - (original_amount_cashpay+0.25),
                                    "settlement_balance": settlement_bal_before + (original_amount_cashpay+0.25)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
                                    "pmt_status":pmt_status,"agent_balance": agentbal_after_cash_payment,
                                    "settlement_balance": settlementbal_after_cash_payment}
                logger.debug(f"actualDBValues : {actualDBValues}")
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)

            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'

            logger.info(f"Completed DB validation for the test case : {testcase_id}")


        # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        #-------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        #----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))










