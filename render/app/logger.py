import logging
import sys

def setup_logging():
    # Force stdout to be unbuffered to ensure logs appear immediately in Render
    # This is a common fix for Python logging in containerized environments
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers (e.g., from FastAPI/Uvicorn defaults)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(logging.INFO)

    # Simple, clear formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # Capture logs from uvicorn and other libraries
    for name in ["uvicorn", "uvicorn.error", "fastapi"]:
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = []
        lib_logger.propagate = True

    logging.info("NORMA AI: Unified logging system initialized.")
    return root_logger

logger = setup_logging()
