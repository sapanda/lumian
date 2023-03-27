import uvicorn
from .server import app

uvicorn.run(app=app, port=3001, log_level='info')