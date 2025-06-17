"""
API views for the StickForStats MainApp module.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
import json
import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List, Tuple, Optional

# Import services
from ..services.advanced_statistical_analysis import get_advanced_statistical_analysis_service
from ..services.analytics.bayesian.bayesian_service import get_bayesian_analysis_service
from ..services.statistical_tests import get_statistical_tests_service
from ..services.report.report_generator_service import get_report_generator_service

# Import serializers (to be created)
from .serializers import (
    StatisticalTestSerializer,
    AdvancedAnalysisSerializer,
    BayesianAnalysisSerializer,
    ReportGenerationSerializer,
    ReportSerializer,
)

logger = logging.getLogger(__name__)

class StatisticalTestView(APIView):
    """API view for performing statistical tests."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Perform a statistical test."""
        serializer = StatisticalTestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the service
                stats_service = get_statistical_tests_service()
                
                # Extract parameters
                test_type = serializer.validated_data['test_type']
                params = serializer.validated_data.get('parameters', {})
                
                # Perform the test
                if test_type == 'normality':
                    result = stats_service.test_normality(**params)
                elif test_type == 't_test':
                    result = stats_service.perform_t_test(**params)
                elif test_type == 'anova':
                    result = stats_service.perform_anova(**params)
                elif test_type == 'chi_square':
                    result = stats_service.perform_chi_square(**params)
                elif test_type == 'correlation':
                    result = stats_service.compute_correlation(**params)
                else:
                    return Response(
                        {"error": f"Unsupported test type: {test_type}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in StatisticalTestView: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvancedAnalysisView(APIView):
    """API view for performing advanced statistical analyses."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Perform an advanced statistical analysis."""
        serializer = AdvancedAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the service
                analysis_service = get_advanced_statistical_analysis_service()
                
                # Extract parameters
                analysis_type = serializer.validated_data['analysis_type']
                params = serializer.validated_data.get('parameters', {})
                
                # Perform the analysis
                if analysis_type == 'clustering':
                    result = analysis_service.perform_clustering(**params)
                elif analysis_type == 'factor_analysis':
                    result = analysis_service.perform_factor_analysis(**params)
                elif analysis_type == 'time_series':
                    result = analysis_service.analyze_time_series(**params)
                else:
                    return Response(
                        {"error": f"Unsupported analysis type: {analysis_type}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in AdvancedAnalysisView: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BayesianAnalysisView(APIView):
    """API view for performing Bayesian analyses."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Perform a Bayesian analysis."""
        serializer = BayesianAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the service
                bayesian_service = get_bayesian_analysis_service()
                
                # Extract parameters
                analysis_type = serializer.validated_data['analysis_type']
                params = serializer.validated_data.get('parameters', {})
                
                # Perform the analysis
                if analysis_type == 'bayesian_t_test':
                    result = bayesian_service.perform_bayesian_t_test(**params)
                elif analysis_type == 'bayesian_correlation':
                    result = bayesian_service.perform_bayesian_correlation(**params)
                elif analysis_type == 'bayesian_regression':
                    result = bayesian_service.perform_bayesian_regression(**params)
                elif analysis_type == 'bayesian_anova':
                    result = bayesian_service.perform_bayesian_anova(**params)
                else:
                    return Response(
                        {"error": f"Unsupported analysis type: {analysis_type}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in BayesianAnalysisView: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportGeneratorView(APIView):
    """API view for generating reports."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate a report."""
        serializer = ReportGenerationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Get the service
                report_service = get_report_generator_service()
                
                # Extract parameters
                title = serializer.validated_data['title']
                analyses = serializer.validated_data['analyses']
                report_format = serializer.validated_data.get('format', 'pdf')
                description = serializer.validated_data.get('description', None)
                include_visualizations = serializer.validated_data.get('include_visualizations', True)
                include_raw_data = serializer.validated_data.get('include_raw_data', False)
                
                # Generate the report
                report_metadata, report_buffer = report_service.generate_report_from_analyses(
                    user_id=str(request.user.id),
                    analyses=analyses,
                    title=title,
                    description=description,
                    report_format=report_format,
                    include_visualizations=include_visualizations,
                    include_raw_data=include_raw_data
                )
                
                # Return the report metadata
                return Response(report_metadata, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in ReportGeneratorView: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportListView(APIView):
    """API view for listing user reports."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get a list of reports for the current user."""
        try:
            # Get the service
            report_service = get_report_generator_service()
            
            # Get the reports
            limit = int(request.query_params.get('limit', 20))
            reports = report_service.get_user_reports(str(request.user.id), limit=limit)
            
            # Return the reports
            return Response(reports, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in ReportListView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportDetailView(APIView):
    """API view for retrieving and downloading reports."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        """Get a specific report."""
        try:
            # Get the service
            report_service = get_report_generator_service()
            
            # Check if the 'download' parameter is present
            download = request.query_params.get('download', 'false').lower() == 'true'
            
            # Get the report metadata
            reports = report_service.get_user_reports(str(request.user.id))
            report = next((r for r in reports if r.get('id') == report_id), None)
            
            if not report:
                return Response(
                    {"error": f"Report not found: {report_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # If download is requested, serve the file
            if download:
                try:
                    file_path = report.get('file_path')
                    if not file_path:
                        return Response(
                            {"error": "Report file path not found"},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    # Serve the file
                    response = FileResponse(open(file_path, 'rb'))
                    response['Content-Disposition'] = f'attachment; filename="{report.get("title", "report")}.{report.get("report_format", "pdf")}"'
                    return response
                except FileNotFoundError:
                    return Response(
                        {"error": "Report file not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Return the report metadata
            return Response(report, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in ReportDetailView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )