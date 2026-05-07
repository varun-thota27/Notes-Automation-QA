import logging
import os
from datetime import datetime

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logs folder if it doesn't exist
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Log file name with timestamp
LOG_FILE = os.path.join(LOGS_DIR, f"test_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with a consistent format.

    Each module should call: logger = get_logger(__name__)
    Logs are written to both console (terminal) and file (logs/ folder)
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler (prints to terminal)
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        # logger.addHandler(console_handler)
        
        # File handler (saves to logs folder)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)
        
        logger.propagate = False
    return logger
