from PageFactory.Portal_BasePage import BasePage
from Utilities import ConfigReader


class PortalLoginPage(BasePage):

    txt_user_name = "input[name=\"username\"]"
    txt_password = "input[name=\"password\"]"

    def __init__(self, page):
        super().__init__(page)

    def perform_login_to_portal(self, username, password):
        url = ConfigReader.read_config("APIs", "baseUrl") + ConfigReader.read_config("APIs", "portalLogin")
        self.page.goto(url)
        self.page.locator(self.txt_user_name).clear()
        self.page.locator(self.txt_user_name).fill(username)
        self.page.locator(self.txt_password).clear()
        self.page.locator(self.txt_password).fill(password)
        self.page.get_by_role("button", name="Sign In").click(timeout=90000)
