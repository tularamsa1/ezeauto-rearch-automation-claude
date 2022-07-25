from datetime import datetime
import pytest
import json
import requests
from termcolor import colored
import shutil
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ReportProcessor, ConfigReader, DBProcessor, APIProcessor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)



@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_011():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_Order_Details
        Sub Feature Description: fetching details of Airtel Merchant having key "get_Order_Details" via fetch/data API
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_Order_Details')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            errorCode = response['data']['response'][0]['errorCode']
            errorMsg = response['data']['response'][0]['errorMsg']
            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success}, {errorCode}, {errorMsg}")

            # ------------------------------------------------------------------------------------------------
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": False, "errorCode": "EZETAP_0000541", "errorMsg": "PLEASE CONTACT CAD AIRTEL TEAM"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "errorCode": errorCode, "errorMsg": errorMsg}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": false, "errorCode": "EZETAP_0000541", "errorMessage": "PLEASE CONTACT CAD AIRTEL TEAM", "data": {"response": [{"errorCode": "EZETAP_0000541", "errorMsg": "PLEASE CONTACT CAD AIRTEL TEAM"}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data.replace("\\", "")}
                logger.debug(f"actualAPIValues: {actualAPIValues2}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/8emaYc/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_Order_Details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))




        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))





@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_012():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_active_mobile
        Sub Feature Description: fetching details of Airtel Merchant having key "get_active_mobile" via fetch/data API
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_active_mobile')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            CAFNumber = response['data']['response'][0]['CAFNumber']
            airtelNo = response['data']['response'][0]['airtelNo']
            amountField = response['data']['response'][0]['_amountField']
            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success}, {CAFNumber}, {airtelNo},{amountField}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "CAFNumber": "D463089156", "airtelNo": "8139886369", "_amountField":"300"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "CAFNumber": CAFNumber, "airtelNo": airtelNo, "_amountField": amountField}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "CAFNumber": "D463089156", "_minAmount": "0.01", "airtelNo": "8139886369", "_amountField": "300", "_maxAmount": "1000000"}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data.replace("\\", "")}
                logger.debug(f"actualAPIValues: {actualAPIValues2}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/jbU5Cg/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_active_mobile') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_302_013():
    """
        Sub Feature Code: NonUI_Common_Config_Airtel_fetch_get_active_landline
        Sub Feature Description: fetching details of Airtel Merchant having key "get_active_landline" via fetch/data API
    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

        GlobalVariables.setupCompletedSuccessfully = True

        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False,config_log=True)

        msg = ""
        GlobalVariables.time_calc.setup.end()
        print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

            api_details = DBProcessor.get_api_details('fetch_get_active_landline')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            CAFNumber = response['data']['response'][0]['CAFNumber']
            amountField = response['data']['response'][0]['_amountField']
            logger.info(f"API Result: Fetch Response for Airtel Merchant : {success}, {CAFNumber},{amountField}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))
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
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        GlobalVariables.time_calc.validation.start()
        print(colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

        # # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "CAFNumber": "d262689839", "_amountField":"300"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "CAFNumber": CAFNumber, "_amountField": amountField}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"msg": "success", "CAFNumber": "d262689839", "_minAmount": "0.01", "_amountField": "300", "_maxAmount": "1000000"}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data.replace("\\", "")}
                logger.debug(f"actualAPIValues: {actualAPIValues2}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/QcZuZJ/application/YyEhtw/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_active_landline') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
                result = DBProcessor.getValueFromDB(query, "config")
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - "+str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result= 'Fail'


        # # -----------------------------------------End of DB Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        print(colored("Validation Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))

    finally:
        if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in finally block (bcz not pausing in previous blocks) of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        GlobalVariables.time_calc.execution.resume()
        print(colored("Execution Timer resumed in finally block of testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='AIRTELULB540943' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query, "config")
            logger.debug(f"Query result URL: {result}")
            if len(result) > 1:
                print("===Result is fetching more than 1 row====")
                logger.error("============Result is fetching more than 1 row================")

        if GlobalVariables.setupCompletedSuccessfully == False:
            print("Test case setup itself failed. So the test case was not executed.")
        else:
            ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # -------------------------------Revert Preconditions done(setup)--------------------------------------------

        # Write the code here to revert the settings that were done as precondition

        # ----------------------------------------------------------------------------------------------------------
        GlobalVariables.time_calc.execution.end()
        print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),'cyan'))