from django.apps import AppConfig


class RagSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stickforstats.rag_system'
    verbose_name = 'RAG System'
    
    def ready(self):
        """
        Initialize the RAG system when Django starts.
        
        This method:
        1. Sets up signal handlers
        2. Registers the module with the central registry
        3. Initializes any required services
        """
        # Import here to avoid circular imports
        from ..core.registry import get_registry
        
        # Import module_info to register with central registry
        from . import module_info  # This will register the module
        
        # Initialize services if needed
        from .services.rag_service import initialize_rag_services
        initialize_rag_services()