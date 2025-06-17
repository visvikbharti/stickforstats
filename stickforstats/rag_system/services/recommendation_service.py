"""
Recommendation Service Module for RAG-based guidance.

This module provides recommendation services based on analysis results,
using a RAG approach to guide users through their statistical analysis journey.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from django.conf import settings
from pgvector.django import L2Distance

from stickforstats.core.models import AnalysisSession, AnalysisResult, RagDocument
from stickforstats.sqc_analysis.models import ControlChartAnalysis, ProcessCapabilityAnalysis

# Get logger
logger = logging.getLogger(__name__)


class AnalysisRecommendationService:
    """Service for generating analysis recommendations."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        pass
    
    def get_next_steps(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Generate recommended next steps based on an analysis result.
        
        Args:
            analysis_result: The analysis result to generate recommendations for
        
        Returns:
            Dictionary containing recommendations
        """
        try:
            analysis_type = analysis_result.analysis_type
            
            # Get recommendations based on analysis type
            if analysis_type.startswith('control_chart_'):
                return self._get_control_chart_recommendations(analysis_result)
            elif analysis_type.startswith('process_capability'):
                return self._get_process_capability_recommendations(analysis_result)
            elif analysis_type.startswith('acceptance_sampling'):
                return self._get_acceptance_sampling_recommendations(analysis_result)
            elif analysis_type.startswith('msa'):
                return self._get_msa_recommendations(analysis_result)
            else:
                # Generic recommendations for unknown types
                return {
                    'recommendations': [
                        {
                            'title': 'Explore other analysis types',
                            'description': 'Consider exploring other analysis types to gain more insights from your data.',
                            'action_type': 'navigation',
                            'action_path': '/dashboard',
                            'severity': 'low'
                        },
                        {
                            'title': 'Generate report',
                            'description': 'Generate a comprehensive report of your analysis results.',
                            'action_type': 'report',
                            'severity': 'medium'
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                'error': f"Error generating recommendations: {str(e)}",
                'recommendations': []
            }
    
    def _get_control_chart_recommendations(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Generate recommendations based on control chart analysis.
        
        Args:
            analysis_result: The control chart analysis result
        
        Returns:
            Dictionary containing recommendations
        """
        recommendations = []
        
        # Get related control chart details
        try:
            control_chart = ControlChartAnalysis.objects.get(analysis_result=analysis_result)
            chart_type = control_chart.chart_type
            has_violations = bool(control_chart.special_causes_detected)
        except ControlChartAnalysis.DoesNotExist:
            chart_type = "unknown"
            has_violations = False
        
        # Process in control or out of control
        if has_violations:
            recommendations.append({
                'title': 'Investigate Special Causes',
                'description': 'Your control chart shows evidence of special cause variation. Investigate the points that violate control rules.',
                'action_type': 'investigate',
                'resource_type': 'special_causes',
                'severity': 'high'
            })
            
            # Get related educational content for special causes
            rag_documents = self._get_related_rag_documents(
                f"special cause variation {chart_type} chart", 
                module='sqc',
                document_type='tutorial',
                limit=2
            )
            
            for doc in rag_documents:
                recommendations.append({
                    'title': doc.title,
                    'description': f"Learn about {doc.title.lower()}",
                    'action_type': 'education',
                    'resource_id': str(doc.id),
                    'severity': 'medium'
                })
        else:
            recommendations.append({
                'title': 'Process appears to be in control',
                'description': 'Your control chart shows no signs of special cause variation. The process appears to be stable.',
                'action_type': 'information',
                'severity': 'low'
            })
        
        # Always recommend process capability analysis after control charts
        recommendations.append({
            'title': 'Process Capability Analysis',
            'description': 'Perform a process capability analysis to evaluate how well your process meets specifications.',
            'action_type': 'analysis',
            'analysis_type': 'process_capability',
            'severity': 'medium' if not has_violations else 'low'
        })
        
        # If using I-MR chart, check for autocorrelation
        if chart_type == 'i_mr':
            autocorrelation = analysis_result.result_detail.get('process_statistics', {}).get('autocorrelation')
            if autocorrelation and abs(autocorrelation) > 0.3:
                recommendations.append({
                    'title': 'Address Autocorrelation',
                    'description': 'Your data shows significant autocorrelation, which may violate control chart assumptions. Consider time series analysis methods.',
                    'action_type': 'analysis',
                    'analysis_type': 'time_series',
                    'severity': 'high'
                })
        
        return {
            'recommendations': recommendations
        }
    
    def _get_process_capability_recommendations(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Generate recommendations based on process capability analysis.
        
        Args:
            analysis_result: The process capability analysis result
        
        Returns:
            Dictionary containing recommendations
        """
        recommendations = []
        
        # Get related process capability details
        try:
            process_capability = ProcessCapabilityAnalysis.objects.get(analysis_result=analysis_result)
            cpk = process_capability.cpk
            ppk = process_capability.ppk
            normal_capability = process_capability.assume_normality
        except ProcessCapabilityAnalysis.DoesNotExist:
            cpk = None
            ppk = None
            normal_capability = True
        
        # Check capability indices
        if cpk is not None:
            if cpk < 1.0:
                severity = 'high' if cpk < 0.67 else 'medium'
                recommendations.append({
                    'title': 'Process Not Capable',
                    'description': f'Your process has a Cpk of {cpk:.2f}, which indicates it is not capable of meeting specifications.',
                    'action_type': 'improvement',
                    'severity': severity
                })
                
                # Get related educational content for process improvement
                rag_documents = self._get_related_rag_documents(
                    "improve process capability low cpk", 
                    module='sqc',
                    document_type='tutorial',
                    limit=2
                )
                
                for doc in rag_documents:
                    recommendations.append({
                        'title': doc.title,
                        'description': f"Learn about {doc.title.lower()}",
                        'action_type': 'education',
                        'resource_id': str(doc.id),
                        'severity': 'medium'
                    })
            else:
                recommendations.append({
                    'title': 'Process is Capable',
                    'description': f'Your process has a Cpk of {cpk:.2f}, which indicates it is capable of meeting specifications.',
                    'action_type': 'information',
                    'severity': 'low'
                })
        
        # Check normality assumption
        if normal_capability:
            recommendations.append({
                'title': 'Verify Normality Assumption',
                'description': 'Your capability analysis assumes normal distribution. Verify this assumption with a normality test.',
                'action_type': 'analysis',
                'analysis_type': 'normality_test',
                'severity': 'medium'
            })
        
        # Recommend design of experiments as a next step
        recommendations.append({
            'title': 'Design of Experiments',
            'description': 'Consider conducting designed experiments to systematically improve your process.',
            'action_type': 'analysis',
            'analysis_type': 'doe',
            'severity': 'medium'
        })
        
        return {
            'recommendations': recommendations
        }
    
    def _get_acceptance_sampling_recommendations(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Generate recommendations based on acceptance sampling analysis.
        
        Args:
            analysis_result: The acceptance sampling analysis result
        
        Returns:
            Dictionary containing recommendations
        """
        recommendations = [
            {
                'title': 'Implement Sampling Plan',
                'description': 'Use this sampling plan for incoming inspection of materials or final product quality verification.',
                'action_type': 'implementation',
                'severity': 'medium'
            },
            {
                'title': 'Consider Control Charts',
                'description': 'For ongoing process monitoring, consider implementing control charts instead of relying solely on acceptance sampling.',
                'action_type': 'analysis',
                'analysis_type': 'control_chart',
                'severity': 'medium'
            }
        ]
        
        # Get related educational content for sampling plan implementation
        rag_documents = self._get_related_rag_documents(
            "acceptance sampling implementation", 
            module='sqc',
            document_type='tutorial',
            limit=2
        )
        
        for doc in rag_documents:
            recommendations.append({
                'title': doc.title,
                'description': f"Learn about {doc.title.lower()}",
                'action_type': 'education',
                'resource_id': str(doc.id),
                'severity': 'low'
            })
        
        return {
            'recommendations': recommendations
        }
    
    def _get_msa_recommendations(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Generate recommendations based on measurement system analysis.
        
        Args:
            analysis_result: The MSA analysis result
        
        Returns:
            Dictionary containing recommendations
        """
        recommendations = []
        
        # Get result summary values
        gage_rr = analysis_result.result_summary.get('gage_rr')
        
        if gage_rr:
            if gage_rr > 30:
                recommendations.append({
                    'title': 'Improve Measurement System',
                    'description': f'Your measurement system has {gage_rr:.1f}% Gage R&R, which is unacceptable. Consider improving your measurement process.',
                    'action_type': 'improvement',
                    'severity': 'high'
                })
            elif gage_rr > 10:
                recommendations.append({
                    'title': 'Measurement System Requires Attention',
                    'description': f'Your measurement system has {gage_rr:.1f}% Gage R&R, which may be acceptable for some applications but requires improvement.',
                    'action_type': 'improvement',
                    'severity': 'medium'
                })
            else:
                recommendations.append({
                    'title': 'Measurement System Acceptable',
                    'description': f'Your measurement system has {gage_rr:.1f}% Gage R&R, which is considered acceptable.',
                    'action_type': 'information',
                    'severity': 'low'
                })
        
        # Add recommendation for control charts after MSA
        recommendations.append({
            'title': 'Implement Control Charts',
            'description': 'Now that you have validated your measurement system, consider implementing control charts for process monitoring.',
            'action_type': 'analysis',
            'analysis_type': 'control_chart',
            'severity': 'medium'
        })
        
        return {
            'recommendations': recommendations
        }
    
    def _get_related_rag_documents(
        self,
        query: str,
        module: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 3
    ) -> List[RagDocument]:
        """
        Get related RAG documents based on a query.
        
        Args:
            query: The query to search for
            module: Optional module to filter by
            document_type: Optional document type to filter by
            limit: Maximum number of documents to return
        
        Returns:
            List of related RagDocument objects
        """
        try:
            # Import only when needed to avoid circular imports
            from stickforstats.rag_system.services.embedding_service import EmbeddingService
            
            # Get query embedding
            embedding_service = EmbeddingService()
            query_vector = embedding_service.get_embedding(query)
            
            if query_vector is None:
                return []
            
            # Query the database for similar documents
            queryset = RagDocument.objects.all()
            
            if module:
                queryset = queryset.filter(module=module)
            
            if document_type:
                queryset = queryset.filter(document_type=document_type)
            
            # Order by vector similarity
            similar_docs = (
                queryset
                .order_by(L2Distance('vector', query_vector))
                .select_related()
                [:limit]
            )
            
            return list(similar_docs)
            
        except Exception as e:
            logger.error(f"Error getting related RAG documents: {str(e)}")
            return []