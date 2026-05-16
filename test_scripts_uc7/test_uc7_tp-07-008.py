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


def test_tp_07_008_role_conflict_handling(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    target_user = "Jackson Wang"
    
    # ==========================================
    # PART 1: LOCATE AND CLICK EDIT
    # ==========================================
    
    try:
        edit_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//tr[contains(., '{target_user}')]//button[contains(@class, 'text-accent-blue')]"
        )))
        edit_button.click()
    except Exception:
        pytest.fail(f"Test Failed: Could not find user '{target_user}' to edit. Ensure test data is seeded.")
        
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Update User']")))
    
    # ==========================================
    # PART 2: ATTEMPT TO ASSIGN CONFLICTING ROLE
    # ==========================================
    
    try:
        # Note: In the provided React code, Role is read-only and only has "user" or "admin".
        # This tests the SRS requirement directly. If the UI lacks this field, it correctly fails the test.
        role_select = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'space-y-4')]//label[contains(., 'Role')]/following-sibling::select"
        )))
        role_select.send_keys("Primary Admin")
    except Exception:
        pytest.fail("Test Failed: Cannot change role to 'Primary Admin'. The UI does not support this field or option, conflicting with TP-07-008.")

    # Click the Update User button
    update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Update User')]")))
    update_btn.click()
    
    # ==========================================
    # PART 3: VERIFY CONFLICT DETECTION
    # ==========================================
    
    # Verify the system detects the conflict and displays a warning or prompt
    try:
        warning_block = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'text-red-700') or contains(@class, 'bg-yellow-100')]")))
        assert warning_block.is_displayed(), "Test Failed: Expected a role conflict warning, but none was displayed."
    except Exception:
        pytest.fail("Test Failed: Timeout waiting for role conflict detection prompt or warning.")
