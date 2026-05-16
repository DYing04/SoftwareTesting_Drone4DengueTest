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


def test_tp_07_003_change_user_role(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    target_user = "Jason"
    
    # ==========================================
    # PART 1: LOCATE AND CLICK EDIT
    # ==========================================
    
    # Locate the Edit button for the target user
    edit_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//tr[contains(., '{target_user}')]//button[contains(@class, 'text-accent-blue')]"
    )))
    edit_button.click()
    
    # Wait for the Update User modal to appear
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Update User']")))
    
    # ==========================================
    # PART 2: UPDATE ROLE
    # ==========================================
    
    try:
        # Attempt to locate a select dropdown for Role. 
        # NOTE: This will likely fail based on the UI code (where Role is a read-only div). 
        # This catch will flag the mismatch between the UI and the SRS.
        role_select = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'space-y-4')]//label[contains(., 'Role')]/following-sibling::select"
        )))
        role_select.send_keys("Admin")
        
    except Exception:
        pytest.fail("Test Failed: Cannot change role. The 'Role' field is read-only in the UI, which conflicts with test procedure TP-07-003.")
        
    # Click the Update User button
    update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Update User')]")))
    update_btn.click()
    
    # ==========================================
    # PART 3: VERIFY UPDATE
    # ==========================================
    
    # Wait for the modal to close completely
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[text()='Update User']")))
    time.sleep(1)
    
    # Verify the updated role appears in the target user's row
    updated_row = driver.find_element(By.XPATH, f"//tr[contains(., '{target_user}')]")
    
    assert "admin" in updated_row.text.lower(), f"Test Failed: Role for {target_user} was not updated to Admin in the table."