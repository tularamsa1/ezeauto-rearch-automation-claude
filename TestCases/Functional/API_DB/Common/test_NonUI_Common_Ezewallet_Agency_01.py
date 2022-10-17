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
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor, merchant_creator,Ezewallet_processor
from Utilities.execution_log_processor import EzeAutoLogger



logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_200_201_001():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agency
        Sub Feature Description: API to perform a Digital TopUp of an Agency using Card Payment
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
            device_serial = merchant_creator.get_device_serial_of_merchant(org_code=Ezewallet_processor.org_code,acquisition="HDFC",payment_gateway="DUMMY")
            api_details = DBProcessor.get_api_details('Digital_Agency_TopUp_Card', request_body={"deviceSerial":device_serial,"username": Ezewallet_processor.admin_user, "password": Ezewallet_processor.admin_password,
                                                                        "amount": original_amount, "externalRefNumber" : "UFAZMJK1ON071341J1" + str(random.randint(0,9))})
            response = APIProcessor.send_request(api_details)

            card_payment_success = response['success']
            amount = float(response['amount'])
            payment_mode = response['paymentMode']
            txn_id = response['txnId']
            status = response['status']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of Card Payment - Digital Agency Top Up: {card_payment_success}, {amount}, {txn_id}, {status},{settlement_status},{payment_mode}, {account_label}")

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
                if card_payment_success == True:
                    time.sleep(4)
                    expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"AUTHORIZED","settle_status":"PENDING",
                                        "pmt_mode":"CARD", "account_label": "TOPUP", "balance":agency_balance_before+original_amount}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code  + "';"
                    result = DBProcessor.getValueFromDB(query, "closedloop")
                    bal_after_posting = float(result["balance"].iloc[0])

                    actualAPIValues = {"success": card_payment_success, "txn_amt": amount, "pmt_status":status,"settle_status":settlement_status,
                                        "pmt_mode":payment_mode,
                                           "account_label": account_label, "balance":bal_after_posting}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                    if GlobalVariables.str_api_val_result == "Pass":
                        logger.info("Posting is Successfull")
                    else:
                        logger.error("Posting is Unsuccesfull")
                else:
                    raise Exception("Card Payment is not successfull")

            except Exception as e:
                msg = "Digital Top up has been failed for an Agency" + Ezewallet_processor.org_code
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

                expectedDBValues = {"txn_amt":original_amount,"pmt_mode":payment_mode, "settle_status":settlement_status,
                                    "pmt_status":status,
                                    "agency_balance": (agency_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '"+txn_id+"';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_wallet = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_wallet}")
                result_wallet = DBProcessor.getValueFromDB(query_wallet, "closedloop")
                logger.debug(f"Query result URL: {result_wallet}")
                bal_after_posting = float(result_wallet["balance"].iloc[0])


                actualDBValues = {"txn_amt":txn_amt,"pmt_mode":pmt_mode, "settle_status":settle_status,
                                    "pmt_status":pmt_status,"agency_balance": bal_after_posting}
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
def test_common_200_201_002():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_DigitalTopUp_Agency_UPI
        Sub Feature Description: API to perform a Digital TopUp of an Agency using UPI Payment and validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
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
            original_amount = random.randint(200,300)
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('Digital_Agency_TopUp_UPI', request_body={"username": Ezewallet_processor.admin_user,
                                                                                               "password": Ezewallet_processor.admin_password,
                                                                                                "amount": original_amount})
            response = APIProcessor.send_request(api_details)

            upi_payment_success = response['success']
            amount = float(response['amount'])
            txn_id = response['txnId']
            payment_mode = response['paymentMode']
            status = response['status']
            settlement_status = response['settlementStatus']
            account_label = response['accountLabel']
            logger.info(f"API Result: Fetch Response of UPI QR genaration: {upi_payment_success}, {amount}, {txn_id},{payment_mode},{settlement_status}, {status}, {account_label}")

            if upi_payment_success == True:
                time.sleep(2)
                api_details = DBProcessor.get_api_details('Confirm_UPI',
                                                          request_body={"username": Ezewallet_processor.admin_user,
                                                                        "password": Ezewallet_processor.admin_password,
                                                                        "txnId": txn_id})
                response = APIProcessor.send_request(api_details)
                confirm_upi_success = response['success']
                error_code = response['errorCode']
                real_code = response['realCode']
                confirm_amount = response['amount']
                confirm_settlement_status = response['settlementStatus']
                confirm_status = response['status']
                confirm_accountlabel = response['accountLabel']
                confirm_payment_mode = response['paymentMode']
                logger.info(f"API Result: Fetch Response of UPI confirm - Digital Agent Top Up: {confirm_upi_success}, {error_code}, {real_code},{confirm_amount},{confirm_payment_mode},{confirm_status}, {confirm_settlement_status}, {confirm_accountlabel}")

            else:
                logger.error("UPI QR generation is not successfull")

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

                expectedAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":"PENDING",
                                    "settle_status":"PENDING","account_label": "TOPUP","pmt_mode":"UPI",
                                      "confirm_success":False,"error_code":"EZETAP_0000703","real_code":"STOP_PAYMENT_NOT_ALLOWED_FOR_AUTHORIZED_TRANSACTION",
                                     "confirm_amt":original_amount,"confirm_settle_status":"SETTLED", "confirm_pmt_status":"AUTHORIZED",
                                     "confirm_account_label":"TOPUP","confirm_pmt_mode":"UPI","balance":agency_balance_before+original_amount}
                logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                result = DBProcessor.getValueFromDB(query, "closedloop")
                bal_after_posting = float(result["balance"].iloc[0])

                actualAPIValues = {"success": True, "txn_amt": original_amount, "pmt_status":status,
                                    "settle_status":settlement_status,"account_label":account_label,"pmt_mode":payment_mode,
                                      "confirm_success":confirm_upi_success,"error_code":error_code,"real_code":real_code,
                                     "confirm_amt":confirm_amount,"confirm_settle_status":confirm_settlement_status, "confirm_pmt_status":confirm_status,
                                     "confirm_account_label":confirm_accountlabel,"confirm_pmt_mode":confirm_payment_mode,"balance":bal_after_posting}
                logger.debug(f"actualAPIValues: {actualAPIValues}")


                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)

            except Exception as e:
                msg = "Digital Top up has been failed for an Agency" + Ezewallet_processor.org_code
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

                expectedDBValues = {"txn_amt": original_amount, "pmt_mode": confirm_payment_mode,
                                    "settle_status": confirm_settlement_status,
                                    "pmt_status": confirm_status,
                                    "agency_balance": (agency_balance_before + original_amount)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_txn = "select id, amount, payment_mode, settlement_status, status from txn where id = '" + txn_id + "';"
                result_txn = DBProcessor.getValueFromDB(query_txn)
                logger.debug(f"Query result URL: {result_txn}")

                txn_amt = float(result_txn["amount"].iloc[0])
                pmt_mode = result_txn["payment_mode"].iloc[0]
                settle_status = result_txn["settlement_status"].iloc[0]
                pmt_status = result_txn["status"].iloc[0]

                query_wallet = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query_wallet}")
                result_wallet = DBProcessor.getValueFromDB(query_wallet, "closedloop")
                logger.debug(f"Query result URL: {result_wallet}")
                bal_after_posting = float(result_wallet["balance"].iloc[0])

                actualDBValues = {"txn_amt": txn_amt, "pmt_mode": pmt_mode, "settle_status": settle_status,
                                  "pmt_status": pmt_status, "agency_balance": bal_after_posting}
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
def test_common_200_201_003():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Transfer_FromAgency_ToAgent
        Sub Feature Description: API to perform a Transfer transaction from Agency to Agent account and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        agent_bal_check = "select balance from account where entity_id = '" + Ezewallet_processor.agent_user + "';"
        balance = DBProcessor.getValueFromDB(agent_bal_check, "closedloop")
        agent_balance_before = float(balance["balance"].iloc[0])

        agency_bal_check = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code+ "';"
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
            api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent',
                                                      request_body={"username":Ezewallet_processor.admin_user,
                                                                    "password":Ezewallet_processor.admin_password,
                                                                    "agentId": Ezewallet_processor.agent_user})
            original_transfer_amt = float(api_details['RequestBody']['amount'])
            response = APIProcessor.send_request(api_details)
            transfer_pay_success = response['success']
            realcode = response['realCode']
            successcode = response['successCode']
            wallet_txn_id = response['walletTxnId']
            credit_acc_bal = float(response['creditAccBalance'])
            debit_acc_bal = float(response['debitAccBalance'])

            logger.info(f"API Result: Fetch Response of transfer Payment - To Agent: {transfer_pay_success},{wallet_txn_id}, {credit_acc_bal}, {debit_acc_bal}")

            GlobalVariables.transfer_amt += original_transfer_amt
            GlobalVariables.transfer_count += 1

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
                if transfer_pay_success == True:
                    expectedAPIValues = {"success": True,
                                     "real_code": "TRANSACTION_SUCCESSFUL", "success_code": "CLOSED_LOOP_000027",
                                     "credit_acc_balance": agent_balance_before + original_transfer_amt,
                                     "debit_acc_balance": agency_balance_before - original_transfer_amt,
                                     "bal_after_transfer": agency_balance_before - original_transfer_amt}

                    query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                    result = DBProcessor.getValueFromDB(query, "closedloop")
                    agency_bal_after = float(result["balance"].iloc[0])

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")
                    actualAPIValues = {"success": transfer_pay_success,
                                       "real_code": realcode, "success_code": successcode,
                                       "credit_acc_balance": credit_acc_bal, "debit_acc_balance": debit_acc_bal,
                                        "bal_after_transfer": agency_bal_after}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)
                else:
                    raise Exception("Transfer from Agency Failed")

            except Exception as e:
                msg = "Transfer has been failed from " + Ezewallet_processor.org_code
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

                expectedDBValues = {"clw_txn_amt":original_transfer_amt,"clw_merchant_id":Ezewallet_processor.org_code,"clw_transfer_mode":"TRANSFER",
                                    "clw_transfer_status":"SUCCESS","clw_transfer_type":"MANUAL","clw_leg_amt_cr":original_transfer_amt,
                                    "clw_account_entity_type_cr":"AGENT","clw_source_type_cr":"CREDIT","clw_leg_amt_dt":original_transfer_amt,
                                    "clw_account_entity_type_dt":"MERCHANT","clw_source_type_dt":"DEBIT",
                                    "agency_balance": (agency_balance_before - original_transfer_amt)}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query_wallet_txn_db = "select amount, merchant_id, transfer_mode, txn_status, transfer_type from wallet_txn where wallet_txn_id = '" + wallet_txn_id + "';"
                result_wallet_txn_db = DBProcessor.getValueFromDB(query_wallet_txn_db, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_db}")

                clw_txn_amt = float(result_wallet_txn_db['amount'].iloc[0])
                clw_merchant_id =result_wallet_txn_db['merchant_id'].iloc[0]
                clw_transfer_mode =result_wallet_txn_db['transfer_mode'].iloc[0]
                clw_transfer_status =result_wallet_txn_db['txn_status'].iloc[0]
                clw_transfer_type =result_wallet_txn_db['transfer_type'].iloc[0]

                query_wallet_txn_leg_cr = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'CREDIT';"
                result_wallet_txn_leg_cr = DBProcessor.getValueFromDB(query_wallet_txn_leg_cr, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_cr}")

                clw_leg_amt_cr = float(result_wallet_txn_leg_cr['amount'].iloc[0])
                clw_account_entity_type_cr = result_wallet_txn_leg_cr['account_entity_type'].iloc[0]
                clw_source_type_cr =result_wallet_txn_leg_cr['source_type'].iloc[0]

                query_wallet_txn_leg_dt = "select amount, account_entity_type, source_type from wallet_txn_leg where wallet_txn_id = '" + wallet_txn_id + "' and source_type = 'DEBIT';"
                result_wallet_txn_leg_dt = DBProcessor.getValueFromDB(query_wallet_txn_leg_dt, "closedloop")
                logger.debug(f"Query result URL: {result_wallet_txn_leg_dt}")

                clw_leg_amt_dt = float(result_wallet_txn_leg_dt['amount'].iloc[0])
                clw_account_entity_type_dt = result_wallet_txn_leg_dt['account_entity_type'].iloc[0]
                clw_source_type_dt = result_wallet_txn_leg_dt['source_type'].iloc[0]

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"clw_txn_amt":clw_txn_amt,"clw_merchant_id":clw_merchant_id,"clw_transfer_mode":clw_transfer_mode,
                                    "clw_transfer_status":clw_transfer_status,"clw_transfer_type":clw_transfer_type,
                                  "clw_leg_amt_cr": clw_leg_amt_cr,
                                  "clw_account_entity_type_cr": clw_account_entity_type_cr, "clw_source_type_cr": clw_source_type_cr,
                                  "clw_leg_amt_dt": clw_leg_amt_dt,
                                  "clw_account_entity_type_dt": clw_account_entity_type_dt, "clw_source_type_dt": clw_source_type_dt,
                                  "agency_balance": agency_bal_after}
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
def test_common_200_201_004():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Transfer_FromAgency_ToAgent_MoreThan_Balance
        Sub Feature Description: API to perform a Transfer transaction from Agency to Agent account where amount is more than a balance
        and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

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
            api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent',
                                                      request_body={"username": Ezewallet_processor.admin_user,
                                                                    "password":Ezewallet_processor.admin_password,
                                                                    "agentId": Ezewallet_processor.agent_user})
            original_transfer_amt = float(api_details['RequestBody']['amount'])
            api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent',
                                                      request_body={"username": Ezewallet_processor.admin_user,
                                                                    "password":Ezewallet_processor.admin_password,
                                                                    "agentId": Ezewallet_processor.agent_user,
                                                                    "amount": agency_balance_before + (original_transfer_amt+1)})
            response = APIProcessor.send_request(api_details)
            transfer_pay_success = response['success']
            error_message = response['errorMessage']

            logger.info(f"API Result: Fetch Response of transfer Payment - To Agent: {transfer_pay_success},{error_message}")

            GlobalVariables.transfer_amt += original_transfer_amt
            GlobalVariables.transfer_count += 1

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
                                     "error_message": "Insufficient funds for ' MERCHANT " + Ezewallet_processor.org_code+ "'"}

                    logger.debug(f"expectedAPIValues: {expectedAPIValues}")

                    actualAPIValues = {"success": transfer_pay_success,
                                     "error_message": error_message}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)


            except Exception as e:
                msg = "Transfer has been failed from " + Ezewallet_processor.org_code
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

                expectedDBValues = {"agency_balance": agency_balance_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"agency_balance": agency_bal_after}
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
def test_common_200_201_005():
    """
        Sub Feature Code: NonUI_Common_Ezewallet_Transfer_FromAgency_ToAgent_Zero_Amount
        Sub Feature Description: API to perform a Transfer transaction from Agency to Agent account where amount is zero
        and Validate the same
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

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
            api_details = DBProcessor.get_api_details('Transfer_Agency_To_Agent',
                                                      request_body={"username":Ezewallet_processor.admin_user,
                                                                    "password":Ezewallet_processor.admin_password,
                                                                    "agentId": Ezewallet_processor.agent_user,
                                                                    "amount": agency_balance_before - agency_balance_before})
            original_transfer_amt = float(api_details['RequestBody']['amount'])

            response = APIProcessor.send_request(api_details)
            transfer_pay_success = response['success']
            error_message = response['errorMessage']

            logger.info(f"API Result: Fetch Response of transfer Payment - To Agent: {transfer_pay_success},{error_message}")

            GlobalVariables.transfer_amt += original_transfer_amt
            GlobalVariables.transfer_count += 1

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

                    actualAPIValues = {"success": transfer_pay_success,
                                     "error_message": error_message}
                    logger.debug(f"actualAPIValues: {actualAPIValues}")


                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues, actualAPI=actualAPIValues)


            except Exception as e:
                msg = "Transfer has been failed from " + Ezewallet_processor.org_code
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
                logger.debug(f"Actual amount for Transfer  : {agency_balance_before - agency_balance_before}")

                expectedDBValues = {"agency_balance": agency_balance_before}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select balance from account where account_type = 'LEDGER_ACCOUNT' and entity_id = '" + Ezewallet_processor.org_code + "';"
                logger.debug(f"Query to fetch data from account table : {query}")
                result = DBProcessor.getValueFromDB(query, "closedloop")
                logger.debug(f"Query result URL: {result}")
                agency_bal_after = float(result["balance"].iloc[0])
                actualDBValues = {"agency_balance": agency_bal_after}
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



