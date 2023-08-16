from PageFactory.merchant_portal.Portal_BasePage import BasePage
from Utilities import ConfigReader

class PortalLoginPage(BasePage):

    txt_username = "Username"
    txt_password = "Password"

    def __init__(self, page):
        super().__init__(page)

    def perform_login_to_portal(self, username, password):
        url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
        self.page.goto(url)
        self.page.get_by_label(self.txt_username).clear()
        self.page.get_by_label(self.txt_username).fill(username)
        self.page.get_by_label(self.txt_password).clear()
        self.page.get_by_label(self.txt_password).fill(password)
        self.page.get_by_role("button", name="Login").click(timeout=90000)
