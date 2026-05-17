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
    password_field.send_keys("your_password_here") # Replace with actual admin password

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN')]")))
    login_btn.click()
    
    yield driver # This passes the logged-in browser to test functions
    
    # 3. Teardown
    driver.quit()


def test_tp_09_001_view_weather_records(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module [cite: 220]
    # Use a flexible XPath to match the sidebar item based on text
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    
    # Wait for the page transition
    time.sleep(2)
    
    # ==========================================
    # PART 1: WAIT FOR DATA TO LOAD
    # ==========================================
    
    # The React component displays "Loading weather data..." or "Loading company locations..." while fetching.
    # Wait for these loading indicators to disappear before evaluating the table.
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass # The state might resolve faster than Selenium checks it
        
    # Wait specifically for the table body to render, indicating data (or empty state) has resolved
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody")))
    except Exception:
        # If the table isn't there, check if it hit the "No Weather Data" empty state
        empty_state = driver.find_elements(By.XPATH, "//*[contains(text(), 'No Weather Data') or contains(text(), 'No Company Locations')]")
        if empty_state:
            pytest.fail("Test Failed: System displayed 'No Weather Data' or 'No Company Locations' empty state instead of the records table.")
        else:
            pytest.fail("Test Failed: Weather Data table did not render. Possible backend or UI failure.")
            
    # ==========================================
    # PART 2: VERIFY EXISTING WEATHER RECORDS
    # ==========================================
    
    # 2. Verify that the system displays at least 3 existing weather records [cite: 220]
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    
    assert len(rows) >= 3, f"Test Failed: Expected at least 3 weather records, but found only {len(rows)}."