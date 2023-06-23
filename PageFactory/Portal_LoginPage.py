from PageFactory.Portal_BasePage import BasePage
from Utilities import ConfigReader
import playwright

class PortalLoginPage(BasePage):

    txt_username = "Username"
    txt_password = "Password"

    def __init__(self, page):
        super().__init__(page)

    def perform_login_to_portal(self, username, password):
        url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
        # url = "https://dev17.ezetap.com/merchantPortal/login"
        self.page.goto(url)
        self.page.get_by_label(self.txt_username).clear()
        self.page.get_by_label(self.txt_username).fill(username)
        self.page.get_by_label(self.txt_password).clear()
        self.page.get_by_label(self.txt_password).fill(password)
        self.page.get_by_role("button", name="Login").click(timeout=90000)


# class PortalLoginPage(BasePage):
#
#     txt_user_name = "input[name=\"username\"]"
#     txt_password = "input[name=\"password\"]"
#
#     def __init__(self, page):
#         super().__init__(page)
#
#     def perform_login_to_portal(self, username, password):
#         # url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
#         url = "https://dev17.ezetap.com/merchantPortal/login"
#         self.page.goto(url)
#         self.page.get_by_label("Username").clear()
#         self.page.get_by_label("Username").fill(username)
#         self.page.get_by_label("Password").clear()
#         self.page.get_by_label("Password").fill(password)
#         self.page.get_by_role("button", name="Login").click(timeout=90000)
#
#         # page.get_by_label("Username").click()
#         # page.get_by_label("Password").click()
#         # page.get_by_role("button", name="Login").click()
