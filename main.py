from fastapi import FastAPI
import cohere
from app.api_layer.routes import router

app = FastAPI()
co = cohere.Client("A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO")
app.include_router(router)
