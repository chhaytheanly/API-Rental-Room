import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

def setup_logger():
    logger = logging.getLogger("security_audit")
    logger.setLevel(logging.INFO)

    # Format: Time | Level | IP | OS | Device | Message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler (Rotating: 10MB max, keep 5 backup files)
    fh = RotatingFileHandler("logs/security_audit.log", maxBytes=10*1024*1024, backupCount=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

security_logger = setup_logger()