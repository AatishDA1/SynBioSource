import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataset.models import AllUsers
import jwt
from datetime import datetime, timedelta

# Run with: python manage.py test synbiosource.test_selenium
class UserAuthTests(StaticLiveServerTestCase):
    def setUp(self):
        # Set up the Chrome WebDriver using the ChromeDriverManager to handle driver installation.
        self.browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        # Create a test user.
        self.user = AllUsers.objects.create_user(
            email='testuser@example.com',
            password='password123',
            full_name='Test User'
        )

    def tearDown(self):
        # Quit the browser after each test to ensure a clean state.
        self.browser.quit()

    def test_register_and_login(self):
        # Test user registration and login.
        self.browser.get(self.live_server_url + reverse('register'))
        self.browser.find_element(By.NAME, 'fullname').send_keys('New User')
        self.browser.find_element(By.NAME, 'email').send_keys('newuser@example.com')
        self.browser.find_element(By.NAME, 'password1').send_keys('SecurePassword123!')
        self.browser.find_element(By.NAME, 'password2').send_keys('SecurePassword123!')
        self.browser.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('Welcome to SynBio Source', self.browser.page_source)

        # Log out.
        self.browser.find_element(By.LINK_TEXT, 'Logout').click()
        self.assertIn('Welcome to SynBio Source', self.browser.page_source)

        # Log in.
        self.browser.get(self.live_server_url + reverse('login'))
        self.browser.find_element(By.NAME, 'email').send_keys('newuser@example.com')
        self.browser.find_element(By.NAME, 'password').send_keys('SecurePassword123!')
        self.browser.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('Welcome to SynBio Source', self.browser.page_source)

    def test_forgot_password(self):
        # Test forgot password functionality.
        self.browser.get(self.live_server_url + reverse('forgot-password'))
        self.browser.find_element(By.NAME, 'email').send_keys('testuser@example.com')
        self.browser.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('An email has been sent to you', self.browser.page_source)

    def test_reset_password(self):
        # Test reset password functionality.
        jwt_token = jwt.encode({"id": self.user.id, "exp": datetime.now() + timedelta(hours=1)}, os.getenv('SCREATE'), algorithm="HS256")
        reset_url = f"{self.live_server_url}/reset-password/{jwt_token}"

        self.browser.get(reset_url)
        self.browser.find_element(By.NAME, 'new_password').send_keys('NewSecurePassword123!')
        self.browser.find_element(By.NAME, 'confirm_password').send_keys('NewSecurePassword123!')
        self.browser.find_element(By.CSS_SELECTOR, 'button.btn-submit').click()
        self.assertIn('Password has been reset successfully', self.browser.page_source)

if __name__ == '__main__':
    unittest.main()
