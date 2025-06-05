from fastapi import APIRouter, Depends, HTTPException
from app.data_models.search import SearchQuery
from app.data_models.chunk import Chunk
from app.services.index_service import IndexService
from app.repository.mongo_repository import MongoRepository
import logging

logger = logging.getLogger(__name__)

search_router = APIRouter(prefix="/search")


def get_index_service(repo: MongoRepository = Depends()):
    return IndexService(repo)


@search_router.post("/", response_model=list[Chunk])
def search(
    query: SearchQuery,
    index_service: IndexService = Depends(get_index_service),
):
    try:
        chunks = index_service.search(query.library_id, query.query, k=query.k)
        return chunks
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
