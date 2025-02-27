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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_chrome_processes():
    """Check for running Chrome processes."""
    logger.info("=" * 80)
    logger.info("CHECKING FOR CHROME PROCESSES")
    logger.info("=" * 80)
    
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
            logger.info(f"Found {len(chrome_processes)} Chrome processes running:")
            for proc in chrome_processes:
                logger.info(f"  PID: {proc['pid']}, Name: {proc['name']}")
                if proc.get('cmdline'):
                    logger.info(f"  Command: {' '.join(proc['cmdline'])}")
                logger.info("-" * 40)
        else:
            logger.info("No Chrome processes found running")
            
    except ImportError:
        logger.error("psutil not installed, cannot check processes")
        logger.error("Install with: pip install psutil")
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
        all_dirs = os.listdir(temp_dir)
        chrome_dirs = [d for d in all_dirs if 'chrome' in d.lower()]
        
        if chrome_dirs:
            logger.info(f"Found {len(chrome_dirs)} Chrome-related directories in temp:")
            for chrome_dir in chrome_dirs:
                full_path = os.path.join(temp_dir, chrome_dir)
                if os.path.isdir(full_path):
                    size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                              for dirpath, _, filenames in os.walk(full_path) 
                              for filename in filenames)
                    logger.info(f"  {chrome_dir} (Size: {size/1024/1024:.2f} MB)")
                    
                    # Check if directory is locked
                    try:
                        test_file = os.path.join(full_path, 'test_lock')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        logger.info(f"  Directory is NOT locked")
                    except Exception as e:
                        logger.info(f"  Directory appears to be LOCKED: {str(e)}")
        else:
            logger.info("No Chrome-related directories found in temp")
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
    
    # Check if Chrome is installed and log its version
    try:
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
    
    # Log environment variables that might be relevant
    logger.info("Environment Variables:")
    for var in ['HOME', 'TEMP', 'TMP', 'USER', 'PATH']:
        if var in os.environ:
            logger.info(f"  {var}: {os.environ.get(var)}")
    
    # Log Chrome-specific environment variables
    chrome_vars = [v for v in os.environ if 'CHROME' in v]
    for var in chrome_vars:
        logger.info(f"  {var}: {os.environ.get(var)}")
    
    logger.info("=" * 80)

if __name__ == "__main__":
    logger.info("Chrome Process Checker")
    check_system_info()
    check_chrome_processes()
    check_chrome_user_data_dirs()
    logger.info("Check complete") 