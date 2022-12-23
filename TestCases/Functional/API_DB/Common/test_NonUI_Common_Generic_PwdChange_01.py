import string
import sys
import random
import pytest
from Configuration import Configuration
from DataProvider import GlobalVariables
from Utilities import Validator, ConfigReader, DBProcessor, APIProcessor, Generic_processor
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_038():
    """
    Sub Feature Code: NonUI_Common_Generic_pwdChange_without_specialChars
    Sub Feature Description: Add new password without special chars
    TC naming code description: 400: Generic functions,401: Autologin,038: TC038
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            org_code = Generic_processor.get_generic_details_from_excel("PRITHI")["MerchantCode"]
            logger.debug(f"Fetching the org_code from Generic sheet : {org_code}")
            app_username = Generic_processor.get_generic_details_from_excel("PRITHI")["Username"]
            logger.debug(f"Fetching the app_username from Generic sheet : {app_username}")
            app_password = Generic_processor.get_generic_details_from_excel("PRITHI")["Password"]
            logger.debug(f"Fetching the app_password from Generic sheet : {app_password}")

            portal_username = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Username"]
            logger.debug(f"Fetching the portal_username from Generic sheet : {portal_username}")
            portal_password = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Password"]
            logger.debug(f"Fetching the Portal_password from Generic sheet : {portal_password}")

            #fetching the old password_hash value
            query = "select password_hash from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch password_hash from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result from the DB : {result}")
            password_hash = result['password_hash'].values[0]
            logger.debug(f"Fetching password_hash of the User {app_username}, password_hash : {password_hash}")

            #randomly generating the newpassword without special characters
            lower_letters = string.ascii_lowercase
            logger.debug(f"Fetching lower_letters value : {lower_letters}")
            upper_letters = string.ascii_uppercase
            logger.debug(f"Fetching upper_letters value : {upper_letters}")
            digits = string.digits
            logger.debug(f"Fetching digits value : {digits}")
            result_lower_letters = ''.join(random.choice(lower_letters) for i in range(2))
            logger.debug(f"Fetching result_lower_letters value : {result_lower_letters}")
            result_upper_letters = ''.join(random.choice(upper_letters) for i in range(3))
            logger.debug(f"Fetching result_upper_letters value : {result_upper_letters}")
            result_digits = ''.join(random.choice(digits) for i in range(2))
            logger.debug(f"Fetching result_digits value : {result_digits}")
            new_password_generated = result_lower_letters + result_upper_letters + result_digits
            logger.debug(f"new_password_generated is : {new_password_generated}")

            # for newPassword variable add the new_password_generated
            api_details = DBProcessor.get_api_details('PasswordChange', request_body={
                "username": app_username,
                "password": app_password,
                "newPassword": new_password_generated
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"Change Password response is : {response}")
            password_change_success = response['success']
            logger.debug(f"password_change_success is : {password_change_success}")

            if password_change_success == True:
                #user should be able to login with new_password_generated
                api_details = DBProcessor.get_api_details('Login', request_body={
                    "username": app_username,
                    "password": new_password_generated
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Login response is : {response}")
                login_success = response['success']
                logger.debug(f"success is : {login_success}")

                #updating the password_hash value with old_password_hash value in org_employee table
                Generic_processor.update_org_employee_table(password_hash, org_code, app_username, portal_username,portal_password)

                if login_success == True:
                    # user should be able to login with new_password_generated
                    api_details = DBProcessor.get_api_details('Login', request_body={
                        "username": app_username,
                        "password": app_password
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Login Response for old password : {response}")
                    login_success = response['success']
                    logger.debug(f"success is : {login_success}")
                    logger.info(f"user is able to login with old password")

                else:
                    logger.error(f"user is not able to login with old password")

            else:
                logger.error(f"User is not able to login with New Password Generated")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": password_change_success
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_039():
    """
    Sub Feature Code: NonUI_Common_Generic_pwdChange_with_specialChars
    Sub Feature Description: Add new password with special chars
    TC naming code description: 400: Generic functions, 401: Autologin, 039: TC039
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            org_code = Generic_processor.get_generic_details_from_excel("PRITHI")["MerchantCode"]
            logger.debug(f"Fetching the org_code from Generic sheet : {org_code}")
            app_username = Generic_processor.get_generic_details_from_excel("PRITHI")["Username"]
            logger.debug(f"Fetching the app_username from Generic sheet : {app_username}")
            app_password = Generic_processor.get_generic_details_from_excel("PRITHI")["Password"]
            logger.debug(f"Fetching the app_password from Generic sheet : {app_password}")

            portal_username = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Username"]
            logger.debug(f"Fetching the portal_username from Generic sheet : {portal_username}")
            portal_password = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Password"]
            logger.debug(f"Fetching the Portal_password from Generic sheet : {portal_password}")

            # fetching the old password_hash value
            query = "select password_hash from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch password_hash from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result from the DB : {result}")
            password_hash = result['password_hash'].values[0]
            logger.debug(f"Fetching password_hash of the User {app_username}, password_hash : {password_hash}")

            #randomly generating the newpassword with special characters
            lower_letters = string.ascii_lowercase
            logger.debug(f"Fetching lower_letters value : {lower_letters}")
            upper_letters = string.ascii_uppercase
            logger.debug(f"Fetching upper_letters value : {upper_letters}")
            digits = string.digits
            logger.debug(f"Fetching digits value : {digits}")
            result_lower_letters = ''.join(random.choice(lower_letters) for i in range(1))
            logger.debug(f"Fetching result_lower_letters value : {result_lower_letters}")
            result_upper_letters = ''.join(random.choice(upper_letters) for i in range(3))
            logger.debug(f"Fetching result_upper_letters value : {result_upper_letters}")
            result_digits = ''.join(random.choice(digits) for i in range(2))
            logger.debug(f"Fetching result_digits value : {result_digits}")
            result_special_char = ''.join(random.choice(string.punctuation) for i in range(1))
            logger.debug(f"Fetching result_special_char value : {result_special_char}")
            new_password_generated = result_lower_letters + result_upper_letters + result_digits + result_special_char
            logger.debug(f"new_password_generated is : {new_password_generated}")

            # for newPassword variable add the new_password_generated
            api_details = DBProcessor.get_api_details('PasswordChange', request_body={
                "username": app_username,
                "password": app_password,
                "newPassword": new_password_generated
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"ChangePassword response is : {response}")
            password_change_success = response['success']
            logger.debug(f"password_change_success is : {password_change_success}")

            if password_change_success == True:
                #user should be able to login with new_password_generated
                api_details = DBProcessor.get_api_details('Login', request_body={
                    "username": app_username,
                    "password": new_password_generated
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Login Response is : {response}")
                login_success = response['success']
                logger.debug(f"success is : {login_success}")

                #updating the password_hash value with old_password_hash value in org_employee table
                Generic_processor.update_org_employee_table(password_hash, org_code, app_username, portal_username,portal_password)

                if login_success == True:
                    # user should be able to login with new_password_generated
                    api_details = DBProcessor.get_api_details('Login', request_body={
                        "username": app_username,
                        "password": app_password
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Login Response for old password : {response}")
                    login_success = response['success']
                    logger.debug(f"success is : {login_success}")
                    logger.info(f"user is able to login with old password")

                else:
                    logger.error(f"user is not able to login with old password")

            else:
                logger.error(f"User is not able to login with New Password Generated")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": password_change_success
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_040():
    """
    Sub Feature Code: NonUI_Common_Generic_pwdChange_with_upper_numbers
    Sub Feature Description: Add new password with uppercase and numbers
    TC naming code description: 400: Generic functions, 401: Autologin, 040: TC040
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            org_code = Generic_processor.get_generic_details_from_excel("PRITHI")["MerchantCode"]
            logger.debug(f"Fetching the org_code from Generic sheet : {org_code}")
            app_username = Generic_processor.get_generic_details_from_excel("PRITHI")["Username"]
            logger.debug(f"Fetching the app_username from Generic sheet : {app_username}")
            app_password = Generic_processor.get_generic_details_from_excel("PRITHI")["Password"]
            logger.debug(f"Fetching the app_password from Generic sheet : {app_password}")

            portal_username = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Username"]
            logger.debug(f"Fetching the portal_username from Generic sheet : {portal_username}")
            portal_password = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Password"]
            logger.debug(f"Fetching the Portal_password from Generic sheet : {portal_password}")

            # fetching the old password_hash value
            query = "select password_hash from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch password_hash from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result from the DB : {result}")
            password_hash = result['password_hash'].values[0]
            logger.debug(f"Fetching password_hash of the User {app_username}, password_hash : {password_hash}")

            # generating randomly upper_letters and digits
            upper_letters = string.ascii_uppercase
            logger.debug(f"Fetching upper_letters value : {upper_letters}")
            digits = string.digits
            logger.debug(f"Fetching digits value : {digits}")
            result_upper_letters = ''.join(random.choice(upper_letters) for i in range(3))
            logger.debug(f"Fetching result_upper_letters value : {result_upper_letters}")
            result_digits = ''.join(random.choice(digits) for i in range(4))
            logger.debug(f"Fetching result_digits value : {result_digits}")
            new_password_generated = result_upper_letters + result_digits
            logger.debug(f"new_password_generated is : {new_password_generated}")

            # for newPassword variable add the new_password_generated
            api_details = DBProcessor.get_api_details('PasswordChange', request_body={
                "username": app_username,
                "password": app_password,
                "newPassword": new_password_generated
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"ChangePassword response is : {response}")
            password_change_success = response['success']
            logger.debug(f"password_change_success response is : {password_change_success}")

            if password_change_success == True:
                #user should be able to login with new_password_generated
                api_details = DBProcessor.get_api_details('Login', request_body={
                    "username": app_username,
                    "password": new_password_generated
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Login response is : {response}")
                login_success = response['success']
                logger.debug(f"success is : {login_success}")

                #updating the password_hash value with old_password_hash value in org_employee table
                Generic_processor.update_org_employee_table(password_hash, org_code, app_username, portal_username,portal_password)

                if login_success == True:
                    # user should be able to login with new_password_generated
                    api_details = DBProcessor.get_api_details('Login', request_body={
                        "username": app_username,
                        "password": app_password
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Login Response for old password : {response}")
                    login_success = response['success']
                    logger.debug(f"success is : {login_success}")
                    logger.info(f"user is able to login with old password")

                else:
                    logger.error(f"user is not able to login with old password")

            else:
                logger.error(f"User is not able to login with New Password Generated")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": password_change_success
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_041():
    """
    Sub Feature Code: NonUI_Common_Generic_pwdChange_with_upper_number_specialChars
    Sub Feature Description: Add new password with uppercase, numbers and special characters
    TC naming code description:400: Generic functions,401: Password change,041: TC041
    """

    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            org_code = Generic_processor.get_generic_details_from_excel("PRITHI")["MerchantCode"]
            logger.debug(f"Fetching the org_code from Generic sheet : {org_code}")
            app_username = Generic_processor.get_generic_details_from_excel("PRITHI")["Username"]
            logger.debug(f"Fetching the app_username from Generic sheet : {app_username}")
            app_password = Generic_processor.get_generic_details_from_excel("PRITHI")["Password"]
            logger.debug(f"Fetching the app_password from Generic sheet : {app_password}")

            portal_username = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Username"]
            logger.debug(f"Fetching the portal_username from Generic sheet : {portal_username}")
            portal_password = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Password"]
            logger.debug(f"Fetching the Portal_password from Generic sheet : {portal_password}")

            # fetching the old password_hash value
            query = "select password_hash from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch password_hash from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result from the DB : {result}")
            password_hash = result['password_hash'].values[0]
            logger.debug(f"Fetching password_hash of the User {app_username}, password_hash : {password_hash}")

            # generating randomly uppercase, numbers and special characters
            upper_letters = string.ascii_uppercase
            logger.debug(f"Fetching upper_letters value : {upper_letters}")
            digits = string.digits
            logger.debug(f"Fetching digits value : {digits}")
            result_upper_letters = ''.join(random.choice(upper_letters) for i in range(3))
            logger.debug(f"Fetching upper_letters value : {result_upper_letters}")
            result_digits = ''.join(random.choice(digits) for i in range(2))
            logger.debug(f"Fetching result_digits value : {result_digits}")
            result_special_char = ''.join(random.choice(string.punctuation) for i in range(2))
            logger.debug(f"Fetching result_special_char value : {result_special_char}")
            new_password_generated = result_upper_letters + result_digits + result_special_char
            logger.debug(f"new_password_generated is : {new_password_generated}")

            # for newPassword variable add the new_password_generated
            api_details = DBProcessor.get_api_details('PasswordChange', request_body={
                "username": app_username,
                "password": app_password,
                "newPassword": new_password_generated
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"ChangePassword response is : {response}")
            password_change_success = response['success']
            logger.debug(f"password_change_success is : {password_change_success}")

            if password_change_success == True:
                #user should be able to login with new_password_generated
                api_details = DBProcessor.get_api_details('Login', request_body={
                    "username": app_username,
                    "password": new_password_generated
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Login Response is : {response}")
                login_success = response['success']
                logger.debug(f"success is : {login_success}")

                #updating the password_hash value with old_password_hash value in org_employee table
                Generic_processor.update_org_employee_table(password_hash, org_code, app_username, portal_username,portal_password)

                if login_success == True:
                    # user should be able to login with new_password_generated
                    api_details = DBProcessor.get_api_details('Login', request_body={
                        "username": app_username,
                        "password": app_password
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Login Response for old password : {response}")
                    login_success = response['success']
                    logger.debug(f"success is : {login_success}")
                    logger.info(f"user is able to login with old password")

                else:
                    logger.error(f"user is not able to login with old password")

            else:
                logger.error(f"User is not able to login with New Password Generated")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")
            try:
                expected_api_values = {
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": password_change_success
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)


@pytest.mark.usefixtures("log_on_success", "method_setup")
@pytest.mark.apiVal
def test_common_400_401_042():
    """
    Sub Feature Code: NonUI_Common_Generic_pwdChange_with_lower_numbers
    Sub Feature Description: Add new password with lowercase and numbers
    TC naming code description: 400: Generic functions,401: Password change,042: TC042
    """
    try:
        testcase_id = sys._getframe().f_code.co_name
        GlobalVariables.time_calc.setup.resume()
        logger.debug(f"Setup Timer resumed in testcase function : {testcase_id}")

        # -------------------------------Reset Settings to default(started)---------------------------------------------
        logger.info(f"Reverting back all the settings that were done as preconditions : {testcase_id}")
        logger.info(f"Reverted back all the settings that were done as preconditions : {testcase_id}")
        # -------------------------------Reset Settings to default(completed)-------------------------------------------
        # -----------------------------PreConditions(Setup to be done for the test case)--------------------------------
        logger.info(f"Starting Precondition setup for the test case : {testcase_id}")
        GlobalVariables.setupCompletedSuccessfully = True
        logger.info(f"Completed Precondition setup for the test case : {testcase_id}")
        # -----------------------------PreConditions(Completed)---------------------------------------------------------
        Configuration.configureLogCaptureVariables(apiLog=True, portalLog=False, cnpwareLog=False, middlewareLog=False, config_log=False)

        GlobalVariables.time_calc.setup.end()
        logger.debug(f"Setup Timer ended in testcase function : {testcase_id}")

        # -----------------------------------------Start of Test Execution----------------------------------------------
        try:
            logger.info(f"Starting execution for the test case : {testcase_id}")
            GlobalVariables.time_calc.execution.start()
            logger.debug(f"Execution Timer started in testcase function : {testcase_id}")

            org_code = Generic_processor.get_generic_details_from_excel("PRITHI")["MerchantCode"]
            logger.debug(f"Fetching the org_code from Generic sheet : {org_code}")
            app_username = Generic_processor.get_generic_details_from_excel("PRITHI")["Username"]
            logger.debug(f"Fetching the app_username from Generic sheet : {app_username}")
            app_password = Generic_processor.get_generic_details_from_excel("PRITHI")["Password"]
            logger.debug(f"Fetching the app_password from Generic sheet : {app_password}")

            portal_username = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Username"]
            logger.debug(f"Fetching the portal_username from Generic sheet : {portal_username}")
            portal_password = Generic_processor.get_generic_details_from_excel("Portal_SWA")["Password"]
            logger.debug(f"Fetching the Portal_password from Generic sheet : {portal_password}")

            # fetching the old password_hash value
            query = "select password_hash from org_employee where username='" + str(app_username) + "';"
            logger.debug(f"Query to fetch password_hash from the DB : {query}")
            result = DBProcessor.getValueFromDB(query)
            logger.debug(f"Query to fetch result from the DB : {result}")
            password_hash = result['password_hash'].values[0]
            logger.debug(f"Fetching password_hash of the User {app_username}, password_hash : {password_hash}")

            # generating randomly lowercase and numbers
            lower_letters = string.ascii_lowercase
            logger.debug(f"Fetching lower_letters value : {lower_letters}")
            digits = string.digits
            logger.debug(f"Fetching digits value : {digits}")
            result_lower_letters = ''.join(random.choice(lower_letters) for i in range(4))
            logger.debug(f"Fetching result_lower_letters value : {result_lower_letters}")
            result_digits = ''.join(random.choice(digits) for i in range(3))
            logger.debug(f"Fetching result_digits value : {result_digits}")
            new_password_generated = result_lower_letters + result_digits
            logger.debug(f"new_password_generated is : {new_password_generated}")

            # for newPassword variable add the new_password_generated
            api_details = DBProcessor.get_api_details('PasswordChange', request_body={
                "username": app_username,
                "password": app_password,
                "newPassword": new_password_generated
            })

            response = APIProcessor.send_request(api_details)
            logger.debug(f"ChangePassword response is : {response}")
            password_change_success = response['success']
            logger.debug(f"password_change_success is : {password_change_success}")

            if password_change_success == True:
                #user should be able to login with new_password_generated
                api_details = DBProcessor.get_api_details('Login', request_body={
                    "username": app_username,
                    "password": new_password_generated
                })

                response = APIProcessor.send_request(api_details)
                logger.debug(f"Login Response is : {response}")
                login_success = response['success']
                logger.debug(f"success is : {login_success}")

                #updating the password_hash value with old_password_hash value in org_employee table
                Generic_processor.update_org_employee_table(password_hash, org_code, app_username, portal_username,portal_password)

                if login_success == True:
                    # user should be able to login with new_password_generated
                    api_details = DBProcessor.get_api_details('Login', request_body={
                        "username": app_username,
                        "password": app_password
                    })

                    response = APIProcessor.send_request(api_details)
                    logger.debug(f"Login Response for old password : {response}")
                    login_success = response['success']
                    logger.debug(f"success is : {login_success}")
                    logger.info(f"user is able to login with old password")

                else:
                    logger.error(f"user is not able to login with old password")

            else:
                logger.error(f"User is not able to login with New Password Generated")

            GlobalVariables.EXCEL_TC_Execution = "Pass"
            GlobalVariables.time_calc.execution.pause()
            logger.debug(f"Execution Timer paused in try block of testcase function : {testcase_id}")
            logger.info(f"Execution is completed for the test case : {testcase_id}")

        except Exception as e:
            Configuration.perform_exe_exception(testcase_id)
            pytest.fail("Test case execution failed due to the exception -" + str(e))
        # -----------------------------------------End of Test Execution--------------------------------------

        # -----------------------------------------Start of Validation----------------------------------------
        logger.info(f"Starting Validation for the test case : {testcase_id}")
        GlobalVariables.time_calc.validation.start()
        logger.debug(f"Validation Timer started in testcase function : {testcase_id}")
        # -----------------------------------------Start of API Validation------------------------------------
        if (ConfigReader.read_config("Validations", "api_validation")) == "True":
            logger.info(f"Started API validation for the test case : {testcase_id}")

            try:
                expected_api_values = {
                    "success": True
                }

                logger.debug(f"expected_api_values: {expected_api_values}")

                actual_api_values = {
                    "success": password_change_success
                }

                logger.debug(f"actual_api_values : {actual_api_values}")

                Validator.validationAgainstAPI(expectedAPI=expected_api_values, actualAPI=actual_api_values)

            except Exception as e:
                Configuration.perform_api_val_exception(testcase_id, e)
            logger.info(f"Completed API validation for the test case : {testcase_id}")
        # -----------------------------------------End of API Validation---------------------------------------
        GlobalVariables.time_calc.validation.end()
        logger.debug(f"Validation Timer ended in testcase function : {testcase_id}")
        logger.info(f"Completed Validation for the test case : {testcase_id}")
        # -------------------------------------------End of Validation---------------------------------------------
    finally:
        Configuration.executeFinallyBlock(testcase_id)

