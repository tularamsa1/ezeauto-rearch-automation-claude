# # available_org_user = [('9940743566', 'A123456')]
# # username = available_org_user[0]
# # password = available_org_user[1]
# # print(username)
# # print(password)
# #
# #
# # from datetime import datetime
# # #
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%M%S%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%f")}')
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # print(f'D{datetime.now().strftime("%m%d%H%M%S%f")}')
# # # print(f'D{datetime.now()}')
# # from PIL import Image
# # from pytesseract import pytesseract
# #
# # # Defining paths to tesseract.exe
# # # and the image we would be using
# # # path_to_tesseract = r"/home/ezetap/Downloads/HDFC.png"
# # # image_path = r"csv\sample_text.png"
# # #
# # # # Opening the image & storing it in an image object
# # # img = Image.open(image_path)
# # #
# # # # Providing the tesseract executable
# # # # location to pytesseract library
# # # pytesseract.tesseract_cmd = path_to_tesseract
# # #
# # # # Passing the image object to image_to_string() function
# # # # This function will extract the text from the image
# # # text = pytesseract.image_to_string(img)
# # #
# # # # Displaying the extracted text
# # # print(text[:-1])
# # users = ['avi']
# #
# # if users:
# #     count = 0
# #     for user in users:
# #         if count > 0:
# #             print('inside if block')
# #         print('outside if block')
# #     count += 1
# #
# import sqlite3
#
# from DataProvider import GlobalConstants
# from Utilities import DBProcessor
#
# conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
# cursor = conn.cursor()
# # cursor.execute("SELECT Category FROM users WHERE MerchantCode = 'Dev11_July17_01';")
# # app_users = cursor.fetchall()
# # print(app_users[0][0])
# # print(type(app_users[0][0]))
# cursor.execute("SELECT * FROM users;")
# app_users = cursor.fetchall()
# username_list = []
# if app_users:
#     print(app_users)
#     # if app_users[0][8] != "NA" and app_users[0][8] != "nan":
#     for app_user in app_users:
#         print(f"'{app_user[2]}'", end=' ')
#         username_list.append(app_user[2])
#     print(tuple(username_list))
# query = f"select username from org_employee where username in {tuple(username_list)}"
# result = DBProcessor.getValueFromDB(query)
# for i in range(len(result)):
#     username = (result.iloc[i]['username'])
#     cursor.execute(f"SELECT * FROM users where Username = '{username}' and MerchantCode != 'EZETAP';")
#     app_user = cursor.fetchone()
#     if app_user:
#         query = f"select username from org_employee where username = '{username}' and org_code != '{app_user[1]}'"
#         result1 = DBProcessor.getValueFromDB(query)
#         print(result1.iloc[0]['username'])
import sqlite3

from DataProvider import GlobalConstants
from Utilities import DBProcessor


def check_if_username_exists():
    """
    This method is used for checking if the user is already available in the system
    """
    # global result1
    try:
        conn = sqlite3.connect(GlobalConstants.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        app_users = cursor.fetchall()
        username_list = []
        if app_users:
            for app_user in app_users:
                username_list.append(app_user[2])
            print(tuple(username_list))
        query = f"select username from org_employee where username in {tuple(username_list)}"
        result = DBProcessor.getValueFromDB(query)
        for i in range(len(result)):
            username = (result.iloc[i]['username'])
            cursor.execute(f"SELECT * FROM users where Username = '{username}' and MerchantCode != 'EZETAP';")
            app_user = cursor.fetchone()
            print(f"app_user : {app_user}")
            if app_user:
                query = f"select username from org_employee where username = '{username}' and org_code != '{app_user[1]}'"
                result1 = DBProcessor.getValueFromDB(query)
                print(result1.iloc[0]['username'])
                print(f"killing the python process because {result1.iloc[0]['username']} is already exist in db "
                      f"please fill unique username in merchant_user_creation.xlsx sheet which is not present in the "
                      f"db")
                return len(result1)
            else:
                return 0
        cursor.close()
        conn.close()
    except Exception as e:
        print("Merchant creation details db is empty")
        # logger.fatal(f"Exception occurred while checking username in org_employee table : {e}")


print(check_if_username_exists())