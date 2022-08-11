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
def test_common_200_201_006():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Withdraw_FromAgent_ToAgency
        Sub Feature Description: API to perform a Withdraw transaction from Agent to Agency account and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency',
                                                      request_body={"username": GlobalConstants.ADMIN_USER,
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "agentId": GlobalConstants.AGENT_USER})
            original_withdraw_amt = float(api_details['RequestBody']['amount'])
            response = APIProcessor.send_request(api_details)
            withdraw_pay_success = response['success']
            realcode = response['realCode']
            successcode = response['successCode']
            wallet_txn_id = response['walletTxnId']
            credit_acc_bal = float(response['creditAccBalance'])
            debit_acc_bal = float(response['debitAccBalance'])

            logger.info(f"API Result: Fetch Response of Withdraw Payment - From Agent: {withdraw_pay_success},{wallet_txn_id}, {credit_acc_bal}, {debit_acc_bal}")

            GlobalVariables.withdraw_amt += original_withdraw_amt
            GlobalVariables.withdraw_count += 1

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
                if withdraw_pay_success == True:
                    expectedAPIValues = {"success": True,
                                     "realCode": "TRANSACTION_SUCCESSFUL", "successCode": "CLOSED_LOOP_000027",
                                     "creditAccBalance": agency_balance_before + original_withdraw_amt,
                                     "debitAccBalance": agent_balance_before - original_withdraw_amt,
                                     "bal_after_withdraw": agency_balance_before + original_withdraw_amt}

                    query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                    result = DBProcessor.getValueFromDB(query, "closedloop")
                    agency_bal_after = float(result["balance"].iloc[0])

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": withdraw_pay_success,
                                       "realCode": realcode, "successCode": successcode,
                                       "creditAccBalance": credit_acc_bal, "debitAccBalance": debit_acc_bal,
                                        "bal_after_withdraw": agency_bal_after}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Withdraw from Agent Failed")

            except Exception as e:
                msg = "Withdraw has been failed to " + GlobalConstants.ORG
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
                logger.debug(f"Agency Balance before Withdraw : {agency_balance_before}")
                logger.debug(f"Actual amount for Withdraw  : {original_withdraw_amt}")

                expectedDBValues = {"Agency balance": (agency_balance_before + original_withdraw_amt)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_bal_after}
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
def test_common_200_201_007():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Withdraw_FromAgent_More_than_Balance
        Sub Feature Description: API to perform a Withdraw transaction from Agent to Agency account more than Agent balance and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency',
                                                      request_body={"username": GlobalConstants.ADMIN_USER,
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "agentId": GlobalConstants.AGENT_USER})
            original_withdraw_amt = float(api_details['RequestBody']['amount'])

            api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency',
                                                      request_body={"username": GlobalConstants.ADMIN_USER,
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "agentId": GlobalConstants.AGENT_USER,
                                                                    "amount" : agent_balance_before + (original_withdraw_amt+1)})
            response = APIProcessor.send_request(api_details)
            withdraw_pay_success = response['success']
            error_message = response['errorMessage']

            logger.info(f"API Result: Fetch Response of Withdraw Payment - From Agent: {withdraw_pay_success},{error_message}")

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
                    expectedAPIValues = {"success": False,
                                     "error_message": "Insufficient funds for ' AGENT " + GlobalConstants.AGENT_USER+ "'"}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": withdraw_pay_success,
                                       "error_message": error_message}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)


            except Exception as e:
                msg = "Withdraw has been failed to" + GlobalConstants.ORG
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
                logger.debug(f"Agency Balance before Withdraw : {agency_balance_before}")
                logger.debug(f"Actual amount for Withdraw  : {agent_balance_before + (original_withdraw_amt+1)}")

                expectedDBValues = {"Agency balance": (agency_balance_before)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_bal_after}
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
def test_common_200_201_008():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Withdraw_FromAgent_Zero_amount
        Sub Feature Description: API to perform a Withdraw transaction from Agent to Agency account with 0 amount and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

            api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency',
                                                      request_body={"username": GlobalConstants.ADMIN_USER,
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "agentId": GlobalConstants.AGENT_USER,
                                                                    "amount" : agent_balance_before - agent_balance_before})
            response = APIProcessor.send_request(api_details)
            withdraw_pay_success = response['success']
            error_message = response['errorMessage']

            logger.info(f"API Result: Fetch Response of Withdraw Payment - From Agent: {withdraw_pay_success},{error_message}")

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
                    expectedAPIValues = {"success": False,
                                     "error_message": "Invalid Amount"}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": withdraw_pay_success,
                                       "error_message": error_message}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)


            except Exception as e:
                msg = "Withdraw has been failed to" + GlobalConstants.ORG
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
                logger.debug(f"Agency Balance before Withdraw : {agency_balance_before}")
                logger.debug(f"Actual amount for Withdraw  : {agent_balance_before-agent_balance_before}")

                expectedDBValues = {"Agency balance": (agency_balance_before)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_bal_after}
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