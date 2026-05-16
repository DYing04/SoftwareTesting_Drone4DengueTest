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


def test_tp_07_005_add_new_user(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    # ==========================================
    # PART 1: OPEN ADD USER MODAL
    # ==========================================
    
    add_user_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New User')]")))
    add_user_btn.click()
    
    # Wait for modal to appear
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Add New User']")))
    
    # ==========================================
    # PART 2: ATTEMPT TO FILL FULL REGISTRATION DETAILS
    # ==========================================
    
    try:
        # The email field exists, so this will pass
        email_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter email address']")))
        email_field.send_keys("aliabu@gmail.com")
        
        # Following TP-07-005 strict procedure: The system should prompt for full registration details.
        # This will throw a TimeoutException because these fields do not exist in the React UI for "Add New User".
        full_name_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter full name' or contains(@name, 'name')]")))
        full_name_field.send_keys("Ali Abu")
        
        username_field = driver.find_element(By.XPATH, "//input[contains(@name, 'username')]")
        username_field.send_keys("Ali Abu")
        
        phone_field = driver.find_element(By.XPATH, "//input[@type='tel' or contains(@placeholder, 'phone')]")
        phone_field.send_keys("01123456576")
        
        password_field = driver.find_element(By.XPATH, "//input[@type='password' and contains(@name, 'password')]")
        password_field.send_keys("Aa123456789@")
        
        confirm_password_field = driver.find_element(By.XPATH, "//input[@type='password' and contains(@name, 'confirm')]")
        confirm_password_field.send_keys("Aa123456789@")
        
        role_select = driver.find_element(By.XPATH, "//div[contains(@class, 'space-y-4')]//select")
        role_select.send_keys("User")
        
        # Click Create User
        submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Create User')]")
        submit_btn.click()
        
    except Exception as e:
        # Explicitly fail the test according to the SRS vs UI discrepancy
        pytest.fail("Test Failed: TP-07-005 expects full registration details (Full Name, Username, Phone Number, Password, Confirm Password), but the Add New User UI only provides Email and Role inputs.")