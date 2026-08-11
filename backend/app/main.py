from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from .api.routes import router
from .config import settings
from .database import Base,engine
from . import models
settings.media_root.mkdir(parents=True,exist_ok=True);Base.metadata.create_all(engine)
app=FastAPI(title="CIVIC EYE API",version="0.1.0")
origins=["*"] if settings.cors_origins=="*" else [x.strip() for x in settings.cors_origins.split(",")]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=origins!=["*"],allow_methods=["*"],allow_headers=["*"])
app.mount("/media",StaticFiles(directory=settings.media_root),name="media");app.include_router(router)
@app.get("/health")
def health():
 try:
  with engine.connect() as c:c.execute(text("SELECT 1"))
  return {"status":"ok","database":True,"postgis":engine.url.get_backend_name().startswith("postgres")}
 except Exception:return {"status":"degraded","database":False,"postgis":False}
