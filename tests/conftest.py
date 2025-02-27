import uuid
import pytest
import logging
import os
import platform
import sys
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import SessionNotCreatedException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

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


@pytest.fixture
def driver(browser_name, headless, selenium_host, selenium_port):
    """
    Set up WebDriver instance for Selenium Grid.
    
    Usage:
        pytest --browser=chrome
        pytest --selenium-host=localhost --selenium-port=4444
    """
    logger.info(f"Setting up RemoteWebDriver for {browser_name}")
    logger.info(f"System info: {platform.platform()}, Python: {platform.python_version()}")
    
    try:
        # Create RemoteWebDriver options
        if browser_name.lower() == "chrome":
            options = ChromeOptions()
            logger.info("Initializing Chrome options")
            
            if headless:
                logger.info("Adding --headless argument")
                options.add_argument("--headless")
            
            logger.info("Adding --no-sandbox argument")
            options.add_argument("--no-sandbox")
            
            logger.info("Adding --disable-dev-shm-usage argument")
            options.add_argument("--disable-dev-shm-usage")
            
        elif browser_name.lower() == "firefox":
            options = FirefoxOptions()
            logger.info("Initializing Firefox options")
            
            if headless:
                logger.info("Adding --headless argument to Firefox")
                options.add_argument("--headless")
        else:
            error_msg = f"Unsupported browser: {browser_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Set up RemoteWebDriver
        selenium_url = f"http://{selenium_host}:{selenium_port}/wd/hub"
        logger.info(f"Connecting to Selenium Grid at: {selenium_url}")
        
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
        
        logger.info("RemoteWebDriver session created successfully")
        logger.info(f"Session ID: {driver.session_id}")
        
        # Wait for browser to be ready
        logger.info("Maximizing browser window")
        driver.maximize_window()
        
        yield driver
        
        logger.info("Quitting WebDriver session")
        driver.quit()
        logger.info("WebDriver session terminated")
        
    except Exception as e:
        logger.error(f"Error creating WebDriver: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(call, report):
    """
    Hook to capture and log exceptions during test execution.
    Specifically focused on SessionNotCreatedException.
    """
    if call.excinfo is not None:
        exception = call.excinfo.value
        if isinstance(exception, SessionNotCreatedException):
            logger.error("=" * 80)
            logger.error("SessionNotCreatedException DETECTED IN HOOK")
            logger.error("=" * 80)
            logger.error(f"Exception message: {str(exception)}")
            
            # Check for running Chrome processes
            try:
                import subprocess
                import psutil
                
                logger.error("Checking for running Chrome processes:")
                chrome_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc.info)
                
                if chrome_processes:
                    logger.error(f"Found {len(chrome_processes)} Chrome processes running:")
                    for proc in chrome_processes[:5]:  # Limit to first 5 to avoid log spam
                        logger.error(f"  PID: {proc['pid']}, Name: {proc['name']}")
                else:
                    logger.error("No Chrome processes found running")
                    
                # Check for Chrome user data directories
                logger.error("Checking for Chrome user data directories:")
                temp_dir = tempfile.gettempdir()
                try:
                    chrome_dirs = [d for d in os.listdir(temp_dir) if 'chrome' in d.lower()]
                    if chrome_dirs:
                        logger.error(f"Found Chrome directories in temp: {chrome_dirs[:5]}")
                    else:
                        logger.error("No Chrome directories found in temp")
                except Exception as e:
                    logger.error(f"Error checking temp directories: {str(e)}")
                    
            except ImportError:
                logger.error("psutil not installed, skipping process check")
            except Exception as e:
                logger.error(f"Error checking Chrome processes: {str(e)}")
                
            logger.error("=" * 80)


def pytest_sessionstart(session):
    """
    Hook that runs before the test session starts.
    Log information about the test environment.
    """
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTING")
    logger.info("=" * 80)
    
    # Log system information
    logger.info(f"OS: {platform.system()} {platform.release()} {platform.version()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"pytest: {pytest.__version__}")
    
    # Log current working directory and temp directory
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Temp directory: {tempfile.gettempdir()}")
    
    # Check if Chrome is installed and log its version
    try:
        import subprocess
        if platform.system() == 'Linux':
            chrome_path = subprocess.check_output(['which', 'google-chrome']).decode().strip()
            chrome_version = subprocess.check_output(['google-chrome', '--version']).decode().strip()
        elif platform.system() == 'Darwin':  # macOS
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            if os.path.exists(chrome_path):
                chrome_version = subprocess.check_output([chrome_path, '--version']).decode().strip()
            else:
                chrome_path = 'Not found'
                chrome_version = 'Not installed'
        elif platform.system() == 'Windows':
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                chrome_path = winreg.QueryValue(key, None)
                chrome_version = subprocess.check_output([chrome_path, '--version']).decode().strip()
            except:
                chrome_path = 'Not found in registry'
                chrome_version = 'Unknown'
        
        logger.info(f"Chrome path: {chrome_path}")
        logger.info(f"Chrome version: {chrome_version}")
    except Exception as e:
        logger.info(f"Failed to detect Chrome: {str(e)}")
    
    # Log available browsers from webdriver_manager
    try:
        logger.info("Available browser drivers:")
        logger.info(f"  Chrome driver: {ChromeDriverManager().driver_version}")
        logger.info(f"  Firefox driver: {GeckoDriverManager().driver_version}")
    except Exception as e:
        logger.info(f"Failed to get browser driver versions: {str(e)}")
    
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