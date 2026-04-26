from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_phi_db, get_profile_db
from app.api import webhook
from app.logger import logger, log_buffer, log_listeners
from app.services.automation_service import automation_service
import asyncio
from datetime import datetime

app = FastAPI(title="Norma AI Standalone Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)

async def automation_loop():
    while True:
        try:
            await automation_service.run_upcoming_alerts()
            now = datetime.utcnow()
            if now.hour == 8 and now.minute == 0:
                await automation_service.send_doctor_daily_briefing()
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"AUTOMATION_LOOP ERROR: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    asyncio.create_task(automation_loop())

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

@app.get("/db-test")
async def test_db():
    """Diagnostic route to check DB connectivity and content."""
    phi = get_phi_db()
    profile = get_profile_db()
    try:
        p_count = await phi.patients.count_documents({})
        d_count = await profile.doctors.count_documents({})
        s_count = await profile.staff_users.count_documents({})
        return {
            "status": "connected",
            "database": phi.name,
            "counts": {
                "patients": p_count,
                "doctors": d_count,
                "staff": s_count
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/logs", response_class=HTMLResponse)
async def get_logs_page():
    """Returns a real-time auto-updating log viewer."""
    html_content = """
    <html>
        <head>
            <title>Norma AI - Live Logs</title>
            <style>
                body { background: #121212; color: #00ff00; font-family: 'Courier New', monospace; padding: 20px; }
                #log-container { border: 1px solid #333; padding: 10px; height: 80vh; overflow-y: scroll; display: flex; flex-direction: column-reverse; }
                .log-entry { margin-bottom: 5px; border-bottom: 1px solid #1a1a1a; padding-bottom: 2px; }
                .header { color: #fff; border-bottom: 2px solid #00ff00; padding-bottom: 10px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Norma AI - Live Terminal</h1>
                <p>Status: <span style="color: #00ff00;">● Operational</span> | Auto-updating</p>
            </div>
            <div id="log-container">
                <div id="logs"></div>
            </div>
            <script>
                const logContainer = document.getElementById('logs');
                const scrollContainer = document.getElementById('log-container');
                
                async function loadInitialLogs() {
                    const response = await fetch('/logs/raw');
                    const text = await response.text();
                    text.split('\\n').forEach(line => {
                        if (line.trim()) appendLog(line);
                    });
                }

                function appendLog(text) {
                    const div = document.createElement('div');
                    div.className = 'log-entry';
                    div.innerText = text;
                    logContainer.appendChild(div);
                    scrollContainer.scrollTop = scrollContainer.scrollHeight;
                }

                function startStreaming() {
                    const eventSource = new EventSource("/logs/stream");
                    eventSource.onmessage = function(event) {
                        appendLog(event.data);
                    };
                    eventSource.onerror = function() {
                        eventSource.close();
                        setTimeout(startStreaming, 2000);
                    };
                }

                loadInitialLogs().then(startStreaming);
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/logs/raw")
async def get_raw_logs():
    return Response(content="\n".join(log_buffer), media_type="text/plain")

@app.get("/logs/stream")
async def stream_logs():
    async def log_generator():
        queue = asyncio.Queue()
        log_listeners.append(queue)
        try:
            while True:
                log = await queue.get()
                yield f"data: {log}\n\n"
        except asyncio.CancelledError:
            log_listeners.remove(queue)
            raise
    return StreamingResponse(log_generator(), media_type="text/event-stream")

@app.get("/")
async def health():
    return {"status": "operational"}
