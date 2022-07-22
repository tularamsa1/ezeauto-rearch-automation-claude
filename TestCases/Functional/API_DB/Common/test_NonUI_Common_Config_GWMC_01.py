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
@pytest.mark.dbVal
@pytest.mark.appVal
def test_common_300_303_001():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_User_Charges_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "User_Charges_Tax_PullV2" via fetch/data API
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
            print(colored("Execution Timer startd in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
            api_details = DBProcessor.get_api_details('fetch_User_Charges_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['schema']['id']
            OWNEROFTHESHOP = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['OWNEROFTHESHOP']
            SHOP_NAME = response['data']['response'][0]['Body']['userchargesdemandResponse']['userchargesdemandResult']['diffgram']['NewDataSet']['gcharges_demand']['SHOP_NAME']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {OWNEROFTHESHOP},{SHOP_NAME}")

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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet", "OWNEROFTHESHOP": "BHARAT NARANG", "SHOP_NAME":"ASIAN SRIDEVI SCREEN 3"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id, "OWNEROFTHESHOP": OWNEROFTHESHOP, "SHOP_NAME": SHOP_NAME}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")
        #          ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"userchargesdemandResponse": {"userchargesdemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "SHOPID", "type": "xs:double"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "SHOP_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "OWNEROFTHESHOP", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}, {"minOccurs": "0", "name": "GNAME", "type": "xs:string"}, {"minOccurs": "0", "name": "GID", "type": "xs:double"}]}}, "name": "gcharges_demand"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"gcharges_demand": {"CURRAMT": "0", "OWNEROFTHESHOP": "BHARAT NARANG", "ARRAMT": "0", "GID": "25", "CLOSING": "0", "HOUSENO": "#7-1-89", "CITY_NAME": "BALASAMUDRAM", "SHOP_NAME": "ASIAN SRIDEVI SCREEN 3", "id": "gcharges_demand1", "rowOrder": "0", "SHOPID": "18324", "GNAME": "CINEMA HALLS AND ENTERTINMENT"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/ZStN9b/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'User_Charges_Tax_PullV2') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_002():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_Meter_Charges_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "Meter_Charges_Tax_PullV2" via fetch/data API

    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(
            colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------
        # Write the setup code here

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
            api_details = DBProcessor.get_api_details('fetch_Meter_Charges_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['schema']['id']
            OWNER = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['OWNER']
            CURRAMT = response['data']['response'][0]['Body']['metertapdemandResponse']['metertapdemandResult']['diffgram']['NewDataSet']['metertapview']['CURRAMT']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {OWNER},{CURRAMT}")

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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet", "OWNER": "GOPU VENNAMMA", "CURRAMT":"2040"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id, "OWNER": OWNER, "CURRAMT": CURRAMT}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"metertapdemandResponse": {"metertapdemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "MNNO", "type": "xs:decimal"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "OWNER", "type": "xs:string"}, {"minOccurs": "0", "name": "STATUS", "type": "xs:string"}, {"minOccurs": "0", "name": "DIASIZE", "type": "xs:string"}, {"minOccurs": "0", "name": "ASSESMENT_DESC", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}]}}, "name": "metertapview"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"metertapview": {"CURRAMT": "2040", "OWNER": "GOPU VENNAMMA", "STATUS": "NULL", "ARRAMT": "3570", "CLOSING": "5610", "HOUSENO": "#1-7-985", "ASSESMENT_DESC": "APARTMENTS", "MNNO": "674", "CITY_NAME": "ADVOCATE COLONY", "DIASIZE": "1.5", "id": "metertapview1", "rowOrder": "0"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/YvTmTy/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'Meter_Charges_Tax_PullV2') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_003():
    """
        Sub Feature Code: NonUI_Common_Config_GWMC_fetch_Trade_Tax_PullV2
        Sub Feature Description: fetching details of GWMC Merchant having key "Trade_Tax_PullV2" via fetch/data API

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
            api_details = DBProcessor.get_api_details('fetch_Trade_Tax_PullV2')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            id = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['schema']['id']
            AADHAR = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['AADHAR']
            CURRAMT = response['data']['response'][0]['Body']['tradedemandResponse']['tradedemandResult']['diffgram']['NewDataSet']['TRADEDEMAND']['CURRAMT']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {id}, {AADHAR},{CURRAMT}")

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
                expectedAPIValues1 = {"success": True, "id": "NewDataSet", "AADHAR": "880601356959", "CURRAMT":"2000"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "id": id, "AADHAR": AADHAR, "CURRAMT": CURRAMT}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"Body": {"tradedemandResponse": {"tradedemandResult": {"schema": {"id": "NewDataSet", "element": {"IsDataSet": "true", "complexType": {"choice": {"minOccurs": "0", "maxOccurs": "unbounded", "element": {"complexType": {"sequence": {"element": [{"minOccurs": "0", "name": "SHOPID", "type": "xs:double"}, {"minOccurs": "0", "name": "SHOP_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "CITY_NAME", "type": "xs:string"}, {"minOccurs": "0", "name": "HNOID", "type": "xs:decimal"}, {"minOccurs": "0", "name": "OWNEROFTHESHOP", "type": "xs:string"}, {"minOccurs": "0", "name": "TRADE_DESC", "type": "xs:string"}, {"minOccurs": "0", "name": "TRADE_CODE", "type": "xs:decimal"}, {"minOccurs": "0", "name": "WARD", "type": "xs:decimal"}, {"minOccurs": "0", "name": "BLOCK", "type": "xs:decimal"}, {"minOccurs": "0", "name": "HNO", "type": "xs:string"}, {"minOccurs": "0", "name": "HOUSENO", "type": "xs:string"}, {"minOccurs": "0", "name": "AGE", "type": "xs:decimal"}, {"minOccurs": "0", "name": "PARTNER", "type": "xs:string"}, {"minOccurs": "0", "name": "AADHAR", "type": "xs:string"}, {"minOccurs": "0", "name": "STATUS", "type": "xs:string"}, {"minOccurs": "0", "name": "ARRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CURRAMT", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CLOSING", "type": "xs:decimal"}, {"minOccurs": "0", "name": "OFINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "FINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "CFINES", "type": "xs:decimal"}, {"minOccurs": "0", "name": "DYEAR", "type": "xs:string"}]}}, "name": "TRADEDEMAND"}}}, "name": "NewDataSet", "UseCurrentLocale": "true"}}, "diffgram": {"NewDataSet": {"TRADEDEMAND": {"PARTNER": "GAJULA RAJAMOULI", "CURRAMT": "2000", "OFINES": "0", "CLOSING": "2000", "HOUSENO": "1-1-227/20/1", "FINES": "0", "DYEAR": "2022-23", "SHOP_NAME": "VARDHAN KIRANAM", "CFINES": "0", "BLOCK": "1", "HNO": "227/20/1", "AADHAR": "880601356959", "rowOrder": "0", "SHOPID": "45067", "OWNEROFTHESHOP": "GAJULA VAMSHI", "STATUS": "-", "ARRAMT": "0", "WARD": "1", "CITY_NAME": "PRASHANTI NAGAR", "TRADE_CODE": "2", "id": "TRADEDEMAND1", "TRADE_DESC": "KIRANA SHOP", "HNOID": "139901", "AGE": "25"}}}}}}}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/efZ1iC/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'Trade_Tax_PullV2') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_004():
    """
             Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_gwmc_tax_wcdemand
            Sub Feature Description: fetching details of GWMC Merchant having key "get_gwmc_tax_wcdemand" via fetch/data API

    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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
            api_details = DBProcessor.get_api_details('fetch_get_gwmc_tax_wcdemand')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            CONSNO = response['data']['response'][0]['CONSNO']
            HOUSENO = response['data']['response'][0]['HOUSENO']
            NAME = response['data']['response'][0]['NAME']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {CONSNO}, {HOUSENO},{NAME}")

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
                expectedAPIValues1 = {"success": True, "CONSNO": "38122", "HOUSENO": "16-10-1347", "NAME":"AMARAVADHI VIJAYA SARADHI  AND A.SHESHA CHALA"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "CONSNO": CONSNO, "HOUSENO": HOUSENO, "NAME": NAME}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"CONSNO": "38122", "OFINES": "0", "FINES": "0", "HOUSENO": "16-10-1347", "GTAX": "1440", "CELLNO": "9296452832", "CLGT": "1440", "CLWC": "1800", "rowOrder": "0", "WC": "1800", "NAME": "AMARAVADHI VIJAYA SARADHI  AND A.SHESHA CHALA", "CLPT": "3316", "ARSWC": "0", "ARSGT": "0", "CITY_NAME": "SHIVA NAGAR", "id": "HouseMaster1", "ARSPT": "0", "IDNO": "0916101447", "errorcode": "00", "PTAX": "3316", "HNOID": "105821"}]}}'}
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/1h7nkR/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_gwmc_tax_wcdemand') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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
def test_common_300_303_005():
    """
            Sub Feature Code: NonUI_Common_Config_GWMC_fetch_get_gwmc_tax_head
            Sub Feature Description: fetching details of GWMC Merchant having key "get_gwmc_tax_head" via fetch/data API

    """
    try:
        GlobalVariables.time_calc.setup.resume()
        print(colored("Setup Timer resumed in testcase function".center(shutil.get_terminal_size().columns, "="), 'cyan'))
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
            api_details = DBProcessor.get_api_details('fetch_get_gwmc_tax_head')
            response = APIProcessor.send_request(api_details)
            response_data = json.dumps(response)
            success = response['success']
            HEADCODE = response['data']['response'][0]['keys'][0]['HEADCODE']
            HEADNAME = response['data']['response'][0]['keys'][0]['HEADNAME']
            errorcode = response['data']['response'][0]['errorcode']
            logger.info(f"API Result: Fetch Response for GWMC Merchant : {success}, {HEADCODE}, {HEADNAME},{errorcode}")

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
                expectedAPIValues1 = {"success": True, "HEADCODE": "253", "HEADNAME": "COVID 19 FINES", "errorcode":"00"}
                logger.debug(f"expectedAPIValues: {expectedAPIValues1}")
                actualAPIValues1 = {"success": success, "HEADCODE": HEADCODE, "HEADNAME": HEADNAME, "errorcode": errorcode}
                logger.debug(f"actualAPIValues: {actualAPIValues1}")

                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues1, actualAPI=actualAPIValues1)

                # Whole String comparision
                expectedAPIValues2 = {"Result": '{"success": true, "data": {"response": [{"keys": [{"AMOUNT": "0", "HEADCODE": "253", "HEADNAME": "COVID 19 FINES"}, {"AMOUNT": "0", "HEADCODE": "229", "HEADNAME": "FINES ON LITTERING"}, {"AMOUNT": "0", "HEADCODE": "230", "HEADNAME": "FINES ON PLASTIC"}, {"AMOUNT": "0", "HEADCODE": "195", "HEADNAME": "SWM FINES"}], "errorcode": "00"}]}}'}
                logger.debug(f"expectedAPIValues: {expectedAPIValues2}")
                actualAPIValues2 = {"Result": response_data}
                logger.debug(f"actualAPIValues: {actualAPIValues2}")
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
                expectedDBValues = {"url": "http://139.162.27.215:80/castlemock/mock/rest/project/4VHvCp/application/POh9sU/"}
                logger.debug(f"expectedDBValues: {expectedDBValues}")

                query = "select url from external_api_adapter where rule_id in (select id from rule where fetch_option_id in (select id from fetch_option where fetch_key = 'get_gwmc_tax_head') and active = 1);"
                logger.debug(f"Query to fetch data from external_api_adapter table : {query}")
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
            query = "select * from ca_usergroup_org_map where org_code='GWMCCONFIGMERCHANT' and is_active;"
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