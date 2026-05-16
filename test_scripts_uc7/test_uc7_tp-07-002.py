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



def test_tp_07_002_edit_user_address(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    # Test Data
    target_user = "Jason"
    new_address = "Johor Bahru"
    
    # ==========================================
    # PART 1: LOCATE AND CLICK EDIT
    # ==========================================
    
    # Locate the Edit button for the target user (Jason)
    # From source code: the edit button has 'text-accent-blue' class
    edit_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//tr[contains(., '{target_user}')]//button[contains(@class, 'text-accent-blue')]"
    )))
    edit_button.click()
    
    # ==========================================
    # PART 2: UPDATE ADDRESS
    # ==========================================
    
    # Wait for the Update User modal to appear and find the address input
    address_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter address']")))
    address_input.clear()
    address_input.send_keys(new_address)
    
    # Click the Update User button
    update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Update User')]")))
    update_btn.click()
    
    # ==========================================
    # PART 3: VERIFY UPDATE
    # ==========================================
    
    # Wait for the modal to close completely
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[text()='Update User']")))
    
    # Wait a brief moment for the React state to update the table UI
    time.sleep(1)
    
    # Verify the updated address appears in the target user's row
    updated_row = driver.find_element(By.XPATH, f"//tr[contains(., '{target_user}')]")
    
    assert new_address in updated_row.text, f"Test Failed: Address for {target_user} was not updated to {new_address} in the table."