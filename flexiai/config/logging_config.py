# FILE: flexiai/config/logging_config.py

"""
Configures application-wide logging with rotating file and console handlers.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(
        root_level: int = logging.DEBUG,
        file_level: int = logging.DEBUG,
        console_level: int = logging.INFO,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True
        ) -> None:
    """Configure root, file, and console logging.

    Sets up:
      - Root logger at `root_level`.
      - RotatingFileHandler writing to 'logs/app.log' (max 5 MB, 3 backups) at `file_level`.
      - StreamHandler (console) at `console_level`.
      - Formatter: '%(asctime)s - %(levelname)s - %(filename)s - %(message)s'.

    Args:
        root_level (int): Logging level for the root logger.
        file_level (int): Logging level for the file handler.
        console_level (int): Logging level for the console handler.
        enable_file_logging (bool): Whether to enable file logging.
        enable_console_logging (bool): Whether to enable console logging.

    Returns:
        None

    Side effects:
        - Creates the 'logs/' directory if it does not exist.
        - Clears existing handlers on the root logger.
        - Prints directory and creation status to stdout.

    Raises:
        OSError: If the log directory cannot be created.
    """
    # Print current working directory to ensure we are in the correct location
    current_directory = os.getcwd()
    print(f"Current working directory: {current_directory}")

    # Define log directory and file relative to the project root
    log_directory = os.path.join(current_directory, "logs")
    log_file = os.path.join(log_directory, "app.log")

    # Ensure the log directory exists
    try:
        os.makedirs(log_directory, exist_ok=True)
        print(f"Log directory '{log_directory}' created/exists.")
    except OSError as e:
        print(f"Error creating log directory {log_directory}: {e}")
        return

    # Get the root logger instance
    logger = logging.getLogger()

    # Clear existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    try:
        # Set the logging level for the root logger
        logger.setLevel(root_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
        )

        if enable_file_logging:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,
                backupCount=3
            )
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    except Exception as e:
        print(f"Error setting up logging: {e}")
