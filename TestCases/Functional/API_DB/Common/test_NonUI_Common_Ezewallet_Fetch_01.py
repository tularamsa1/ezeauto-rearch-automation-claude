import random
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
def test_common_200_203_001():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agency_Fetch_Passbook_statement
        Sub Feature Description: API to perform a Digital TopUp of Agency using Card Payment and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(100,1000)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Digital_Agency_TopUp_Card', request_body={"username": GlobalConstants.ADMIN_USER, "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agency Top Up: {card_payment_success}, {amount}, {txn_id}, {status}, {account_label}")

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
                expectedAPIValues = {"success": True, "cardpay_amount": original_amount, "status":"AUTHORIZED",
<<<<<<< HEAD
                                     "account_label": "TOPUP","txn_status": "SUCCESS", "transfer_mode": "ADDFUNDS",
=======
                                     "accountLabel": "TOPUP","txnStatus": "SUCCESS", "transferMode": "ADDFUNDS",
>>>>>>> Added Ezewallet related TCS
                                     "fetch_amount": amount, "externalRefId": txn_id}
                if card_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statment_success, "cardpay_amount": amount, "status":status,
<<<<<<< HEAD
                                       "account_label": account_label, "txn_status": txn_status, "transfer_mode": transfer_mode ,
=======
                                       "accountLabel": account_label, "txnStatus": txn_status, "transferMode": transfer_mode ,
