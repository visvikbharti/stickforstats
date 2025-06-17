"""
Session management service for the StickForStats application.

This module provides services for managing analysis sessions, results tracking,
and history management, adapted from the original Streamlit-based session_manager.py.
"""
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
import pandas as pd

from django.conf import settings
from django.db import transaction, models
from django.db.models import Q, Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from stickforstats.mainapp.models import (
    User, AnalysisSession, AnalysisResult, Dataset, Visualization
)

from ..services.report.report_generator_service import get_report_generator_service

# Configure logging
logger = logging.getLogger(__name__)


class SessionService:
    """
    Handles user sessions, analysis history, and state management within the application.
    
    This service provides methods for:
    - Tracking analysis history
    - Saving and loading analysis results
    - Managing visualizations
    - Retrieving user history
    - Generating reports from analysis results
    - Exporting analysis data in different formats
    """
    
    def __init__(self, base_storage_path: str = None):
        """
        Initialize the session service.
        
        Args:
            base_storage_path: Base path for storing files (defaults to settings.MEDIA_ROOT)
        """
        self.base_storage_path = base_storage_path or getattr(settings, 'MEDIA_ROOT', 'media')
        self._ensure_storage_directories()
    
    def _ensure_storage_directories(self) -> None:
        """Ensure required storage directories exist."""
        directories = [
            os.path.join(self.base_storage_path, "user_sessions"),
            os.path.join(self.base_storage_path, "analysis_history"),
            os.path.join(self.base_storage_path, "plots"),
            os.path.join(self.base_storage_path, "reports"),
            os.path.join(self.base_storage_path, "exports"),
            os.path.join(self.base_storage_path, "reports", "pdf"),
            os.path.join(self.base_storage_path, "reports", "html"),
            os.path.join(self.base_storage_path, "reports", "docx")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_analysis_session(self, 
                               user: User, 
                               name: str,
                               module: str = 'core',
                               description: str = None,
                               dataset: Optional[Dataset] = None,
                               configuration: Optional[Dict[str, Any]] = None) -> AnalysisSession:
        """
        Create a new analysis session.
        
        Args:
            user: User who owns the session
            name: Session name
            module: Module that will handle the analysis
            description: Optional description
            dataset: Optional dataset to analyze
            configuration: Optional configuration parameters
            
        Returns:
            Created AnalysisSession instance
        """
        try:
            session = AnalysisSession.objects.create(
                user=user,
                name=name,
                description=description,
                module=module,
                dataset=dataset,
                configuration=configuration or {},
                status='created'
            )
            logger.info(f"Created analysis session {session.id} for user {user.username}")
            return session
        except Exception as e:
            logger.error(f"Error creating analysis session: {str(e)}")
            raise
    
    def save_analysis_result(self, 
                           session: AnalysisSession,
                           name: str, 
                           analysis_type: str, 
                           parameters: Dict[str, Any],
                           result_summary: Dict[str, Any],
                           result_detail: Optional[Dict[str, Any]] = None,
                           interpretation: Optional[str] = None,
                           plot_data: Optional[Dict[str, Any]] = None,
                           visualizations: Optional[List[Dict[str, Any]]] = None) -> AnalysisResult:
        """
        Save analysis results with associated visualizations.
        
        Args:
            session: Analysis session to associate results with
            name: Name for the result
            analysis_type: Type of analysis performed
            parameters: Parameters used in the analysis
            result_summary: Summary of analysis results
            result_detail: Detailed results (optional)
            interpretation: Text interpretation of results (optional)
            plot_data: Plot data for rendering visualizations (optional)
            visualizations: List of visualization configurations (optional)
            
        Returns:
            Created AnalysisResult instance
        """
        try:
            with transaction.atomic():
                # Create analysis result
                result = AnalysisResult.objects.create(
                    session=session,
                    name=name,
                    analysis_type=analysis_type,
                    parameters=parameters,
                    result_summary=result_summary,
                    result_detail=result_detail or {},
                    interpretation=interpretation,
                    plot_data=plot_data or {}
                )
                
                # Create visualizations if provided
                if visualizations:
                    for viz_data in visualizations:
                        Visualization.objects.create(
                            analysis_result=result,
                            title=viz_data.get('title', 'Visualization'),
                            description=viz_data.get('description'),
                            visualization_type=viz_data.get('type', 'other'),
                            figure_data=viz_data.get('figure', {}),
                            figure_layout=viz_data.get('layout', {})
                        )
                
                # Update session status
                session.status = 'completed'
                session.completed_at = datetime.now()
                session.save()
                
                logger.info(f"Saved analysis result {result.id} for session {session.id}")
                return result
                
        except Exception as e:
            logger.error(f"Error saving analysis result: {str(e)}")
            # Update session status to failed
            session.status = 'failed'
            session.save()
            raise
    
    def get_analysis_result(self, result_id: Union[str, uuid.UUID]) -> Optional[AnalysisResult]:
        """
        Retrieve analysis result by ID.
        
        Args:
            result_id: UUID of the analysis result
            
        Returns:
            AnalysisResult if found, None otherwise
        """
        try:
            return AnalysisResult.objects.get(id=result_id)
        except AnalysisResult.DoesNotExist:
            logger.warning(f"Analysis result {result_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving analysis result {result_id}: {str(e)}")
            return None
    
    def get_user_history(self, user: User, 
                        module: Optional[str] = None, 
                        analysis_type: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: int = 100,
                        include_visualizations: bool = True,
                        order_by: str = '-created_at') -> List[Dict[str, Any]]:
        """
        Get user's analysis history.
        
        Args:
            user: User to get history for
            module: Optional module filter
            analysis_type: Optional analysis type filter
            start_date: Optional start date for filtering results
            end_date: Optional end date for filtering results
            limit: Maximum number of results to return
            include_visualizations: Whether to include visualization data
            order_by: Field to order results by (prefix with '-' for descending)
            
        Returns:
            List of analysis results as dictionaries
        """
        try:
            # Build base query
            query = AnalysisSession.objects.filter(user=user)
            
            # Apply module filter if provided
            if module:
                query = query.filter(module=module)
            
            # Apply date filters if provided
            if start_date:
                query = query.filter(created_at__gte=start_date)
                
            if end_date:
                query = query.filter(created_at__lte=end_date)
            
            # Get sessions with results, ordered by creation date
            sessions = query.filter(
                status='completed'
            ).select_related(
                'dataset'
            ).prefetch_related(
                'results'
            ).order_by(order_by)
            
            # Apply analysis type filter if needed (has to be done after prefetching)
            results_query = None
            if analysis_type:
                results_query = AnalysisResult.objects.filter(analysis_type=analysis_type)
                
            # Get the results and apply limit
            all_results = []
            for session in sessions:
                if results_query:
                    session_results = results_query.filter(session=session)
                else:
                    session_results = session.results.all()
                
                all_results.extend(session_results)
                if len(all_results) >= limit:
                    all_results = all_results[:limit]
                    break
            
            # Format results
            history = []
            for result in all_results:
                session = result.session
                result_dict = {
                    'id': str(result.id),
                    'session_id': str(session.id),
                    'timestamp': result.created_at.strftime('%Y%m%d_%H%M%S'),
                    'name': result.name,
                    'analysis_type': result.analysis_type,
                    'parameters': result.parameters,
                    'results': result.result_summary,
                    'interpretation': result.interpretation,
                    'dataset': {
                        'id': str(session.dataset.id) if session.dataset else None,
                        'name': session.dataset.name if session.dataset else None
                    } if session.dataset else None,
                    'module': session.module,
                    'date_created': result.created_at.isoformat()
                }
                
                # Include visualizations if requested
                if include_visualizations:
                    visualizations = result.visualizations.all()
                    if visualizations:
                        result_dict['visualizations'] = [
                            {
                                'id': str(viz.id),
                                'title': viz.title,
                                'description': viz.description,
                                'type': viz.visualization_type,
                                'figure': viz.figure_data,
                                'layout': viz.figure_layout
                            }
                            for viz in visualizations
                        ]
                
                history.append(result_dict)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting user history: {str(e)}")
            return []
    
    def clear_user_history(self, user: User) -> bool:
        """
        Clear user's analysis history.
        
        Args:
            user: User to clear history for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                # Get all user sessions
                sessions = AnalysisSession.objects.filter(user=user)
                
                # Get all result IDs
                result_ids = AnalysisResult.objects.filter(
                    session__in=sessions
                ).values_list('id', flat=True)
                
                # Delete visualizations
                Visualization.objects.filter(
                    analysis_result_id__in=result_ids
                ).delete()
                
                # Delete results
                AnalysisResult.objects.filter(id__in=result_ids).delete()
                
                # Delete sessions
                sessions.delete()
                
                return True
                
        except Exception as e:
            logger.error(f"Error clearing user history: {str(e)}")
            return False
    
    def generate_report_from_history(self,
                                user: User,
                                title: str = "Analysis History Report",
                                description: Optional[str] = None,
                                module: Optional[str] = None,
                                analysis_type: Optional[str] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                limit: int = 20,
                                report_format: str = 'pdf') -> Tuple[Dict[str, Any], Any]:
        """
        Generate a report from user's analysis history.
        
        Args:
            user: User to generate report for
            title: Report title
            description: Optional report description
            module: Optional module filter
            analysis_type: Optional analysis type filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of analyses to include
            report_format: Report format ('pdf', 'html', 'docx')
            
        Returns:
            Tuple of (report metadata, report buffer)
        """
        try:
            # Get the report service
            report_service = get_report_generator_service()
            
            # Get user history with filtering
            history = self.get_user_history(
                user,
                module=module,
                analysis_type=analysis_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                include_visualizations=True
            )
            
            if not history:
                logger.warning(f"No analysis history found for user {user.id}")
                return None, None
            
            # Convert history to analysis results format expected by report service
            analyses = []
            for item in history:
                analysis = {
                    'id': item['id'],
                    'name': item['name'],
                    'analysis_type': item['analysis_type'],
                    'parameters': item['parameters'],
                    'results': item['results'],
                    'visualizations': item.get('visualizations', [])
                }
                analyses.append(analysis)
            
            # Generate the report
            report_metadata, report_buffer = report_service.generate_report_from_analyses(
                user_id=str(user.id),
                analyses=analyses,
                title=title,
                description=description,
                report_format=report_format,
                include_visualizations=True
            )
            
            return report_metadata, report_buffer
            
        except Exception as e:
            logger.error(f"Error generating report from history: {str(e)}")
            return None, None
    
    def export_analysis_data(self, user: User, format: str = 'json', 
                             module: Optional[str] = None,
                             analysis_type: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Optional[str]:
        """
        Export user's analysis history in specified format.
        
        Args:
            user: User to export data for
            format: Export format ('json' or 'csv')
            module: Optional module filter
            analysis_type: Optional analysis type filter
            start_date: Optional start date for filtering results
            end_date: Optional end date for filtering results
            
        Returns:
            Path to the exported file, or None if export failed
        """
        try:
            # Get user history with filters
            history = self.get_user_history(
                user, 
                module=module,
                analysis_type=analysis_type,
                start_date=start_date,
                end_date=end_date,
                include_visualizations=False
            )
            
            if not history:
                return None
            
            # Create export directory
            export_dir = os.path.join(self.base_storage_path, 'exports', str(user.id))
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_export_{timestamp}.{format}"
            filepath = os.path.join(export_dir, filename)
            
            if format == 'json':
                # Export as JSON
                with open(filepath, 'w') as f:
                    json.dump(history, f, indent=2)
            elif format == 'csv':
                # Convert to DataFrame and export as CSV
                flat_data = []
                for item in history:
                    flat_item = {
                        'id': item['id'],
                        'session_id': item['session_id'],
                        'timestamp': item['timestamp'],
                        'name': item['name'],
                        'analysis_type': item['analysis_type'],
                        'interpretation': item['interpretation'],
                        'module': item['module'],
                        'date_created': item['date_created']
                    }
                    
                    # Flatten parameters and results
                    for key, value in item['parameters'].items():
                        if isinstance(value, (str, int, float, bool)):
                            flat_item[f"param_{key}"] = value
                    
                    for key, value in item['results'].items():
                        if isinstance(value, (str, int, float, bool)):
                            flat_item[f"result_{key}"] = value
                    
                    flat_data.append(flat_item)
                
                # Create DataFrame and save as CSV
                df = pd.DataFrame(flat_data)
                df.to_csv(filepath, index=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting analysis data: {str(e)}")
            return None
    
    def get_recent_session_stats(self, user: User, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics about recent user sessions.
        
        Args:
            user: User to get stats for
            days: Number of days to consider as "recent"
            
        Returns:
            Dictionary with session statistics
        """
        try:
            # Count total sessions
            total_sessions = AnalysisSession.objects.filter(user=user).count()
            
            # Count total results
            total_results = AnalysisResult.objects.filter(session__user=user).count()
            
            # Count total visualizations
            total_visualizations = Visualization.objects.filter(
                analysis_result__session__user=user
            ).count()
            
            # Count sessions by module
            module_counts = AnalysisSession.objects.filter(
                user=user
            ).values('module').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            # Get recent sessions (last N days)
            recent_date = datetime.now() - timedelta(days=days)
            recent_sessions = AnalysisSession.objects.filter(
                user=user, 
                created_at__gte=recent_date
            ).count()
            
            # Get recent activity by date
            recent_activity = AnalysisSession.objects.filter(
                user=user,
                created_at__gte=recent_date
            ).extra(
                select={'date': "DATE(created_at)"}
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')
            
            return {
                'total_sessions': total_sessions,
                'total_results': total_results,
                'total_visualizations': total_visualizations,
                'recent_sessions': recent_sessions,
                'module_distribution': {
                    item['module']: item['count'] for item in module_counts
                },
                'activity_timeline': {
                    str(item['date']): item['count'] for item in recent_activity
                },
                'time_range_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting session stats: {str(e)}")
            return {
                'total_sessions': 0,
                'total_results': 0,
                'total_visualizations': 0,
                'recent_sessions': 0,
                'module_distribution': {},
                'activity_timeline': {},
                'time_range_days': days
            }


# Create singleton instance
session_service = SessionService()

def get_session_service() -> SessionService:
    """Get global session service instance."""
    return session_service