from fastapi import FastAPI
import cohere
from app.api_layer.routes import router
from app.api_layer.search_routes import search_router

app = FastAPI()
co = cohere.Client("A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO")
app.include_router(router)
app.include_router(search_router)