import logging
import sys
import asyncio
from collections import deque

# In-memory log buffer for the /logs route
log_buffer = deque(maxlen=100)
# List of active log listeners (asyncio queues)
log_listeners = []

class MemoryHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            log_buffer.append(log_entry)
            
            # Broadcast to all active listeners
            for listener in log_listeners:
                try:
                    # Use call_soon_threadsafe because logging can happen from any thread
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.call_soon_threadsafe(listener.put_nowait, log_entry)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)

def setup_logging():
    # Force unbuffered output
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    logging_level = logging.INFO
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)

    # Clear handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Stdout Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)

    # Memory Handler for /logs route
    mem_handler = MemoryHandler()
    mem_handler.setFormatter(formatter)
    root_logger.addHandler(mem_handler)

    # Propagation
    for name in ["uvicorn", "uvicorn.error", "fastapi", "app"]:
        l = logging.getLogger(name)
        l.setLevel(logging_level)
        l.propagate = True

    logging.info("NORMA AI: Unified Logging + Memory Buffer initialized.")
    return root_logger

logger = setup_logging()
