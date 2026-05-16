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



def test_tp_07_001_search_and_filter_user(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    # Test Data
    search_keyword = "Jason"
    
    # ==========================================
    # PART 1: SEARCH FOR USER
    # ==========================================
    
    # Locate the search bar and input the keyword
    search_bar = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search users...']")))
    search_bar.clear()
    search_bar.send_keys(search_keyword)
    
    # Wait a moment for the React state to filter the table
    time.sleep(1) 
    
    # ==========================================
    # PART 2: VERIFY SEARCH RESULTS
    # ==========================================
    
    # Get all visible rows in the table body
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    
    # Assert that the table is not empty after filtering
    assert len(rows) > 0, "Test Failed: The filtered list is empty. Check if the database contains the test data or if the API failed."
    
    # Assert that the search keyword is present in the filtered rows
    keyword_found = any(search_keyword in row.text for row in rows)
    assert keyword_found is True, f"Test Failed: User '{search_keyword}' was not found in the filtered list."