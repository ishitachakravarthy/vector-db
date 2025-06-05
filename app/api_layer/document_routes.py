from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from app.data_models.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.data_models.metadata import DocumentMetadata
from app.services.document_service import DocumentService
from app.repository.mongo_repository import MongoRepository

document_router = APIRouter(prefix="/document")

def get_document_service(repo: MongoRepository = Depends()):
    return DocumentService(repo)

@document_router.post("/", response_model=DocumentResponse)
def create_document(
    library_id: UUID = Query(..., description="ID of the library this document belongs to"),
    title: str = Query(..., description="Title of the document"),
    author: Optional[str] = Query(None, description="Author of the document"),
    status: Optional[str] = Query(None, description="Status of the document (draft, published, archived)"),
    service: DocumentService = Depends(get_document_service)
):
    """Create a new document."""
    try:
        # Create DocumentCreate object from individual fields
        document_create = DocumentCreate(
            library_id=library_id,
            title=title
        )
        
        # Only create metadata if we have values to set
        if author is not None or status is not None:
            metadata = {}
            if author is not None:
                metadata["author"] = author
            if status is not None:
                metadata["status"] = status
            document_create.metadata = DocumentMetadata(**metadata)

        return service.create_document(document_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@document_router.get("/", response_model=List[DocumentResponse])
def list_documents(
    service: DocumentService = Depends(get_document_service)
):
    """List all documents."""
    try:
        return service.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@document_router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get a document by ID."""
    try:
        document = service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@document_router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID,
    title: Optional[str] = Query(None, description="New title for the document"),
    author: Optional[str] = Query(None, description="New author of the document"),
    status: Optional[str] = Query(None, description="New status of the document (draft, published, archived)"),
    service: DocumentService = Depends(get_document_service)
):
    """Update a document."""
    try:
        # Create DocumentUpdate object from individual fields
        document_update = DocumentUpdate()
        if title is not None:
            document_update.title = title
            
        # Only create metadata if we have values to set
        if author is not None or status is not None:
            metadata = {}
            if author is not None:
                metadata["author"] = author
            if status is not None:
                metadata["status"] = status
            document_update.metadata = DocumentMetadata(**metadata)

        document = service.update_document(document_id, document_update)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@document_router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document."""
    try:
        success = service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
