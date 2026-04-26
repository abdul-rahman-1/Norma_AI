import logging
import sys

def setup_logging():
    # Force unbuffered output so logs appear instantly in Render/Docker
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    # Use the root logger to capture everything
    logging_level = logging.INFO
    
    # Simple, standard formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set up stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    
    # Only add handler if not already present to prevent duplicates
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(stdout_handler)

    # Ensure library loggers propagate to root
    for name in ["uvicorn", "uvicorn.error", "fastapi", "app"]:
        logger = logging.getLogger(name)
        logger.setLevel(logging_level)
        logger.propagate = True

    logging.info("NORMA AI: Unified Render-compliant logging active.")
    return root_logger

logger = setup_logging()
