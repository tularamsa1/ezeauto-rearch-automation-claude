import paramiko
from DataProvider import GlobalVariables
from PageFactory import Base_Actions

GlobalVariables.ssh = paramiko.SSHClient()
router_ip = Base_Actions.environment("ip")  # dev11
router_username = Base_Actions.environment("username")
router_port = Base_Actions.environment("port")
key_filename = Base_Actions.environment("key_filename")


# Login to the server
def ssh_connection(ip_address, routerPort, username, key_filename):
    GlobalVariables.ssh.load_system_host_keys()
    GlobalVariables.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        GlobalVariables.ssh.connect(ip_address, port=routerPort, username=username,
                    pkey=paramiko.RSAKey.from_private_key_file(key_filename))
        return True
    except Exception as error_message:
        print("Unable to connect")
        print(error_message)
        return False
