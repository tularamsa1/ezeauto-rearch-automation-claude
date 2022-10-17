import random
import shutil
import time
from datetime import datetime, date
import pytest
import sys
from termcolor import colored

from Configuration import Configuration
from DataProvider import GlobalVariables, GlobalConstants
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, merchant_creator, \
    Ezewallet_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_203_011():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Digital TopUp of an Agent using Card Payment and fetch Passbook statement of an Agent
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        GlobalVariables.setupCompletedSuccessfully = True


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            original_amount = random.randint(100,1000)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=Ezewallet_processor.org_code,acquisition="HDFC",payment_gateway="DUMMY")
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card', request_body={"deviceSerial":device_serial,"username": Ezewallet_processor.agent_user, "password": Ezewallet_processor.agent_password,
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
                expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"AUTHORIZED",
                                     "account_label": "TOPUP","txn_status": "SUCCESS", "transfer_mode": "TRANSFER","merchant_id":Ezewallet_processor.org_code,
                                     "fetch_amt": amount, "external_ref_id": txn_id,
                                     "agent_id":Ezewallet_processor.agent_user, "balance":agent_balance_before+original_amount}
                if card_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": Ezewallet_processor.agent_user,
                                                                        "password": Ezewallet_processor.agent_password,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statement_success = response['success']
                    wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    merchant_id = response['response']['elements'][0]['merchantId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statement_success, "txn_amt": amount, "pmt_status":status,
                                       "account_label": account_label, "txn_status": txn_status,
                                       "transfer_mode": transfer_mode ,"merchant_id":merchant_id,"fetch_amt": actual_amount, "external_ref_id" : external_ref_Id,
                                       "agent_id":agent_id, "balance":balance_amount}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Card Payment is not successfull")



            except Exception as e:
                msg = "Digital Top up has been failed for an Agent" + Ezewallet_processor.agent_user
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

                expectedDBValues = {"clw_txn_amt":original_amount,"clw_merchant_id":Ezewallet_processor.org_code,"clw_transfer_mode":"TRANSFER",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"DIGITAL","clw_leg_amt_cr":original_amount,
                                    "clw_account_entity_type_cr":"AGENT","clw_source_type_cr":"CREDIT","clw_leg_amt_dt":original_amount,
                                    "clw_account_entity_type_dt":"MERCHANT","clw_source_type_dt":"DEBIT","agent_balance": (agent_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agent_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,
                                  "agent_balance": agent_bal_after}
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
def test_common_200_203_012():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Cash_collection_Fetch_passbook_statement
        Sub Feature Description: API to perform a Cash payment as a BILLPAY and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
            api_details = DBProcessor.get_api_details('Cash_Collection', request_body={"username": Ezewallet_processor.agent_user,
                                                                                       "password": Ezewallet_processor.agent_password})
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
                expectedAPIValues = {"success": True, "username": Ezewallet_processor.agent_user, "txn_amt": original_amount_cashpay, "pmt_status":"AUTHORIZED",
                                     "settle_status":"SETTLED","account_label": "BILLPAY","clw_status": "SUCCESS",
                                     "txn_status": "SUCCESS", "transfer_mode": "PAYMENT","merchant_id":Ezewallet_processor.org_code,
                                     "fetch_amt": amount, "external_ref_id": txn_id,
                                     "agent_id":Ezewallet_processor.agent_user, "balance":agent_balance_before - original_amount_cashpay}
                if cash_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": Ezewallet_processor.agent_user,
                                                                        "password": Ezewallet_processor.agent_password,
                                                                        "startDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    merchant_id = response['response']['elements'][0]['merchantId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statment_success, "username": username, "txn_amt": amount, "pmt_status":status,
                                     "settle_status":settlement_status,"account_label": account_label,"clw_status": clw_status,
                                     "txn_status": txn_status, "transfer_mode": transfer_mode,"merchant_id":merchant_id,
                                     "fetch_amt": actual_amount, "external_ref_id": external_ref_Id,
                                     "agent_id":agent_id, "balance":balance_amount}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Cash Payment is not successfull")

            except Exception as e:
                msg = "Cash Payment has been failed" + Ezewallet_processor.agent_user
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

                expectedDBValues = {"clw_txn_amt":original_amount_cashpay,"clw_merchant_id":Ezewallet_processor.org_code,"clw_transfer_mode":"PAYMENT",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"DIGITAL","clw_leg_amt_cr":original_amount_cashpay,
                                    "clw_account_entity_type_cr":"MERCHANT","clw_source_type_cr":"CREDIT","clw_leg_amt_dt":original_amount_cashpay,
                                    "clw_account_entity_type_dt":"AGENT","clw_source_type_dt":"DEBIT","agent_balance": agent_balance_before - original_amount_cashpay,
                                    "settlement_balance": settlement_bal_before + original_amount_cashpay}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_cash_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_cash_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,
                                  "agent_balance": agentbal_after_cash_payment,
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
def test_common_200_203_013():
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

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
                                                      request_body={"username": Ezewallet_processor.agent_user,
                                                                    "password": Ezewallet_processor.agent_password,
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
                expectedAPIValues = {"success": True, "username": Ezewallet_processor.agent_user,
                                     "txn_amt": original_amount_refunded, "pmt_status": "REFUNDED",
                                     "settle_status": "SETTLED", "account_label": "BILLPAY",
                                     "txn_status": "SUCCESS", "transfer_mode": "REFUND","merchant_id":Ezewallet_processor.org_code,
                                     "fetch_amt": amount, "external_ref_id": GlobalVariables.cash_txn_id,
                                     "agent_id": Ezewallet_processor.agent_user,
                                     "balance": agent_balance_before + original_amount_refunded}
                if refund_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                              request_body={"username": Ezewallet_processor.agent_user,
                                                                            "password": Ezewallet_processor.agent_password,
                                                                            "startDate": str(date.today()),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    merchant_id = response['response']['elements'][0]['merchantId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    agent_id = response['response']['elements'][0]['agentId']
                    balance_amount = float(response['response']['elements'][0]['balance'])
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": fetch_statment_success, "username": username,
                                       "txn_amt": amount, "pmt_status": status,
                                       "settle_status": settlement_status, "account_label": account_label,
                                       "txn_status": txn_status, "transfer_mode": transfer_mode,"merchant_id":merchant_id,
                                       "fetch_amt": actual_amount, "external_ref_id": external_ref_Id,
                                       "agent_id": agent_id, "balance": balance_amount}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Refund Payment is not successfull")

            except Exception as e:
                msg = "Refund Payment has been failed" + Ezewallet_processor.agent_user
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

                expectedDBValues = {"clw_txn_amt":original_amount_refunded,"clw_merchant_id":Ezewallet_processor.org_code,"clw_transfer_mode":"REFUND",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"DIGITAL","clw_leg_amt_cr":original_amount_refunded,
                                    "clw_account_entity_type_cr":"AGENT","clw_source_type_cr":"CREDIT","clw_leg_amt_dt":original_amount_refunded,
                                    "clw_account_entity_type_dt":"MERCHANT","clw_source_type_dt":"DEBIT","agent_balance": agent_balance_before + original_amount_refunded,
                                    "settlement_balance": settlement_bal_before -  original_amount_refunded}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query_agent_bal = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
                query_settlement_bal = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_bal}, {query_settlement_bal}")
                result_agent_bal = DBProcessor.getValueFromDB(query_agent_bal, "closedloop")
                result_settlement_bal = DBProcessor.getValueFromDB(query_settlement_bal, "closedloop")
                logger.debug(f"Query result URL: {result_agent_bal}, {result_settlement_bal}")
                agentbal_after_refund_payment = float(result_agent_bal["balance"].iloc[0])
                settlementbal_after_refund_payment = float(result_settlement_bal["balance"].iloc[0])

                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,
                                  "agent_balance": agentbal_after_refund_payment,
                                  "settlement_balance": settlementbal_after_refund_payment}
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
def test_common_200_203_014():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Withdraw_FromAgent_Fetch_passbook_statement
        Sub Feature Description: API to perform a Withdraw transaction from Agent to Agency account and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
                                                      request_body={"username": Ezewallet_processor.admin_user,
                                                                    "password": Ezewallet_processor.admin_password,
                                                                    "agentId": Ezewallet_processor.agent_user})
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
                expectedAPIValues = {"success": True, "wallet_txn_id": wallet_txn_id,
                                     "real_code": "TRANSACTION_SUCCESSFUL", "success_code": "CLOSED_LOOP_000027",
                                     "transfer_mode": "WITHDRAW","merchant_id":Ezewallet_processor.org_code,
                                     "credit_acc_balance": agency_balance_before + original_withdraw_amt,
                                     "debit_acc_balance": agent_balance_before - original_withdraw_amt
                    , "agent_id": Ezewallet_processor.agent_user, "txn_status": "SUCCESS",
                                     "amt_withdraw": original_withdraw_amt,
                                     "bal_after_withdraw": agent_balance_before - original_withdraw_amt}
                if withdraw_pay_success == True:
                    api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                              request_body={"username": Ezewallet_processor.admin_user,
                                                                            "password": Ezewallet_processor.admin_password,
                                                                            "startDate": str(date.today()),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    actual_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    merchant_id = response['response']['elements'][0]['merchantId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "wallet_txn_id": actual_wallet_txn_id,
                                       "real_code": realcode, "success_code": successcode, "transfer_mode": transfer_mode,"merchant_id":merchant_id,
                                       "credit_acc_balance": credit_acc_bal, "debit_acc_balance": debit_acc_bal
                                        , "agent_id": agent_Id, "txn_status": txn_status, "amt_withdraw": amount_withdraw,
                                       "bal_after_withdraw": bal_after_withdraw}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Withdraw from Agent Failed")

            except Exception as e:
                msg = "WIthdraw has been failed" + Ezewallet_processor.agent_user
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

                expectedDBValues = {"clw_txn_amt":original_withdraw_amt,"clw_merchant_id":Ezewallet_processor.org_code,"clw_transfer_mode":"WITHDRAW",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"MANUAL","clw_leg_amt_cr":original_withdraw_amt,
                                    "clw_account_entity_type_cr":"MERCHANT","clw_source_type_cr":"CREDIT","clw_leg_amt_dt":original_withdraw_amt,
                                    "clw_account_entity_type_dt":"AGENT","clw_source_type_dt":"DEBIT","agent_balance": (agent_balance_before - original_withdraw_amt)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + actual_wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + actual_wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + actual_wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agent_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,
                                  "agent_balance": agent_bal_after}
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
def test_common_200_203_015():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Multiple_transactions_Fetch_passbook_statement_Agent
        Sub Feature Description: API to perform an Agent Top Up, Cash Payment-BILLPAY, Refund transaction, Withdraw and fetch passbook statement
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
        result = DBProcessor.getValueFromDB(agency_bal_check, "closedloop")
        agency_balance_before = float(result["balance"].iloc[0])

        agent_balance_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        result = DBProcessor.getValueFromDB(agent_balance_check, "closedloop")
        agent_balance_before = float(result["balance"].values[0])

        settlement_bal_check = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
            original_amount_card = random.randint(100, 1000)
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=Ezewallet_processor.org_code,acquisition="HDFC",payment_gateway="DUMMY")
            api_details = DBProcessor.get_api_details('Digital_Agent_TopUp_Card',
                                                      request_body={"deviceSerial":device_serial,"username": Ezewallet_processor.agent_user,
                                                                    "password": Ezewallet_processor.agent_password,
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
                                                          request_body={"username": Ezewallet_processor.agent_user,
                                                                        "password": Ezewallet_processor.agent_password})
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
                                                              request_body={"username": Ezewallet_processor.agent_user,
                                                                            "password": Ezewallet_processor.agent_password,
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
                                                              request_body={"username": Ezewallet_processor.admin_user,
                                                                            "password": Ezewallet_processor.admin_password,
                                                                            "agentId": Ezewallet_processor.agent_user})
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
                        logger.error("Refund Payment of cash collected Failed")
                        raise Exception("Refund Payment of cash collected Failed")

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
                expectedAPIValues = {"success": True, "topup_txn_status": "SUCCESS", "topup_transfer_mode":"TRANSFER","topup_txn_amt":original_amount_card,
                                     "external_ref_id_card":card_txn_id, "bal_after_topup":agent_balance_before+original_amount_card,
                                     "cash_txn_status":"AUTHORIZED_REFUNDED","cash_transfer_mode":"PAYMENT","external_ref_id_cash":cash_txn_id,
                                     "cash_agent_id":Ezewallet_processor.agent_user, "cash_txn_amt":original_amount_cashpay,
                                     "bal_after_cashpay":(agent_balance_before+original_amount_card) - original_amount_cashpay,
                                     "refund_txn_status":"SUCCESS","refund_transfer_mode":"REFUND","refund_txn_amt":original_amount_refunded,"refund_agent_id":Ezewallet_processor.agent_user,
                                     "external_ref_id":cash_txn_id,"balance_after_refund":(((agent_balance_before+original_amount_card)-original_amount_cashpay)+original_amount_refunded),
                                     "withdraw_wallet_txn_id":withdraw_wallet_txn_id,
                                     "withdraw_txn_status":"SUCCESS","withdraw_transfer_mode": "WITHDRAW", "withdraw_agent_Id": Ezewallet_processor.agent_user,
                                     "withdraw_txn_amt" : original_withdraw_amt,
                                     "bal_after_withdraw" : ((((agent_balance_before + original_amount_card) - original_amount_cashpay)+original_amount_refunded) - original_withdraw_amt)
                                     }

                api_details = DBProcessor.get_api_details('Fetch_Passbook_Statement',
                                                          request_body={"username": Ezewallet_processor.agent_user,
                                                                        "password": Ezewallet_processor.agent_password,
                                                                        "startDate": str(date.today()),
                                                                        })
                response = APIProcessor.send_request(api_details)


                fetch_statment_success = response['success']
                if fetch_statment_success == True:

                    topup_txn_status = response['response']['elements'][3]['txnStatus']
                    topup_clw_txn_id = response['response']['elements'][3]['walletTxnId']
                    topup_transfer_mode = response['response']['elements'][3]['transferMode']
                    topup_amount = float(response['response']['elements'][3]['amount'])
                    external_ref_Id_card = response['response']['elements'][3]['externalRefId']
                    bal_after_topup = response['response']['elements'][3]['balance']

                    #
                    cash_txn_status = response['response']['elements'][2]['txnStatus']
                    cash_clw_txn_id = response['response']['elements'][2]['walletTxnId']
                    cash_transfer_mode = response['response']['elements'][2]['transferMode']
                    cash_agent_Id = response['response']['elements'][2]['agentId']
                    amount_cashpay = float(response['response']['elements'][2]['amount'])
                    bal_after_cashpay = float(response['response']['elements'][2]['balance'])
                    external_ref_Id_cash = response['response']['elements'][2]['externalRefId']

                    #
                    refund_txn_status = response['response']['elements'][1]['txnStatus']
                    refund_clw_txn_id = response['response']['elements'][1]['walletTxnId']
                    refund_transfer_mode = response['response']['elements'][1]['transferMode']
                    refund_agent_Id = response['response']['elements'][1]['agentId']
                    refund_amt = float(response['response']['elements'][1]['amount'])
                    bal_after_refund = float(response['response']['elements'][1]['balance'])
                    external_ref_Id_refund = response['response']['elements'][1]['externalRefId']

                    #
                    withdraw_clw_txn_id = response['response']['elements'][0]['walletTxnId']
                    withdraw_txn_status = response['response']['elements'][0]['txnStatus']
                    withdraw_transfer_mode = response['response']['elements'][0]['transferMode']
                    withdraw_agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "topup_txn_status": topup_txn_status, "topup_transfer_mode":topup_transfer_mode,"topup_txn_amt":topup_amount,
                                     "external_ref_id_card":external_ref_Id_card, "bal_after_topup":bal_after_topup,
                                     "cash_txn_status":cash_txn_status,"cash_transfer_mode":cash_transfer_mode,"external_ref_id_cash":external_ref_Id_cash,
                                     "cash_agent_id":cash_agent_Id, "cash_txn_amt":amount_cashpay,
                                     "bal_after_cashpay":bal_after_cashpay, "refund_txn_status":refund_txn_status,"refund_transfer_mode":refund_transfer_mode,
                                    "refund_txn_amt":refund_amt,"refund_agent_id":refund_agent_Id,
                                     "external_ref_id":external_ref_Id_refund,"balance_after_refund":bal_after_refund,
                                    "withdraw_wallet_txn_id":withdraw_clw_txn_id,
                                     "withdraw_txn_status":withdraw_txn_status,"withdraw_transfer_mode": withdraw_transfer_mode, "withdraw_agent_Id": withdraw_agent_Id,
                                     "withdraw_txn_amt" : amount_withdraw,
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

                expectedDBValues = {"clw_topup_txn_amt":original_amount_card,"clw_topup_merchant_id":Ezewallet_processor.org_code,"clw_topup_transfer_mode":"TRANSFER",
                                    "clw_topup_transfer_status":"SUCCESS","clw_topup_transfer_type":"DIGITAL","clw_topup_leg_amt_cr":original_amount_card,
                                    "clw_topup_account_entity_type_cr":"AGENT","clw_topup_source_type_cr":"CREDIT","clw_topup_leg_amt_dt":original_amount_card,
                                    "clw_topup_account_entity_type_dt":"MERCHANT","clw_topup_source_type_dt":"DEBIT","clw_cash_txn_amt":original_amount_cashpay,
                                    "clw_cash_merchant_id":Ezewallet_processor.org_code,"clw_cash_transfer_mode":"PAYMENT",
                                    "clw_cash_transfer_status":"AUTHORIZED_REFUNDED","clw_cash_transfer_type":"DIGITAL","clw_cash_leg_amt_cr":original_amount_cashpay,
                                    "clw_cash_account_entity_type_cr":"MERCHANT","clw_cash_source_type_cr":"CREDIT","clw_cash_leg_amt_dt":original_amount_cashpay,
                                    "clw_cash_account_entity_type_dt":"AGENT","clw_cash_source_type_dt":"DEBIT","clw_refund_txn_amt":original_amount_refunded,
                                    "clw_refund_merchant_id":Ezewallet_processor.org_code,"clw_refund_transfer_mode":"REFUND",
                                    "clw_refund_transfer_status":"SUCCESS","clw_refund_transfer_type":"DIGITAL","clw_refund_leg_amt_cr":original_amount_refunded,
                                    "clw_refund_account_entity_type_cr":"AGENT","clw_refund_source_type_cr":"CREDIT","clw_refund_leg_amt_dt":original_amount_refunded,
                                    "clw_refund_account_entity_type_dt":"MERCHANT","clw_refund_source_type_dt":"DEBIT","clw_withdraw_txn_amt":original_withdraw_amt,
                                    "clw_withdraw_merchant_id":Ezewallet_processor.org_code,"clw_withdraw_transfer_mode":"WITHDRAW",
                                    "clw_withdraw_transfer_status":"SUCCESS","clw_withdraw_transfer_type":"MANUAL","clw_withdraw_leg_amt_cr":original_withdraw_amt,
                                    "clw_withdraw_account_entity_type_cr":"MERCHANT","clw_withdraw_source_type_cr":"CREDIT","clw_withdraw_leg_amt_dt":original_withdraw_amt,
                                    "clw_withdraw_account_entity_type_dt":"AGENT","clw_withdraw_source_type_dt":"DEBIT",
                                    "agent_balance": ((((agent_balance_before + original_amount_card) - original_amount_cashpay)+original_amount_refunded) - original_withdraw_amt)
                                    , "settlement_account_Balance": (settlement_bal_before + original_amount_cashpay)- original_amount_refunded}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + topup_clw_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_topup_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_topup_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_topup_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_topup_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_topup_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + topup_clw_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_topup_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_topup_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_topup_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + topup_clw_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_topup_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_topup_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_topup_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                #
                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + cash_clw_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_cash_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_cash_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_cash_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_cash_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_cash_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + cash_clw_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_cash_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_cash_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_cash_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + cash_clw_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_cash_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_cash_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_cash_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                #
                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + refund_clw_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_refund_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_refund_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_refund_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_refund_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_refund_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + refund_clw_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_refund_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_refund_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_refund_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + refund_clw_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_refund_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_refund_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_refund_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                #
                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + withdraw_clw_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_withdraw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_withdraw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_withdraw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_withdraw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_withdraw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + withdraw_clw_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_withdraw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_withdraw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_withdraw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + withdraw_clw_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_withdraw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_withdraw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_withdraw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                #
                query_agent_acc = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
                logger.debug(f"Query to fetch data from account table : {query_agent_acc}")
                result_agent_acc = DBProcessor.getValueFromDB(query_agent_acc, "closedloop")
                logger.debug(f"Query result URL: {result_agent_acc}")
                agent_balance_after = float(result_agent_acc["balance"].iloc[0])

                query_settle_acc = "select balance from account where account_type = 'COLLECTION_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_settle_acc}")
                result_settle_acc = DBProcessor.getValueFromDB(query_settle_acc, "closedloop")
                logger.debug(f"Query result URL: {result_settle_acc}")
                settlement_balance_after = float(result_settle_acc["balance"].iloc[0])
                actualDBValues = {"clw_topup_txn_amt":clw_topup_txn_amt,"clw_topup_merchant_id":clw_topup_merchant_id,"clw_topup_transfer_mode":clw_topup_transfer_mode,
                                    "clw_topup_transfer_status":clw_topup_transfer_status,"clw_topup_transfer_type":clw_topup_transfer_type,"clw_topup_leg_amt_cr":clw_topup_leg_amt_cr,
                                    "clw_topup_account_entity_type_cr":clw_topup_account_entity_type_cr,"clw_topup_source_type_cr":clw_topup_source_type_cr,"clw_topup_leg_amt_dt":clw_topup_leg_amt_dt,
                                    "clw_topup_account_entity_type_dt":clw_topup_account_entity_type_dt,"clw_topup_source_type_dt":clw_topup_source_type_dt,"clw_cash_txn_amt":clw_cash_txn_amt,
                                    "clw_cash_merchant_id":clw_cash_merchant_id,"clw_cash_transfer_mode":clw_cash_transfer_mode,
                                    "clw_cash_transfer_status":clw_cash_transfer_status,"clw_cash_transfer_type":clw_cash_transfer_type,"clw_cash_leg_amt_cr":clw_cash_leg_amt_cr,
                                    "clw_cash_account_entity_type_cr":clw_cash_account_entity_type_cr,"clw_cash_source_type_cr":clw_cash_source_type_cr,"clw_cash_leg_amt_dt":clw_cash_leg_amt_dt,
                                    "clw_cash_account_entity_type_dt":clw_cash_account_entity_type_dt,"clw_cash_source_type_dt":clw_cash_source_type_dt,"clw_refund_txn_amt":clw_refund_txn_amt,
                                    "clw_refund_merchant_id":clw_refund_merchant_id,"clw_refund_transfer_mode":clw_refund_transfer_mode,
                                    "clw_refund_transfer_status":clw_refund_transfer_status,"clw_refund_transfer_type":clw_refund_transfer_type,"clw_refund_leg_amt_cr":clw_refund_leg_amt_cr,
                                    "clw_refund_account_entity_type_cr":clw_refund_account_entity_type_cr,"clw_refund_source_type_cr":clw_refund_source_type_cr,"clw_refund_leg_amt_dt":clw_refund_leg_amt_dt,
                                    "clw_refund_account_entity_type_dt":clw_refund_account_entity_type_dt,"clw_refund_source_type_dt":clw_refund_source_type_dt,"clw_withdraw_txn_amt":clw_withdraw_txn_amt,
                                    "clw_withdraw_merchant_id":clw_withdraw_merchant_id,"clw_withdraw_transfer_mode":clw_withdraw_transfer_mode,
                                    "clw_withdraw_transfer_status":clw_withdraw_transfer_status,"clw_withdraw_transfer_type":clw_withdraw_transfer_type,"clw_withdraw_leg_amt_cr":clw_withdraw_leg_amt_cr,
                                    "clw_withdraw_account_entity_type_cr":clw_withdraw_account_entity_type_cr,"clw_withdraw_source_type_cr":clw_withdraw_source_type_cr,"clw_withdraw_leg_amt_dt":clw_withdraw_leg_amt_dt,
                                    "clw_withdraw_account_entity_type_dt":clw_withdraw_account_entity_type_dt,"clw_withdraw_source_type_dt":clw_withdraw_source_type_dt,
                                  "agent_balance": agent_balance_after, "settlement_account_Balance": settlement_balance_after}
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



