from django.apps import AppConfig


class DOEAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stickforstats.doe_analysis'
    verbose_name = 'Design of Experiments Analysis'
    
    def ready(self):
        """Import signals when the app is ready"""
        import stickforstats.doe_analysis.signals