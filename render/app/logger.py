import logging
import sys

def setup_logging():
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Formatter for Render logs (Clean, one line per log)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Stream handler for stdout (Render captures this)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    logging.info("NORMA AI: Structured logging initialized.")
    return logger

logger = setup_logging()
