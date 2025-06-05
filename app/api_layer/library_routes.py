from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from app.data_models.library import LibraryCreate, LibraryUpdate, LibraryResponse
from app.services.library_service import LibraryService
from app.repository.mongo_repository import MongoRepository

library_router = APIRouter(prefix="/library")

def get_library_service(repo: MongoRepository = Depends()):
    return LibraryService(repo)

# TODO: TESTING
@library_router.post("/", response_model=LibraryResponse)
def create_library(
    library: LibraryCreate,
    service: LibraryService = Depends(get_library_service)
):
    return service.save_library(library)

@library_router.get("/", response_model=List[LibraryResponse])
def list_libraries(
    service: LibraryService = Depends(get_library_service)
):
    return service.list_libraries()

@library_router.get("/{library_id}", response_model=LibraryResponse)
def get_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service)
):
    library = service.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@library_router.put("/{library_id}", response_model=LibraryResponse)
def update_library(
    library_id: UUID, 
    library_update: LibraryUpdate, 
    service: LibraryService = Depends(get_library_service)
):
    library = service.save_library(library_update)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@library_router.delete("/{library_id}")
def delete_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service)
):
    success = service.delete_library(library_id)
    if not success:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"message": "Library deleted successfully"} 