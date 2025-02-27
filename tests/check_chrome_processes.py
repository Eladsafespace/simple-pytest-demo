#!/usr/bin/env python
"""
Chrome Process Checker

This script checks for running Chrome processes and Chrome user data directories
in the temporary directory. It's useful for diagnosing SessionNotCreatedException
errors in Selenium tests.

Usage:
    python check_chrome_processes.py

"""

import os
import sys
import tempfile
import platform
import subprocess
import logging
import socket
import json
import time
import requests
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def run_shell_command(command):
    """Execute a shell command properly handling pipes."""
    try:
        # Use shell=True for commands with pipes
        if '|' in command:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
        else:
            # Split command for non-piped commands
            result = subprocess.run(command.split(), text=True, capture_output=True)
            
        if result.returncode != 0 and result.stderr:
            logging.error(f"  {result.stderr}")
        return result.stdout
    except Exception as e:
        logging.error(f"Error executing command '{command}': {e}")
        return ""

def check_chrome_processes():
    """Check for running Chrome processes."""
    logger.info("=" * 80)
    logger.info("CHECKING FOR CHROME PROCESSES")
    logger.info("=" * 80)
    
    try:
        # Check using ps
        logger.info("Using ps to check for Chrome processes:")
        run_shell_command("ps -ef")
        
        logger.info("Filtering for chrome processes:")
        run_shell_command("ps -ef | grep chrome")
        
        # Check using pgrep
        logger.info("Using pgrep to check for Chrome processes:")
        run_shell_command("pgrep -a chrome")
        
        # Try with psutil if available
        try:
            import psutil
            
            chrome_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if chrome_processes:
                logger.info(f"Found {len(chrome_processes)} Chrome processes using psutil:")
                for proc in chrome_processes:
                    logger.info(f"  PID: {proc['pid']}, Name: {proc['name']}")
                    if proc.get('cmdline'):
                        logger.info(f"  Command: {' '.join(proc['cmdline'])}")
                    logger.info("-" * 40)
            else:
                logger.info("No Chrome processes found using psutil")
        except ImportError:
            logger.warning("psutil not installed, skipping psutil checks")
            
    except Exception as e:
        logger.error(f"Error checking Chrome processes: {str(e)}")
    
    logger.info("=" * 80)

def check_chrome_user_data_dirs():
    """Check for Chrome user data directories in temp."""
    logger.info("=" * 80)
    logger.info("CHECKING FOR CHROME USER DATA DIRECTORIES")
    logger.info("=" * 80)
    
    temp_dir = tempfile.gettempdir()
    logger.info(f"Temporary directory: {temp_dir}")
    
    try:
        # Check using find
        logger.info("Using find to search for Chrome directories:")
        stdout = run_shell_command(f"find {temp_dir} -name '*chrome*' -type d -print")
        
        if stdout:
            chrome_dirs = stdout.strip().split('\n')
            logger.info(f"Found {len(chrome_dirs)} Chrome-related directories:")
            for chrome_dir in chrome_dirs:
                if os.path.isdir(chrome_dir):
                    try:
                        size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                                for dirpath, _, filenames in os.walk(chrome_dir) 
                                for filename in filenames)
                        logger.info(f"  {chrome_dir} (Size: {size/1024/1024:.2f} MB)")
                    except:
                        logger.info(f"  {chrome_dir} (Size: unknown)")
                    
                    # Check if directory is locked
                    try:
                        test_file = os.path.join(chrome_dir, 'test_lock')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        logger.info(f"  Directory is NOT locked")
                    except Exception as e:
                        logger.info(f"  Directory appears to be LOCKED: {str(e)}")
        else:
            logger.info("No Chrome-related directories found using find")
            
        # Check using ls
        logger.info(f"Contents of {temp_dir}:")
        run_shell_command(f"ls -la {temp_dir}")
            
    except Exception as e:
        logger.error(f"Error checking Chrome directories: {str(e)}")
    
    logger.info("=" * 80)

