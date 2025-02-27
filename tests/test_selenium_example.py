import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.selenium
def test_google_search(driver):
    """
    A simple test that searches Google and verifies results appear.
    
    This test demonstrates how to use the driver fixture from conftest.py.
    """
    # Navigate to Google
    driver.get("https://www.google.com")
    
    # Accept cookies if the dialog appears (this may vary by region)
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
        ).click()
    except:
        # Cookie dialog might not appear, so we can continue
        pass
    
    # Find the search box and enter a query
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.send_keys("Selenium WebDriver")
    search_box.submit()
    
    # Verify search results appear
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
    
    # Assert that the page title contains our search query
    assert "Selenium WebDriver" in driver.title


@pytest.mark.selenium
def test_calculator_with_selenium(driver):
    """
    This test demonstrates how we could test our calculator in a web context.
    
    Note: This is a mock example as we don't have a web interface for our calculator.
    In a real project, you would navigate to your application's URL.
    """
    # This is a mock test - in a real project, you would navigate to your app
    driver.get("https://www.example.com")
    
    # For demonstration purposes only - showing how you might interact with a calculator UI
    # In a real test, you would use actual selectors from your application
    try:
        # Mock interaction with a calculator UI
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "calculator"))
        )
        
        # This is just to show the pattern - these elements don't exist on example.com
        # first_number = driver.find_element(By.ID, "first-number")
        # second_number = driver.find_element(By.ID, "second-number")
        # add_button = driver.find_element(By.ID, "add-button")
        # result = driver.find_element(By.ID, "result")
        
        # first_number.send_keys("2")
        # second_number.send_keys("3")
        # add_button.click()
        
        # WebDriverWait(driver, 5).until(
        #     EC.text_to_be_present_in_element((By.ID, "result"), "5")
        # )
        
        # assert result.text == "5"
        
    except:
        # Since this is a mock test, we expect it to not find these elements
        pytest.skip("This is a mock test - skipping actual assertions") 