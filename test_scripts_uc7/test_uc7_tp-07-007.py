import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://localhost:3000"

@pytest.fixture
def admin_driver():
    # 1. Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    
    # 2. Perform Admin Login (Pre-condition for UC-7)
    # Wait up to 10 seconds for the email field to appear on the screen
    email_field = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_field.send_keys("your_email_here") # Replace with actual admin email
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    password_field.send_keys("your_passsword_here") # Replace with actual admin password

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN')]")))
    login_btn.click()
    
    yield driver # This passes the logged-in browser to test functions
    
    # 3. Teardown
    driver.quit()


def test_tp_07_007_invite_unregistered_user(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    # Test Data: An email that is not currently in the system database
    unregistered_email = "karen22@gmail.com"
    role = "User"
    
    # ==========================================
    # PART 1: OPEN ADD USER MODAL
    # ==========================================
    
    # Click the button to add a new user
    add_user_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New User')]")))
    add_user_btn.click()
    
    # Wait for the Add New User modal to appear
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Add New User']")))
    
    # ==========================================
    # PART 2: ENTER UNREGISTERED USER DETAILS
    # ==========================================
    
    # Enter the unregistered email address
    email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter email address']")))
    email_field.send_keys(unregistered_email)
    
    # Set the role
    role_select = driver.find_element(By.XPATH, "//div[contains(@class, 'space-y-4')]//select")
    role_select.send_keys(role)
    
    # ==========================================
    # PART 3: SUBMIT AND VERIFY INVITATION TRIGGER
    # ==========================================
    
    # Click "Create User & Send Invite"
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create User & Send Invite')]")))
    submit_btn.click()
    
    # Verify the system triggers the success dialog indicating the invitation was processed
    try:
        success_dialog = wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[text()='Success!']")))
        assert success_dialog.is_displayed(), "Test Failed: The success dialog did not appear after submitting an unregistered email."
    except Exception:
        pytest.fail("Test Failed: Timeout waiting for the success dialog. The invitation process may have failed.")
    
    # Optional: Click 'Great!' to close the modal and clean up the UI state
    great_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Great!')]")))
    great_btn.click()
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h3[text()='Success!']")))