>>>>>>> Added Ezewallet related TCS
                                       "fetch_amount":actual_amount, "externalRefId" : external_ref_Id}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Card Payment is not successfull")

            except Exception as e:
                msg = "Digital Top up has been failed for an Agency" + GlobalConstants.ORG
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
                logger.debug(f"Agency Balance before Top Up : {agency_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")

                expectedDBValues = {"Agency balance": (agency_balance_before + actual_amount) }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_posting = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": bal_after_posting}
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
def test_common_200_203_002():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_TransferAmount_ToAgent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Transfer of an Amount from Agency Account to Agent Account and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        agent_balance_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        result = DBProcessor.getValueFromDB(agent_balance_check, "closedloop")
        agent_balance_before = float(result["balance"].values[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent', request_body={"username": GlobalConstants.ADMIN_USER, "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "agentId": GlobalConstants.AGENT_USER})
            original_transfer_amt = float(api_details['RequestBody']['amount'])
            response = APIProcessor.send_request(api_details)
            transfer_pay_success = response['success']
            realcode = response['realCode']
            successcode = response['successCode']
            wallet_txn_id = response['walletTxnId']
            bal_amt = float(response['balance'])
            credit_acc_bal = float(response['creditAccBalance'])
            debit_acc_bal = float(response['debitAccBalance'])

            logger.info(f"API Result: Fetch Response of Transfer Payment - To Agent: {transfer_pay_success},{wallet_txn_id}, {bal_amt}, {credit_acc_bal}, {debit_acc_bal}")

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
            #time.sleep(5)
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expectedAPIValues = {"success": True, "walletTxnId":wallet_txn_id, "realCode": "TRANSACTION_SUCCESSFUL", "successCode":"CLOSED_LOOP_000027", "transferMode": "TRANSFER", "creditAccBalance": agent_balance_before + original_transfer_amt, "debitAccBalance": agency_balance_before - original_transfer_amt
                                     , "agentID" : GlobalConstants.AGENT_USER, "txn_status":"SUCCESS", "amount_transfered" : original_transfer_amt, "bal_after_transfer" : original_transfer_amt + agent_balance_before}
                if transfer_pay_success == True:
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    actual_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    agent_Id = response['response']['elements'][0]['agentId']
                    amount_transfered = float(response['response']['elements'][0]['amount'])
                    bal_after_transfer = float(response['response']['elements'][0]['balance'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "walletTxnId": actual_wallet_txn_id, "realCode":realcode, "successCode": successcode, "transferMode": transfer_mode ,"creditAccBalance":credit_acc_bal, "debitAccBalance" : debit_acc_bal
                                       ,"agentID" : agent_Id, "txn_status": txn_status, "amount_transfered" : amount_transfered, "bal_after_transfer": bal_after_transfer}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Transfer to Agent Failed")

            except Exception as e:
                msg = "Transfer has been failed to an Agent" + GlobalConstants.AGENT_USER
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
                logger.debug(f"Agency Balance before Transfer : {agency_balance_before}")
                logger.debug(f"Actual amount for Transfer  : {original_transfer_amt}")


                expectedDBValues = {"Agency balance": (agency_balance_before - original_transfer_amt) }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_balance_after}
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
def test_common_200_203_003():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_WithdrawAmount_FromAgent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Withdraw of an Amount from Agent Account to Agency Account and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        agent_balance_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        result = DBProcessor.getValueFromDB(agent_balance_check, "closedloop")
        agent_balance_before = float(result["balance"].values[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency', request_body={"username": GlobalConstants.ADMIN_USER, "password": GlobalConstants.ADMIN_PASSWORD,
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
            #time.sleep(5)
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expectedAPIValues = {"success": True, "walletTxnId":wallet_txn_id, "realCode": "TRANSACTION_SUCCESSFUL", "successCode":"CLOSED_LOOP_000027", "transferMode": "WITHDRAW", "creditAccBalance": agency_balance_before + original_withdraw_amt, "debitAccBalance": agent_balance_before - original_withdraw_amt
                                     , "agentID" : GlobalConstants.AGENT_USER, "txn_status":"SUCCESS", "amount_withdraw" : original_withdraw_amt, "bal_after_withdraw" : agent_balance_before - original_withdraw_amt}
                if withdraw_pay_success == True:
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    actual_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "walletTxnId": actual_wallet_txn_id, "realCode":realcode, "successCode": successcode, "transferMode": transfer_mode ,"creditAccBalance":credit_acc_bal, "debitAccBalance" : debit_acc_bal
                                       ,"agentID" : agent_Id, "txn_status": txn_status, "amount_withdraw" : amount_withdraw, "bal_after_withdraw": bal_after_withdraw}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    logger.error("Withdraw from Agent Failed")

            except Exception as e:
                msg = "Withdraw has been failed from an Agent" + GlobalConstants.AGENT_USER
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

                expectedDBValues = {"Agency balance": (agency_balance_before + original_withdraw_amt) }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_balance_after}
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
def test_common_200_203_004():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Multiple_transactions_Fetch_passbook_statement_Agency
        Sub Feature Description: API to perform a Agency Top Up, Transfer, Withdraw and Validate to Agency Balance and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        agent_balance_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        result = DBProcessor.getValueFromDB(agent_balance_check, "closedloop")
        agent_balance_before = float(result["balance"].values[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            original_amount = random.randint(100, 1000)
            api_details = DBProcessor.get_api_details('Digital_Agency_TopUp_Card',
                                                      request_body={"username": GlobalConstants.ADMIN_USER,
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "amount": original_amount,
                                                                    "externalRefNumber": "UFAZMJK1ON071341J1" + str(
                                                                        random.randint(0, 9))})
            response = APIProcessor.send_request(api_details)
            card_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agency Top Up: {card_payment_success}, {amount}, {txn_id}, {status}, {account_label}")

            if card_payment_success == True:
                time.sleep(3)
                api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "agentId": GlobalConstants.AGENT_USER})
                original_transfer_amt = float(api_details['RequestBody']['amount'])
                response = APIProcessor.send_request(api_details)
                transfer_pay_success = response['success']
                transfer_wallet_txn_id = response['walletTxnId']
                bal_amt = float(response['balance'])
                credit_acc_bal = float(response['creditAccBalance'])
                debit_acc_bal = float(response['debitAccBalance'])
                logger.info(f"API Result: Fetch Response of Transfer Payment - To Agent: {original_transfer_amt}, {transfer_pay_success},{transfer_wallet_txn_id}, {bal_amt}, {credit_acc_bal}, {debit_acc_bal}")
                if transfer_pay_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Withdraw_From_Agent_Agency',
                                                              request_body={"username": GlobalConstants.ADMIN_USER,
                                                                            "password": GlobalConstants.ADMIN_PASSWORD,
                                                                            "agentId": GlobalConstants.AGENT_USER})
                    original_withdraw_amt = float(api_details['RequestBody']['amount'])
                    response = APIProcessor.send_request(api_details)
                    withdraw_pay_success = response['success']
                    withdraw_wallet_txn_id = response['walletTxnId']
                    credit_acc_bal = float(response['creditAccBalance'])
                    debit_acc_bal = float(response['debitAccBalance'])
                    logger.info(f"API Result: Fetch Response of Withdraw Payment - From Agent: {withdraw_pay_success},{withdraw_wallet_txn_id}, {credit_acc_bal}, {debit_acc_bal}")
                    if withdraw_pay_success == True:
                        logger.info("Agency Top Up, Transfer to Agent and withdraw from Agent Successfull")
                    else:
                        logger.error("Withdraw from Agent Failed")
                        raise Exception("Withdraw from Agent Failed")

                else:
                    logger.error("Transfer to Agent Failed")
                    raise Exception("Transfer to Agent Failed")

            else:
                logger.error("Digital Agency Top Up Failed")
                raise Exception("Digital Agency Top Up Failed")

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
                expectedAPIValues = {"success": True, "topup_txn_status": "SUCCESS", "topup_transfer_mode":"ADDFUNDS","topup_amount":original_amount,
                                    "external_ref_Id":txn_id, "trans_wallet_txnid":transfer_wallet_txn_id, "transfer_txn_status":"SUCCESS",
                                     "trans_transfer_mode":"TRANSFER", "transfer_agent_Id":GlobalConstants.AGENT_USER, "amount_transfered":original_transfer_amt,
                                     "bal_after_transfer":(original_transfer_amt + agent_balance_before), "withdraw_wallet_txn_id":withdraw_wallet_txn_id,
                                     "withdraw_txn_status":"SUCCESS","withdraw_transfer_mode": "WITHDRAW", "withdraw_agent_Id": GlobalConstants.AGENT_USER,
                                     "amount_withdraw" : original_withdraw_amt,
                                     "bal_after_withdraw" : (agent_balance_before + original_transfer_amt) - original_withdraw_amt}

                api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                response = APIProcessor.send_request(api_details)


                fetch_statment_success = response['success']
                if fetch_statment_success == True:

                    topup_txn_status = response['response']['elements'][2]['txnStatus']
                    topup_transfer_mode = response['response']['elements'][2]['transferMode']
                    topup_amount = float(response['response']['elements'][2]['amount'])
                    external_ref_Id = response['response']['elements'][2]['externalRefId']

                    #
                    trans_wallet_txnid = response['response']['elements'][1]['walletTxnId']
                    transfer_txn_status = response['response']['elements'][1]['txnStatus']
                    trans_transfer_mode = response['response']['elements'][1]['transferMode']
                    transfer_agent_Id = response['response']['elements'][1]['agentId']
                    amount_transfered = float(response['response']['elements'][1]['amount'])
                    bal_after_transfer = float(response['response']['elements'][1]['balance'])

                    #
                    withdraw_wallet_txnid = response['response']['elements'][0]['walletTxnId']
                    withdraw_txn_status = response['response']['elements'][0]['txnStatus']
                    withdraw_transfer_mode = response['response']['elements'][0]['transferMode']
                    withdraw_agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "topup_txn_status": topup_txn_status, "topup_transfer_mode":topup_transfer_mode,"topup_amount":topup_amount,
                                    "external_ref_Id":external_ref_Id, "trans_wallet_txnid":trans_wallet_txnid, "transfer_txn_status":transfer_txn_status,
                                     "trans_transfer_mode":trans_transfer_mode, "transfer_agent_Id":transfer_agent_Id, "amount_transfered":amount_transfered,
                                     "bal_after_transfer":bal_after_transfer, "withdraw_wallet_txn_id":withdraw_wallet_txnid,
                                     "withdraw_txn_status":withdraw_txn_status,"withdraw_transfer_mode": withdraw_transfer_mode, "withdraw_agent_Id": withdraw_agent_Id,
                                     "amount_withdraw" : amount_withdraw,
                                     "bal_after_withdraw" : bal_after_withdraw}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Fetch Merchant Statement Failed")

            except Exception as e:
                msg = "API Validation falied"
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
                logger.debug(f"Agency Balance before all transactions : {agency_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")
                logger.debug(f"Actual amount for Transfer  : {original_transfer_amt}")
                logger.debug(f"Actual amount for Withdraw  : {original_withdraw_amt}")

                expectedDBValues = {"Agency balance": ((agency_balance_before + original_amount + original_withdraw_amt) - original_transfer_amt) }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": agency_balance_after}
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
def test_common_200_203_005():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_fetch_Invalid_Merchant_Passbook_statement
        Sub Feature Description: API to perform fetch invalid merchant passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                      request_body={"username": "7777770000",
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "startDate": str(date.today()),
                                                                    })
            response = APIProcessor.send_request(api_details)

            username = response['username']
            error_code = response['errorCode']
            error_message = response['errorMessage']
            real_code = response['realCode']
            fetch_success = response['success']
            logger.info(f"API Result: Fetch Response of Invalid merchant passbook: {username}, {error_code}, {error_message}, {real_code}, {fetch_success}")

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
                expectedAPIValues = {"success": False, "username": "7777770000", "error_code":"EZETAP_0000073", "error_message": "Invalid credentials. Verify your credentials, login again, or contact your supervisor.",
                                     "real_code": "AUTH_FAILED"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                actualAPIValues = {"success": fetch_success, "username": username, "error_code":error_code, "error_message": error_message,
                                   "real_code": real_code}
                logger.debug(f"actualAPIValues: {actualAPIValues}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "API Validation failed due to exception"
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
                logger.debug(f"Agency Balance before fetch passbook : {agency_balance_before}")

                expectedDBValues = {"Agency balance": agency_balance_before }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"

                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_fetch = float(result["balance"].iloc[0])
                actualDBValues = {"Agency balance": bal_after_fetch}
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









