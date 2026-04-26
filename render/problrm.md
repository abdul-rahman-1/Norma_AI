2026-04-26T04:52:41.800670481Z ==> Deploying...
2026-04-26T04:52:41.858590979Z ==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
2026-04-26T04:52:56.077337964Z ==> Running 'python run.py'
2026-04-26T04:53:01.478208431Z [2026-04-26 04:53:01] INFO: NORMA AI: Unified Render-compliant logging active.
2026-04-26T04:53:01.478316634Z [2026-04-26 04:53:01] INFO: NORMA AI: Starting WhatsApp Orchestrator on port 5000
2026-04-26T04:53:22.582363565Z /opt/render/project/src/render/app/services/ai_service.py:1: FutureWarning: 
2026-04-26T04:53:22.582392706Z 
2026-04-26T04:53:22.582397866Z All support for the `google.generativeai` package has ended. It will no longer be receiving 
2026-04-26T04:53:22.582404176Z updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
2026-04-26T04:53:22.582409606Z See README for more details:
2026-04-26T04:53:22.582414106Z 
2026-04-26T04:53:22.582418686Z https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
2026-04-26T04:53:22.582422856Z 
2026-04-26T04:53:22.582427387Z   import google.generativeai as genai
2026-04-26T04:53:22.786795327Z INFO:     Started server process [59]
2026-04-26T04:53:22.786817628Z INFO:     Waiting for application startup.
2026-04-26T04:53:26.942005557Z [2026-04-26 04:53:26] INFO: --- DATABASE CONNECTED ---
2026-04-26T04:53:26.942046488Z [2026-04-26 04:53:26] INFO: PHI DB: clinic_default_phi
2026-04-26T04:53:26.942058948Z [2026-04-26 04:53:26] INFO: Profile DB: clinic_default_profile
2026-04-26T04:53:26.942489549Z INFO:     Application startup complete.
2026-04-26T04:53:26.943156347Z INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
2026-04-26T04:53:27.649542141Z INFO:     127.0.0.1:39800 - "HEAD / HTTP/1.1" 405 Method Not Allowed
2026-04-26T04:53:33.174662616Z ==> Your service is live 🎉
2026-04-26T04:53:33.275549697Z INFO:     35.197.37.4:0 - "GET / HTTP/1.1" 200 OK
2026-04-26T04:53:33.315840604Z ==> 
2026-04-26T04:53:33.318332618Z ==> ///////////////////////////////////////////////////////////
2026-04-26T04:53:33.320719479Z ==> 
2026-04-26T04:53:33.323324415Z ==> Available at your primary URL https://twilio-server-tek9.onrender.com
2026-04-26T04:53:33.325685337Z ==> 
2026-04-26T04:53:33.328498287Z ==> ///////////////////////////////////////////////////////////



still no logs at all make a custom loggeet at the /log rout where we can se our sever logs 

and 

me : Hi
bot : I encountered a clinical error. Please try again later.