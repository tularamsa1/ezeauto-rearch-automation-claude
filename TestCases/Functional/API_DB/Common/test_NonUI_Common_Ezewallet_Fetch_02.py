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
def test_common_200_203_006():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Digital TopUp of an Agent using Card Payment and fetch Passbook statement of an Agent
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

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
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card', request_body={"username": GlobalConstants.AGENT_USER, "password": GlobalConstants.AGENT_PASSWORD,
                                                                        "amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)

            card_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agent Top Up: {card_payment_success}, {amount}, {txn_id}, {status}, {account_label}")

            GlobalVariables.selftopup_amt += original_amount
            GlobalVariables.selftopup_count += 1

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
                                     "accountLabel": "TOPUP","txnStatus": "SUCCESS", "transferMode": "TRANSFER",
                                     "fetch_amount": amount, "externalRefId": txn_id,
                                     "agent_id":GlobalConstants.AGENT_USER, "balance":agent_balance_before+original_amount}
                if card_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.AGENT_USER,
                                                                        "password": GlobalConstants.AGENT_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statement_success = response['success']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statement_success, "cardpay_amount": amount, "status":status,
                                       "accountLabel": account_label, "txnStatus": txn_status,
                                       "transferMode": transfer_mode ,"fetch_amount": actual_amount, "externalRefId" : external_ref_Id,
                                       "agent_id":agent_id, "balance":balance_amount}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Card Payment is not successfull")



            except Exception as e:
                msg = "Digital Top up has been failed for an Agent" + GlobalConstants.AGENT_USER
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
                logger.debug(f"Agent Balance before Top Up : {agent_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount}")

                expectedDBValues = {"Agent balance": (agent_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_posting = float(result["balance"].iloc[0])
                actualDBValues = {"Agent balance": bal_after_posting}
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
def test_common_200_203_007():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Cash_collection_Fetch_passbook_statement
        Sub Feature Description: API to perform a Cash payment as a BILLPAY and fetch passbook statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Cash_Collection', request_body={"username": GlobalConstants.AGENT_USER,
                                                                                       "password": GlobalConstants.AGENT_PASSWORD})
            response = APIProcessor.send_request(api_details)

            original_amount_cashpay = float(api_details["RequestBody"]["amount"])
            cash_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            status = response['status']
            settlement_status = response['settlementStatus']
            clw_status = response['clwStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Cash Payment - BILLPAY: {cash_payment_success}, {original_amount_cashpay}, {username}, {amount},{settlement_status}, {clw_status}, {txn_id}, {status}, {account_label}")

            GlobalVariables.cash_txn_id = txn_id
            GlobalVariables.collection_amt += original_amount_cashpay
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
                expectedAPIValues = {"success": True, "username": GlobalConstants.AGENT_USER, "cashpay_amount": original_amount_cashpay, "status":"AUTHORIZED",
                                     "settlementStatus":"SETTLED","accountLabel": "BILLPAY","clwStatus": "SUCCESS",
                                     "transaction_status": "SUCCESS", "transferMode": "PAYMENT",
                                     "fetch_amount": amount, "externalRefId": txn_id,
                                     "agent_id":GlobalConstants.AGENT_USER, "balance":agent_balance_before - original_amount_cashpay}
                if cash_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.AGENT_USER,
                                                                        "password": GlobalConstants.AGENT_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statment_success, "username": username, "cashpay_amount": amount, "status":status,
                                     "settlementStatus":settlement_status,"accountLabel": account_label,"clwStatus": clw_status,
                                     "transaction_status": txn_status, "transferMode": transfer_mode,
                                     "fetch_amount": actual_amount, "externalRefId": external_ref_Id,
                                     "agent_id":agent_id, "balance":balance_amount}
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
                logger.debug(f"Actual amount for BILLPAY  : {original_amount_cashpay}")

                expectedDBValues = {"Agent_balance": agent_balance_before - original_amount_cashpay,
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

                actualDBValues = {"Agent_balance": agentbal_after_cash_payment,
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
def test_common_200_203_008():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Refund_Cash_collected_fetch_passbook_statement
        Sub Feature Description: API to perform a Refund txn for the cash collected as a BILLPAY and fetch the passbook statement
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
                                                   config_log=False)

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
                                                                    "originalTransactionId": GlobalVariables.cash_txn_id})
            response = APIProcessor.send_request(api_details)

            original_amount_refunded = float(api_details["RequestBody"]["amount"])
            refund_payment_success = response['success']
            username = response['username']
            amount = float(response['amount'])
            txn_id = response['txnId']
            txn_type = response['txnType']
            status = response['status']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{txn_type},{original_amount_refunded}, {username}, {amount},{settlement_status}, {txn_id}, {status}, {account_label}")


            GlobalVariables.refund_amt += original_amount_refunded
            GlobalVariables.refund_count += 1
            GlobalVariables.collection_amt -= original_amount_refunded
            GlobalVariables.collection_count -= 1

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
                expectedAPIValues = {"success": True, "username": GlobalConstants.AGENT_USER,
                                     "cashpay_amount": original_amount_refunded, "status": "REFUNDED",
                                     "settlementStatus": "SETTLED", "accountLabel": "BILLPAY",
                                     "transaction_status": "SUCCESS", "transferMode": "REFUND",
                                     "fetch_amount": amount, "externalRefId": GlobalVariables.cash_txn_id,
                                     "agent_id": GlobalConstants.AGENT_USER,
                                     "balance": agent_balance_before + original_amount_refunded}
                if refund_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                              request_body={"username": GlobalConstants.AGENT_USER,
                                                                            "password": GlobalConstants.AGENT_PASSWORD,
                                                                            "startDate": str(date.today()),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statment_success, "username": username,
                                       "cashpay_amount": amount, "status": status,
                                       "settlementStatus": settlement_status, "accountLabel": account_label,
                                       "transaction_status": txn_status, "transferMode": transfer_mode,
                                       "fetch_amount": actual_amount, "externalRefId": external_ref_Id,
                                       "agent_id": agent_id, "balance": balance_amount}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Refund Payment is not successfull")

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

                expectedDBValues = {"Agent_balance": agent_balance_before + original_amount_refunded,
                                    "settlement_balance": settlement_bal_before -  original_amount_refunded}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_bal = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"Agent_balance": agentbal_after_cash_payment,
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
def test_common_200_203_009():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Withdraw_FromAgent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Withdraw transaction from Agent to Agency account and fetch passbook statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

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
                expectedAPIValues = {"success": True, "walletTxnId": wallet_txn_id,
                                     "realCode": "TRANSACTION_SUCCESSFUL", "successCode": "CLOSED_LOOP_000027",
                                     "transferMode": "WITHDRAW",
                                     "creditAccBalance": agency_balance_before + original_withdraw_amt,
                                     "debitAccBalance": agent_balance_before - original_withdraw_amt
                    , "agentID": GlobalConstants.AGENT_USER, "txn_status": "SUCCESS",
                                     "amount_withdraw": original_withdraw_amt,
                                     "bal_after_withdraw": agent_balance_before - original_withdraw_amt}
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
                    actualAPIValues = {"success": fetch_statment_success, "walletTxnId": actual_wallet_txn_id,
                                       "realCode": realcode, "successCode": successcode, "transferMode": transfer_mode,
                                       "creditAccBalance": credit_acc_bal, "debitAccBalance": debit_acc_bal
                                        , "agentID": agent_Id, "txn_status": txn_status, "amount_withdraw": amount_withdraw,
                                       "bal_after_withdraw": bal_after_withdraw}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Withdraw from Agent Failed")

            except Exception as e:
                msg = "WIthdraw has been failed" + GlobalConstants.AGENT_USER
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
                logger.debug(f"Agent Balance before Withdraw : {agent_balance_before}")
                logger.debug(f"Actual amount for Withdraw  : {original_withdraw_amt}")

                expectedDBValues = {"Agent balance": (agent_balance_before - original_withdraw_amt)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agent_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"Agent balance": agent_bal_after}
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
def test_common_200_203_010():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Multiple_transactions_Fetch_passbook_statement_Agent
        Sub Feature Description: API to perform an Agent Top Up, Cash Payment-BILLPAY, Refund transaction, Withdraw and fetch passbook statement
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

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
        balance = DBProcessor.getValueFromDB(settlement_bal_check, "closedloop")
        settlement_bal_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            original_amount_card = random.randint(100, 1000)
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card',
                                                      request_body={"username": GlobalConstants.AGENT_USER,
                                                                    "password": GlobalConstants.AGENT_PASSWORD,
                                                                    "amount": original_amount_card,
                                                                    "externalRefNumber": "UFAZMJK1ON071341J1" + str(
                                                                        random.randint(0, 9))})
            response = APIProcessor.send_request(api_details)

            card_payment_success = response['success']
            card_pay_amount = float(response['amount'])
            card_txn_id = response['txnId']
            card_status = response['status']
            card_account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agency Top Up: {card_payment_success}, {card_pay_amount}, {card_txn_id}, {card_status}, {card_account_label}")
            GlobalVariables.selftopup_amt += original_amount_card
            GlobalVariables.selftopup_count += 1

            if card_payment_success == True:
                time.sleep(3)
                api_details = DBProcessor.get_api_details('Cash_Collection',
                                                          request_body={"username": GlobalConstants.AGENT_USER,
                                                                        "password": GlobalConstants.AGENT_PASSWORD})
                response = APIProcessor.send_request(api_details)

                original_amount_cashpay = float(api_details["RequestBody"]["amount"])
                cash_payment_success = response['success']
                cash_username = response['username']
                cash_pay_amount = float(response['amount'])
                cash_txn_id = response['txnId']
                cash_status = response['status']
                cash_settlement_status = response['settlementStatus']
                clw_status = response['clwStatus']
                cash_account_label = response['accountLabel']
                logger.info(f"API Result: Fetch Response of Cash Payment - BILLPAY: {cash_payment_success}, {original_amount_cashpay}, {cash_username}, {cash_pay_amount},{cash_settlement_status}, {clw_status}, {cash_txn_id}, {cash_status}, {cash_account_label}")
                GlobalVariables.collection_amt += original_amount_cashpay
                GlobalVariables.collection_count += 1

                if cash_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Refund_cash_Payment',
                                                              request_body={"username": GlobalConstants.AGENT_USER,
                                                                            "password": GlobalConstants.AGENT_PASSWORD,
                                                                            "originalTransactionId": cash_txn_id})
                    response = APIProcessor.send_request(api_details)

                    original_amount_refunded = float(api_details["RequestBody"]["amount"])
                    refund_payment_success = response['success']
                    refund_username = response['username']
                    refund_amount = float(response['amount'])
                    refund_txn_id = response['txnId']
                    refund_txn_type = response['txnType']
                    refund_status = response['status']
                    refund_settlement_status = response['settlementStatus']
                    refund_account_label = response['accountLabel']
                    logger.info(f"API Result: Fetch Response of Refund Payment: {refund_payment_success},{refund_txn_type},{original_amount_refunded}, {refund_username}, {refund_amount},{refund_settlement_status}, {refund_txn_id}, {refund_status}, {refund_account_label}")
                    GlobalVariables.refund_amt += original_amount_refunded
                    GlobalVariables.refund_count += 1
                    GlobalVariables.collection_amt -= original_amount_refunded
                    GlobalVariables.collection_count -= 1

                    if refund_payment_success == True:
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
                        GlobalVariables.withdraw_amt += original_withdraw_amt
                        GlobalVariables.withdraw_count += 1

                        if withdraw_pay_success == True:
                            logger.info("Agent Top Up, Cash Payment-BILLPAY and Withdraw from Agent Successfull")
                        else:
                            logger.error("Withdraw from Agent Failed")
                            raise Exception("Withdraw from Agent Failed")
                    else:
