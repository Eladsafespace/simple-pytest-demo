import uuid
import pytest
import logging
import os
import platform
import sys
import tempfile
import socket
import json
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_selenium_server(host, port):
    """Check if Selenium server is running and return status info."""
    try:
        url = f"http://{host}:{port}/wd/hub/status"
        logger.info(f"Checking Selenium server at {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Selenium server status: {json.dumps(data, indent=2)}")
            return True, data
        else:
            logger.error(f"Selenium server returned status code: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Selenium server at {host}:{port}")
        return False, None
    except Exception as e:
        logger.error(f"Error checking Selenium server: {str(e)}")
        return False, None

def check_container_processes():
    """Run ps command to check for Selenium/Chrome processes."""
    try:
        logger.info("Checking all processes in container:")
        result = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "chrome" in line.lower() or "selenium" in line.lower() or "java" in line.lower():
                logger.info(f"  {line.strip()}")
        
        logger.info("Checking for listening ports:")
        result = subprocess.run(["netstat", "-tuln"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "LISTEN" in line:
                logger.info(f"  {line.strip()}")
    except Exception as e:
        logger.error(f"Error checking container processes: {str(e)}")

def pytest_addoption(parser):
    """Add command-line options for browser selection."""
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome", 
        help="Browser to run tests: chrome or firefox"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--selenium-host",
        action="store",
        default="localhost",
        help="Selenium Grid host"
    )
    parser.addoption(
        "--selenium-port",
        action="store",
        default="4444",
        help="Selenium Grid port"
    )
    parser.addoption(
        "--remote",
        action="store_true",
        default=False,
        help="Use RemoteWebDriver instead of local WebDriver"
    )


@pytest.fixture(scope="session")
def browser_name(request):
    """Get the browser name from command line option."""
    browser = request.config.getoption("--browser")
    logger.info(f"Selected browser: {browser}")
    return browser


@pytest.fixture(scope="session")
def headless(request):
    """Get the headless mode from command line option."""
    is_headless = request.config.getoption("--headless")
    logger.info(f"Headless mode: {is_headless}")
    return is_headless


@pytest.fixture(scope="session")
def selenium_host(request):
    """Get the Selenium Grid host."""
    host = request.config.getoption("--selenium-host")
    logger.info(f"Selenium host: {host}")
    return host


@pytest.fixture(scope="session")
def selenium_port(request):
    """Get the Selenium Grid port."""
    port = request.config.getoption("--selenium-port")
    logger.info(f"Selenium port: {port}")
    return port


@pytest.fixture(scope="session")
def use_remote(request):
    """Whether to use RemoteWebDriver."""
    remote = request.config.getoption("--remote")
    logger.info(f"Using RemoteWebDriver: {remote}")
    return remote


@pytest.fixture
def driver(browser_name, headless, selenium_host, selenium_port, use_remote):
    """
    Set up WebDriver instance based on browser selection.
    
    Usage:
        pytest --browser=chrome --remote --selenium-host=localhost --selenium-port=4444
        pytest --browser=chrome  # for local WebDriver
    """
    logger.info(f"Setting up {'Remote' if use_remote else 'Local'} WebDriver for {browser_name}")
    logger.info(f"System info: {platform.platform()}, Python: {platform.python_version()}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Check if running in Selenium container
    in_selenium_container = os.path.exists('/opt/selenium') or os.environ.get('HOME') == '/home/seluser'
    logger.info(f"Running in Selenium container: {in_selenium_container}")
    
    # Always check container environment
    check_container_processes()
    
    # If remote is specified or we're in a Selenium container, check Selenium server
    if use_remote or in_selenium_container:
        server_running, server_info = check_selenium_server(selenium_host, selenium_port)
        logger.info(f"Selenium server running: {server_running}")
    
    try:
        if browser_name.lower() == "chrome":
            options = ChromeOptions()
            logger.info("Initializing Chrome options")
            
            if headless:
                logger.info("Adding --headless argument")
                options.add_argument("--headless=new")
            
            logger.info("Adding --no-sandbox argument")
            options.add_argument("--no-sandbox")
            
            logger.info("Adding --disable-dev-shm-usage argument")
            options.add_argument("--disable-dev-shm-usage")
            
            # Add user-data-dir for better session management
            user_data_dir = os.path.join(tempfile.gettempdir(), f"chrome-user-data-{uuid.uuid4()}")
            logger.info(f"Adding --user-data-dir argument: {user_data_dir}")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Log Chrome options
            logger.info(f"Chrome options: {options.arguments}")
            
            # Use RemoteWebDriver if specified or if we're in a Selenium container
            if use_remote or in_selenium_container:
                # Set up RemoteWebDriver
                selenium_url = f"http://{selenium_host}:{selenium_port}/wd/hub"
                logger.info(f"Connecting to Selenium Grid at: {selenium_url}")
                
                driver = webdriver.Remote(
                    command_executor=selenium_url,
                    options=options
                )
                logger.info(f"RemoteWebDriver session created with ID: {driver.session_id}")
            else:
                # Use local ChromeDriver
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                logger.info("Installing ChromeDriver")
                chrome_driver_path = ChromeDriverManager().install()
                logger.info(f"ChromeDriver installed at: {chrome_driver_path}")
                
                logger.info("Creating Chrome WebDriver instance")
                driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
                logger.info(f"ChromeDriver session created with ID: {driver.session_id}")
                
        elif browser_name.lower() == "firefox":
            options = FirefoxOptions()
            logger.info("Initializing Firefox options")
            
            if headless:
                logger.info("Adding --headless argument to Firefox")
                options.add_argument("--headless")
                
            logger.info(f"Firefox options: {options.arguments}")
            
            if use_remote or in_selenium_container:
                # Set up RemoteWebDriver
                selenium_url = f"http://{selenium_host}:{selenium_port}/wd/hub"
                logger.info(f"Connecting to Selenium Grid at: {selenium_url}")
                
                driver = webdriver.Remote(
                    command_executor=selenium_url,
                    options=options
                )
                logger.info(f"RemoteWebDriver session created with ID: {driver.session_id}")
            else:
                # Use local GeckoDriver
                from selenium.webdriver.firefox.service import Service
                from webdriver_manager.firefox import GeckoDriverManager
                
                logger.info("Installing GeckoDriver")
                gecko_driver_path = GeckoDriverManager().install()
                logger.info(f"GeckoDriver installed at: {gecko_driver_path}")
                
                logger.info("Creating Firefox WebDriver instance")
                driver = webdriver.Firefox(service=Service(gecko_driver_path), options=options)
                logger.info(f"GeckoDriver session created with ID: {driver.session_id}")
        else:
            error_msg = f"Unsupported browser: {browser_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Maximizing browser window")
        driver.maximize_window()
        
        yield driver
        
        logger.info(f"Quitting WebDriver session: {driver.session_id}")
        driver.quit()
        logger.info("WebDriver session terminated")
        
    except Exception as e:
        logger.error(f"Error creating WebDriver: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        
        if isinstance(e, SessionNotCreatedException):
            logger.error("=" * 80)
            logger.error("SessionNotCreatedException DETECTED")
            logger.error("=" * 80)
            logger.error(f"Exception message: {str(e)}")
            
            # Check for running Chrome processes
            try:
                logger.error("Running ps -ef to check all processes:")
                result = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
                logger.error(result.stdout)
                
                logger.error("Checking for Chrome user data directories:")
                result = subprocess.run(["find", "/tmp", "-name", "*chrome*"], capture_output=True, text=True)
                logger.error(result.stdout)
                
                logger.error("Checking Selenium server status:")
                status_result = subprocess.run(["curl", f"http://{selenium_host}:{selenium_port}/wd/hub/status"], 
                                            capture_output=True, text=True)
                logger.error(status_result.stdout)
            except Exception as check_e:
                logger.error(f"Error during diagnostic checks: {str(check_e)}")
                
        raise

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Log environment information at the start of the test session."""
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTING")
    logger.info("=" * 80)
    logger.info(f"OS: {platform.system()} {platform.release()} {platform.version()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Check container-specific information
    logger.info("Container information:")
    try:
        # Check if running in Docker
        in_docker = os.path.exists('/.dockerenv')
        logger.info(f"Running in Docker: {in_docker}")
        
        # Check hostname
        hostname = socket.gethostname()
        logger.info(f"Hostname: {hostname}")
        
        # Check important environment variables
        env_vars = ['HOME', 'USER', 'PATH', 'SELENIUM_BROWSER', 'DISPLAY', 
                    'CHROME_BIN', 'CHROMEWEBDRIVER', 'SE_OPTS']
        logger.info("Environment variables:")
        for var in env_vars:
            if var in os.environ:
                logger.info(f"  {var}: {os.environ[var]}")
                
        # Check if this is a Selenium container
        is_selenium_container = os.path.exists('/opt/selenium')
        logger.info(f"Is Selenium container: {is_selenium_container}")
        
        # Check Selenium-specific directories
        selenium_dirs = ['/opt/selenium', '/opt/bin', '/opt/drivers']
        for d in selenium_dirs:
            if os.path.exists(d):
                logger.info(f"Directory {d} exists")
                try:
                    files = os.listdir(d)
                    logger.info(f"  Contents: {', '.join(files[:5])}{' (more...)' if len(files) > 5 else ''}")
                except:
                    logger.info(f"  Could not list contents")
    except Exception as e:
        logger.info(f"Error checking container info: {str(e)}")
        
    logger.info("=" * 80)


def pytest_sessionfinish(session, exitstatus):
    """
    Hook that runs after the test session finishes.
    Log information about the test results.
    """
    logger.info("=" * 80)
    logger.info("TEST SESSION FINISHED")
    logger.info("=" * 80)
    logger.info(f"Exit status: {exitstatus}")
    
    # Log test summary
    if hasattr(session, 'testscollected'):
        logger.info(f"Total tests collected: {session.testscollected}")
    if hasattr(session, 'testsfailed'):
        logger.info(f"Tests failed: {session.testsfailed}")
    
    logger.info("=" * 80) 