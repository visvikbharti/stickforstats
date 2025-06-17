"""
RAG Service

This module provides the main RAG (Retrieval-Augmented Generation) service
that combines embedding, retrieval, and generation services.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from django.conf import settings
from django.utils import timezone
import uuid
import json
import time
import psutil
import os
import pickle

from ..models import (
    Document, 
    DocumentChunk, 
    UserQuery, 
    RetrievedDocument, 
    GeneratedResponse, 
    Conversation,
    ConversationMessage
)
from .embeddings.embedding_service import EmbeddingService, EmbeddingResult
from .retrieval.retrieval_service import RetrievalService, RetrievalResult
from .generation.generation_service import GenerationService
from .websocket_metrics import websocket_metrics
from .websocket_metrics_config import RAG_WEBSOCKET_THRESHOLDS, RAG_PERFORMANCE_METRICS
from .cache_service import cache_service

logger = logging.getLogger(__name__)

# Global variable to hold service instances
_embedding_service = None
_retrieval_service = None
_generation_service = None

def initialize_rag_services():
    """
    Initialize the RAG services.
    
    This function creates the singleton instances of the embedding,
    retrieval, and generation services.
    """
    global _embedding_service, _retrieval_service, _generation_service
    
    logger.info("Initializing RAG services...")
    
    try:
        # Initialize embedding service
        _embedding_service = EmbeddingService()
        
        # Initialize retrieval service
        _retrieval_service = RetrievalService()
        
        # Initialize generation service
        _generation_service = GenerationService()
        
        logger.info("RAG services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing RAG services: {str(e)}")
        raise

class RAGService:
    """
    Main RAG service that combines embedding, retrieval, and generation.
    
    This service provides the complete RAG pipeline, from processing user
    queries to returning generated responses with relevant context.
    """
    
    def __init__(self):
        """Initialize the RAG service with its component services."""
        global _embedding_service, _retrieval_service, _generation_service
        
        # Use singleton instances if available
        if _embedding_service is None:
            _embedding_service = EmbeddingService()
        
        if _retrieval_service is None:
            _retrieval_service = RetrievalService()
        
        if _generation_service is None:
            _generation_service = GenerationService()
        
        self.embedding_service = _embedding_service
        self.retrieval_service = _retrieval_service
        self.generation_service = _generation_service
    
    def process_query(self, query_text: str, user, 
                      conversation_id: Optional[str] = None,
                      context: Optional[Dict[str, Any]] = None,
                      filters: Optional[Dict[str, Any]] = None,
                      channel_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Process a user query through the full RAG pipeline.
        
        Args:
            query_text: The user's query text
            user: The user making the query
            conversation_id: Optional ID of an existing conversation
            context: Optional additional context for the query
            filters: Optional filters for the retrieval stage
            channel_name: Optional WebSocket channel name for metrics tracking
            
        Returns:
            A tuple of (response_text, metadata)
        """
        # Start query processing timer and memory tracking
        query_start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Initialize performance metrics
        performance_metrics = dict(RAG_PERFORMANCE_METRICS['default_values'])
        
        try:
            # Set default values
            context = context or {}
            filters = filters or {}
            
            # Check cache for this query+context+user combination
            if settings.RAG_SYSTEM.get('CACHE_QUERIES', True):
                user_id = str(user.id) if user else None
                cached_response = cache_service.get_query_response(
                    query=query_text,
                    context=context,
                    user_id=user_id
                )
                
                if cached_response:
                    cache_time = time.time() - query_start_time
                    logger.info(f"Using cached response for query: '{query_text[:50]}...' (retrieved in {cache_time*1000:.2f}ms)")
                    
                    # Record metrics for cache usage
                    performance_metrics['cache_hit'] = True
                    performance_metrics['cache_retrieval_time'] = cache_time * 1000  # ms
                    
                    # We're still going to update the conversation and create a new query record
                    # but skip the expensive embedding/retrieval/generation steps
                    conversation, user_query = self._ensure_conversation_and_query(
                        user=user,
                        query_text=query_text,
                        conversation_id=conversation_id,
                        context=context
                    )
                    
                    # Use cached response
                    response_text = cached_response['response_text']
                    sources = cached_response.get('sources', [])
                    cached_metrics = cached_response.get('performance_metrics', {})
                    response_id = cached_response.get('response_id')
                    
                    # Add message to conversation
                    ConversationMessage.objects.create(
                        conversation=conversation,
                        message_type='assistant',
                        content=response_text,
                        metadata={
                            'response_id': response_id,
                            'retrieved_count': len(sources),
                            'from_cache': True,
                            'performance_metrics': performance_metrics
                        }
                    )
                    
                    # Update conversation
                    conversation.updated_at = timezone.now()
                    conversation.save()
                    
                    # Calculate total query processing time with caching
                    query_processing_time = (time.time() - query_start_time) * 1000  # ms
                    performance_metrics['total_query_processing_time'] = query_processing_time
                    
                    # Track metrics if channel provided
                    if channel_name:
                        self._track_rag_metrics(channel_name, performance_metrics)
                    
                    # Prepare metadata
                    metadata = {
                        'conversation_id': str(conversation.id),
                        'query_id': str(user_query.id),
                        'response_id': response_id,
                        'sources': sources,
                        'from_cache': True,
                        'processing_time': query_processing_time,
                        'performance_metrics': performance_metrics
                    }
                    
                    return response_text, metadata
            
            # Get or create conversation
            conversation, user_query = self._ensure_conversation_and_query(
                user=user,
                query_text=query_text,
                conversation_id=conversation_id,
                context=context
            )
            
            # Generate query embedding - track time
            embedding_start_time = time.time()
            # Query embedding is done inside the retrieval service, but we'll track the time here
            
            # Retrieve relevant documents
            retrieval_start_time = time.time()
            retrieved_results = self.retrieval_service.retrieve(
                query=query_text,
                top_k=5,
                filters=filters,
                user_query=user_query
            )
            retrieval_end_time = time.time()
            
            # Track retrieval time
            retrieval_time = (retrieval_end_time - retrieval_start_time) * 1000  # ms
            performance_metrics['document_retrieval_time'] = retrieval_time
            performance_metrics['retrieved_document_count'] = len(retrieved_results)
            performance_metrics['cache_hit'] = False
            
            # Calculate embedding time (estimation)
            embedding_time = (retrieval_start_time - embedding_start_time) * 1000  # ms
            performance_metrics['query_embedding_time'] = embedding_time
            
            # Get conversation history
            conversation_history = []
            if conversation:
                messages = ConversationMessage.objects.filter(
                    conversation=conversation
                ).order_by('created_at')[:10]  # Limit to last 10 messages
                
                conversation_history = [
                    {
                        'role': 'user' if msg.message_type == 'user' else 'assistant',
                        'content': msg.content
                    }
                    for msg in messages
                ]
            
            # Generate response - track time
            generation_start_time = time.time()
            response_text = self.generation_service.generate_response(
                query=query_text,
                retrieved_results=retrieved_results,
                conversation_history=conversation_history,
                user_query=user_query
            )
            generation_end_time = time.time()
            
            # Track generation time
            generation_time = (generation_end_time - generation_start_time) * 1000  # ms
            performance_metrics['response_generation_time'] = generation_time
            
            # Create response record
            response = GeneratedResponse.objects.create(
                user_query=user_query,
                response_text=response_text,
                metadata={
                    'context': context,
                    'filters': filters,
                    'retrieved_count': len(retrieved_results),
                    'performance_metrics': performance_metrics
                }
            )
            
            # Link retrieved documents to response
            for result in retrieved_results:
                if hasattr(result, 'retrieved_document'):
                    response.retrieved_documents.add(result.retrieved_document)
            
            # Add message to conversation
            ConversationMessage.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=response_text,
                metadata={
                    'response_id': str(response.id),
                    'retrieved_count': len(retrieved_results),
                    'performance_metrics': performance_metrics
                }
            )
            
            # Update conversation
            conversation.updated_at = timezone.now()
            conversation.save()
            
            # Prepare metadata for return
            sources = []
            for result in retrieved_results:
                if hasattr(result, 'retrieved_document'):
                    chunk = result.retrieved_document.document_chunk
                    document = chunk.document
                    sources.append({
                        'document_id': str(document.id),
                        'title': document.title,
                        'chunk_text': chunk.text,
                        'relevance_score': result.retrieved_document.relevance_score
                    })
                else:
                    # Handle the case where we're working with direct retrieval results
                    sources.append({
                        'document_id': result.document_id,
                        'title': result.document_title,
                        'chunk_text': result.chunk_content,
                        'relevance_score': result.score
                    })
            
            # Calculate total query processing time
            query_processing_time = (time.time() - query_start_time) * 1000  # ms
            performance_metrics['total_query_processing_time'] = query_processing_time
            
            # Calculate memory usage
            end_memory = self._get_memory_usage()
            memory_used_mb = (end_memory - start_memory) / (1024 * 1024) if start_memory > 0 else 0
            performance_metrics['memory_usage_per_query'] = memory_used_mb
            
            # Track RAG-specific metrics in WebSocket metrics if channel name provided
            if channel_name:
                self._track_rag_metrics(channel_name, performance_metrics)
                
                # Check for performance issues
                self._check_performance_thresholds(channel_name, performance_metrics)
            
            metadata = {
                'conversation_id': str(conversation.id),
                'query_id': str(user_query.id),
                'response_id': str(response.id),
                'sources': sources,
                'processing_time': query_processing_time,
                'performance_metrics': performance_metrics
            }
            
            # Cache the result for future queries
            if settings.RAG_SYSTEM.get('CACHE_QUERIES', True):
                user_id = str(user.id) if user else None
                cache_data = {
                    'response_text': response_text,
                    'response_id': str(response.id),
                    'sources': sources,
                    'performance_metrics': performance_metrics
                }
                
                cache_service.store_query_response(
                    query=query_text,
                    response=cache_data,
                    context=context,
                    user_id=user_id
                )
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            
            # Track error in WebSocket metrics if channel name provided
            if channel_name:
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="query_processing_error",
                    error_message=str(e)
                )
            
            # Calculate total processing time even for errors
            error_processing_time = (time.time() - query_start_time) * 1000  # ms
            
            # Return a graceful error message
            error_response = "I'm sorry, but I encountered an error while processing your query. Please try again later."
            error_metadata = {
                'error': str(e),
                'conversation_id': str(conversation.id) if 'conversation' in locals() and conversation else None,
                'processing_time': error_processing_time
            }
            return error_response, error_metadata
            
    def _ensure_conversation_and_query(self, user, query_text, conversation_id=None, context=None):
        """
        Get or create conversation and user query records.
        
        Args:
            user: The user making the query
            query_text: The user's query text
            conversation_id: Optional ID of an existing conversation
            context: Optional additional context for the query
            
        Returns:
            A tuple of (conversation, user_query)
        """
        # Get or create conversation
        conversation = None
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                logger.warning(f"Conversation {conversation_id} not found for user {user.username}")
        
        if not conversation:
            # Create new conversation
            conversation = Conversation.objects.create(
                user=user,
                title=query_text[:50] + "..." if len(query_text) > 50 else query_text,
                context=context or {}
            )
        
        # Create user query record
        user_query = UserQuery.objects.create(
            user=user,
            query_text=query_text,
            conversation=conversation,
            context=context or {}
        )
        
        # Add message to conversation
        ConversationMessage.objects.create(
            conversation=conversation,
            message_type='user',
            content=query_text,
            metadata=context or {}
        )
        
        return conversation, user_query
    
    def _get_memory_usage(self):
        """Get current memory usage of this process in bytes."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception as e:
            logger.warning(f"Error getting memory usage: {e}")
            return 0
    
    def _track_rag_metrics(self, channel_name: str, metrics: Dict[str, float]):
        """
        Track RAG-specific metrics in WebSocket metrics.
        
        Args:
            channel_name: The WebSocket channel name
            metrics: Dictionary of RAG performance metrics
        """
        try:
            # We'll store RAG metrics in the channel metrics custom data
            # This approach allows for extending the metrics system without modifying its core
            
            # First, record the standard message processing time
            websocket_metrics.record_message_processing(
                channel_name=channel_name,
                processing_time=metrics['total_query_processing_time'],
                message_type="rag_query"
            )
            
            # Store RAG-specific metrics in a custom format in the WebSocket metrics
            # This is channel-specific data that won't affect the global metrics
            for metric_name, metric_value in metrics.items():
                if metric_name in RAG_PERFORMANCE_METRICS['monitored_metrics']:
                    # Use a message_type pattern that can be parsed in reporting
                    websocket_metrics.record_message_processing(
                        channel_name=channel_name,
                        processing_time=metric_value,
                        message_type=f"rag_metric_{metric_name}"
                    )
        except Exception as e:
            logger.error(f"Error tracking RAG metrics: {e}")
    
    def _check_performance_thresholds(self, channel_name: str, metrics: Dict[str, float]):
        """
        Check RAG performance metrics against thresholds and log warnings.
        
        Args:
            channel_name: The WebSocket channel name
            metrics: Dictionary of RAG performance metrics
        """
        try:
            # Check embedding time
            if metrics['query_embedding_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['embedding_critical_time_ms']:
                logger.warning(f"Critical: Embedding time too high: {metrics['query_embedding_time']:.2f}ms")
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="embedding_time_critical",
                    error_message=f"Embedding time of {metrics['query_embedding_time']:.2f}ms exceeds critical threshold"
                )
            elif metrics['query_embedding_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['embedding_warning_time_ms']:
                logger.warning(f"Warning: Embedding time high: {metrics['query_embedding_time']:.2f}ms")
            
            # Check retrieval time
            if metrics['document_retrieval_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['retrieval_critical_time_ms']:
                logger.warning(f"Critical: Retrieval time too high: {metrics['document_retrieval_time']:.2f}ms")
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="retrieval_time_critical",
                    error_message=f"Retrieval time of {metrics['document_retrieval_time']:.2f}ms exceeds critical threshold"
                )
            elif metrics['document_retrieval_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['retrieval_warning_time_ms']:
                logger.warning(f"Warning: Retrieval time high: {metrics['document_retrieval_time']:.2f}ms")
            
            # Check generation time
            if metrics['response_generation_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['generation_critical_time_ms']:
                logger.warning(f"Critical: Generation time too high: {metrics['response_generation_time']:.2f}ms")
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="generation_time_critical",
                    error_message=f"Generation time of {metrics['response_generation_time']:.2f}ms exceeds critical threshold"
                )
            elif metrics['response_generation_time'] > RAG_WEBSOCKET_THRESHOLDS['rag_operations']['generation_warning_time_ms']:
                logger.warning(f"Warning: Generation time high: {metrics['response_generation_time']:.2f}ms")
            
            # Check total query processing time
            if metrics['total_query_processing_time'] > RAG_WEBSOCKET_THRESHOLDS['query_processing']['critical_time_ms']:
                logger.warning(f"Critical: Total query processing time too high: {metrics['total_query_processing_time']:.2f}ms")
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="query_processing_time_critical",
                    error_message=f"Query processing time of {metrics['total_query_processing_time']:.2f}ms exceeds critical threshold"
                )
            elif metrics['total_query_processing_time'] > RAG_WEBSOCKET_THRESHOLDS['query_processing']['warning_time_ms']:
                logger.warning(f"Warning: Total query processing time high: {metrics['total_query_processing_time']:.2f}ms")
            
            # Check memory usage
            if metrics['memory_usage_per_query'] > RAG_WEBSOCKET_THRESHOLDS['query_processing']['memory_critical_mb']:
                logger.warning(f"Critical: Memory usage too high: {metrics['memory_usage_per_query']:.2f}MB")
                websocket_metrics.record_error(
                    channel_name=channel_name,
                    error_type="memory_usage_critical",
                    error_message=f"Memory usage of {metrics['memory_usage_per_query']:.2f}MB exceeds critical threshold"
                )
            elif metrics['memory_usage_per_query'] > RAG_WEBSOCKET_THRESHOLDS['query_processing']['memory_warning_mb']:
                logger.warning(f"Warning: Memory usage high: {metrics['memory_usage_per_query']:.2f}MB")
        
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {e}")
    
    def index_document(self, document: Document) -> Dict[str, Any]:
        """
        Index a document for the RAG system.
        
        Args:
            document: The document to index
            
        Returns:
            Dictionary with indexing results
        """
        try:
            # Delete existing chunks
            DocumentChunk.objects.filter(document=document).delete()
            
            # Invalidate related caches
            self._invalidate_document_related_caches(document)
            
            # Split document into chunks
            chunks = self.embedding_service.chunk_text(document.content)
            
            # Create document chunks with embeddings
            for i, chunk_text in enumerate(chunks):
                # Generate embedding
                embedding_result = self.embedding_service.embed_text(
                    chunk_text,
                    metadata={
                        'document_id': str(document.id),
                        'chunk_index': i,
                        'document_type': document.document_type,
                        'module': document.module,
                        'topic': document.topic
                    }
                )
                
                # Create document chunk
                DocumentChunk.objects.create(
                    document=document,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=embedding_result.embedding,
                    metadata={
                        'document_type': document.document_type,
                        'module': document.module,
                        'topic': document.topic
                    }
                )
            
            return {
                'document_id': str(document.id),
                'chunks_created': len(chunks),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error indexing document {document.id}: {str(e)}")
            return {
                'document_id': str(document.id),
                'status': 'error',
                'error': str(e)
            }
            
    def _invalidate_document_related_caches(self, document: Document) -> None:
        """
        Invalidate caches related to a document.
        
        Args:
            document: The document that has been updated
        """
        try:
            # Invalidate retrieval cache to ensure results reflect the latest content
            cache_service.invalidate_retrieval_cache()
            
            # Invalidate query cache for queries related to this document's topics
            if document.topic:
                cache_service.invalidate_query_cache(query_prefix=document.topic)
            
            if document.module:
                cache_service.invalidate_query_cache(query_prefix=document.module)
                
            logger.info(f"Invalidated caches related to document: {document.title} (ID: {document.id})")
        except Exception as e:
            logger.error(f"Error invalidating document caches: {str(e)}")
            
    def invalidate_all_caches(self) -> Dict[str, Any]:
        """
        Invalidate all RAG system caches.
        
        This is useful when there are significant changes to the knowledge base
        or when troubleshooting cache-related issues.
        
        Returns:
            Dictionary with cache invalidation results
        """
        try:
            # Invalidate all caches
            embeddings_invalidated = cache_service.invalidate_embedding_cache()
            retrieval_invalidated = cache_service.invalidate_retrieval_cache()
            queries_invalidated = cache_service.invalidate_query_cache()
            
            logger.info("Invalidated all RAG system caches")
            
            return {
                'status': 'success',
                'embeddings_invalidated': embeddings_invalidated,
                'retrieval_invalidated': retrieval_invalidated,
                'queries_invalidated': queries_invalidated
            }
        except Exception as e:
            logger.error(f"Error invalidating all caches: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # Get cache statistics from the cache service
            stats = cache_service.get_cache_stats()
            
            # Calculate hit rates
            for cache_type, cache_stats in stats.items():
                if cache_stats['hits'] + cache_stats['misses'] > 0:
                    hit_rate = (cache_stats['hits'] / (cache_stats['hits'] + cache_stats['misses'])) * 100
                else:
                    hit_rate = 0
                
                stats[cache_type]['hit_rate'] = round(hit_rate, 2)
            
            return {
                'status': 'success',
                'statistics': stats
            }
        except Exception as e:
            logger.error(f"Error getting cache statistics: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_system_status(self) -> Dict[str, Any]:
        """
        Check the status of the RAG system.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Check documents
            document_count = Document.objects.count()
            
            # Check document chunks
            chunk_count = DocumentChunk.objects.count()
            
            # Check embeddings
            chunks_with_embeddings = DocumentChunk.objects.exclude(embedding=None).count()
            embedding_percentage = 0
            if chunk_count > 0:
                embedding_percentage = (chunks_with_embeddings / chunk_count) * 100
            
            # Check if system is ready
            system_ready = document_count > 0 and chunk_count > 0 and embedding_percentage > 90
            
            return {
                'status': 'ready' if system_ready else 'not_ready',
                'message': 'RAG system is ready' if system_ready else 'RAG system is not fully ready',
                'document_count': document_count,
                'indexed_chunks': chunk_count,
                'chunks_with_embeddings': chunks_with_embeddings,
                'embedding_percentage': embedding_percentage,
                'system_ready': system_ready
            }
            
        except Exception as e:
            logger.error(f"Error checking RAG system status: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error checking RAG system status: {str(e)}',
                'system_ready': False
            }
    
    def record_feedback(self, response_id: str, rating: int, 
                       feedback_text: Optional[str] = None,
                       improvement_suggestions: Optional[str] = None) -> Dict[str, Any]:
        """
        Record user feedback for a generated response.
        
        Args:
            response_id: The ID of the response
            rating: The rating (1-5)
            feedback_text: Optional feedback text
            improvement_suggestions: Optional improvement suggestions
            
        Returns:
            Dictionary with feedback results
        """
        try:
            # Get response
            response = GeneratedResponse.objects.get(id=response_id)
            
            # Update response with feedback
            response.feedback_rating = rating
            if feedback_text:
                response.feedback_text = feedback_text
            if improvement_suggestions:
                response.improvement_suggestions = improvement_suggestions
            
            # Add feedback to metadata
            metadata = response.metadata or {}
            metadata['feedback'] = {
                'rating': rating,
                'feedback_text': feedback_text,
                'improvement_suggestions': improvement_suggestions,
                'timestamp': timezone.now().isoformat()
            }
            response.metadata = metadata
            
            response.save()
            
            return {
                'status': 'success',
                'response_id': response_id,
                'message': 'Feedback recorded successfully'
            }
            
        except GeneratedResponse.DoesNotExist:
            logger.error(f"Response {response_id} not found")
            return {
                'status': 'error',
                'message': f'Response {response_id} not found'
            }
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error recording feedback: {str(e)}'
            }