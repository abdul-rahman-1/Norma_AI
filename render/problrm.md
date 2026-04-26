my message: Hi , I am Abdul Rahman. remember me ??
serveere responce: Hello Abdul Rahman! Yes, I remember you. We were just in the process of getting you registered as a new patient. To complete your registration, I'll need your full name, date of birth, and gender. Could you please provide these details?

to gemini cli : see it didnt recognize me and themost big problem is that it is not looging the log in the rendeer.com logs terminal 


the log only iget are {

2026-04-26T04:11:06.061134551Z   Using cached grpcio_status-1.78.0-py3-none-any.whl.metadata (1.3 kB)
2026-04-26T04:11:06.064196475Z   Using cached grpcio_status-1.76.0-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:06.067362661Z   Using cached grpcio_status-1.75.1-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:06.06999707Z Collecting googleapis-common-protos<2.0.0,>=1.63.2 (from google-api-core->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:06.071151487Z   Using cached googleapis_common_protos-1.73.1-py3-none-any.whl.metadata (9.2 kB)
2026-04-26T04:11:06.075421838Z INFO: pip is still looking at multiple versions of grpcio-status to determine which version is compatible with other requirements. This could take a while.
2026-04-26T04:11:06.076988171Z   Using cached googleapis_common_protos-1.73.0-py3-none-any.whl.metadata (9.4 kB)
2026-04-26T04:11:06.150247747Z   Using cached googleapis_common_protos-1.72.0-py3-none-any.whl.metadata (9.4 kB)
2026-04-26T04:11:06.154089733Z INFO: This is taking longer than usual. You might need to provide the dependency resolver with stricter constraints to reduce runtime. See https://pip.pypa.io/warnings/backtracking for guidance. If you want to abort this run, press Ctrl + C.
2026-04-26T04:11:06.158224003Z   Using cached googleapis_common_protos-1.71.0-py3-none-any.whl.metadata (9.4 kB)
2026-04-26T04:11:06.165465688Z   Using cached googleapis_common_protos-1.70.0-py3-none-any.whl.metadata (9.3 kB)
2026-04-26T04:11:06.172752105Z   Using cached googleapis_common_protos-1.69.2-py3-none-any.whl.metadata (9.3 kB)
2026-04-26T04:11:06.180097552Z   Using cached googleapis_common_protos-1.69.1-py2.py3-none-any.whl.metadata (9.3 kB)
2026-04-26T04:11:06.187644961Z   Using cached googleapis_common_protos-1.69.0-py2.py3-none-any.whl.metadata (5.1 kB)
2026-04-26T04:11:06.194662173Z   Using cached googleapis_common_protos-1.68.0-py2.py3-none-any.whl.metadata (5.1 kB)
2026-04-26T04:11:06.201648345Z   Using cached googleapis_common_protos-1.67.0-py2.py3-none-any.whl.metadata (5.1 kB)
2026-04-26T04:11:06.208581156Z   Using cached googleapis_common_protos-1.66.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:06.327689689Z   Using cached googleapis_common_protos-1.65.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:06.335072606Z   Using cached googleapis_common_protos-1.64.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:06.341941336Z   Using cached googleapis_common_protos-1.63.2-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:06.349491376Z Collecting google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1 (from google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:06.350622272Z   Using cached google_api_core-2.30.2-py3-none-any.whl.metadata (3.1 kB)
2026-04-26T04:11:06.422769302Z   Using cached google_api_core-2.30.1-py3-none-any.whl.metadata (3.1 kB)
2026-04-26T04:11:06.745296944Z   Using cached google_api_core-2.30.0-py3-none-any.whl.metadata (3.1 kB)
2026-04-26T04:11:06.835488176Z Collecting googleapis-common-protos<2.0.0,>=1.56.3 (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1->google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:06.836198266Z   Using cached googleapis_common_protos-1.63.1-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:06.984603245Z   Using cached googleapis_common_protos-1.63.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.029756672Z Collecting protobuf (from google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:07.03093715Z   Using cached protobuf-4.25.9-cp37-abi3-manylinux2014_x86_64.whl.metadata (541 bytes)
2026-04-26T04:11:07.091533581Z Collecting googleapis-common-protos<2.0.0,>=1.56.3 (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1->google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:07.092771459Z   Using cached googleapis_common_protos-1.62.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.099308214Z   Using cached googleapis_common_protos-1.61.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.106194685Z   Using cached googleapis_common_protos-1.60.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.112685599Z   Using cached googleapis_common_protos-1.59.1-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.119119802Z   Using cached googleapis_common_protos-1.59.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.12785244Z   Using cached googleapis_common_protos-1.58.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.135857726Z   Using cached googleapis_common_protos-1.57.1-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.143850532Z   Using cached googleapis_common_protos-1.57.0-py2.py3-none-any.whl.metadata (1.5 kB)
2026-04-26T04:11:07.151869179Z   Using cached googleapis_common_protos-1.56.4-py2.py3-none-any.whl.metadata (1.3 kB)
2026-04-26T04:11:07.267538672Z   Using cached googleapis_common_protos-1.56.3-py2.py3-none-any.whl.metadata (1.3 kB)
2026-04-26T04:11:07.274527073Z Collecting google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1 (from google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:07.2756678Z   Using cached google_api_core-2.29.0-py3-none-any.whl.metadata (3.3 kB)
2026-04-26T04:11:08.004720316Z Collecting googleapis-common-protos<2.0.0,>=1.56.2 (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1->google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:08.006035875Z   Using cached googleapis_common_protos-1.56.2-py2.py3-none-any.whl.metadata (1.3 kB)
2026-04-26T04:11:08.057089618Z Collecting protobuf (from google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:08.058309286Z   Using cached protobuf-3.20.3-py2.py3-none-any.whl.metadata (720 bytes)
2026-04-26T04:11:08.115169893Z Collecting google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1 (from google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:08.116417701Z   Using cached google_api_core-2.28.1-py3-none-any.whl.metadata (3.3 kB)
2026-04-26T04:11:08.305106576Z   Using cached google_api_core-2.28.0-py3-none-any.whl.metadata (3.2 kB)
2026-04-26T04:11:08.492466772Z   Using cached google_api_core-2.27.0-py3-none-any.whl.metadata (3.2 kB)
2026-04-26T04:11:08.697693918Z   Using cached google_api_core-2.26.0-py3-none-any.whl.metadata (3.2 kB)
2026-04-26T04:11:08.8855306Z   Using cached google_api_core-2.25.2-py3-none-any.whl.metadata (3.0 kB)
2026-04-26T04:11:08.898292956Z Collecting grpcio-status<2.0.0,>=1.33.2 (from google-api-core[grpc]!=2.0.*,!=2.1.*,!=2.10.*,!=2.2.*,!=2.3.*,!=2.4.*,!=2.5.*,!=2.6.*,!=2.7.*,!=2.8.*,!=2.9.*,<3.0.0dev,>=1.34.1->google-ai-generativelanguage==0.6.15->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:08.899454993Z   Using cached grpcio_status-1.75.0-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.902871292Z   Using cached grpcio_status-1.74.0-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.906263812Z   Using cached grpcio_status-1.73.1-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.951770754Z   Using cached grpcio_status-1.73.0-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.955248474Z   Using cached grpcio_status-1.72.2-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.958665764Z   Using cached grpcio_status-1.72.1-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:08.962075774Z   Using cached grpcio_status-1.71.2-py3-none-any.whl.metadata (1.1 kB)
2026-04-26T04:11:09.172653377Z Collecting charset_normalizer<4,>=2 (from requests>=2.0.0->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.173937236Z   Using cached charset_normalizer-3.4.7-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
2026-04-26T04:11:09.195404398Z Collecting idna<4,>=2.5 (from requests>=2.0.0->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.196527025Z   Using cached idna-3.13-py3-none-any.whl.metadata (8.0 kB)
2026-04-26T04:11:09.228012273Z Collecting urllib3<3,>=1.26 (from requests>=2.0.0->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.229269241Z   Using cached urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
2026-04-26T04:11:09.266191398Z Collecting ecdsa!=0.15 (from python-jose[cryptography]->-r requirements.txt (line 14))
2026-04-26T04:11:09.267315485Z   Using cached ecdsa-0.19.2-py2.py3-none-any.whl.metadata (29 kB)
2026-04-26T04:11:09.288947389Z Collecting rsa!=4.1.1,!=4.4,<5.0,>=4.0 (from python-jose[cryptography]->-r requirements.txt (line 14))
2026-04-26T04:11:09.290024025Z   Using cached rsa-4.9.1-py3-none-any.whl.metadata (5.6 kB)
2026-04-26T04:11:09.314033084Z Collecting pyasn1>=0.5.0 (from python-jose[cryptography]->-r requirements.txt (line 14))
2026-04-26T04:11:09.31514401Z   Using cached pyasn1-0.6.3-py3-none-any.whl.metadata (8.4 kB)
2026-04-26T04:11:09.365595294Z Collecting aiohappyeyeballs>=2.5.0 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.36668639Z   Using cached aiohappyeyeballs-2.6.1-py3-none-any.whl.metadata (5.9 kB)
2026-04-26T04:11:09.384145394Z Collecting aiosignal>=1.4.0 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.38523563Z   Using cached aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
2026-04-26T04:11:09.421784662Z Collecting attrs>=17.3.0 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.422947359Z   Using cached attrs-26.1.0-py3-none-any.whl.metadata (8.8 kB)
2026-04-26T04:11:09.488200448Z Collecting frozenlist>=1.1.1 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.489419476Z   Using cached frozenlist-1.8.0-cp314-cp314-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (20 kB)
2026-04-26T04:11:09.706446863Z Collecting multidict<7.0,>=4.5 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.707757222Z   Using cached multidict-6.7.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (5.3 kB)
2026-04-26T04:11:09.760919075Z Collecting propcache>=0.2.0 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.762131333Z   Using cached propcache-0.4.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (13 kB)
2026-04-26T04:11:09.995884684Z Collecting yarl<2.0,>=1.17.0 (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 7))
2026-04-26T04:11:09.997188873Z   Using cached yarl-1.23.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (79 kB)
2026-04-26T04:11:10.207813547Z Collecting cffi>=2.0.0 (from cryptography>=38.0.3->google-auth>=2.15.0->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.209090786Z   Using cached cffi-2.0.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
2026-04-26T04:11:10.226723932Z Collecting pycparser (from cffi>=2.0.0->cryptography>=38.0.3->google-auth>=2.15.0->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.227823638Z   Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
2026-04-26T04:11:10.248129783Z Collecting six>=1.9.0 (from ecdsa!=0.15->python-jose[cryptography]->-r requirements.txt (line 14))
2026-04-26T04:11:10.249211939Z   Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
2026-04-26T04:11:10.287214292Z Collecting anyio<5,>=3.6.2 (from starlette>=0.46.0->fastapi->-r requirements.txt (line 1))
2026-04-26T04:11:10.288362979Z   Using cached anyio-4.13.0-py3-none-any.whl.metadata (4.5 kB)
2026-04-26T04:11:10.32215022Z Collecting httplib2<1.0.0,>=0.19.0 (from google-api-python-client->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.324233461Z   Using cached httplib2-0.31.2-py3-none-any.whl.metadata (2.2 kB)
2026-04-26T04:11:10.363639494Z Collecting google-auth-httplib2<1.0.0,>=0.2.0 (from google-api-python-client->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.364781431Z   Using cached google_auth_httplib2-0.3.1-py3-none-any.whl.metadata (3.0 kB)
2026-04-26T04:11:10.381641116Z Collecting uritemplate<5,>=3.0.1 (from google-api-python-client->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.382771082Z   Using cached uritemplate-4.2.0-py3-none-any.whl.metadata (2.6 kB)
2026-04-26T04:11:10.433421229Z Collecting pyparsing<4,>=3.1 (from httplib2<1.0.0,>=0.19.0->google-api-python-client->google-generativeai->-r requirements.txt (line 8))
2026-04-26T04:11:10.434701188Z   Using cached pyparsing-3.3.2-py3-none-any.whl.metadata (5.8 kB)
2026-04-26T04:11:10.445528355Z Using cached fastapi-0.136.1-py3-none-any.whl (117 kB)
2026-04-26T04:11:10.446703002Z Using cached uvicorn-0.46.0-py3-none-any.whl (70 kB)
2026-04-26T04:11:10.447840869Z Using cached pydantic-2.13.3-py3-none-any.whl (471 kB)
2026-04-26T04:11:10.4492755Z Using cached pydantic_core-2.46.3-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
2026-04-26T04:11:10.45201606Z Using cached pydantic_settings-2.14.0-py3-none-any.whl (60 kB)
2026-04-26T04:11:10.453086815Z Using cached motor-3.7.1-py3-none-any.whl (74 kB)
2026-04-26T04:11:10.454198041Z Using cached pymongo-4.17.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (2.3 MB)
2026-04-26T04:11:10.457069463Z Using cached dnspython-2.8.0-py3-none-any.whl (331 kB)
2026-04-26T04:11:10.458368362Z Using cached python_dotenv-1.2.2-py3-none-any.whl (22 kB)
2026-04-26T04:11:10.459451148Z Using cached twilio-9.10.5-py2.py3-none-any.whl (2.3 MB)
2026-04-26T04:11:10.462311929Z Using cached pyjwt-2.12.1-py3-none-any.whl (29 kB)
2026-04-26T04:11:10.463385155Z Using cached google_generativeai-0.8.6-py3-none-any.whl (155 kB)
2026-04-26T04:11:10.464562002Z Using cached google_ai_generativelanguage-0.6.15-py3-none-any.whl (1.3 MB)
2026-04-26T04:11:10.466674103Z Using cached google_api_core-2.25.2-py3-none-any.whl (162 kB)
2026-04-26T04:11:10.467901971Z Using cached googleapis_common_protos-1.74.0-py3-none-any.whl (300 kB)
2026-04-26T04:11:10.469154029Z Using cached grpcio_status-1.71.2-py3-none-any.whl (14 kB)
2026-04-26T04:11:10.470203774Z Using cached protobuf-5.29.6-cp38-abi3-manylinux2014_x86_64.whl (320 kB)
2026-04-26T04:11:10.471575504Z Using cached google_auth-2.49.2-py3-none-any.whl (240 kB)
2026-04-26T04:11:10.472795682Z Using cached grpcio-1.80.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (6.8 MB)
2026-04-26T04:11:10.479224475Z Using cached proto_plus-1.27.2-py3-none-any.whl (50 kB)
2026-04-26T04:11:10.480355012Z Using cached requests-2.33.1-py3-none-any.whl (64 kB)
2026-04-26T04:11:10.481462268Z Using cached charset_normalizer-3.4.7-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (215 kB)
2026-04-26T04:11:10.482683566Z Using cached idna-3.13-py3-none-any.whl (68 kB)
2026-04-26T04:11:10.483812522Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
2026-04-26T04:11:10.484881108Z Using cached urllib3-2.6.3-py3-none-any.whl (131 kB)
2026-04-26T04:11:10.486029444Z Using cached python_multipart-0.0.26-py3-none-any.whl (28 kB)
2026-04-26T04:11:10.48712959Z Using cached certifi-2026.4.22-py3-none-any.whl (135 kB)
2026-04-26T04:11:10.488272167Z Using cached email_validator-2.3.0-py3-none-any.whl (35 kB)
2026-04-26T04:11:10.489336143Z Using cached bcrypt-5.0.0-cp39-abi3-manylinux_2_34_x86_64.whl (278 kB)
2026-04-26T04:11:10.490611191Z Using cached python_jose-3.5.0-py2.py3-none-any.whl (34 kB)
2026-04-26T04:11:10.491693277Z Using cached rsa-4.9.1-py3-none-any.whl (34 kB)
2026-04-26T04:11:10.492762602Z Using cached aiohttp-3.13.5-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.7 MB)
2026-04-26T04:11:10.495218498Z Using cached multidict-6.7.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (248 kB)
2026-04-26T04:11:10.496459106Z Using cached yarl-1.23.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (101 kB)
2026-04-26T04:11:10.497631113Z Using cached aiohappyeyeballs-2.6.1-py3-none-any.whl (15 kB)
2026-04-26T04:11:10.498672388Z Using cached aiohttp_retry-2.9.1-py3-none-any.whl (10.0 kB)
2026-04-26T04:11:10.499739224Z Using cached aiosignal-1.4.0-py3-none-any.whl (7.5 kB)
2026-04-26T04:11:10.500800599Z Using cached annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
2026-04-26T04:11:10.501843245Z Using cached annotated_types-0.7.0-py3-none-any.whl (13 kB)
2026-04-26T04:11:10.50288198Z Using cached attrs-26.1.0-py3-none-any.whl (67 kB)
2026-04-26T04:11:10.503986446Z Using cached click-8.3.3-py3-none-any.whl (110 kB)
2026-04-26T04:11:10.505134353Z Using cached cryptography-47.0.0-cp311-abi3-manylinux_2_34_x86_64.whl (4.7 MB)
2026-04-26T04:11:10.509921292Z Using cached cffi-2.0.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
2026-04-26T04:11:10.51114564Z Using cached ecdsa-0.19.2-py2.py3-none-any.whl (150 kB)
2026-04-26T04:11:10.512310667Z Using cached frozenlist-1.8.0-cp314-cp314-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (231 kB)
2026-04-26T04:11:10.513535975Z Using cached h11-0.16.0-py3-none-any.whl (37 kB)
2026-04-26T04:11:10.514625Z Using cached propcache-0.4.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (201 kB)
2026-04-26T04:11:10.515804368Z Using cached pyasn1-0.6.3-py3-none-any.whl (83 kB)
2026-04-26T04:11:10.516908374Z Using cached pyasn1_modules-0.4.2-py3-none-any.whl (181 kB)
2026-04-26T04:11:10.518109691Z Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
2026-04-26T04:11:10.519165597Z Using cached starlette-1.0.0-py3-none-any.whl (72 kB)
2026-04-26T04:11:10.520250932Z Using cached anyio-4.13.0-py3-none-any.whl (114 kB)
2026-04-26T04:11:10.521414709Z Using cached typing_inspection-0.4.2-py3-none-any.whl (14 kB)
2026-04-26T04:11:10.522470574Z Using cached google_api_python_client-2.194.0-py3-none-any.whl (15.0 MB)
2026-04-26T04:11:10.537384591Z Using cached google_auth_httplib2-0.3.1-py3-none-any.whl (9.5 kB)
2026-04-26T04:11:10.538426187Z Using cached httplib2-0.31.2-py3-none-any.whl (91 kB)
2026-04-26T04:11:10.539598814Z Using cached pyparsing-3.3.2-py3-none-any.whl (122 kB)
2026-04-26T04:11:10.540754631Z Using cached uritemplate-4.2.0-py3-none-any.whl (11 kB)
2026-04-26T04:11:10.541841456Z Using cached pycparser-3.0-py3-none-any.whl (48 kB)
2026-04-26T04:11:10.542910082Z Using cached tqdm-4.67.3-py3-none-any.whl (78 kB)
2026-04-26T04:11:10.717457971Z Installing collected packages: urllib3, uritemplate, typing-extensions, tqdm, six, python-multipart, python-dotenv, pyparsing, PyJWT, pycparser, pyasn1, protobuf, propcache, multidict, idna, h11, frozenlist, dnspython, click, charset_normalizer, certifi, bcrypt, attrs, annotated-types, annotated-doc, aiohappyeyeballs, yarl, uvicorn, typing-inspection, rsa, requests, pymongo, pydantic-core, pyasn1-modules, proto-plus, httplib2, grpcio, googleapis-common-protos, email-validator, ecdsa, cffi, anyio, aiosignal, starlette, python-jose, pydantic, motor, grpcio-status, cryptography, aiohttp, pydantic-settings, google-auth, fastapi, aiohttp-retry, twilio, google-auth-httplib2, google-api-core, google-api-python-client, google-ai-generativelanguage, google-generativeai
2026-04-26T04:11:19.166248954Z 
2026-04-26T04:11:19.17217261Z Successfully installed PyJWT-2.12.1 aiohappyeyeballs-2.6.1 aiohttp-3.13.5 aiohttp-retry-2.9.1 aiosignal-1.4.0 annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.13.0 attrs-26.1.0 bcrypt-5.0.0 certifi-2026.4.22 cffi-2.0.0 charset_normalizer-3.4.7 click-8.3.3 cryptography-47.0.0 dnspython-2.8.0 ecdsa-0.19.2 email-validator-2.3.0 fastapi-0.136.1 frozenlist-1.8.0 google-ai-generativelanguage-0.6.15 google-api-core-2.25.2 google-api-python-client-2.194.0 google-auth-2.49.2 google-auth-httplib2-0.3.1 google-generativeai-0.8.6 googleapis-common-protos-1.74.0 grpcio-1.80.0 grpcio-status-1.71.2 h11-0.16.0 httplib2-0.31.2 idna-3.13 motor-3.7.1 multidict-6.7.1 propcache-0.4.1 proto-plus-1.27.2 protobuf-5.29.6 pyasn1-0.6.3 pyasn1-modules-0.4.2 pycparser-3.0 pydantic-2.13.3 pydantic-core-2.46.3 pydantic-settings-2.14.0 pymongo-4.17.0 pyparsing-3.3.2 python-dotenv-1.2.2 python-jose-3.5.0 python-multipart-0.0.26 requests-2.33.1 rsa-4.9.1 six-1.17.0 starlette-1.0.0 tqdm-4.67.3 twilio-9.10.5 typing-extensions-4.15.0 typing-inspection-0.4.2 uritemplate-4.2.0 urllib3-2.6.3 uvicorn-0.46.0 yarl-1.23.0
2026-04-26T04:11:19.177868363Z 
2026-04-26T04:11:19.177881204Z [notice] A new release of pip is available: 25.3 -> 26.0.1
2026-04-26T04:11:19.177884973Z [notice] To update, run: pip install --upgrade pip
2026-04-26T04:11:22.534849461Z ==> Uploading build...
2026-04-26T04:11:28.963838689Z ==> Uploaded in 3.2s. Compression took 3.2s
2026-04-26T04:11:29.054403717Z ==> Build successful 🎉
2026-04-26T04:11:31.094425889Z ==> Deploying...
2026-04-26T04:11:31.150029447Z ==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
2026-04-26T04:11:50.789863259Z ==> Running 'python run.py'
2026-04-26T04:11:56.290487767Z [2026-04-26 04:11:56] INFO in logger: NORMA AI: Structured logging initialized.
2026-04-26T04:11:56.290563528Z [2026-04-26 04:11:56] INFO in run: NORMA AI: Starting WhatsApp Orchestrator on port 5000
2026-04-26T04:12:13.07998223Z /opt/render/project/src/render/app/services/ai_service.py:1: FutureWarning: 
2026-04-26T04:12:13.080005331Z 
2026-04-26T04:12:13.080009591Z All support for the `google.generativeai` package has ended. It will no longer be receiving 
2026-04-26T04:12:13.080014441Z updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
2026-04-26T04:12:13.080017621Z See README for more details:
2026-04-26T04:12:13.080020411Z 
2026-04-26T04:12:13.080023361Z https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
2026-04-26T04:12:13.080026361Z 
2026-04-26T04:12:13.080029761Z   import google.generativeai as genai
2026-04-26T04:12:13.987139033Z INFO:     Started server process [59]
2026-04-26T04:12:13.987195195Z INFO:     Waiting for application startup.
2026-04-26T04:12:19.040323244Z [2026-04-26 04:12:19] INFO in mongodb: --- DATABASE CONNECTED ---
2026-04-26T04:12:19.040360505Z [2026-04-26 04:12:19] INFO in mongodb: DB Name: norma_ai
2026-04-26T04:12:19.041060882Z [2026-04-26 04:12:19] INFO in mongodb: Collections Found: ['login_details', 'clinic_info', 'error_logs', 'patients', 'staff_users', 'messages', 'operating_hours', 'appointments', 'doctors', 'conversations', 'auditlogs']
2026-04-26T04:12:19.041070862Z INFO:     Application startup complete.
2026-04-26T04:12:19.041092233Z INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
2026-04-26T04:12:19.828274543Z INFO:     127.0.0.1:42660 - "HEAD / HTTP/1.1" 405 Method Not Allowed
2026-04-26T04:12:22.256354955Z ==> Your service is live 🎉
2026-04-26T04:12:22.355052697Z ==> 
2026-04-26T04:12:22.359729555Z ==> ///////////////////////////////////////////////////////////
2026-04-26T04:12:22.376779475Z ==> 
2026-04-26T04:12:22.380065168Z ==> Available at your primary URL https://twilio-server-tek9.onrender.com
2026-04-26T04:12:22.384400047Z ==> 
2026-04-26T04:12:22.386764717Z ==> ///////////////////////////////////////////////////////////

}


after this no logs i send message recive responce no log further what to do redesign the loogin syteeem with the render documentation search thee internet 
