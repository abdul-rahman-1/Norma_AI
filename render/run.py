import uvicorn
import os
import sys
import multiprocessing
import time
from app.logger import logger

# Add the current directory (render/) to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_server(port):
    """Function to run uvicorn in a separate process."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    while True:
        logger.info(f"NORMA AI: Starting WhatsApp Orchestrator on port {port}")
        p = multiprocessing.Process(target=start_server, args=(port,))
        p.start()
        
        print(f"\n[SYSTEM] Server is LIVE. Type 'r' and press ENTER to restart, or 'q' to quit.")
        
        while True:
            line = sys.stdin.readline()
            if not line: # EOF
                # In background/non-interactive mode, just wait forever
                while True: time.sleep(3600)
            
            cmd = line.strip().lower()
            if cmd == 'r':
                logger.info("RESTARTING SERVER...")
                p.terminate()
                p.join()
                break # Break inner loop to restart
            elif cmd == 'q':
                logger.info("STOPPING SERVER...")
                p.terminate()
                p.join()
                sys.exit(0)
            else:
                print("Unknown command. Type 'r' to restart.")
