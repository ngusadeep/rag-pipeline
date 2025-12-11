"""
Optional helper to expose Chroma clients/collections via FastAPI Depends.
Uses Chroma Cloud when CHROMA_API_KEY/TENANT/DATABASE are set; otherwise
falls back to local persistent client.
"""
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import Depends

from app.core.config import get_settings

_client: ClientAPI | None = None
_collection: Collection | None = None


def get_chroma_client() -> ClientAPI:
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    if (
        settings.chroma_api_key
        and settings.chroma_tenant
        and settings.chroma_database
    ):
        _client = chromadb.CloudClient(
            api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database,
        )
    else:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
    return _client


def get_chroma_collection(
    client: ClientAPI = Depends(get_chroma_client),
) -> Collection:
    global _collection
    if _collection is None:
        settings = get_settings()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name
        )
    return _collection
