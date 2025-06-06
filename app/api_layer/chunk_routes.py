from fastapi import APIRouter, HTTPException, Query, Depends
from app.repository.mongo_repository import MongoRepository
from uuid import UUID

from app.services.chunk_service import ChunkService
from app.data_models.chunk import ChunkCreate, ChunkUpdate, ChunkResponse
from app.data_models.metadata import ChunkMetadata


chunk_router = APIRouter(prefix="/chunks")

def get_chunk_service(repo: MongoRepository = Depends()):
    return ChunkService(repo)


@chunk_router.post("", response_model=ChunkResponse)
def create_chunk(
    document_id: UUID = Query(..., description="Document ID of chunk"),
    text: str = Query(..., description="Text of the chunk"),
    section: str|None = Query(..., description="Section of the document this chunk belongs to"),
    order: int|None = Query(..., description="Order of the chunk in the document"),
    service: ChunkService = Depends(get_chunk_service)
):
    try:
        metadata = ChunkMetadata(section=section, order=order)
        chunk_data = ChunkCreate(
            document_id=document_id,
            text=text,
            metadata=metadata
        )
        return service.save_chunk(chunk_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@chunk_router.get("/list", response_model=list[UUID])
def list_chunks(
    service: ChunkService = Depends(get_chunk_service)
):
    """List all chunk IDs"""
    try:
        return service.list_chunks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chunk_router.get("/{chunk_id}", response_model=ChunkResponse)
def get_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    try:
        chunk = service.get_chunk(chunk_id)
        if not chunk:
            raise HTTPException(status_code=404, detail=str(e))
        return chunk
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chunk_router.put("/{chunk_id}", response_model=ChunkResponse)
def update_chunk(
    chunk_id: UUID,
    text: str|None = Query(None, description="New text  for the chunk"),
    section: str|None = Query(None, description="New section of the document this chunk belongs to"),
    order: int|None = Query(None, description="New order of the chunk in the document"),
    service: ChunkService = Depends(get_chunk_service)
):
    try:
        metadata = None
        if section is not None or order is not None:
            metadata = ChunkMetadata(
                section=section or None,    
                order=order or 0
            )
        
        update_data = ChunkUpdate(
            text=text,
            metadata=metadata
        )
        updated_chunk = service.update_chunk(chunk_id, update_data)
        if not updated_chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return updated_chunk
    except Exception as e:
        raise

@chunk_router.delete("/{chunk_id}")
def delete_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    try:
        service.delete_chunk(chunk_id)
        return {"message": "Chunk deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
