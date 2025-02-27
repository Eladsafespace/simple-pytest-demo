#!/usr/bin/env python
"""
Direct Selenium Test

This script directly tests the Selenium server without using pytest.
It's useful for diagnosing connection issues with the Selenium container.

Usage:
    python test_selenium_direct.py [host] [port]
"""

import sys
import logging
import time
import json
import socket
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_selenium_server(host, port):
    """Check if Selenium server is running."""
    try:
        url = f"http://{host}:{port}/wd/hub/status"
        logger.info(f"Checking Selenium server at {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Selenium server status: {json.dumps(data, indent=2)}")
            return True
        else:
            logger.error(f"Selenium server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Selenium server at {host}:{port}")
        return False
    except Exception as e:
        logger.error(f"Error checking Selenium server: {str(e)}")
        return False

def test_remote_webdriver(host, port):
    """Test connecting to Selenium Grid with RemoteWebDriver."""
    logger.info("=" * 80)
    logger.info(f"TESTING REMOTE WEBDRIVER CONNECTION TO {host}:{port}")
    logger.info("=" * 80)
    
    if not check_selenium_server(host, port):
        logger.error("Selenium server not available, cannot test RemoteWebDriver")
        return
    
    try:
        # Create Chrome options
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        logger.info(f"Chrome options: {options.arguments}")
        
        # Create RemoteWebDriver
        selenium_url = f"http://{host}:{port}/wd/hub"
        logger.info(f"Connecting to Selenium Grid at: {selenium_url}")
        
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
        
        logger.info(f"RemoteWebDriver session created with ID: {driver.session_id}")
        
        # Test navigation
        logger.info("Navigating to example.com")
        driver.get("https://www.example.com")
        logger.info(f"Current URL: {driver.current_url}")
        logger.info(f"Page title: {driver.title}")
        
        # Take screenshot
        screenshot_file = "selenium_test_screenshot.png"
        driver.save_screenshot(screenshot_file)
        logger.info(f"Screenshot saved to {screenshot_file}")
        
        # Get browser information
        logger.info(f"Browser name: {driver.capabilities.get('browserName')}")
        logger.info(f"Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")
        
        # Quit driver
        logger.info("Quitting RemoteWebDriver")
        driver.quit()
        logger.info("RemoteWebDriver test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing RemoteWebDriver: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")

def main():
    """Main function."""
    # Get host and port from command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = sys.argv[2] if len(sys.argv) > 2 else "4444"
    
    logger.info(f"Testing Selenium server at {host}:{port}")
    
    # Log system info
    logger.info(f"Hostname: {socket.gethostname()}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Test RemoteWebDriver
    test_remote_webdriver(host, port)

if __name__ == "__main__":
    main() 