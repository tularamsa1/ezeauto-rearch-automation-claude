# import pytest
#
# from TestCases import server_logs
# import paramiko
# from appium.webdriver.appium_service import AppiumService
#
#
# # router_ip = '192.168.3.81'    #dev11
# # router_username = 'divyaandrews' # Replace with your username in config file
# # router_port = 22
# # key_filename = '/home/ezetap/.ssh/divya' # Replace with your private key filename
# ssh = paramiko.SSHClient()
# router_ip = '192.168.3.81'    #dev11
# router_username = 'vineethb'
# router_port = 22
# key_filename = '/home/oem/.ssh/vineeth_ssh'
#
# def session_setup():
#     connection_success = server_logs.ssh_connection(router_ip, router_port, router_username, key_filename)
#
#     if connection_success:
#         global appium_service
#         appium_service = AppiumService()
#         appium_service.start()
#         return True
#     else:
#         print("Unable To Connect To The Server")
#         return False
#
#
# def session_teardown():
#     print("INSIDE SESSION TEARDOWN IN SERVER FILE")
#     ssh.close()
#     appium_service.stop()
