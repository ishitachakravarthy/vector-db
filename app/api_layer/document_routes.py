from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from app.data_models.document import Document
from app.services.document_service import DocumentService
from app.repository.mongo_repository import MongoRepository

document_router = APIRouter(prefix="/document")

def get_document_service(repo: MongoRepository = Depends()):
    return DocumentService(repo)

@document_router.post("/", response_model=Document)
def create_document(
    library_id: UUID = Query(..., description="ID of the library this document belongs to"),
    title: str = Query(..., description="Title of the document"),
    service: DocumentService = Depends(get_document_service)
):
    try:
        document = Document(
            library_id=library_id,
            title=title
        )
        return service.save_document(document)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@document_router.get("/", response_model=List[Document])
def list_documents(
    library_id: Optional[UUID] = Query(None, description="Filter documents by library ID"),
    service: DocumentService = Depends(get_document_service)
):
    try:
        if library_id:
            return service.list_documents_by_library(library_id)
        return service.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@document_router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    try:
        document = service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@document_router.put("/{document_id}", response_model=Document)
def update_document(
    document_id: UUID,
    title: Optional[str] = Query(None, description="New title for the document"),
    service: DocumentService = Depends(get_document_service)
):
    try:
        document = service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        
        if title is not None:
            document.update_title(title)
        
        return service.save_document(document)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@document_router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    try:
        success = service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
