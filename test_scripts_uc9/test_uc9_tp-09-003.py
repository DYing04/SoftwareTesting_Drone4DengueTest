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


def test_tp_09_003_input_valid_weather_data_form(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    
    time.sleep(2)
    
    # Wait for initial loading to finish
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass

    # ==========================================
    # PART 1: OPEN THE ADD RECORD FORM
    # ==========================================
    
    # Click the "Add New Record" button inside the Manual Entry card
    add_record_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New Record')]")))
    add_record_btn.click()
    
    # Wait for the form to appear
    date_input = wait.until(EC.visibility_of_element_located((By.ID, "date")))
    
    # ==========================================
    # PART 2: FILL IN THE FORM DETAILS
    # ==========================================
    
    # Date: 15/5/2026. 
    # Bypassing React's state wrapper to ensure the onChange event fires properly.
    driver.execute_script("""
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(arguments[0], '2026-05-15');
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, date_input)
    
    # Temperature = 32
    temp_input = driver.find_element(By.ID, "temperature")
    temp_input.clear()
    temp_input.send_keys("32")
    
    # Humidity = 75
    humidity_input = driver.find_element(By.ID, "humidity")
    humidity_input.clear()
    humidity_input.send_keys("75")
    
    # Rainfall = 12.5
    rainfall_input = driver.find_element(By.ID, "rainfall")
    rainfall_input.clear()
    rainfall_input.send_keys("12.5")
    
    # Location = Kuala Lumpur
    location_input = driver.find_element(By.ID, "location")
    location_input.clear()
    location_input.send_keys("Kuala Lumpur")
    
    # Operational Area = Select the first available option in the dropdown
    area_select = driver.find_element(By.ID, "companyLocationId")
    area_select.click()
    first_area_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='companyLocationId']/option[2]")))
    first_area_option.click()
    
    # ==========================================
    # PART 3: SUBMIT AND VERIFY
    # ==========================================
    
    # Click "Add Record" button
    submit_btn = driver.find_element(By.XPATH, "//form//button[contains(., 'Add Record')]")
    submit_btn.click()
    
    # Verify the system displays the success banner
    try:
        success_alert = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class, 'text-green-800') and contains(text(), 'successfully')]"
        )))
        assert success_alert.is_displayed(), "Test Failed: Success banner was not displayed after submitting the form."
    except Exception:
        pytest.fail("Test Failed: Timeout waiting for the form submission success banner.")
        
    time.sleep(2) # Allow React to refresh the table
    
    # Verify the newly added record appears in the table (check for 32°C and 12.5mm)
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    record_found = any("32" in row.text and "12.5" in row.text for row in rows)
    
    assert record_found is True, "Test Failed: The newly submitted record (32°C, 12.5mm) is not displaying in the table."