"""
Views for the RAG system.

These views handle the main dashboard and integration points for the RAG system.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import logging

from .models import Document, Conversation
from .services.rag_service import RAGService

logger = logging.getLogger(__name__)

@login_required
def rag_dashboard(request):
    """
    Main dashboard view for the RAG system.
    
    Args:
        request: The HTTP request
        
    Returns:
        Rendered template for the RAG dashboard
    """
    context = {
        'title': 'Intelligent Assistant',
        'module': 'rag_system',
        'documents_count': Document.objects.count(),
        'conversations_count': Conversation.objects.filter(user=request.user).count(),
        'rag_config': {
            'max_query_length': getattr(settings, 'RAG_MAX_QUERY_LENGTH', 1000),
            'max_conversation_length': getattr(settings, 'RAG_MAX_CONVERSATION_LENGTH', 20),
            'supports_module_context': True,
            'supports_feedback': True
        }
    }
    
    return render(request, 'rag_system/dashboard.html', context)

@login_required
@require_http_methods(["GET"])
def rag_status(request):
    """
    API view to check the status of the RAG system.
    
    Args:
        request: The HTTP request
        
    Returns:
        JSON response with status information
    """
    try:
        rag_service = RAGService()
        status = rag_service.check_system_status()
        
        response_data = {
            'status': status['status'],
            'message': status['message'],
            'details': {
                'documents_count': Document.objects.count(),
                'indexed_chunks': status.get('indexed_chunks', 0),
                'conversations_count': Conversation.objects.filter(user=request.user).count(),
                'system_ready': status.get('system_ready', False)
            }
        }
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error checking RAG system status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Could not check RAG system status',
            'details': {'error': str(e)}
        }, status=500)

@login_required
@require_http_methods(["GET"])
def module_documents(request, module_name):
    """
    API view to get documents for a specific module.
    
    Args:
        request: The HTTP request
        module_name: The name of the module to get documents for
        
    Returns:
        JSON response with documents for the module
    """
    try:
        documents = Document.objects.filter(module=module_name)
        
        response_data = {
            'module': module_name,
            'document_count': documents.count(),
            'documents': [
                {
                    'id': str(doc.id),
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'topic': doc.topic,
                    'created_at': doc.created_at.isoformat()
                }
                for doc in documents[:100]  # Limit to 100 for performance
            ]
        }
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error getting documents for module {module_name}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Could not get documents for module {module_name}',
            'details': {'error': str(e)}
        }, status=500)