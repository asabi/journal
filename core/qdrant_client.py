import httpx
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from core.config import settings

logger = logging.getLogger(__name__)


class QdrantClient:
    def __init__(self):
        self.base_url = settings.VECTOR_DB_URL
        self.client = httpx.Client(timeout=30.0)
        self.embedding_model = settings.VECTOR_EMBEDDING_OLLAMA_MODEL
        self.embedding_url = settings.VECTOR_EMBEDDING_OLLAMA_URL
        self.collection_name = "daily_summaries"
        self._vector_size = None  # Cache the vector size

    def _generate_point_id(self, date: str) -> int:
        """Generate a consistent integer ID from a date string"""
        # Create a hash of the date string and convert to integer
        hash_object = hashlib.md5(f"summary_{date}".encode())
        # Take first 8 bytes and convert to int (ensures it fits in 64-bit)
        return int.from_bytes(hash_object.digest()[:8], byteorder="big")

    def get_vector_size(self) -> int:
        """Get the vector size for the embedding model by making a test call"""
        if self._vector_size is not None:
            return self._vector_size

        try:
            logger.info(f"Determining vector size for model: {self.embedding_model}")
            response = self.client.post(
                f"{self.embedding_url}/api/embeddings", json={"model": self.embedding_model, "prompt": "test"}
            )
            response.raise_for_status()
            result = response.json()
            embedding = result.get("embedding", [])

            if not embedding:
                logger.warning(f"Model {self.embedding_model} doesn't support embeddings, using default size 1024")
                self._vector_size = 1024
            else:
                self._vector_size = len(embedding)
                logger.info(f"Detected vector size: {self._vector_size} for model {self.embedding_model}")

            return self._vector_size

        except Exception as e:
            logger.error(f"Error determining vector size: {e}")
            logger.warning("Falling back to default vector size of 1024")
            self._vector_size = 1024
            return self._vector_size

    def ensure_collection_exists(self):
        """Ensure the daily_summaries collection exists in Qdrant"""
        try:
            # Check if collection exists
            response = self.client.get(f"{self.base_url}/collections/{self.collection_name}")
            if response.status_code == 404:
                # Create collection with dynamic vector size
                vector_size = self.get_vector_size()
                collection_config = {"vectors": {"size": vector_size, "distance": "Cosine"}}
                response = self.client.put(
                    f"{self.base_url}/collections/{self.collection_name}", json=collection_config
                )
                response.raise_for_status()
                logger.info(f"Created collection: {self.collection_name} with vector size: {vector_size}")
            else:
                response.raise_for_status()
                # Verify the existing collection has the right vector size
                collection_info = response.json()
                existing_size = collection_info["result"]["config"]["params"]["vectors"]["size"]
                expected_size = self.get_vector_size()

                if existing_size != expected_size:
                    logger.warning(
                        f"Collection vector size mismatch! Expected: {expected_size}, Found: {existing_size}"
                    )
                    logger.warning("Consider recreating the collection or changing the embedding model")
                else:
                    logger.info(f"Collection {self.collection_name} exists with correct vector size: {existing_size}")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the configured embedding model"""
        try:
            response = self.client.post(
                f"{self.embedding_url}/api/embeddings", json={"model": self.embedding_model, "prompt": text}
            )
            response.raise_for_status()
            result = response.json()
            embedding = result.get("embedding", [])

            if not embedding:
                logger.warning(f"Model {self.embedding_model} doesn't support embeddings")
                # Return a dummy embedding with the correct size
                vector_size = self.get_vector_size()
                return [0.0] * vector_size

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return a dummy embedding with the correct size
            vector_size = self.get_vector_size()
            return [0.0] * vector_size

    def store_daily_summary(self, date: str, summary: str, metadata: Dict[str, Any]):
        """Store a daily summary in Qdrant"""
        try:
            self.ensure_collection_exists()

            # Generate embedding for the summary
            embedding = self.generate_embedding(summary)

            # Create point for Qdrant
            point = {
                "id": self._generate_point_id(date),
                "vector": embedding,
                "payload": {"date": date, "summary": summary, "created_at": datetime.utcnow().isoformat(), **metadata},
            }

            # Store in Qdrant
            response = self.client.put(
                f"{self.base_url}/collections/{self.collection_name}/points", json={"points": [point]}
            )
            response.raise_for_status()
            logger.info(f"Stored daily summary for {date}")

        except Exception as e:
            logger.error(f"Error storing daily summary: {e}")
            raise

    def search_summaries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search daily summaries using semantic search"""
        try:
            self.ensure_collection_exists()

            # Generate embedding for the query
            query_embedding = self.generate_embedding(query)

            # Search in Qdrant
            search_request = {"vector": query_embedding, "limit": limit, "with_payload": True}

            response = self.client.post(
                f"{self.base_url}/collections/{self.collection_name}/points/search", json=search_request
            )
            response.raise_for_status()

            results = response.json()
            return results.get("result", [])

        except Exception as e:
            logger.error(f"Error searching summaries: {e}")
            raise

    def close(self):
        """Close the HTTP client"""
        self.client.close()
