import uvicorn

uvicorn.run('server:fast_api', port=3000, log_level='info')