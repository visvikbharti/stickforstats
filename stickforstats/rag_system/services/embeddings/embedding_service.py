import numpy as np
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import pickle
import re
from dataclasses import dataclass
import uuid
import os
import time
from django.conf import settings

# This is a placeholder for actual embedding libraries
# In a real implementation, you would import libraries like:
# from sentence_transformers import SentenceTransformer
# or
# import openai
# or
# import google.generativeai as genai

# Import cache service
from ..cache_service import cache_service

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Class to store embedding results."""
    text: str
    embedding: np.ndarray
    model_name: str
    metadata: Optional[Dict[str, Any]] = None

class EmbeddingService:
    """
    Service for generating embeddings from text using various models.
    
    Supports different embedding models (OpenAI, SentenceTransformers, etc.)
    and provides methods to embed documents and queries.
    """
    
    def __init__(self, model_name: str = "default", cache_dir: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the embedding model to use
            cache_dir: Directory to cache embeddings (optional)
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.join(settings.BASE_DIR, 'data', 'embeddings_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load the appropriate embedding model based on model_name
        self._load_model(model_name)
    
    def _load_model(self, model_name: str):
        """
        Load the specified embedding model.
        
        Args:
            model_name: Name of the model to load
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        # This is a placeholder for actual model loading code
        # In a real implementation, you would have code like:
        
        if model_name == "sentence-transformers":
            # self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_type = "sentence-transformers"
            logger.info("Loaded SentenceTransformer model")
            
        elif model_name == "openai":
            # Import and configure OpenAI
            # openai.api_key = settings.OPENAI_API_KEY
            self.model_type = "openai"
            logger.info("Configured OpenAI embeddings")
            
        elif model_name == "google":
            # Configure Google's generative AI
            # genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model_type = "google"
            logger.info("Configured Google embeddings")
            
        else:
            # Default to a simple embedding approach for demonstration
            logger.warning(f"Using demo embedding model (not for production)")
            self.model_type = "demo"
            
        # For demonstration, we'll use a simple method to create embeddings
        # This is NOT suitable for production use
    
    def _demo_embedding(self, text: str) -> np.ndarray:
        """
        Generate a demo embedding (not for production use).
        
        Args:
            text: The text to embed
            
        Returns:
            A numpy array representing the embedding
        """
        # This is just a toy embedding function for demonstration
        # It creates a deterministic "embedding" based on text characteristics
        # DO NOT use this in production!
        
        # Create a simple hash of the text
        hash_val = sum(ord(c) for c in text)
        # Use hash to seed numpy's random number generator
        np.random.seed(hash_val)
        # Generate a 384-dimensional "embedding" (common dimension for small models)
        return np.random.randn(384)
    
    def embed_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> EmbeddingResult:
        """
        Generate an embedding for a single text.
        
        Args:
            text: The text to embed
            metadata: Optional metadata to store with the embedding
            
        Returns:
            An EmbeddingResult containing the text and its embedding
        """
        try:
            # Check Redis cache first
            start_time = time.time()
            cached_embedding = cache_service.get_embedding(text, self.model_name)
            
            if cached_embedding is not None:
                cache_time = time.time() - start_time
                logger.debug(f"Using Redis cached embedding for text: {text[:50]}... (retrieved in {cache_time*1000:.2f}ms)")
                return EmbeddingResult(text=text, embedding=cached_embedding, 
                                      model_name=self.model_name, metadata=metadata)
            
            # Fall back to file cache if Redis cache misses
            cache_key = self._generate_cache_key(text)
            file_cached_embedding = self._get_from_cache(cache_key)
            
            if file_cached_embedding is not None:
                # Store in Redis for faster future access
                cache_service.store_embedding(text, file_cached_embedding, self.model_name)
                logger.debug(f"Using file cached embedding for text: {text[:50]}... (stored in Redis)")
                return EmbeddingResult(text=text, embedding=file_cached_embedding, 
                                      model_name=self.model_name, metadata=metadata)
            
            # Generate embedding based on model type
            embedding_start_time = time.time()
            
            if self.model_type == "sentence-transformers":
                # embedding = self.model.encode(text, convert_to_numpy=True)
                embedding = self._demo_embedding(text)
                
            elif self.model_type == "openai":
                # response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
                # embedding = np.array(response['data'][0]['embedding'])
                embedding = self._demo_embedding(text)
                
            elif self.model_type == "google":
                # result = genai.embed_content(model="embedding-001", content=text)
                # embedding = np.array(result['embedding'])
                embedding = self._demo_embedding(text)
                
            else:
                # Demo embedding
                embedding = self._demo_embedding(text)
            
            embedding_time = time.time() - embedding_start_time
            logger.debug(f"Generated embedding in {embedding_time*1000:.2f}ms")
            
            # Save to both caches
            self._save_to_cache(cache_key, embedding)
            cache_service.store_embedding(text, embedding, self.model_name)
            
            return EmbeddingResult(text=text, embedding=embedding, 
                                  model_name=self.model_name, metadata=metadata)
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return empty embedding in case of error
            return EmbeddingResult(text=text, embedding=np.zeros(384), 
                                  model_name=self.model_name, metadata=metadata)
    
    def embed_texts(self, texts: List[str], 
                   metadata: Optional[List[Dict[str, Any]]] = None) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            metadata: Optional list of metadata for each text
            
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        
        # Process metadata
        if metadata is None:
            metadata = [None] * len(texts)
        elif len(metadata) != len(texts):
            raise ValueError(f"Length of metadata ({len(metadata)}) must match length of texts ({len(texts)})")
        
        for i, (text, meta) in enumerate(zip(texts, metadata)):
            logger.debug(f"Embedding text {i+1}/{len(texts)}")
            result = self.embed_text(text, meta)
            results.append(result)
        
        return results
    
    def embed_chunks(self, text: str, chunk_size: int = 1000, 
                    overlap: int = 200, metadata: Optional[Dict[str, Any]] = None) -> List[EmbeddingResult]:
        """
        Split text into chunks and embed each chunk.
        
        Args:
            text: Text to split and embed
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            metadata: Optional metadata to associate with all chunks
            
        Returns:
            List of EmbeddingResult objects, one for each chunk
        """
        chunks = self._split_text(text, chunk_size, overlap)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta['chunk_index'] = i
            chunk_meta['total_chunks'] = len(chunks)
            chunk_metadata.append(chunk_meta)
        
        return self.embed_texts(chunks, chunk_metadata)
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        # If text is shorter than chunk_size, return it as a single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the current chunk
            end = start + chunk_size
            
            # If we've reached the end of the text, add the final chunk and break
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a natural break point (e.g., end of sentence or paragraph)
            natural_break = self._find_natural_break(text, end)
            
            if natural_break > start:  # If we found a valid break point
                chunks.append(text[start:natural_break])
                start = natural_break - overlap  # Move start with overlap
            else:
                # If we couldn't find a natural break, just use the chunk_size
                chunks.append(text[start:end])
                start = end - overlap
            
            # Ensure we make progress
            if start < 0 or len(chunks) > 1000:  # Safety check
                logger.warning(f"Possible infinite loop in text splitting. Breaking.")
                break
        
        return chunks
    
    def _find_natural_break(self, text: str, position: int) -> int:
        """
        Find a natural break point in text near the given position.
        
        Args:
            text: The text to search in
            position: The approximate position to find a break
            
        Returns:
            The position of the natural break
        """
        # Look for paragraph break
        paragraph_match = re.search(r'\n\s*\n', text[max(0, position-100):min(len(text), position+100)])
        if paragraph_match:
            return max(0, position-100) + paragraph_match.end()
        
        # Look for sentence end
        sentence_match = re.search(r'[.!?]\s+', text[max(0, position-50):min(len(text), position+50)])
        if sentence_match:
            return max(0, position-50) + sentence_match.end()
        
        # If no natural break found, return the original position
        return position
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate a cache key for a text.
        
        Args:
            text: The text to generate a key for
            
        Returns:
            A string key
        """
        # Generate a deterministic cache key based on model name and text
        import hashlib
        key = f"{self.model_name}_{hashlib.md5(text.encode()).hexdigest()}"
        return key
    
    def _get_from_cache(self, key: str) -> Optional[np.ndarray]:
        """
        Retrieve an embedding from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached embedding or None if not found
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Error loading from cache: {str(e)}")
                return None
        
        return None
    
    def _save_to_cache(self, key: str, embedding: np.ndarray) -> bool:
        """
        Save an embedding to the cache.
        
        Args:
            key: The cache key
            embedding: The embedding to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = os.path.join(self.cache_dir, f"{key}.pkl")
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embedding, f)
            return True
        except Exception as e:
            logger.warning(f"Error saving to cache: {str(e)}")
            return False