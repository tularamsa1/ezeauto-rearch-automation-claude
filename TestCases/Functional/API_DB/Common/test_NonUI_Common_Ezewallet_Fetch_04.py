import random
import shutil
import time
from datetime import datetime, date
from datetime import timedelta
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
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agency_Fetch_Merchant_statement
        Sub Feature Description: API to perform a Digital TopUp of Agency using Card Payment and fetch merchant statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

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
                expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"AUTHORIZED",
                                     "account_label": "TOPUP","txn_status": "SUCCESS", "transfer_mode": "ADDFUNDS",
                                     "fetch_amt": amount, "external_ref_id": txn_id, "balance": agency_balance_before + original_amount,
                                     "opening_bal": float(agency_balance_before + original_amount) }
                if card_payment_success == True:
                    time.sleep(3)
                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "viewDate": str(date.today()) ,
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    merchant_statment_success = response['success']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    actual_amount = float(response['response']['elements'][0]['amount'])
                    external_ref_Id = response['response']['elements'][0]['externalRefId']
                    wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    balance_after_topup = response['response']['elements'][0]['balance']
                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                              request_body={"username": GlobalConstants.ADMIN_USER,
                                                                            "password": GlobalConstants.ADMIN_PASSWORD,
                                                                            "viewDate": str(date.today()+ timedelta(days=1)),
                                                                            })

                    response = APIProcessor.send_request(api_details)
                    opening_bal = float(response['response']['openingBalLedger'])

                    actualAPIValues = {"success": merchant_statment_success, "txn_amt": amount, "pmt_status":status,
                                       "account_label": account_label, "txn_status": txn_status, "transfer_mode": transfer_mode ,
                                       "fetch_amt":actual_amount, "external_ref_id" : external_ref_Id, "balance": balance_after_topup,
                                       "opening_bal": opening_bal}
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

                expectedDBValues = {"clw_txn_amt":original_amount,"clw_merchant_id":GlobalConstants.ORG,"clw_transfer_mode":"ADDFUNDS",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"ADMIN_DIGITAL","clw_leg_amt_cr":original_amount,
                                    "clw_account_entity_type_cr":"MERCHANT","clw_source_type_cr":"CREDIT","agency_balance": (agency_balance_before + original_amount) }
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

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_posting = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "agency_balance": bal_after_posting}
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
        Sub Feature Code: NonUI_Common_Ezewallet_TransferAmount_ToAgent_Fetch_merchant_statement
        Sub Feature Description: API to perform a Transfer of an Amount from Agency Account to Agent Account and fetch merchant statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

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
                expectedAPIValues = {"success": True, "wallet_txn_id":wallet_txn_id, "real_code": "TRANSACTION_SUCCESSFUL",
                                     "success_code":"CLOSED_LOOP_000027",
                                     "transfer_mode": "TRANSFER", "credit_acc_balance": agent_balance_before + original_transfer_amt,
                                     "debit_acc_balance": agency_balance_before - original_transfer_amt
                                     , "agent_id" : GlobalConstants.AGENT_USER, "txn_status":"SUCCESS",
                                     "amt_transfered" : original_transfer_amt,
                                     "bal_after_transfer" : agency_balance_before - original_transfer_amt,
                                     "opening_bal": float(agency_balance_before - original_transfer_amt)}
                if transfer_pay_success == True:
                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "viewDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    actual_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    agent_Id = response['response']['elements'][0]['agentId']
                    amount_transfered = float(response['response']['elements'][0]['amount'])
                    bal_after_transfer = float(response['response']['elements'][0]['balance'])

                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                              request_body={"username": GlobalConstants.ADMIN_USER,
                                                                            "password": GlobalConstants.ADMIN_PASSWORD,
                                                                            "viewDate": str(date.today() + timedelta(days=1)),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    opening_bal = float(response['response']['openingBalLedger'])

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "wallet_txn_id": actual_wallet_txn_id,
                                       "real_code":realcode, "success_code": successcode,
                                       "transfer_mode": transfer_mode ,"credit_acc_balance":credit_acc_bal,
                                       "debit_acc_balance" : debit_acc_bal
                                       ,"agent_id" : agent_Id, "txn_status": txn_status, "amt_transfered" : amount_transfered,
                                       "bal_after_transfer": bal_after_transfer,
                                       "opening_bal": opening_bal}
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


                expectedDBValues = {"clw_txn_amt":original_transfer_amt,
                                    "clw_merchant_id":GlobalConstants.ORG,"clw_transfer_mode":"TRANSFER",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"MANUAL",
                                    "clw_leg_amt_cr":original_transfer_amt,
                                    "clw_account_entity_type_cr":"AGENT","clw_source_type_cr":"CREDIT",
                                    "clw_leg_amt_dt":original_transfer_amt,
                                    "clw_account_entity_type_dt":"MERCHANT","clw_source_type_dt":"DEBIT",
                                    "agency_balance": (agency_balance_before - original_transfer_amt) }
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

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,"agency_balance": agency_balance_after}
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
        Sub Feature Code: NonUI_Common_Ezewallet_WithdrawAmount_FromAgent_Fetch_merchant_statement
        Sub Feature Description: API to perform a Withdraw of an Amount from Agent Account to Agency Account and fetch merchant statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

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
                expectedAPIValues = {"success": True, "wallet_txn_id":wallet_txn_id, "real_code": "TRANSACTION_SUCCESSFUL",
                                     "success_code":"CLOSED_LOOP_000027", "transfer_mode": "WITHDRAW",
                                     "credit_acc_balance": agency_balance_before + original_withdraw_amt,
                                     "debit_acc_balance": agent_balance_before - original_withdraw_amt
                                     , "agent_id" : GlobalConstants.AGENT_USER, "txn_status":"SUCCESS",
                                     "amt_withdraw" : original_withdraw_amt,
                                     "bal_after_withdraw" : agency_balance_before + original_withdraw_amt,
                                     "opening_bal": float(agency_balance_before + original_withdraw_amt)}
                if withdraw_pay_success == True:
                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "viewDate": str(date.today()),
                                                                        })
                    response = APIProcessor.send_request(api_details)
                    fetch_statment_success = response['success']
                    actual_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    txn_status = response['response']['elements'][0]['txnStatus']
                    transfer_mode = response['response']['elements'][0]['transferMode']
                    agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])

                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                              request_body={"username": GlobalConstants.ADMIN_USER,
                                                                            "password": GlobalConstants.ADMIN_PASSWORD,
                                                                            "viewDate": str(
                                                                                date.today() + timedelta(days=1)),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    opening_bal = float(response['response']['openingBalLedger'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "wallet_txn_id": actual_wallet_txn_id,
                                       "real_code":realcode, "success_code": successcode,
                                       "transfer_mode": transfer_mode ,"credit_acc_balance":credit_acc_bal,
                                       "debit_acc_balance" : debit_acc_bal
                                       ,"agent_id" : agent_Id, "txn_status": txn_status,
                                       "amt_withdraw" : amount_withdraw, "bal_after_withdraw": bal_after_withdraw,
                                       "opening_bal": opening_bal}
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

                expectedDBValues = {"clw_txn_amt":original_withdraw_amt,
                                    "clw_merchant_id":GlobalConstants.ORG,"clw_transfer_mode":"WITHDRAW",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"MANUAL",
                                    "clw_leg_amt_cr":original_withdraw_amt,
                                    "clw_account_entity_type_cr":"MERCHANT","clw_source_type_cr":"CREDIT",
                                    "clw_leg_amt_dt":original_withdraw_amt,
                                    "clw_account_entity_type_dt":"AGENT","clw_source_type_dt":"DEBIT",
                                    "agency_balance": (agency_balance_before + original_withdraw_amt) }
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

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt": clw_txn_amt, "clw_merchant_id": clw_merchant_id,
                                  "clw_transfer_mode": clw_transfer_mode,
                                  "clw_transfer_status": clw_transfer_status, "clw_transfer_type": clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr,
                                  "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt,
                                  "clw_source_type_dt": clw_source_type_dt,"agency_balance": agency_balance_after}
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
def test_common_200_203_009():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Multiple_transactions_Fetch_merchant_statement
        Sub Feature Description: API to perform a Agency Top Up, Transfer, Withdraw and Validate to Agency Balance and fetch merchant statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

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
                expectedAPIValues = {"success": True, "topup_txn_status": "SUCCESS", "topup_transfer_mode":"ADDFUNDS","topup_txn_amt":original_amount,
                                    "external_ref_id":txn_id, "tf_wallet_txnid":transfer_wallet_txn_id, "tf_txn_status":"SUCCESS",
                                     "tf_transfer_mode":"TRANSFER", "tf_agent_Id":GlobalConstants.AGENT_USER, "tf_txn_amt":original_transfer_amt,
                                     "bal_after_transfer":((agency_balance_before + original_amount) - original_transfer_amt), "wd_wallet_txn_id":withdraw_wallet_txn_id,
                                     "wd_txn_status":"SUCCESS","wd_transfer_mode": "WITHDRAW", "wd_agent_Id": GlobalConstants.AGENT_USER,
                                     "wd_txn_amt" : original_withdraw_amt,
                                     "bal_after_withdraw" : (((agency_balance_before + original_amount)- original_transfer_amt) + original_withdraw_amt),
                                     "opening_bal": float(((agency_balance_before + original_amount) - original_transfer_amt) + original_withdraw_amt)}

                api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                          request_body={"username": GlobalConstants.ADMIN_USER,
                                                                        "password": GlobalConstants.ADMIN_PASSWORD,
                                                                        "viewDate": str(date.today()),
                                                                        })
                response = APIProcessor.send_request(api_details)


                fetch_statment_success = response['success']
                if fetch_statment_success == True:
                    time.sleep(2)

                    topup_txn_status = response['response']['elements'][2]['txnStatus']
                    topup_transfer_mode = response['response']['elements'][2]['transferMode']
                    topup_amount = float(response['response']['elements'][2]['amount'])
                    external_ref_Id = response['response']['elements'][2]['externalRefId']
                    topup_wallet_txn_id = response['response']['elements'][2]['walletTxnId']

                    #
                    trans_wallet_txn_id = response['response']['elements'][1]['walletTxnId']
                    transfer_txn_status = response['response']['elements'][1]['txnStatus']
                    trans_transfer_mode = response['response']['elements'][1]['transferMode']
                    transfer_agent_Id = response['response']['elements'][1]['agentId']
                    amount_transfered = float(response['response']['elements'][1]['amount'])
                    bal_after_transfer = float(response['response']['elements'][1]['balance'])

                    #
                    withdraw_wallet_txn_id = response['response']['elements'][0]['walletTxnId']
                    withdraw_txn_status = response['response']['elements'][0]['txnStatus']
                    withdraw_transfer_mode = response['response']['elements'][0]['transferMode']
                    withdraw_agent_Id = response['response']['elements'][0]['agentId']
                    amount_withdraw = float(response['response']['elements'][0]['amount'])
                    bal_after_withdraw = float(response['response']['elements'][0]['balance'])

                    api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                              request_body={"username": GlobalConstants.ADMIN_USER,
                                                                            "password": GlobalConstants.ADMIN_PASSWORD,
                                                                            "viewDate": str(
                                                                                date.today() + timedelta(days=1)),
                                                                            })
                    response = APIProcessor.send_request(api_details)
                    opening_bal = float(response['response']['openingBalLedger'])


                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": fetch_statment_success, "topup_txn_status": topup_txn_status, "topup_transfer_mode":topup_transfer_mode,"topup_txn_amt":topup_amount,
                                    "external_ref_id":external_ref_Id, "tf_wallet_txnid":trans_wallet_txn_id, "tf_txn_status":transfer_txn_status,
                                     "tf_transfer_mode":trans_transfer_mode, "tf_agent_Id":transfer_agent_Id, "tf_txn_amt":amount_transfered,
                                     "bal_after_transfer":bal_after_transfer, "wd_wallet_txn_id":withdraw_wallet_txn_id,
                                     "wd_txn_status":withdraw_txn_status,"wd_transfer_mode": withdraw_transfer_mode, "wd_agent_Id": withdraw_agent_Id,
                                     "wd_txn_amt" : amount_withdraw,
                                     "bal_after_withdraw" : bal_after_withdraw,"opening_bal":opening_bal}
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

                expectedDBValues = {"clw_topup_txn_amt":original_amount,"clw_topup_merchant_id":GlobalConstants.ORG,"clw_topup_transfer_mode":"ADDFUNDS",
                                    "clw_topup_transfer_status":"SUCCESS","clw_topup_transfer_type":"ADMIN_DIGITAL","clw_topup_leg_amt_cr":original_amount,
                                    "clw_topup_account_entity_type_cr":"MERCHANT","clw_topup_source_type_cr":"CREDIT","clw_tf_txn_amt":original_transfer_amt,
                                    "clw_tf_merchant_id":GlobalConstants.ORG,"clw_tf_transfer_mode":"TRANSFER",
                                    "clw_tf_transfer_status":"SUCCESS","clw_tf_transfer_type":"MANUAL","clw_tf_leg_amt_cr":original_transfer_amt,
                                    "clw_tf_account_entity_type_cr":"AGENT","clw_tf_source_type_cr":"CREDIT","clw_tf_leg_amt_dt":original_transfer_amt,
                                    "clw_tf_account_entity_type_dt":"MERCHANT","clw_tf_source_type_dt":"DEBIT","clw_wd_txn_amt":original_withdraw_amt,
                                    "clw_wd_merchant_id":GlobalConstants.ORG,"clw_wd_transfer_mode":"WITHDRAW",
                                    "clw_wd_transfer_status":"SUCCESS","clw_wd_transfer_type":"MANUAL","clw_wd_leg_amt_cr":original_withdraw_amt,
                                    "clw_wd_account_entity_type_cr":"MERCHANT","clw_wd_source_type_cr":"CREDIT","clw_wd_leg_amt_dt":original_withdraw_amt,
                                    "clw_wd_account_entity_type_dt":"AGENT","clw_wd_source_type_dt":"DEBIT",
                                    "agency_balance": ((agency_balance_before + original_amount + original_withdraw_amt) - original_transfer_amt) }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + topup_wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_topup_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_topup_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_topup_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_topup_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_topup_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + topup_wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_topup_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_topup_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_topup_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                #
                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + trans_wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_trans_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_trans_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_trans_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_trans_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_trans_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + trans_wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_trans_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_trans_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_trans_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + trans_wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_trans_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_trans_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_trans_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                #
                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + withdraw_wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_withdraw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_withdraw_merchant_id = result_wallet_txn_db['merchant_id'].iloc[0]
                clw_withdraw_transfer_mode = result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_withdraw_transfer_status = result_wallet_txn_db['txn_status'].iloc[0]
                clw_withdraw_transfer_type = result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + withdraw_wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_withdraw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_withdraw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_withdraw_source_type_cr = result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + withdraw_wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_withdraw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_withdraw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_withdraw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_balance_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_topup_txn_amt":clw_topup_txn_amt,"clw_topup_merchant_id":clw_topup_merchant_id,"clw_topup_transfer_mode":clw_topup_transfer_mode,
                                    "clw_topup_transfer_status":clw_topup_transfer_status,"clw_topup_transfer_type":clw_topup_transfer_type,"clw_topup_leg_amt_cr":clw_topup_leg_amt_cr,
                                    "clw_topup_account_entity_type_cr":clw_topup_account_entity_type_cr,"clw_topup_source_type_cr":clw_topup_source_type_cr,"clw_tf_txn_amt":clw_trans_txn_amt,
                                    "clw_tf_merchant_id":clw_trans_merchant_id,"clw_tf_transfer_mode":clw_trans_transfer_mode,
                                    "clw_tf_transfer_status":clw_trans_transfer_status,"clw_tf_transfer_type":clw_trans_transfer_type,"clw_tf_leg_amt_cr":clw_trans_leg_amt_cr,
                                    "clw_tf_account_entity_type_cr":clw_trans_account_entity_type_cr,"clw_tf_source_type_cr":clw_trans_source_type_cr,"clw_tf_leg_amt_dt":clw_trans_leg_amt_dt,
                                    "clw_tf_account_entity_type_dt":clw_trans_account_entity_type_dt,"clw_tf_source_type_dt":clw_trans_source_type_dt,"clw_wd_txn_amt":clw_withdraw_txn_amt,
                                    "clw_wd_merchant_id":clw_withdraw_merchant_id,"clw_wd_transfer_mode":clw_withdraw_transfer_mode,
                                    "clw_wd_transfer_status":clw_withdraw_transfer_status,"clw_wd_transfer_type":clw_withdraw_transfer_type,"clw_wd_leg_amt_cr":clw_withdraw_leg_amt_cr,
                                    "clw_wd_account_entity_type_cr":clw_withdraw_account_entity_type_cr,"clw_wd_source_type_cr":clw_withdraw_source_type_cr,"clw_wd_leg_amt_dt":clw_withdraw_leg_amt_dt,
                                    "clw_wd_account_entity_type_dt":clw_withdraw_account_entity_type_dt,"clw_wd_source_type_dt":clw_withdraw_source_type_dt,"agency_balance": agency_balance_after}
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
        Sub Feature Code: NonUI_Common_Ezewallet_fetch_Invalid_Merchant_statement
        Sub Feature Description: API to perform fetch invalid merchant statement
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


        Configuration.configureLogCaptureVariables(apiLog = True, portalLog = False, cnpwareLog = False, middlewareLog = False, config_log= False,closedloop_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Merchant_Statement',
                                                      request_body={"username": "7777770000",
                                                                    "password": GlobalConstants.ADMIN_PASSWORD,
                                                                    "viewDate": str(date.today()),
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

                expectedDBValues = {"agency_balance": agency_balance_before }
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + GlobalConstants.ORG + "';"

                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                bal_after_fetch = float(result["balance"].iloc[0])
                actualDBValues = {"agency_balance": bal_after_fetch}
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