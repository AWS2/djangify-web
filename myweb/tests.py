import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

class MyseleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


    def compare_strs(self, expected_str, current_str, success_msg, failure_msg):
        if current_str == expected_str:
            print(success_msg)
        else:
            print(failure_msg)


    def check_url(self, open_home, need_cookies, btn, url, open_window):

        # Open the home page
        if open_home:
            self.selenium.get(f"{self.live_server_url}/home")
            time.sleep(2)

        # Store the original window handle
        original_window = self.selenium.current_window_handle

        # Accept the cookies if necessary
        if need_cookies:
            self.selenium.find_element(By.XPATH, "//button[contains(text(), 'Accept')]").click()
            time.sleep(2)

        # Click the button
        self.selenium.execute_script("arguments[0].click();", self.selenium.find_element(By.LINK_TEXT, btn))
        time.sleep(6)

        # Get all window handles and switch to the new tab
        if open_window:
            all_windows = self.selenium.window_handles
            new_window = [window for window in all_windows if window != original_window][0]
            self.selenium.switch_to.window(new_window)

        # Verify the URL in the new tab
        self.compare_strs(
            expected_str=url,
            current_str=self.selenium.current_url,
            success_msg=f"\033[92mSUCCESS: Redirect to '{url}' worked correctly!\033[0m",
            failure_msg=f"\033[91mFAILURE: Expected '{url}' but got '{self.selenium.current_url}'\033[0m"
        )


    def login(self, usr, pwd):

        # Open the login page
        self.selenium.get(f"{self.live_server_url}/login")
        time.sleep(2)

        # Enter previous credentials
        self.selenium.find_element(By.ID, "id_username").send_keys(usr)
        self.selenium.find_element(By.ID, "id_password").send_keys(pwd)

        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[contains(text(), 'Log in')]").click()
        time.sleep(2)


    def check_content(self, expected_elements, missing_elements):

        # Open the home page
        self.selenium.get(f"{self.live_server_url}/home")
        time.sleep(2)

        # Check presence of each expected element
        for element in expected_elements:
            try:
                self.selenium.find_element(By.CLASS_NAME, element)
                print(f"\033[92mSUCCESS: Element with class name '{element}' is present!\033[0m")
            except Exception:
                missing_elements.append(element)
                print(f"\033[91mFAILURE: Element with class name '{element}' is missing\033[0m")

        # Verify all of the home page elements have been found
        if not missing_elements:
            print("\033[92mSUCCESS: All expected page elements are present!\033[0m")
        else:
            print(f"\033[91mFAILURE: Missing page elements: {', '.join(missing_elements)}\033[0m")


    def home_content(self):
        self.check_content(expected_elements=["home-main", "home-about", "home-features"], missing_elements=[])

    def footer_content(self):
        self.check_content(expected_elements=["multilengual", "legal", "copyright"], missing_elements=[])


    def footer(self):

        # Find all footer link URLs
        footer_links = self.selenium.find_elements(By.CSS_SELECTOR, ".legal .legal-link")
        hrefs = [link.get_attribute("href") for link in footer_links]

        # Visit and verify each link by URL

        successful_url = 0

        for href in hrefs:

            self.selenium.get(href)
            time.sleep(2)

            expected_url = href.replace(self.live_server_url, f"{self.live_server_url}/en") + "/"
            current_url = self.selenium.current_url

            if current_url == expected_url:
                successful_url += 1
                print(f"\033[92mSUCCESS: Redirect to '{expected_url}' worked correctly!\033[0m")
            else:
                print(f"\033[91mFAILURE: Expected '{expected_url}' but got '{current_url}'\033[0m")

        if successful_url == len(hrefs):
            print(f"\033[92mSUCCESS: Footer works correctly!\033[0m")


    def header(self):

        # Find the header link by the h1 title text "Djangify"
        self.selenium.find_element(By.LINK_TEXT, "Djangify").click()
        time.sleep(2)

        # Verify we're on the home page
        expected_url = f"{self.live_server_url}/en/home/"
        current_url = self.selenium.current_url
        self.compare_strs(
            expected_str=expected_url,
            current_str=current_url,
            success_msg=f"\033[92mSUCCESS: Redirect to '{expected_url}' worked correctly!\nSUCCESS: Header works correctly!\033[0m",
            failure_msg=f"\033[91mFAILURE: Expected '{expected_url}' but got '{current_url}'\033[0m"
        )


    def github_url(self):
        self.check_url(
            open_home=True,
            need_cookies=False,
            btn="Source Code",
            url="https://github.com/AWS2/djangify-web",
            open_window=True
        )


    def login_url(self):
        self.check_url(
            open_home=True,
            need_cookies=True,
            btn="Create your project",
            url=f"{self.live_server_url}/en/login/?next=/en/dashboard/",
            open_window=False
        )


    def login_failure(self):

        # Try to log in
        self.login(usr="invalid_user", pwd="wrong_password")

        # Verify error message exists and contains the expected text
        expected_msg = "Please enter a correct username and password. Note that both fields may be case-sensitive."
        current_msg = self.selenium.find_element(By.CSS_SELECTOR, "ul.errorlist").text
        self.compare_strs(
            expected_str=expected_msg,
            current_str=current_msg,
            success_msg=f"\033[92mSUCCESS: The user can't log in with invalid credentials!\033[0m",
            failure_msg=f"\033[91mFAILURE: Expected '{expected_msg}' but got '{current_msg}'\033[0m"
        )


    def login_success(self):

        # Open the signin page
        self.selenium.get(f"{self.live_server_url}/en/signin/")
        time.sleep(2)

        # Enter new credentials
        self.selenium.find_element(By.NAME, "username").send_keys("jba")
        self.selenium.find_element(By.NAME, "email").send_keys("jberzalalamo.cf@iesesteveterradas.cat")
        self.selenium.find_element(By.NAME, "password").send_keys("jba")
        self.selenium.find_element(By.NAME, "password_confirm").send_keys("jba")
        time.sleep(2)

        # Submit the form
        self.selenium.find_element(By.XPATH, "//button[contains(text(), 'Sign up')]").click()
        time.sleep(2)

        # Try to log in
        self.login(usr="jba", pwd="jba")

        # Verify we're on the dashboard page
        self.compare_strs(
            expected_str="dashboard-body",
            current_str=self.selenium.find_element(By.TAG_NAME, "body").get_attribute("class"),
            success_msg=f"\033[92mSUCCESS: The user has loged in!\033[0m",
            failure_msg=f"\033[91mFAILURE: The user is still on the login page\033[0m"
        )


    def new_project_url(self):
        self.check_url(
            open_home=False,
            need_cookies=False,
            btn="Crea tu proyecto",
            url=f"{self.live_server_url}/en/new_project/",
            open_window=False
        )


    def create_project(self):

        # Make the petition to the AI
        self.selenium.find_element(By.ID, "project-name").send_keys("Tienda Informática")
        self.selenium.find_element(By.ID, "user-input").send_keys("Crea una tienda informática")
        time.sleep(2)

        # Click the send button
        self.selenium.execute_script(
            "arguments[0].click();", self.selenium.find_element(By.CSS_SELECTOR, "#chat-form .chat-submit-btn")
        )
        time.sleep(4)

        # Verify the AI has responded
        messages = self.selenium.find_element(By.CLASS_NAME, "chat-box").find_elements(By.CLASS_NAME, "chat-message")
        print(len(messages))
        if len(messages) > 1:
            print(f"\033[92mSUCCESS: The AI has responded!\033[0m")
        else:
            print(f"\033[91mFAILURE: The AI is not responding\033[0m")


    def logout(self):

        # Find the header link by the h1 title text "Djangify"
        self.selenium.find_element(By.LINK_TEXT, "Djangify").click()
        time.sleep(2)

        # Click the login button of the home page
        self.selenium.execute_script("arguments[0].click();", self.selenium.find_element(By.LINK_TEXT, "Create your project"))
        time.sleep(2)

        # Verify we're on the dashboard page
        self.compare_strs(
            expected_str="dashboard-body",
            current_str=self.selenium.find_element(By.TAG_NAME, "body").get_attribute("class"),
            success_msg=f"\033[92mSUCCESS: Redirect to dashboard page worked correctly!\nSUCCESS: The user can try to log out!\033[0m",
            failure_msg=f"\033[91mFAILURE: The user is not on the dashboard page\nFAILURE: The user is not able to log out\033[0m"
        )

        # Verify if the previous verification has been successful

        if self.selenium.find_element(By.TAG_NAME, "body").get_attribute("class") == "dashboard-body":

            # Find the header's logout button
            self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit'][title='Cerrar sesión']").click()
            time.sleep(2)

            # Verify we're on the home page
            self.compare_strs(
                expected_str=f"{self.live_server_url}/en/home/",
                current_str=self.selenium.current_url,
                success_msg=f"\033[92mSUCCESS: The user has loged out!\033[0m",
                failure_msg=f"\033[91mFAILURE: The user is still on the dashboard page\033[0m"
            )

            # Click the login button of the home page
            self.selenium.execute_script("arguments[0].click();", self.selenium.find_element(By.LINK_TEXT, "Create your project"))
            time.sleep(2)

            # Verify we're on the login page
            self.compare_strs(
                expected_str="login-body",
                current_str=self.selenium.find_element(By.TAG_NAME, "body").get_attribute("class"),
                success_msg=f"\033[92mSUCCESS: Redirect to login page worked correctly!\nSUCCESS: Logout works as expected!\033[0m",
                failure_msg=f"\033[91mFAILURE: The user has been sent to the dashboard page\nFAILURE:Logout doesn't work as expected\033[0m"
            )


    def test_all(self):

        # Execute the home content test
        print("\n=============================================================================================\n" +
            "BEGGINING HOME CONTENT TEST" +
            "\n=============================================================================================\n")
        self.home_content()

        # Execute the footer content test
        print("\n=============================================================================================\n" +
            "BEGGINING FOOTER CONTENT TEST" +
            "\n=============================================================================================\n")
        self.footer_content()

        # Execute the footer test
        print("\n=============================================================================================\n" +
            "BEGGINING FOOTER TEST" +
            "\n=============================================================================================\n")
        self.footer()

        # Execute the header test
        print("\n=============================================================================================\n" +
            "BEGGINING HEADER TEST" +
            "\n=============================================================================================\n")
        self.header()

        # Execute the Github URL test
        print("\n=============================================================================================\n" +
            "BEGGINING GITHUB URL TEST" +
            "\n=============================================================================================\n")
        self.github_url()

        # Execute the login URL test
        print("\n=============================================================================================\n" +
            "BEGGINING LOGIN URL TEST" +
            "\n=============================================================================================\n")
        self.login_url()

        # Execute the login failure test
        print("\n=============================================================================================\n" +
            "BEGGINING LOGIN FAILURE TEST" +
            "\n=============================================================================================\n")
        self.login_failure()

        # Execute the login success test
        print("\n=============================================================================================\n" +
            "BEGGINING LOGIN SUCCESS TEST" +
            "\n=============================================================================================\n")
        self.login_success()
        """
        # Execute the new project URL test
        print("\n=============================================================================================\n" +
            "BEGGINING NEW PROJECT URL TEST" +
            "\n=============================================================================================\n")
        self.new_project_url()

        # Execute the create project test
        print("\n=============================================================================================\n" +
            "BEGGINING CREATE PROJECT TEST" +
            "\n=============================================================================================\n")
        self.create_project()
        """
        # Execute the logout test
        print("\n=============================================================================================\n" +
            "BEGGINING LOGOUT TEST" +
            "\n=============================================================================================\n")
        self.logout()
