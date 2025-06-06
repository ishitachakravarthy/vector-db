from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from app.data_models.library import LibraryCreate, LibraryUpdate, LibraryResponse
from app.services.library_service import LibraryService
from app.repository.mongo_repository import MongoRepository

library_router = APIRouter(prefix="/library")

def get_library_service(repo: MongoRepository = Depends()):
    return LibraryService(repo)

@library_router.post("/", response_model=LibraryResponse)
async def create_library(
    title: str = Query(..., description="Title of the library"),
    description: Optional[str] = Query(None, description="Description of the library"),
    index_type: Optional[str] = Query(None, description="Type of index to use (flat, ivf or hnsw)"),
    service: LibraryService = Depends(get_library_service)
):
    try:
        library_create = LibraryCreate(
            title=title,
            description=description,
            index_type=index_type
        )
        return await service.create_library(library_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create library: {str(e)}")

@library_router.get("/list", response_model=List[LibraryResponse])
async def list_libraries(
    service: LibraryService = Depends(get_library_service)
):
    try:
        return await service.list_libraries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list libraries: {str(e)}")

@library_router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(library_id: UUID, service: LibraryService = Depends(get_library_service)):
    try:
        library = await service.get_library(library_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get library: {str(e)}")

@library_router.put("/{library_id}", response_model=LibraryResponse)
async def update_library(
    library_id: UUID,
    title: Optional[str] = Query(None, description="New title for the library"),
    description: Optional[str] = Query(None, description="New description for the library"),
    index_type: Optional[str] = Query(None, description="New index type (flat, ivf or hnsw)"),
    service: LibraryService = Depends(get_library_service)
):
    try:
        library_update = LibraryUpdate(
            title=title,
            description=description,
            index_type=index_type
        )
        library = await service.update_library(library_id, library_update)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update library: {str(e)}")

@library_router.delete("/{library_id}")
async def delete_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service)
):
    try:
        success = await service.delete_library(library_id)
        if not success:
            raise HTTPException(status_code=404, detail="Library not found")
        return {"message": "Library deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete library: {str(e)}") 
