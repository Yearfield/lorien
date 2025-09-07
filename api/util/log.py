import logging
import os

def get_logger(name="lorien"):
    level = os.getenv("LORIEN_LOG_LEVEL", "WARNING").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