<<<<<<< HEAD
                        logger.error("Refund Payment of cash collected Failed")
                        raise Exception("Refund Payment of cash collected Failed")
=======
                        logger.error("Refund Payment of cash colllected Failed")
                        raise Exception("Refund Payment of cash colllected Failed")
>>>>>>> Added Ezewallet related TCS

                else:
                    logger.error("Cash Payment Failed")
                    raise Exception("Cash Payment Failed")

            else:
                logger.error("Digital Agent Top Up Failed")
                raise Exception("Digital Agent Top Up Failed")



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
                expectedAPIValues = {"success": True, "topup_txn_status": "SUCCESS", "topup_transfer_mode":"TRANSFER","topup_amount":original_amount_card,
                                     "external_ref_Id_card":card_txn_id, "bal_after_topup":agent_balance_before+original_amount_card,
                                     "cash_txn_status":"AUTHORIZED_REFUNDED","cash_transfer_mode":"PAYMENT","external_ref_Id_cash":cash_txn_id,
                                     "cash_agent_Id":GlobalConstants.AGENT_USER, "amount_cashpay":original_amount_cashpay,
                                     "bal_after_cashpay":(agent_balance_before+original_amount_card) - original_amount_cashpay,
                                     "refund_txn_status":"SUCCESS","refund_transfer_mode":"REFUND","refund_amount":original_amount_refunded,"refund_agent_id":GlobalConstants.AGENT_USER,
                                     "externalRefId":cash_txn_id,"balance_after_refund":(((agent_balance_before+original_amount_card)-original_amount_cashpay)+original_amount_refunded),
                                     "withdraw_wallet_txn_id":withdraw_wallet_txn_id,
                                     "withdraw_txn_status":"SUCCESS","withdraw_transfer_mode": "WITHDRAW", "withdraw_agent_Id": GlobalConstants.AGENT_USER,
                                     "amount_withdraw" : original_withdraw_amt,
                                     "bal_after_withdraw" : ((((agent_balance_before + original_amount_card) - original_amount_cashpay)+original_amount_refunded) - original_withdraw_amt)
                                     }

                api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": GlobalConstants.AGENT_USER,
                                                                        "password": GlobalConstants.AGENT_PASSWORD,
                                                                        "startDate": str(date.today()),
                                                                        })
                response = APIProcessor.send_request(api_details)


                fetch_statment_success = response['success']
                if fetch_statment_success == True:

                    topup_txn_status = response['response']['elements'][3]['txnStatus']
                    topup_transfer_mode = response['response']['elements'][3]['transferMode']
                    topup_amount = float(response['response']['elements'][3]['amount'])
                    external_ref_Id_card = response['response']['elements'][3]['externalRefId']
                    bal_after_topup = response['response']['elements'][3]['balance']

                    #
                    cash_txn_status = response['response']['elements'][2]['txnStatus']
                    cash_transfer_mode = response['response']['elements'][2]['transferMode']
                    cash_agent_Id = response['response']['elements'][2]['agentId']
                    amount_cashpay = float(response['response']['elements'][2]['amount'])
                    bal_after_cashpay = float(response['response']['elements'][2]['balance'])
                    external_ref_Id_cash = response['response']['elements'][2]['externalRefId']

                    #
                    refund_txn_status = response['response']['elements'][1]['txnStatus']
                    refund_transfer_mode = response['response']['elements'][1]['transferMode']
                    refund_agent_Id = response['response']['elements'][1]['agentId']
                    refund_amt = float(response['response']['elements'][1]['amount'])
                    bal_after_refund = float(response['response']['elements'][1]['balance'])
                    external_ref_Id_refund = response['response']['elements'][1]['externalRefId']

                    #
                    withdraw_wallet_txnid = response['response']['elements'][0]['walletTxnId']
                    withdraw_txn_status = response['response']['elements'][0]['txnStatus']
                    withdraw_transfer_mode = response['response']['elements'][0]['transferMode']
                    withdraw_agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "topup_txn_status": topup_txn_status, "topup_transfer_mode":topup_transfer_mode,"topup_amount":topup_amount,
                                     "external_ref_Id_card":external_ref_Id_card, "bal_after_topup":bal_after_topup,
                                     "cash_txn_status":cash_txn_status,"cash_transfer_mode":cash_transfer_mode,"external_ref_Id_cash":external_ref_Id_cash,
                                     "cash_agent_Id":cash_agent_Id, "amount_cashpay":amount_cashpay,
                                     "bal_after_cashpay":bal_after_cashpay, "refund_txn_status":refund_txn_status,"refund_transfer_mode":refund_transfer_mode,
                                    "refund_amount":refund_amt,"refund_agent_id":refund_agent_Id,
                                     "externalRefId":external_ref_Id_refund,"balance_after_refund":bal_after_refund,
                                    "withdraw_wallet_txn_id":withdraw_wallet_txnid,
                                     "withdraw_txn_status":withdraw_txn_status,"withdraw_transfer_mode": withdraw_transfer_mode, "withdraw_agent_Id": withdraw_agent_Id,
                                     "amount_withdraw" : amount_withdraw,
                                     "bal_after_withdraw" : bal_after_withdraw}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Fetch Agent Statement Failed")

            except Exception as e:
                msg = "API Validation failed"
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
                logger.debug(f"Agent Balance before all transactions : {agent_balance_before}")
                logger.debug(f"Actual amount for Top Up  : {original_amount_card}")
                logger.debug(f"Actual amount for CashPayment-BILLPAY  : {original_amount_cashpay}")
                logger.debug(f"Actual amount for Refund  : {original_amount_refunded}")
                logger.debug(f"Actual amount for Withdraw  : {original_withdraw_amt}")

                expectedDBValues = {"Agent_balance": ((((agent_balance_before + original_amount_card) - original_amount_cashpay)+original_amount_refunded) - original_withdraw_amt)
                                    , "Settlement_Account_Balance": (settlement_bal_before + original_amount_cashpay)- original_amount_refunded}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_agent_acc = "select balance from account where entity_id = '" + GlobalConstants.AGENT_USER + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_acc}")
                result_agent_acc = DBProcessor.getValueFromDB(query_agent_acc, "closedloop")
                logger.debug(f"Query result URL: {result_agent_acc}")
                agent_balance_after = float(result_agent_acc["balance"].iloc[0])

                query_settle_acc = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query_settle_acc}")
                result_settle_acc = DBProcessor.getValueFromDB(query_settle_acc, "closedloop")
                logger.debug(f"Query result URL: {result_settle_acc}")
                settlement_balance_after = float(result_settle_acc["balance"].iloc[0])
                actualDBValues = {"Agent_balance": agent_balance_after, "Settlement_Account_Balance": settlement_balance_after}
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



