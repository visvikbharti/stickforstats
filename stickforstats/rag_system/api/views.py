from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404
import time

from .permissions import IsDocumentOwnerOrAdmin, IsConversationParticipant

# Import monitoring and logging services
from ..services.logging_service import logging_service
from ..services.monitoring_service import monitoring_service
from ..services.dashboard_service import dashboard_service
from ..services.alerting_service import alerting_service
from ..prometheus_metrics import metrics_exporter

from ..models import (
    Document, 
    DocumentChunk, 
    UserQuery,
    RetrievedDocument,
    GeneratedResponse,
    Conversation,
    ConversationMessage
)
from .serializers import (
    DocumentSerializer,
    DocumentChunkSerializer,
    UserQuerySerializer,
    RetrievedDocumentSerializer,
    GeneratedResponseSerializer,
    ConversationSerializer,
    ConversationMessageSerializer,
    QueryRequestSerializer,
    QueryResponseSerializer,
    FeedbackSerializer
)
from ..services.rag_service import RAGService
from ..services.cache_service import cache_service


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing knowledge base documents."""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDocumentOwnerOrAdmin]
    
    def get_queryset(self):
        """Filter documents based on query parameters."""
        queryset = Document.objects.all()
        
        # Apply filters if provided
        document_type = self.request.query_params.get('document_type', None)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
            
        module = self.request.query_params.get('module', None)
        if module:
            queryset = queryset.filter(module=module)
            
        topic = self.request.query_params.get('topic', None)
        if topic:
            queryset = queryset.filter(topic=topic)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Return all chunks for a specific document."""
        document = self.get_object()
        chunks = DocumentChunk.objects.filter(document=document)
        serializer = DocumentChunkSerializer(chunks, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    
    def get_queryset(self):
        """Return conversations for the current user."""
        return Conversation.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Return all messages for a specific conversation."""
        conversation = self.get_object()
        messages = ConversationMessage.objects.filter(conversation=conversation)
        serializer = ConversationMessageSerializer(messages, many=True)
        return Response(serializer.data)


class QueryView(APIView):
    """API view for processing user queries through the RAG system."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process a user query and return a response."""
        start_time = time.time()
        
        # Log query received event
        logging_service.log_event(
            event_type='QUERY_RECEIVED',
            message=f"User query received",
            user_id=str(request.user.id) if request.user.is_authenticated else None,
            context={
                'path': request.path,
                'method': request.method
            }
        )
        
        serializer = QueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            # Log validation error
            logging_service.log_event(
                event_type='ERROR',
                message=f"Query validation error: {serializer.errors}",
                user_id=str(request.user.id) if request.user.is_authenticated else None,
                level='warning'
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        query = serializer.validated_data['query']
        conversation_id = serializer.validated_data.get('conversation_id')
        context = serializer.validated_data.get('context', {})
        filters = serializer.validated_data.get('filters', {})
        
        # Create RAG service instance
        rag_service = RAGService()
        
        try:
            # Process the query
            response_text, metadata = rag_service.process_query(
                query_text=query,
                user=request.user,
                conversation_id=conversation_id,
                context=context,
                filters=filters
            )
            
            # Log query processed event
            processing_time = (time.time() - start_time) * 1000  # ms
            
            # Record metrics
            user_type = 'authenticated' if request.user.is_authenticated else 'anonymous'
            cache_hit = metadata.get('from_cache', False)
            metrics_exporter.track_query(user_type, processing_time, cache_hit)
            
            # Log performance metrics
            logging_service.log_performance(
                operation='total_query_processing',
                duration_ms=processing_time,
                context={
                    'query_id': metadata.get('query_id'),
                    'conversation_id': metadata.get('conversation_id'),
                    'from_cache': cache_hit
                }
            )
            
            # Track performance metrics in detail if available
            performance_metrics = metadata.get('performance_metrics', {})
            if performance_metrics:
                # Track embedding time
                if 'query_embedding_time' in performance_metrics:
                    metrics_exporter.track_embedding(
                        performance_metrics['query_embedding_time'],
                        cache_hit=performance_metrics.get('cache_hit', False)
                    )
                
                # Track retrieval time
                if 'document_retrieval_time' in performance_metrics:
                    metrics_exporter.track_retrieval(
                        performance_metrics['document_retrieval_time'],
                        cache_hit=performance_metrics.get('cache_hit', False)
                    )
                
                # Track generation time
                if 'response_generation_time' in performance_metrics:
                    metrics_exporter.track_generation(
                        performance_metrics['response_generation_time']
                    )
            
            # Check for slow processing
            if processing_time > 5000:  # 5 seconds
                logging_service.log_event(
                    event_type='PERFORMANCE_WARNING',
                    message=f"Slow query processing: {processing_time:.2f}ms",
                    user_id=str(request.user.id) if request.user.is_authenticated else None,
                    context={
                        'query_id': metadata.get('query_id'),
                        'processing_time': processing_time,
                        'performance_metrics': performance_metrics
                    },
                    level='warning'
                )
            
            # Log successful query response
            logging_service.log_event(
                event_type='RESPONSE_GENERATED',
                message=f"Response generated for query",
                user_id=str(request.user.id) if request.user.is_authenticated else None,
                context={
                    'query_id': metadata.get('query_id'),
                    'response_id': metadata.get('response_id'),
                    'processing_time': processing_time,
                    'from_cache': cache_hit
                }
            )
            
            # Create response data
            response_data = {
                'response': response_text,
                'conversation_id': metadata.get('conversation_id'),
                'sources': metadata.get('sources', []),
                'metadata': metadata
            }
            
            return Response(response_data)
            
        except Exception as e:
            # Log error
            error_processing_time = (time.time() - start_time) * 1000  # ms
            
            logging_service.log_error(
                error_message=f"Error processing query: {str(e)}",
                exception=e,
                user_id=str(request.user.id) if request.user.is_authenticated else None,
                context={
                    'query': query,
                    'conversation_id': conversation_id,
                    'processing_time': error_processing_time
                }
            )
            
            # Send alert for critical errors
            alerting_service.send_alert(
                alert_type='RAG_PROCESSING_ERROR',
                message=f"Error processing RAG query: {str(e)}",
                severity='error',
                context={
                    'user_id': str(request.user.id) if request.user.is_authenticated else None,
                    'processing_time': error_processing_time,
                    'query': query
                }
            )
            
            # Track error in metrics
            metrics_exporter.track_websocket_error('query_processing_error')
            
            return Response(
                {'error': f'Error processing query: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackView(APIView):
    """API view for submitting feedback on generated responses."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process feedback on a generated response."""
        serializer = FeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validated data
        response_id = serializer.validated_data['response_id']
        rating = serializer.validated_data['rating']
        feedback_text = serializer.validated_data.get('feedback_text')
        improvement_suggestions = serializer.validated_data.get('improvement_suggestions')
        
        try:
            # Get the response object
            response_obj = GeneratedResponse.objects.get(id=response_id)
            
            # Check permissions
            if response_obj.user_query.user != request.user:
                return Response(
                    {'error': 'You do not have permission to provide feedback for this response'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update response with feedback
            response_obj.feedback_rating = rating
            if feedback_text:
                response_obj.feedback_text = feedback_text
            if improvement_suggestions:
                response_obj.improvement_suggestions = improvement_suggestions
            response_obj.save()
            
            return Response({'status': 'feedback recorded'}, status=status.HTTP_200_OK)
            
        except GeneratedResponse.DoesNotExist:
            return Response(
                {'error': 'Response not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class RecentQueriesView(APIView):
    """API view for retrieving recent queries by the user."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return recent queries made by the user."""
        limit = int(request.query_params.get('limit', 10))
        
        # Get recent queries
        recent_queries = UserQuery.objects.filter(
            user=request.user
        ).order_by('-created_at')[:limit]
        
        # Get responses for these queries
        query_data = []
        for query in recent_queries:
            try:
                response = GeneratedResponse.objects.get(user_query=query)
                response_text = response.response_text
                response_id = response.id
            except GeneratedResponse.DoesNotExist:
                response_text = None
                response_id = None
                
            query_data.append({
                'id': query.id,
                'query_text': query.query_text,
                'created_at': query.created_at,
                'response_text': response_text,
                'response_id': response_id,
                'conversation_id': query.conversation.id if query.conversation else None
            })
            
        return Response(query_data)


class CacheStatsView(APIView):
    """API view for retrieving RAG system cache statistics."""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get(self, request):
        """Return cache statistics."""
        rag_service = RAGService()
        stats = rag_service.get_cache_statistics()
        return Response(stats)


class CacheManagementView(APIView):
    """API view for managing RAG system cache."""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def post(self, request):
        """
        Manage the cache based on the action.
        
        Actions:
        - invalidate_all: Invalidate all caches
        - invalidate_embeddings: Invalidate embedding cache
        - invalidate_retrieval: Invalidate retrieval cache
        - invalidate_queries: Invalidate query cache
        """
        action = request.data.get('action')
        
        if not action:
            return Response(
                {'error': 'Action is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rag_service = RAGService()
        
        if action == 'invalidate_all':
            result = rag_service.invalidate_all_caches()
            return Response(result)
        
        elif action == 'invalidate_embeddings':
            success = cache_service.invalidate_embedding_cache()
            return Response({'status': 'success' if success else 'error'})
        
        elif action == 'invalidate_retrieval':
            success = cache_service.invalidate_retrieval_cache()
            return Response({'status': 'success' if success else 'error'})
        
        elif action == 'invalidate_queries':
            success = cache_service.invalidate_query_cache()
            return Response({'status': 'success' if success else 'error'})
        
        else:
            return Response(
                {'error': f'Unknown action: {action}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class MonitoringDashboardView(APIView):
    """API view for retrieving monitoring dashboard data."""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get(self, request):
        """Return monitoring dashboard data."""
        action = request.query_params.get('action', 'system_health')
        time_range = request.query_params.get('time_range', 'day')
        
        if action == 'system_health':
            data = dashboard_service.get_system_health_data()
        elif action == 'performance_metrics':
            data = dashboard_service.get_performance_metrics(time_range)
        elif action == 'rag_operations':
            data = dashboard_service.get_rag_operations_metrics(time_range)
        elif action == 'error_analytics':
            data = dashboard_service.get_error_analytics(time_range)
        elif action == 'usage_analytics':
            data = dashboard_service.get_usage_analytics(time_range)
        else:
            return Response(
                {'error': f'Unknown action: {action}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(data)


class AlertingView(APIView):
    """API view for managing alerts."""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get(self, request):
        """Get recent alerts."""
        limit = int(request.query_params.get('limit', 50))
        severity = request.query_params.get('severity')
        
        alerts = alerting_service.get_recent_alerts(limit=limit, severity=severity)
        return Response({'alerts': alerts})
    
    def post(self, request):
        """Test alert or manage alert settings."""
        action = request.data.get('action')
        
        if action == 'test_alert':
            message = request.data.get('message', 'Test alert')
            severity = request.data.get('severity', 'info')
            alert_type = request.data.get('alert_type', 'TEST_ALERT')
            
            # Send test alert
            alerting_service.send_alert(
                alert_type=alert_type,
                message=message,
                severity=severity,
                context={'test': True}
            )
            
            return Response({'status': 'alert sent'})
        else:
            return Response(
                {'error': f'Unknown action: {action}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )