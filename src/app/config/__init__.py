import importlib

from .session import get_db, local_session
from .config import settings
from .scheduler import init_scheduler, shutdown_scheduler, get_scheduler

security_logger = None

def get_security_logger():
    """
    Lazily import and return the security_logger to avoid side effects at import time.
    """
    global security_logger
    if security_logger is None:
        logger_module = importlib.import_module('.logger', __package__)
        security_logger_instance = logger_module.security_logger
        globals()['security_logger'] = security_logger_instance
        security_logger = security_logger_instance
    return security_logger
