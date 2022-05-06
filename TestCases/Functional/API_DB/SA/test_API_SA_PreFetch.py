import json
import random

import allure
import pytest
from datetime import datetime
from DataProvider import GlobalVariables
from TestCases import setUp
from Utilities.APIPost import post
from Utilities.CalculateEMI import CalculateEMI
from allure_commons.types import AttachmentType

import requests


username = '7204644888'
Env = "DEV11"
password = 'A123456'
url = 'https://dev11.ezetap.com/api/2.0/emi/preFetch'
amount = random.randint(200,500)


@pytest.mark.apiVal
@pytest.mark.usefixtures("log_on_success")
def test_API_SA_PreFetch_01(method_setup):
    GlobalVariables.apiLogs = True
    GlobalVariables.portalLogs = False
    GlobalVariables.cnpWareLogs = False
    GlobalVariables.middleWareLogs = False

    global success_Val_Execution
    success_Val_Execution = True
    global expectedAPIValue

    try:
        # login_payload = {'username' : username, 'password' : password}
        # post(login_payload)
        prefetch_payload = {'username' : username, 'password' : password, 'amount': amount}
        prefetch_payload_resp = post(prefetch_payload,url)
        resultValuelist = prefetch_payload_resp['emiDetails']
        setUp.get_TC_Exe_Time()
        print(resultValuelist)

    except:
        # allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
        #               attachment_type=AttachmentType.PNG)
        setUp.get_TC_Exe_Time()
        print("Testcase did not complete due to exception in testcase execution")
        print("")
        GlobalVariables.EXCEL_TC_Execution = "Fail"
        GlobalVariables.Incomplete_ExecutionCount += 1
        pytest.fail()

    else:
        print("===============Inside validation==================")

        GlobalVariables.EXCEL_TC_Execution = "Pass"
        current = datetime.now()
        GlobalVariables.EXCEL_TC_Val_Starting_Time = current.strftime("%H:%M:%S")
        try:
            #Validation
            print("===========Inside Try============")

            for i in resultValuelist:
                if i['bankCode'] == "HDFC" and i['cardType'] == "CREDIT":
                    expResult = round(CalculateEMI(int(amount),int(i['roi']),int(str(i['tenure']).split(" ")[0])))
                    ActualResult = round(i['emiAmount'])
                    if expResult == ActualResult:
                        expectedAPIValue = "Success:Success"
                    else:
                        expectedAPIValue = "Success:Fail"


        except:
            # allure.attach(GlobalVariables.appDriver.get_screenshot_as_png(), name="screenshot",
            #       attachment_type=AttachmentType.PNG)
            print("Inside except block")
            print("API Validation did not complete")
            print("")
            GlobalVariables.api_ValidationFailureCount+= 1
            expectedAPIValue = "Failed"
            GlobalVariables.EXCEL_API_Val = "Fail"
            success_Val_Execution = False

        success = setUp.validateValues(expectedAPIValue, "", "", "")
        if success_Val_Execution == False:
            if success == False:
                pass
            else:
                pytest.fail()
