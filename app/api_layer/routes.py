from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from uuid import UUID
import cohere
from app.data_models.library import Library
from app.data_models.document import Document
from app.services.document_service import DocumentService
from app.repository.mongo_repository import MongoRepository

router = APIRouter(prefix="/api/v1")

@router.get("/")
async def root():
    return {"message": "Hello World2"} 

# Dependency
def get_repository():
    return MongoRepository()

def get_document_service(repo: MongoRepository = Depends(get_repository)):
    return DocumentService(repo)


@router.post("/documents", response_model=Document)
async def create_document(
    document: Document, doc_service: DocumentService = Depends(get_document_service)
):
    try:
        created_document = doc_service.save_document(document)
        return created_document
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create document: {str(e)}"
        )
