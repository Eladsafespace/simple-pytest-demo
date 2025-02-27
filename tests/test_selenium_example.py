import pytest
import logging
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


@pytest.mark.selenium
def test_google_search(driver):
    """
    A simple test that searches Google and verifies results appear.
    
    This test demonstrates how to use the driver fixture from conftest.py.
    """
    logger.info("Starting test_google_search")
    
    # Log browser capabilities
    logger.info(f"Browser name: {driver.capabilities.get('browserName')}")
    logger.info(f"Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")
    
    # Navigate to Google
    logger.info("Navigating to Google")
    driver.get("https://www.google.com")
    logger.info(f"Current URL: {driver.current_url}")
    
    # Accept cookies if the dialog appears (this may vary by region)
    try:
        logger.info("Checking for cookie consent dialog")
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
        ).click()
        logger.info("Clicked 'Accept all' on cookie dialog")
    except Exception as e:
        logger.info("Cookie dialog not found or not clickable")
        # Cookie dialog might not appear, so we can continue
        pass
    
    # Find the search box and enter a query
    logger.info("Looking for search box")
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    logger.info("Found search box, entering query")
    search_box.send_keys("Selenium WebDriver")
    logger.info("Submitting search query")
    search_box.submit()
    
    # Verify search results appear
    logger.info("Waiting for search results")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )
    logger.info("Search results found")
    
    # Assert that the page title contains our search query
    logger.info(f"Page title: {driver.title}")
    assert "Selenium WebDriver" in driver.title
    logger.info("Test passed: Title contains search query")


@pytest.mark.selenium
def test_calculator_with_selenium(driver):
    """
    This test demonstrates how we could test our calculator in a web context.
    
    Note: This is a mock example as we don't have a web interface for our calculator.
    In a real project, you would navigate to your application's URL.
    """
    logger.info("Starting test_calculator_with_selenium")
    
    # Log browser capabilities
    logger.info(f"Browser name: {driver.capabilities.get('browserName')}")
    
    # This is a mock test - in a real project, you would navigate to your app
    logger.info("Navigating to example.com")
    driver.get("https://www.example.com")
    logger.info(f"Current URL: {driver.current_url}")
    logger.info(f"Page title: {driver.title}")
    
    # For demonstration purposes only - showing how you might interact with a calculator UI
    # In a real test, you would use actual selectors from your application
    try:
        # Mock interaction with a calculator UI
        logger.info("Looking for calculator element (expected to fail)")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "calculator"))
        )
        logger.info("Found calculator element (unexpected)")
        
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
        
    except Exception as e:
        # Since this is a mock test, we expect it to not find these elements
        logger.info("Expected exception occurred - calculator element not found")
        logger.info("Skipping test as expected - this is a mock test")
        pytest.skip("This is a mock test - skipping actual assertions") 