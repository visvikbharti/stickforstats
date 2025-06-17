import numpy as np
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import pickle
import os
import time
import json

from django.conf import settings
from ...models import Document, DocumentChunk, UserQuery, RetrievedDocument
from ..embeddings.embedding_service import EmbeddingService, EmbeddingResult
from ..cache_service import cache_service

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Class to store retrieval results."""
    query: str
    document_id: str
    document_title: str
    chunk_id: str
    chunk_content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class RetrievalService:
    """
    Service for retrieving relevant documents based on queries.
    
    Uses vector similarity search to find documents that match user queries.
    """
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None,
                index_path: Optional[str] = None):
        """
        Initialize the retrieval service.
        
        Args:
            embedding_service: Service to generate embeddings
            index_path: Path to load/save vector index
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.index_path = index_path or os.path.join(settings.BASE_DIR, 'data', 'vector_index.pkl')
        
        # This would normally be a proper vector database like FAISS, Pinecone, etc.
        # For demonstration, we'll use a simple in-memory index
        self.document_embeddings = {}  # {document_chunk_id: embedding}
        self.document_metadata = {}  # {document_chunk_id: metadata}
        
        # Load index if it exists
        self._load_index()
    
    def _load_index(self):
        """Load the document index from disk if it exists."""
        if os.path.exists(self.index_path):
            try:
                logger.info(f"Loading vector index from {self.index_path}")
                with open(self.index_path, 'rb') as f:
                    index_data = pickle.load(f)
                    self.document_embeddings = index_data.get('embeddings', {})
                    self.document_metadata = index_data.get('metadata', {})
                logger.info(f"Loaded {len(self.document_embeddings)} document embeddings")
            except Exception as e:
                logger.error(f"Error loading vector index: {str(e)}")
                # Initialize empty index
                self.document_embeddings = {}
                self.document_metadata = {}
    
    def _save_index(self):
        """Save the document index to disk."""
        try:
            logger.info(f"Saving vector index to {self.index_path}")
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, 'wb') as f:
                pickle.dump({
                    'embeddings': self.document_embeddings,
                    'metadata': self.document_metadata
                }, f)
            logger.info(f"Saved {len(self.document_embeddings)} document embeddings")
            return True
        except Exception as e:
            logger.error(f"Error saving vector index: {str(e)}")
            return False
    
    def index_document(self, document: Document) -> bool:
        """
        Index a document in the vector database.
        
        Args:
            document: The Document model instance to index
            
        Returns:
            True if indexing was successful
        """
        try:
            logger.info(f"Indexing document: {document.title} ({document.id})")
            
            # Check if document chunks already exist
            chunks = DocumentChunk.objects.filter(document=document)
            
            if not chunks.exists():
                # Split document into chunks and generate embeddings
                logger.info(f"Splitting document into chunks and generating embeddings")
                
                # Generate embeddings for chunks
                chunk_results = self.embedding_service.embed_chunks(
                    document.content,
                    chunk_size=1000,
                    overlap=200,
                    metadata={
                        'document_id': str(document.id),
                        'document_title': document.title,
                        'document_type': document.document_type,
                        'module': document.module,
                        'topic': document.topic
                    }
                )
                
                # Save chunks and embeddings to database
                for i, result in enumerate(chunk_results):
                    # Convert embedding to binary for storage
                    embedding_binary = pickle.dumps(result.embedding)
                    
                    # Create chunk
                    chunk = DocumentChunk.objects.create(
                        document=document,
                        content=result.text,
                        chunk_index=i,
                        embedding=embedding_binary,
                        embedding_model=result.model_name
                    )
                    
                    # Add to in-memory index
                    self.document_embeddings[str(chunk.id)] = result.embedding
                    self.document_metadata[str(chunk.id)] = {
                        'document_id': str(document.id),
                        'document_title': document.title,
                        'chunk_id': str(chunk.id),
                        'chunk_index': i,
                        'document_type': document.document_type,
                        'module': document.module,
                        'topic': document.topic,
                        'content': result.text
                    }
            else:
                # Add existing chunks to in-memory index
                logger.info(f"Loading {chunks.count()} existing chunks into memory")
                for chunk in chunks:
                    if chunk.embedding:
                        # Load embedding from binary
                        embedding = pickle.loads(chunk.embedding)
                        
                        # Add to in-memory index
                        self.document_embeddings[str(chunk.id)] = embedding
                        self.document_metadata[str(chunk.id)] = {
                            'document_id': str(document.id),
                            'document_title': document.title,
                            'chunk_id': str(chunk.id),
                            'chunk_index': chunk.chunk_index,
                            'document_type': document.document_type,
                            'module': document.module,
                            'topic': document.topic,
                            'content': chunk.content
                        }
            
            # Save index to disk
            self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexing document: {str(e)}")
            return False
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the index.
        
        Args:
            document_id: ID of the document to remove
            
        Returns:
            True if removal was successful
        """
        try:
            # Find all chunks for this document
            chunks = DocumentChunk.objects.filter(document_id=document_id)
            chunk_ids = [str(chunk.id) for chunk in chunks]
            
            # Remove from in-memory index
            for chunk_id in chunk_ids:
                if chunk_id in self.document_embeddings:
                    del self.document_embeddings[chunk_id]
                if chunk_id in self.document_metadata:
                    del self.document_metadata[chunk_id]
            
            # Save index to disk
            self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing document from index: {str(e)}")
            return False
    
    def retrieve(self, query: str, top_k: int = 5, 
                filters: Optional[Dict[str, Any]] = None,
                user_query: Optional[UserQuery] = None) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The query text
            top_k: Number of results to return
            filters: Optional filters to apply (e.g., module, document_type)
            user_query: Optional UserQuery model instance to associate results with
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            start_time = time.time()
            
            # Check cache first
            cached_results = cache_service.get_retrieval_results(query, filters)
            if cached_results:
                cache_time = time.time() - start_time
                logger.info(f"Retrieved results from cache in {cache_time*1000:.2f}ms for query: {query[:50]}...")
                
                # Convert cached results back to RetrievalResult objects
                results = []
                for cached_result in cached_results:
                    result = RetrievalResult(
                        query=cached_result['query'],
                        document_id=cached_result['document_id'],
                        document_title=cached_result['document_title'],
                        chunk_id=cached_result['chunk_id'],
                        chunk_content=cached_result['chunk_content'],
                        score=cached_result['score'],
                        metadata=cached_result['metadata']
                    )
                    results.append(result)
                
                # If a UserQuery model is provided, still store the retrieval results in DB
                if user_query:
                    self._store_retrieval_results_in_db(user_query, results)
                
                return results
            
            # Generate embedding for query
            query_embedding_start = time.time()
            query_result = self.embedding_service.embed_text(query)
            query_embedding = query_result.embedding
            query_embedding_time = time.time() - query_embedding_start
            logger.debug(f"Generated query embedding in {query_embedding_time*1000:.2f}ms")
            
            # If a UserQuery model is provided, save the embedding
            if user_query:
                user_query.embedding = pickle.dumps(query_embedding)
                user_query.save()
            
            # Calculate similarity scores
            similarity_start = time.time()
            scores = {}
            for chunk_id, doc_embedding in self.document_embeddings.items():
                # Apply filters if provided
                if filters and not self._check_filters(chunk_id, filters):
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                scores[chunk_id] = similarity
            
            # Sort by score and get top_k
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            similarity_time = time.time() - similarity_start
            logger.debug(f"Calculated similarities for {len(scores)} documents in {similarity_time*1000:.2f}ms")
            
            # Create retrieval results
            results = []
            for i, (chunk_id, score) in enumerate(sorted_scores):
                metadata = self.document_metadata.get(chunk_id, {})
                result = RetrievalResult(
                    query=query,
                    document_id=metadata.get('document_id', ''),
                    document_title=metadata.get('document_title', ''),
                    chunk_id=chunk_id,
                    chunk_content=metadata.get('content', ''),
                    score=float(score),
                    metadata=metadata
                )
                results.append(result)
            
            # If a UserQuery model is provided, save the retrieval results
            if user_query:
                self._store_retrieval_results_in_db(user_query, results)
            
            # Cache the results
            cache_data = [
                {
                    'query': r.query,
                    'document_id': r.document_id,
                    'document_title': r.document_title,
                    'chunk_id': r.chunk_id,
                    'chunk_content': r.chunk_content,
                    'score': r.score,
                    'metadata': r.metadata
                }
                for r in results
            ]
            cache_service.store_retrieval_results(query, cache_data, filters)
            
            total_time = time.time() - start_time
            logger.info(f"Retrieval completed in {total_time*1000:.2f}ms for query: {query[:50]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
            
    def _store_retrieval_results_in_db(self, user_query: UserQuery, results: List[RetrievalResult]):
        """
        Store retrieval results in the database.
        
        Args:
            user_query: The UserQuery model instance
            results: List of RetrievalResult objects
        """
        try:
            for i, result in enumerate(results):
                try:
                    chunk = DocumentChunk.objects.get(id=result.chunk_id)
                    RetrievedDocument.objects.create(
                        query=user_query,
                        document_chunk=chunk,
                        retrieval_score=float(result.score),
                        rank=i
                    )
                except DocumentChunk.DoesNotExist:
                    logger.warning(f"Document chunk {result.chunk_id} not found in database")
        except Exception as e:
            logger.error(f"Error storing retrieval results in database: {str(e)}")
    
    def _check_filters(self, chunk_id: str, filters: Dict[str, Any]) -> bool:
        """
        Check if a document chunk matches the specified filters.
        
        Args:
            chunk_id: ID of the document chunk
            filters: Filters to apply
            
        Returns:
            True if the chunk matches all filters
        """
        metadata = self.document_metadata.get(chunk_id, {})
        
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity (between -1 and 1)
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0
        
        return np.dot(a, b) / (norm_a * norm_b)
    
    def update_index(self):
        """
        Update the vector index with all documents in the database.
        """
        try:
            # Get all documents
            documents = Document.objects.all()
            logger.info(f"Updating index with {documents.count()} documents")
            
            # Index each document
            for document in documents:
                self.index_document(document)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
            return False