def check_system_info():
    """Log system information."""
    logger.info("=" * 80)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 80)
    
    logger.info(f"OS: {platform.system()} {platform.release()} {platform.version()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Temp directory: {tempfile.gettempdir()}")
    
    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv')
    logger.info(f"Running in Docker: {in_docker}")
    
    # Check hostname
    hostname = socket.gethostname()
    logger.info(f"Hostname: {hostname}")
    
    # Check if this is a Selenium container
    is_selenium_container = os.path.exists('/opt/selenium') or os.environ.get('HOME') == '/home/seluser'
    logger.info(f"Is Selenium container: {is_selenium_container}")
    
    # Check Chrome installation
    try:
        if platform.system() == 'Linux':
            chrome_locations = [
                '/usr/bin/google-chrome',
                '/usr/bin/chrome',
                '/opt/google/chrome/chrome',
                '/usr/local/bin/chrome'
            ]
            
            for loc in chrome_locations:
                if os.path.exists(loc):
                    logger.info(f"Chrome found at: {loc}")
                    try:
                        stdout = run_shell_command(f"{loc} --version")
                        if stdout:
                            logger.info(f"Chrome version: {stdout.strip()}")
                    except:
                        pass
            
            # Check ChromeDriver
            chromedriver_locations = [
                '/usr/bin/chromedriver',
                '/usr/local/bin/chromedriver',
                '/opt/selenium/chromedriver'
            ]
            
            for loc in chromedriver_locations:
                if os.path.exists(loc):
                    logger.info(f"ChromeDriver found at: {loc}")
                    try:
                        stdout = run_shell_command(f"{loc} --version")
                        if stdout:
                            logger.info(f"ChromeDriver version: {stdout.strip()}")
                    except:
                        pass
        
    except Exception as e:
        logger.info(f"Failed to detect Chrome: {str(e)}")
    
    # Log environment variables
    logger.info("Environment Variables:")
    for var in sorted(os.environ.keys()):
        if var.lower() in ['home', 'user', 'path', 'temp', 'tmp', 'display'] or 'chrome' in var.lower() or 'selenium' in var.lower():
            logger.info(f"  {var}: {os.environ.get(var)}")
    
    logger.info("=" * 80)

def check_selenium_grid():
    """Check if Selenium Grid is running."""
    logger.info("=" * 80)
    logger.info("CHECKING SELENIUM GRID")
    logger.info("=" * 80)
    
    hosts = ['localhost', '127.0.0.1', '0.0.0.0']
    ports = ['4444', '5555']
    
    for host in hosts:
        for port in ports:
            try:
                url = f"http://{host}:{port}/wd/hub/status"
                logger.info(f"Checking Selenium Grid at {url}")
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Selenium Grid is running at {url}")
                    logger.info(f"Status: {json.dumps(data, indent=2)}")
                    
                    # Check sessions
                    try:
                        sessions_url = f"http://{host}:{port}/wd/hub/sessions"
                        sessions_response = requests.get(sessions_url, timeout=2)
                        if sessions_response.status_code == 200:
                            sessions_data = sessions_response.json()
                            logger.info(f"Active sessions: {json.dumps(sessions_data, indent=2)}")
                    except:
                        pass
                else:
                    logger.info(f"Selenium Grid returned status code: {response.status_code} at {url}")
            except requests.exceptions.ConnectionError:
                logger.info(f"Cannot connect to Selenium Grid at {host}:{port}")
            except Exception as e:
                logger.info(f"Error checking Selenium Grid at {host}:{port}: {str(e)}")
    
    # Check if selenium-server process is running
    logger.info("Checking for Selenium server process:")
    run_shell_command("ps -ef | grep selenium-server")
    
    # Check listening ports
    logger.info("Checking listening ports:")
    run_shell_command("netstat -tuln")
    
    logger.info("=" * 80)

def check_file_permissions():
    """Check file permissions in important directories."""
    logger.info("=" * 80)
    logger.info("CHECKING FILE PERMISSIONS")
    logger.info("=" * 80)
    
    directories = [
        '/tmp',
        '/dev/shm',
        '/home/seluser',
        '/opt/selenium'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            logger.info(f"Checking permissions for {directory}:")
            run_shell_command(f"ls -la {directory}")
            
            # Try to write a test file
            try:
                test_file = os.path.join(directory, f'test_file_{int(time.time())}')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info(f"Successfully wrote and removed test file in {directory}")
            except Exception as e:
                logger.info(f"Failed to write test file in {directory}: {str(e)}")
    
    logger.info("=" * 80)

if __name__ == "__main__":
    logger.info("Chrome Process Checker")
    check_system_info()
    check_chrome_processes()
    check_chrome_user_data_dirs()
    check_selenium_grid()
    check_file_permissions()
    logger.info("Check complete") 