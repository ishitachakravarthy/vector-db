from fastapi import APIRouter, HTTPException, Depends
import cohere

router = APIRouter(prefix="/api1")

co = cohere.Client("A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO")

@router.get("/")
async def root():
    return {"message": "Hello World2"} 
