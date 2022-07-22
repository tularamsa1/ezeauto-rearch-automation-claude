from datetime import datetime
import pytest
import json
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
def test_common_300_304_001():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_mp_property_details
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_property_details" via fetch/data API
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
            api_details = DBProcessor.get_api_details('fetch_get_mp_property_details')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['d']['__metadata']['id']
            type = response['data']['response'][0]['d']['__metadata']['type']
            uri = response['data']['response'][0]['d']['__metadata']['uri']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {id}, {type}, {uri}")

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
                expectedAPIValues1 = {"success": True, "id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection('')", "type":"ZPT_DP_SRV.TransactionDetails","uri":"https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection('')"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id, "type":type, "uri":uri}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"d": {"Propid": "", "MobileNo": "", "EmailId": "", "Address": "", "ArrearTax": "0.000", "Message": "No authorization to view given property!!", "Zone": "00", "LaDiscount": "0.000", "TotalPayable": "0.000", "Ulb": "", "MsgType": "E", "CurrentYearTax": "0.000", "LaOpen": "", "Ward": "", "FullName": "", "Penality": "0.000", "AadharCard": "", "__metadata": {"id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection("")", "type": "ZPT_DP_SRV.TransactionDetails", "uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/TransactionDetailsCollection("")"}, "Transid": "", "FatherName": ""}}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data.replace("'", '"')}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/l2ikZo/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_property_details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
                result = DBProcessor.getValueFromDB(query)
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
            query = "select * from ca_usergroup_org_map where org_code='BHOPALMUNICIPALFDC' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query)
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
def test_common_300_304_002():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_BMC_water
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "BMC_water" via fetch/data API
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
            api_details = DBProcessor.get_api_details('fetch_BMC_water')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            ExConnectionNo = response['data']['response'][0]['data']['ExConnectionNo']
            totalTax = response['data']['response'][0]['tax']['totalTax']
            Arrears = response['data']['response'][0]['tax']['Arrears']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {ExConnectionNo}. {Arrears},{totalTax}")

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
                expectedAPIValues1 = {"success": True, "ExConnectionNo": "2000019368", "Arrears":7452, "totalTax":9972}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "ExConnectionNo": ExConnectionNo, "Arrears": Arrears, "totalTax": totalTax}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"data": {"ExName": "???? ???????", "ExFatherName": ".", "ExConnectionNo": "2000019368", "ExZone": "???? ???. 7", "ExColony": "?? ?? ???", "ExWard": "32 - ????? ??? ?????", "ExAddress": "- 228 ?????? ???? ??.??. ???", "ExWaterBillDetails": {"item": [{"FiscalYear": "2019", "Amount": "2484.0"}, {"FiscalYear": "2020", "Amount": "2484.0"}, {"FiscalYear": "2021", "Amount": "2484.0"}, {"FiscalYear": "2022", "Amount": "2520.0"}]}}, "success": True, "txnRef": "220713E1657715913502", "tax": {"totalTax": 9972, "currentTax": 2520, "Arrears": 7452}}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/vhmMW5/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'BMC_water') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
                result = DBProcessor.getValueFromDB(query)
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
            query = "select * from ca_usergroup_org_map where org_code='BHOPALMUNICIPALFDC' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query)
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
def test_common_300_304_003():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_BMC_prop
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "BMC_prop" via fetch/data API
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
            api_details = DBProcessor.get_api_details('fetch_BMC_prop')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            ExPropertyid = response['data']['response'][0]['data']['ExPropertyid']
            totalTax = response['data']['response'][0]['tax']['totalTax']
            Arrears = response['data']['response'][0]['tax']['Arrears']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {ExPropertyid}. {Arrears},{totalTax}")

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
                expectedAPIValues1 = {"success": True, "ExPropertyid": "1000097140", "Arrears":0, "totalTax":4386}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "ExPropertyid": ExPropertyid, "Arrears": Arrears, "totalTax": totalTax}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"data": {"ExName": "???? ???????", "ExDemandDetails": {"item": [{"FiscalYear": "2022", "Amount": "720.0"}, {"FiscalYear": "2022", "Amount": "3666.0"}]}, "ExPropertyid": "1000097140", "ExFatherName": "???.???? ??????", "ExZone": "???? ???. 18", "ExCircle": "?????????? ???. 4", "ExColony": " ?????? ??????? ????? ???", "ExWard": "82 - ????? ???", "ExAddress": "??-402, ?????? ?????,?????"}, "success": True, "txnRef": "220713E1657715913659", "tax": {"totalTax": 4386, "currentTax": 4386, "Arrears": 0}}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/f8Yyjc/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'BMC_prop') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")#change in all TCS
                result = DBProcessor.getValueFromDB(query)
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
            query = "select * from ca_usergroup_org_map where org_code='BHOPALMUNICIPALFDC' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query)
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
def test_common_300_304_004():
        """
                Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_mp_property_update_details
                Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_property_update_details" via fetch/data API
        """
        try:
            GlobalVariables.time_calc.setup.resume()
            print(
                colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))
            # -----------------------------PreConditions(Setup to be done for the test case)--------------------------

            GlobalVariables.setupCompletedSuccessfully = True
            Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False,middlewareLog=False,config_log=True)

            msg = ""
            GlobalVariables.time_calc.setup.end()
            print(colored("Setup Timer ended in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))

            # -----------------------------------------Start of Test Execution-------------------------------------
            try:
                # ------------------------------------------------------------------------------------------------
                GlobalVariables.time_calc.execution.start()
                print(colored(
                    "Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                    'cyan'))
                api_details = DBProcessor.get_api_details('fetch_get_mp_property_update_details')
                response = APIProcessor.send_request(api_details)
                response_data = json.dumps(response)
                success = response['success']
                id = response['data']['response'][0]['d']['__metadata']['id']
                type = response['data']['response'][0]['d']['__metadata']['type']
                uri = response['data']['response'][0]['d']['__metadata']['uri']
                logger.info(
                    f"API Result: Fetch Response for BMC Merchant : {success}, {success}, {id}, {type}, {uri}")

                # ------------------------------------------------------------------------------------------------
                GlobalVariables.EXCEL_TC_Execution = "Pass"
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in try block of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
            except Exception as e:
                if GlobalVariables.time_calc.execution.is_started and (
                not GlobalVariables.time_calc.execution.is_paused):
                    GlobalVariables.time_calc.execution.pause()
                    print(colored(
                        "Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                            shutil.get_terminal_size().columns, "="), 'cyan'))
                GlobalVariables.time_calc.execution.resume()
                print(colored("Execution Timer resumed in exept block of testcase function".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
                GlobalVariables.EXCEL_TC_Execution = "Fail"
                GlobalVariables.Incomplete_ExecutionCount += 1
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block of testcase function before pytest fails".center(
                    shutil.get_terminal_size().columns, "="), 'cyan'))
                pytest.fail("Test case execution failed due to the exception -" + str(e))
            # -----------------------------------------End of Test Execution--------------------------------------

            # -----------------------------------------Start of Validation----------------------------------------
            GlobalVariables.time_calc.validation.start()
            print(
                colored("Validation Timer started in testcase function".center(shutil.get_terminal_size().columns, "="),
                        'cyan'))

            # # -----------------------------------------Start of API Validation------------------------------------
            if (ConfigReader.read_config("Validations", "api_validation")) == "True":
                try:
                    # --------------------------------------------------------------------------------------------
                    expectedAPIValues1 = {"success": True,
                                         "id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection('S')",
                                         "type": "ZPT_DP_SRV.BapiRet2",
                                         "uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection('S')"}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                    actualAPIValues1 = {"success": success, "id": id, "type": type, "uri": uri}
                    logger.debug(f"actualAPIValues: {actualAPIValues1}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues1, actualAPI=actualAPIValues1)

                    # Whole String comparision
                    expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"d": {"Message": "Transaction Successfully Posted into the System", "LogNo": "", "System": "P01CLNT500", "Field": "", "Type": "S", "Number": "001", "MessageV4": "", "MessageV3": "", "Parameter": "", "Id": "ZPT_MC_DP", "Row": 0, "__metadata": {"id": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection("S")", "type": "ZPT_DP_SRV.BapiRet2", "uri": "https://www.mpenagarpalika.gov.in:8001/prdodata/sap/ZPT_DP_SRV/BapiRet2Collection("S")"}, "LogMsgNo": "000000", "MessageV2": "", "MessageV1": ""}}]}}'}
                    logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                    actualAPIValues2 = {"Result": response_data.replace("'", '"')}
                    logger.debug(f"actualAPIValues: {actualAPIValues2}")

                    Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
                except Exception as e:
                    print("API Validation failed due to exception - " + str(e))
                    msg = msg + "API Validation did not complete due to exception.\n"
                    GlobalVariables.bool_val_exe = False
                    GlobalVariables.str_api_val_result = "Fail"

            # # -----------------------------------------End of API Validation---------------------------------------
            #
            # # -----------------------------------------Start of DB Validation--------------------------------------
            if (ConfigReader.read_config("Validations", "db_validation")) == "True":
                try:
                    # --------------------------------------------------------------------------------------------
                    expectedDBValues = {
                        "url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/sx9b1V/"}
                    logger.debug(f"expectedDBValues: {expectedDBValues}")

                    query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_property_update_details') and active = 1);"
                    logger.debug(f"Query to fetch data from external_api_adapter table : {query}")  # change in all TCS
                    result = DBProcessor.getValueFromDB(query)
                    logger.debug(f"Query result URL: {result}")
                    url_db = result["url"].iloc[0]
                    actualDBValues = {"url": url_db}
                    logger.debug(f"actualDBValues : {actualDBValues}")
                    # ---------------------------------------------------------------------------------------------
                    Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
                except Exception as e:
                    print("DB Validation failed due to exception - " + str(e))
                    msg = msg + "DB Validation did not complete due to exception.\n"
                    GlobalVariables.bool_val_exe = False
                    GlobalVariables.str_db_val_result = 'Fail'

            # # -----------------------------------------End of DB Validation---------------------------------------
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
            print(colored("Execution Timer resumed in finally block of testcase function".center(
                shutil.get_terminal_size().columns, "="), 'cyan'))



            if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
                query = "select * from ca_usergroup_org_map where org_code='BHOPALMUNICIPALFDC' and is_active;"
                logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
                result = DBProcessor.getValueFromDB(query)
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
            print(colored("Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns,"="), 'cyan'))


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
@pytest.mark.dbVal
def test_common_300_304_005():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_mp_water_details
            Sub Feature Description: fetching details of Bhopal Muncipal FDC Merchant having key "get_mp_water_details" via fetch/data API
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

        # -----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.time_calc.execution.start()
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="),
                          'cyan'))
            api_details = DBProcessor.get_api_details('fetch_get_mp_water_details')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            CompanyName = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['CompanyName']
            CANumber = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['CANumber']
            InvoiceNO = response['data']['response'][0]['Body']['BillDetailsResponse']['BillDetailsResult']['InvoiceNO']
            logger.info(f"API Result: Fetch Response for BMC Merchant : {success}, {CompanyName}. {CANumber},{InvoiceNO}")

            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            print(colored("Execution Timer paused in try block of testcase function".center(shutil.get_terminal_size().columns,
                                                                                  "="), 'cyan'))
        except Exception as e:
            if GlobalVariables.time_calc.execution.is_started and (not GlobalVariables.time_calc.execution.is_paused):
                GlobalVariables.time_calc.execution.pause()
                print(colored("Execution Timer paused in exept block (bcz not paused in try block) of testcase function".center(
                        shutil.get_terminal_size().columns, "="), 'cyan'))
            GlobalVariables.time_calc.execution.resume()
            print(colored("Execution Timer resumed in exept block of testcase function".center(shutil.get_terminal_size().columns,
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
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues1 = {"success": True, "CompanyName": "SOUTH BIHAR POWER DISTRIBUTION COMPANY LTD", "CANumber": "102486309" , "InvoiceNO": "10115629079"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "CompanyName": CompanyName, "CANumber": CANumber,
                                   "InvoiceNO": InvoiceNO}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"BillDetailsResponse": {"BillDetailsResult": {"CompanyName": "SOUTH BIHAR POWER DISTRIBUTION COMPANY LTD", "MobileNumber": "7050292987", "Address": " HDUMABD KI . . 804408", "BillMonth": "MAY-2022", "LT_HT": "URBAN", "CANumber": "102486309", "Amount": "772", "ConsumerName": "MD EHTESHAM ANSARI .", "Division": "Jehanabad", "InvoiceNO": "10115629079", "DueDate": "2022-05-22", "SubDivision": "Jehanabad"}}}}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data}
                logger.debug(f"actualAPIValues: {actualAPIValues2}")

                Validator.validationAgainstAPI(expectedAPI=expectedAPIValues2, actualAPI=actualAPIValues2)
            except Exception as e:
                print("API Validation failed due to exception - " + str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result = "Fail"

        # # -----------------------------------------End of API Validation---------------------------------------
        #
        # # -----------------------------------------Start of DB Validation--------------------------------------
        if (ConfigReader.read_config("Validations", "db_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/29d4kh/application/5dhnHE/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_mp_water_details') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")  # change in all TCS
                result = DBProcessor.getValueFromDB(query)
                logger.debug(f"Query result URL: {result}")
                url_db = result["url"].iloc[0]
                actualDBValues = {"url": url_db}
                logger.debug(f"actualDBValues : {actualDBValues}")
                # ---------------------------------------------------------------------------------------------
                Validator.validateAgainstDB(expectedDB=expectedDBValues, actualDB=actualDBValues)
            except Exception as e:
                print("DB Validation failed due to exception - " + str(e))
                msg = msg + "DB Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_db_val_result = 'Fail'

        # # -----------------------------------------End of DB Validation---------------------------------------
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



        if GlobalVariables.EXCEL_TC_Execution == "Fail" or GlobalVariables.str_api_val_result == "Fail" or GlobalVariables.str_db_val_result == 'Fail':
            query = "select * from ca_usergroup_org_map where org_code='BHOPALMUNICIPALFDC' and is_active;"
            logger.debug(f"Query to fetch data from ca_usergroup_org_map table : {query}")
            result = DBProcessor.getValueFromDB(query)
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
        print(colored(
            "Execution Timer end in finally block of testcase function".center(shutil.get_terminal_size().columns, "="),
            'cyan'))




