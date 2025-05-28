from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
import cohere
from app.data_models.library import Library
from app.services.library_service import LibraryService
from app.repository.mongo_repository import MongoRepository

router = APIRouter(prefix="/api/v1")
co = cohere.Client("A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO")
@router.get("/")
async def root():
    return {"message": "Hello World2"} 


# Dependency
def get_repository():
    return MongoRepository()


def get_library_service(repo: MongoRepository = Depends(get_repository)):
    return LibraryService(repo)



@router.get("/libraries", response_model=List[Library])
async def list_libraries(service: LibraryService = Depends(get_library_service)):
    """List all libraries with pagination."""
    return service.list_libraries()
