
import random
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from Utilities.APIPost import post
from Utilities.CalculateEMI import CalculateEMI
from Configuration import Configuration
from Utilities import Validator, ReportProcessor, ConfigReader


username = '7204644888'
Env = "DEV11"
password = 'A123456'
url = 'https://dev11.ezetap.com/api/2.0/emi/preFetch'
amount = random.randint(200,500)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_API_SA_PreFetch_01(): #Make sure to add the test case name as same as the sub feature code.
    try:
        # Set the below variables depending on the log capturing need of the test case.
        Configuration.configureLogCaptureVariables(apiLog = False, portalLog = False, cnpwareLog = False, middlewareLog = False)

        # Variable which tracks if the execution is going on through all the lines of code of test case.
        # Set to failure where ever there are chances of failure.
        msg = ""

        #-----------------------------------------Start of Test Execution-------------------------------------
        try:
            # ------------------------------------------------------------------------------------------------
            #
            print("Inside test case API")
            prefetch_payload = {'username': username, 'password': password, 'amount': amount}
            prefetch_payload_resp = post(prefetch_payload, url)
            resultValuelist = prefetch_payload_resp['emiDetails']
            print("Result value list", resultValuelist)
            #
            # ------------------------------------------------------------------------------------------------
            GlobalVariables.EXCEL_TC_Execution = "Pass"
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
        except Exception as e:
            GlobalVariables.EXCEL_TC_Execution = "Fail"
            GlobalVariables.Incomplete_ExecutionCount += 1
            ReportProcessor.get_TC_Exe_Time()  # Used for identifying the end time of test case execution.
            pytest.fail("Test case execution failed due to the exception -"+str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")

        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            try:
                # --------------------------------------------------------------------------------------------
                expectedAPIValues = {"Result": 'Success'}
                #
                for i in resultValuelist:
                    print("Inside API vale loop")
                    if i['bankCode'] == "HDFC" and i['cardType'] == "CREDIT":
                        expResult = round(CalculateEMI(int(amount), int(i['roi']), int(str(i['tenure']).split(" ")[0])))
                        ActualResult = round(i['emiAmount'])
                        print("Expected:", expResult)
                        print("Actual:", ActualResult)
                        if expResult == ActualResult:
                            actualAPIValues = {"Result": 'Success'}
                        else:
                            actualAPIValues = {"Result": 'Fail'}
                #
               # actualAPIValues = {}
                # ---------------------------------------------------------------------------------------------
                Validator.validationAgainstAPI(expectedAPI= expectedAPIValues, actualAPI=actualAPIValues)
            except Exception as e:
                print("API Validation failed due to exception - "+str(e))
                msg = msg + "API Validation did not complete due to exception.\n"
                GlobalVariables.bool_val_exe = False
                GlobalVariables.str_api_val_result= "Fail"


        # -----------------------------------------End of API Validation---------------------------------------

    # -------------------------------------------End of Validation---------------------------------------------

    finally:
        ReportProcessor.updateTestCaseResult(msg)  # pass msg
        # Test case ID should be passed as argument in string format.
        #Test case ID will be the method name. Eg. test_SubFeatureCode in this case.
        Configuration.executeFinallyBlock("test_API_SA_PreFetch_01")