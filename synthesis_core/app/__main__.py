import uvicorn
from .server import app
uvicorn.run(app=app, port=3001, host = '0.0.0.0', log_level='info')