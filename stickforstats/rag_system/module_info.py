"""
RAG System Module Information

This module registers the RAG system with the central module registry.
"""

from typing import Dict, Any
from ..core.registry import ModuleRegistry

def register(registry: ModuleRegistry) -> None:
    """
    Register the RAG system module with the registry.
    
    Args:
        registry: The module registry to register with
    """
    module_info = {
        'name': 'Intelligent Assistant',
        'description': 'Provides contextual guidance and answers to statistical questions using a Retrieval-Augmented Generation (RAG) system.',
        'version': '1.0.0',
        'author': 'StickForStats Team',
        'entry_point': 'stickforstats.rag_system.views.rag_dashboard',
        'api_namespace': 'stickforstats.rag_system.api.urls',
        'frontend_path': '/rag',
        'capabilities': [
            'rag',
            'query_answering',
            'contextual_guidance',
            'document_retrieval',
            'conversation_management'
        ],
        'dependencies': ['core'],
        'icon': 'QuestionAnswer',
        'category': 'Core',
        'order': 20,  # After main dashboard but before statistical modules
        'enabled': True,
        'metadata': {
            'max_query_length': 1000,
            'max_conversation_length': 20,
            'supports_module_context': True,
            'supports_feedback': True
        },
        'data_handlers': {
            'text_query': {
                'handler': 'stickforstats.rag_system.services.rag_service.process_query',
                'description': 'Processes text queries and returns contextual responses'
            },
            'document': {
                'handler': 'stickforstats.rag_system.services.document_service.process_document',
                'description': 'Processes and indexes documents for the RAG system'
            }
        }
    }
    
    registry.register_module('rag_system', module_info)