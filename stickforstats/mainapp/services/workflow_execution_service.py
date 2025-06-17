"""
Workflow execution service for the StickForStats application.

This module provides services for executing and managing analysis workflows,
with support for asynchronous execution, step dependencies, and error handling.
"""
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
import asyncio
import concurrent.futures
import threading
import traceback

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Prefetch

# Import services
from stickforstats.mainapp.models import (
    User, Workflow, WorkflowStep, AnalysisSession, Dataset, AnalysisResult
)
from .session_service import get_session_service
from .workflow_service import get_workflow_service
from .statistical_tests import get_statistical_tests_service
from .advanced_statistical_analysis import get_advanced_statistical_analysis_service
from ..services.analytics.bayesian.bayesian_service import get_bayesian_analysis_service
from ..services.analytics.machine_learning.ml_service import get_ml_service
from ..services.analytics.time_series.time_series_service import get_time_series_service

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowExecutionService:
    """
    Manages the execution of analysis workflows, including step scheduling,
    dependency resolution, and error handling.
    
    This service provides:
    - Asynchronous workflow execution
    - Step dependency management
    - Progress monitoring and reporting
    - Error handling and recovery
    - Execution history tracking
    """
    
    def __init__(self):
        """Initialize the workflow execution service."""
        self.session_service = get_session_service()
        self.workflow_service = get_workflow_service()
        self.statistical_tests_service = get_statistical_tests_service()
        self.advanced_statistical_service = get_advanced_statistical_analysis_service()
        self.bayesian_service = get_bayesian_analysis_service()
        self.ml_service = get_ml_service()
        self.time_series_service = get_time_series_service()
        
        # Execution tracking
        self.active_executions = {}
        self.execution_history = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.timeout_checker = threading.Thread(target=self._check_timeouts, daemon=True)
        self.timeout_checker.start()
        
    def _check_timeouts(self):
        """Background thread to check for step timeouts."""
        while True:
            try:
                # Check active executions for timeouts
                for workflow_id, execution in list(self.active_executions.items()):
                    if 'current_step' in execution and 'start_time' in execution:
                        step = execution.get('current_step')
                        start_time = execution.get('start_time')
                        timeout = execution.get('timeout_seconds', 3600)  # Default 1 hour
                        
                        if step and start_time:
                            elapsed = (datetime.now() - start_time).total_seconds()
                            if elapsed > timeout:
                                logger.warning(f"Step timeout for workflow {workflow_id}, step {step.get('id')}")
                                self._handle_step_timeout(workflow_id, step)
            except Exception as e:
                logger.error(f"Error in timeout checker: {str(e)}")
                
            # Sleep for a short time to avoid high CPU usage
            time.sleep(5)
            
    def _handle_step_timeout(self, workflow_id: str, step: Dict[str, Any]):
        """
        Handle a step timeout.
        
        Args:
            workflow_id: Workflow ID
            step: Step that timed out
        """
        try:
            # Update step status
            step_id = step.get('id')
            if not step_id:
                return
                
            # Get the actual step from the database
            workflow_step = WorkflowStep.objects.filter(id=step_id).first()
            if not workflow_step:
                return
                
            # Update status
            self.workflow_service.update_step_status(
                workflow_step,
                'failed',
                error_message='Step execution timed out'
            )
            
            # Update execution tracking
            if workflow_id in self.active_executions:
                execution = self.active_executions[workflow_id]
                execution['status'] = 'failed'
                execution['error'] = 'Step execution timed out'
                execution['end_time'] = datetime.now()
                
                # Move to history
                self.execution_history[workflow_id] = execution
                del self.active_executions[workflow_id]
        except Exception as e:
            logger.error(f"Error handling step timeout: {str(e)}")
            
    def execute_workflow(self, workflow_id: Union[str, uuid.UUID], 
                        user: User,
                        execute_from_step: Optional[int] = None) -> Dict[str, Any]:
        """
        Start the execution of a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            user: User executing the workflow
            execute_from_step: Optional step index to start execution from
            
        Returns:
            Dictionary with execution status
        """
        try:
            # Get the workflow
            workflow = self.workflow_service.get_workflow(workflow_id)
            if not workflow:
                return {
                    'status': 'error',
                    'message': f'Workflow {workflow_id} not found'
                }
                
            # Check if workflow belongs to user
            if workflow.user != user and not workflow.is_public:
                return {
                    'status': 'error',
                    'message': 'You do not have permission to execute this workflow'
                }
                
            # Check if workflow already executing
            str_workflow_id = str(workflow_id)
            if str_workflow_id in self.active_executions:
                return {
                    'status': 'error',
                    'message': 'Workflow is already executing'
                }
                
            # Get the steps
            steps = list(workflow.steps.all().order_by('order'))
            if not steps:
                return {
                    'status': 'error',
                    'message': 'Workflow has no steps to execute'
                }
                
            # Determine start step
            start_step_index = 0
            if execute_from_step is not None:
                if execute_from_step < 0 or execute_from_step >= len(steps):
                    return {
                        'status': 'error',
                        'message': f'Invalid step index: {execute_from_step}'
                    }
                start_step_index = execute_from_step
                
            # Create execution tracker
            execution = {
                'workflow_id': str_workflow_id,
                'workflow_name': workflow.name,
                'user_id': str(user.id),
                'start_time': datetime.now(),
                'status': 'in_progress',
                'steps': [],
                'current_step_index': start_step_index,
                'total_steps': len(steps),
                'results': {}
            }
            
            # Store in active executions
            self.active_executions[str_workflow_id] = execution
            
            # Update workflow status
            self.workflow_service.update_workflow_status(workflow, 'in_progress')
            
            # Start execution in a background thread
            self.executor.submit(
                self._execute_workflow_steps, 
                workflow, 
                user, 
                steps, 
                start_step_index, 
                execution
            )
            
            # Return initial status
            return {
                'status': 'started',
                'workflow_id': str_workflow_id,
                'message': f'Workflow execution started with {len(steps)} steps',
                'start_time': execution['start_time'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting workflow execution: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error starting workflow: {str(e)}'
            }
            
    def _execute_workflow_steps(self, workflow: Workflow, user: User, 
                              steps: List[WorkflowStep], start_index: int, 
                              execution: Dict[str, Any]):
        """
        Execute the steps of a workflow.
        
        Args:
            workflow: Workflow to execute
            user: User executing the workflow
            steps: List of workflow steps in execution order
            start_index: Index of the first step to execute
            execution: Execution tracking dictionary
        """
        current_index = start_index
        try:
            # Get the dataset if available
            dataset = workflow.dataset
            
            # Execute each step
            while current_index < len(steps):
                step = steps[current_index]
                execution['current_step_index'] = current_index
                execution['current_step'] = {
                    'id': str(step.id),
                    'name': step.name,
                    'step_type': step.step_type
                }
                execution['start_time'] = datetime.now()
                execution['timeout_seconds'] = step.timeout_seconds
                
                # Check if step has unsatisfied dependencies
                if step.depends_on.exists():
                    unsatisfied = []
                    for dependency in step.depends_on.all():
                        dep_status = dependency.execution_status
                        if dep_status != 'completed':
                            unsatisfied.append(str(dependency.id))
                            
                    if unsatisfied:
                        logger.info(f"Step {step.id} has unsatisfied dependencies: {unsatisfied}")
                        self.workflow_service.update_step_status(
                            step,
                            'skipped',
                            error_message='Dependent steps were not successfully completed'
                        )
                        current_index += 1
                        continue
                
                # Update step status to in_progress
                self.workflow_service.update_step_status(step, 'in_progress')
                
                # Execute the step
                try:
                    # Get or create analysis session for this step
                    session = step.analysis_session
                    if not session:
                        session = self.session_service.create_analysis_session(
                            user=user,
                            name=f"{workflow.name} - {step.name}",
                            module=step.step_type,
                            description=step.description,
                            dataset=dataset,
                            configuration=step.configuration
                        )
                        step.analysis_session = session
                        step.save(update_fields=['analysis_session'])
                    
                    # Execute based on step type
                    result = self._execute_step(step, dataset, user, session)
                    
                    # Store result
                    execution['results'][str(step.id)] = {
                        'success': True,
                        'result_id': result.get('result_id') if isinstance(result, dict) else None,
                        'summary': result.get('summary') if isinstance(result, dict) else str(result)
                    }
                    
                    # Update step status
                    self.workflow_service.update_step_status(step, 'completed')
                    
                except Exception as step_error:
                    logger.error(f"Error executing step {step.id}: {str(step_error)}")
                    logger.error(traceback.format_exc())
                    
                    # Update step status
                    self.workflow_service.update_step_status(
                        step,
                        'failed',
                        error_message=str(step_error)
                    )
                    
                    # Store error
                    execution['results'][str(step.id)] = {
                        'success': False,
                        'error': str(step_error)
                    }
                    
                    # Check if step is required
                    if step.is_required:
                        # Stop execution
                        execution['status'] = 'failed'
                        execution['error'] = f"Required step failed: {step.name}"
                        execution['end_time'] = datetime.now()
                        
                        # Update workflow status
                        self.workflow_service.update_workflow_status(workflow, 'failed')
                        
                        # Move to history
                        self.execution_history[str(workflow.id)] = execution
                        if str(workflow.id) in self.active_executions:
                            del self.active_executions[str(workflow.id)]
                            
                        return
                
                # Move to next step
                current_index += 1
                
            # All steps completed
            execution['status'] = 'completed'
            execution['end_time'] = datetime.now()
            
            # Update workflow status
            self.workflow_service.update_workflow_status(workflow, 'completed')
            
            # Move to history
            self.execution_history[str(workflow.id)] = execution
            if str(workflow.id) in self.active_executions:
                del self.active_executions[str(workflow.id)]
                
        except Exception as e:
            logger.error(f"Error executing workflow {workflow.id}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Update status
            execution['status'] = 'failed'
            execution['error'] = str(e)
            execution['end_time'] = datetime.now()
            
            # Update workflow status
            self.workflow_service.update_workflow_status(workflow, 'failed')
            
            # Move to history
            self.execution_history[str(workflow.id)] = execution
            if str(workflow.id) in self.active_executions:
                del self.active_executions[str(workflow.id)]
            
    def _execute_step(self, step: WorkflowStep, dataset: Optional[Dataset], 
                    user: User, session: AnalysisSession) -> Dict[str, Any]:
        """
        Execute a workflow step.
        
        Args:
            step: Workflow step to execute
            dataset: Dataset to use for the step
            user: User executing the step
            session: Analysis session for the step
            
        Returns:
            Dictionary with execution result
        """
        step_type = step.step_type
        config = step.configuration
        
        # Basic validation
        if step_type not in [
            'data_preprocessing', 'visualization', 'statistical_test', 
            'machine_learning', 'advanced_statistics', 'report_generation',
            'time_series', 'bayesian'
        ]:
            raise ValueError(f"Unsupported step type: {step_type}")
            
        # Execute based on step type
        if step_type == 'data_preprocessing':
            return self._execute_preprocessing_step(step, dataset, user, session, config)
        elif step_type == 'visualization':
            return self._execute_visualization_step(step, dataset, user, session, config)
        elif step_type == 'statistical_test':
            return self._execute_statistical_test_step(step, dataset, user, session, config)
        elif step_type == 'machine_learning':
            return self._execute_machine_learning_step(step, dataset, user, session, config)
        elif step_type == 'advanced_statistics':
            return self._execute_advanced_statistics_step(step, dataset, user, session, config)
        elif step_type == 'report_generation':
            return self._execute_report_generation_step(step, dataset, user, session, config)
        elif step_type == 'time_series':
            return self._execute_time_series_step(step, dataset, user, session, config)
        elif step_type == 'bayesian':
            return self._execute_bayesian_step(step, dataset, user, session, config)
        else:
            raise ValueError(f"Unhandled step type: {step_type}")
            
    def _execute_preprocessing_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                  user: User, session: AnalysisSession, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data preprocessing step."""
        from ..services.data_processing.data_validator import get_data_validator_service
        data_validator = get_data_validator_service()
        
        # Get processing configuration
        processing_type = config.get('processing_type', 'validate')
        
        # Execute the appropriate processing
        if processing_type == 'validate':
            # Validate the dataset
            validation_result = data_validator.validate_dataset(dataset)
            
            # Save result
            result = self.session_service.save_analysis_result(
                session=session,
                name=f"Data Validation - {dataset.name if dataset else 'Unknown'}",
                analysis_type='data_validation',
                parameters=config,
                result_summary=validation_result,
                interpretation="Dataset validation completed"
            )
            
            return {
                'result_id': str(result.id),
                'summary': validation_result
            }
            
        elif processing_type == 'clean':
            # Clean the dataset
            from ..services.data_processing.data_processing_service import get_data_processing_service
            data_processor = get_data_processing_service()
            
            # Get cleaning options
            cleaning_options = config.get('cleaning_options', {})
            
            # Clean the dataset
            cleaning_result = data_processor.clean_dataset(
                dataset, 
                handle_missing=cleaning_options.get('handle_missing', True),
                handle_outliers=cleaning_options.get('handle_outliers', False),
                remove_duplicates=cleaning_options.get('remove_duplicates', True)
            )
            
            # Save result
            result = self.session_service.save_analysis_result(
                session=session,
                name=f"Data Cleaning - {dataset.name if dataset else 'Unknown'}",
                analysis_type='data_cleaning',
                parameters=config,
                result_summary=cleaning_result,
                interpretation="Dataset cleaning completed"
            )
            
            return {
                'result_id': str(result.id),
                'summary': cleaning_result
            }
            
        elif processing_type == 'transform':
            # Transform the dataset
            from ..services.data_processing.data_processing_service import get_data_processing_service
            data_processor = get_data_processing_service()
            
            # Get transformation options
            transform_options = config.get('transform_options', {})
            
            # Transform the dataset
            transform_result = data_processor.transform_dataset(
                dataset,
                transforms=transform_options.get('transforms', []),
                scale_features=transform_options.get('scale_features', False),
                encode_categorical=transform_options.get('encode_categorical', False)
            )
            
            # Save result
            result = self.session_service.save_analysis_result(
                session=session,
                name=f"Data Transformation - {dataset.name if dataset else 'Unknown'}",
                analysis_type='data_transformation',
                parameters=config,
                result_summary=transform_result,
                interpretation="Dataset transformation completed"
            )
            
            return {
                'result_id': str(result.id),
                'summary': transform_result
            }
            
        else:
            raise ValueError(f"Unsupported processing type: {processing_type}")
    
    def _execute_visualization_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                 user: User, session: AnalysisSession, 
                                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data visualization step."""
        from ..services.visualization.visualization_service import get_visualization_service
        visualization_service = get_visualization_service()
        
        # Get visualization configuration
        viz_type = config.get('visualization_type')
        if not viz_type:
            raise ValueError("Visualization type is required")
            
        # Get visualization parameters
        viz_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for visualization")
            
        # Execute the appropriate visualization
        viz_result = visualization_service.create_visualization(
            viz_type=viz_type,
            dataset=dataset,
            parameters=viz_params
        )
        
        # Create visualizations list
        visualizations = []
        for viz in viz_result.get('visualizations', []):
            visualizations.append({
                'title': viz.get('title', f"{viz_type} Visualization"),
                'description': viz.get('description', ''),
                'type': viz_type,
                'figure': viz.get('figure_data', {}),
                'layout': viz.get('layout', {})
            })
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{viz_type.title()} - {dataset.name}",
            analysis_type='visualization',
            parameters=config,
            result_summary=viz_result.get('summary', {}),
            interpretation=viz_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': viz_result.get('summary', {}),
            'visualizations': len(visualizations)
        }
        
    def _execute_statistical_test_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                     user: User, session: AnalysisSession, 
                                     config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a statistical test step."""
        # Get test configuration
        test_type = config.get('test_type')
        if not test_type:
            raise ValueError("Statistical test type is required")
            
        # Get test parameters
        test_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for statistical tests")
            
        # Add dataset reference to parameters if needed
        if 'dataset_id' not in test_params and 'dataset' not in test_params:
            test_params['dataset_id'] = str(dataset.id)
            
        # Execute the appropriate test
        test_result = None
        
        if test_type == 'normality':
            test_result = self.statistical_tests_service.test_normality(**test_params)
        elif test_type == 't_test':
            test_result = self.statistical_tests_service.perform_t_test(**test_params)
        elif test_type == 'anova':
            test_result = self.statistical_tests_service.perform_anova(**test_params)
        elif test_type == 'chi_square':
            test_result = self.statistical_tests_service.perform_chi_square(**test_params)
        elif test_type == 'correlation':
            test_result = self.statistical_tests_service.compute_correlation(**test_params)
        else:
            raise ValueError(f"Unsupported statistical test: {test_type}")
            
        # Extract visualizations if any
        visualizations = []
        if 'visualizations' in test_result:
            for viz in test_result['visualizations']:
                visualizations.append({
                    'title': viz.get('title', f"{test_type} Visualization"),
                    'description': viz.get('description', ''),
                    'type': viz.get('type', 'plot'),
                    'figure': viz.get('figure_data', {}),
                    'layout': viz.get('layout', {})
                })
                
        # Remove visualizations from result summary to avoid duplication
        result_summary = {k: v for k, v in test_result.items() if k != 'visualizations'}
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{test_type.replace('_', ' ').title()} Test",
            analysis_type=f'statistical_test_{test_type}',
            parameters=config,
            result_summary=result_summary,
            interpretation=test_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': result_summary,
            'visualizations': len(visualizations)
        }
        
    def _execute_machine_learning_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                     user: User, session: AnalysisSession, 
                                     config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a machine learning step."""
        # Get ML configuration
        ml_type = config.get('ml_type')
        if not ml_type:
            raise ValueError("Machine learning type is required")
            
        # Get ML parameters
        ml_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for machine learning")
            
        # Add dataset reference to parameters if needed
        if 'dataset_id' not in ml_params and 'dataset' not in ml_params:
            ml_params['dataset_id'] = str(dataset.id)
            
        # Execute the appropriate ML function
        ml_result = None
        
        if ml_type == 'regression':
            ml_result = self.ml_service.train_regression_model(**ml_params)
        elif ml_type == 'classification':
            ml_result = self.ml_service.train_classification_model(**ml_params)
        elif ml_type == 'clustering':
            ml_result = self.ml_service.perform_clustering(**ml_params)
        elif ml_type == 'dimensionality_reduction':
            ml_result = self.ml_service.reduce_dimensions(**ml_params)
        elif ml_type == 'feature_selection':
            ml_result = self.ml_service.select_features(**ml_params)
        else:
            raise ValueError(f"Unsupported machine learning type: {ml_type}")
            
        # Extract visualizations if any
        visualizations = []
        if 'visualizations' in ml_result:
            for viz in ml_result['visualizations']:
                visualizations.append({
                    'title': viz.get('title', f"{ml_type} Visualization"),
                    'description': viz.get('description', ''),
                    'type': viz.get('type', 'plot'),
                    'figure': viz.get('figure_data', {}),
                    'layout': viz.get('layout', {})
                })
                
        # Remove visualizations from result summary to avoid duplication
        result_summary = {k: v for k, v in ml_result.items() if k != 'visualizations'}
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{ml_type.replace('_', ' ').title()}",
            analysis_type=f'machine_learning_{ml_type}',
            parameters=config,
            result_summary=result_summary,
            interpretation=ml_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': result_summary,
            'visualizations': len(visualizations)
        }
        
    def _execute_advanced_statistics_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                       user: User, session: AnalysisSession, 
                                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an advanced statistics step."""
        # Get analysis configuration
        analysis_type = config.get('analysis_type')
        if not analysis_type:
            raise ValueError("Advanced statistics analysis type is required")
            
        # Get analysis parameters
        analysis_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for advanced statistics")
            
        # Add dataset reference to parameters if needed
        if 'dataset_id' not in analysis_params and 'dataset' not in analysis_params:
            analysis_params['dataset_id'] = str(dataset.id)
            
        # Execute the appropriate analysis
        analysis_result = None
        
        if analysis_type == 'pca':
            analysis_result = self.advanced_statistical_service.perform_pca(**analysis_params)
        elif analysis_type == 'factor_analysis':
            analysis_result = self.advanced_statistical_service.perform_factor_analysis(**analysis_params)
        elif analysis_type == 'cluster_analysis':
            analysis_result = self.advanced_statistical_service.perform_cluster_analysis(**analysis_params)
        elif analysis_type == 'manova':
            analysis_result = self.advanced_statistical_service.perform_manova(**analysis_params)
        elif analysis_type == 'survival_analysis':
            analysis_result = self.advanced_statistical_service.perform_survival_analysis(**analysis_params)
        else:
            raise ValueError(f"Unsupported advanced statistics analysis: {analysis_type}")
            
        # Extract visualizations if any
        visualizations = []
        if 'visualizations' in analysis_result:
            for viz in analysis_result['visualizations']:
                visualizations.append({
                    'title': viz.get('title', f"{analysis_type} Visualization"),
                    'description': viz.get('description', ''),
                    'type': viz.get('type', 'plot'),
                    'figure': viz.get('figure_data', {}),
                    'layout': viz.get('layout', {})
                })
                
        # Remove visualizations from result summary to avoid duplication
        result_summary = {k: v for k, v in analysis_result.items() if k != 'visualizations'}
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{analysis_type.replace('_', ' ').title()} Analysis",
            analysis_type=f'advanced_statistics_{analysis_type}',
            parameters=config,
            result_summary=result_summary,
            interpretation=analysis_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': result_summary,
            'visualizations': len(visualizations)
        }
        
    def _execute_time_series_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                user: User, session: AnalysisSession, 
                                config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a time series analysis step."""
        # Get analysis configuration
        analysis_type = config.get('analysis_type')
        if not analysis_type:
            raise ValueError("Time series analysis type is required")
            
        # Get analysis parameters
        analysis_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for time series analysis")
            
        # Add dataset reference to parameters if needed
        if 'dataset_id' not in analysis_params and 'dataset' not in analysis_params:
            analysis_params['dataset_id'] = str(dataset.id)
            
        # Execute the appropriate analysis
        analysis_result = None
        
        if analysis_type == 'decomposition':
            analysis_result = self.time_series_service.decompose_time_series(**analysis_params)
        elif analysis_type == 'stationarity':
            analysis_result = self.time_series_service.test_stationarity(**analysis_params)
        elif analysis_type == 'autocorrelation':
            analysis_result = self.time_series_service.compute_autocorrelation(**analysis_params)
        elif analysis_type == 'forecasting':
            analysis_result = self.time_series_service.forecast_time_series(**analysis_params)
        elif analysis_type == 'anomaly_detection':
            analysis_result = self.time_series_service.detect_anomalies(**analysis_params)
        else:
            raise ValueError(f"Unsupported time series analysis: {analysis_type}")
            
        # Extract visualizations if any
        visualizations = []
        if 'visualizations' in analysis_result:
            for viz in analysis_result['visualizations']:
                visualizations.append({
                    'title': viz.get('title', f"{analysis_type} Visualization"),
                    'description': viz.get('description', ''),
                    'type': viz.get('type', 'plot'),
                    'figure': viz.get('figure_data', {}),
                    'layout': viz.get('layout', {})
                })
                
        # Remove visualizations from result summary to avoid duplication
        result_summary = {k: v for k, v in analysis_result.items() if k != 'visualizations'}
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{analysis_type.replace('_', ' ').title()} Analysis",
            analysis_type=f'time_series_{analysis_type}',
            parameters=config,
            result_summary=result_summary,
            interpretation=analysis_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': result_summary,
            'visualizations': len(visualizations)
        }
        
    def _execute_bayesian_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                             user: User, session: AnalysisSession, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Bayesian analysis step."""
        # Get analysis configuration
        analysis_type = config.get('analysis_type')
        if not analysis_type:
            raise ValueError("Bayesian analysis type is required")
            
        # Get analysis parameters
        analysis_params = config.get('parameters', {})
        
        # Get dataset data
        if not dataset:
            raise ValueError("Dataset is required for Bayesian analysis")
            
        # Add dataset reference to parameters if needed
        if 'dataset_id' not in analysis_params and 'dataset' not in analysis_params:
            analysis_params['dataset_id'] = str(dataset.id)
            
        # Execute the appropriate analysis
        analysis_result = None
        
        if analysis_type == 'bayesian_t_test':
            analysis_result = self.bayesian_service.perform_bayesian_t_test(**analysis_params)
        elif analysis_type == 'bayesian_correlation':
            analysis_result = self.bayesian_service.perform_bayesian_correlation(**analysis_params)
        elif analysis_type == 'bayesian_regression':
            analysis_result = self.bayesian_service.perform_bayesian_regression(**analysis_params)
        elif analysis_type == 'bayesian_anova':
            analysis_result = self.bayesian_service.perform_bayesian_anova(**analysis_params)
        elif analysis_type == 'bayesian_model_comparison':
            analysis_result = self.bayesian_service.compare_bayesian_models(**analysis_params)
        else:
            raise ValueError(f"Unsupported Bayesian analysis: {analysis_type}")
            
        # Extract visualizations if any
        visualizations = []
        if 'visualizations' in analysis_result:
            for viz in analysis_result['visualizations']:
                visualizations.append({
                    'title': viz.get('title', f"{analysis_type} Visualization"),
                    'description': viz.get('description', ''),
                    'type': viz.get('type', 'plot'),
                    'figure': viz.get('figure_data', {}),
                    'layout': viz.get('layout', {})
                })
                
        # Remove visualizations from result summary to avoid duplication
        result_summary = {k: v for k, v in analysis_result.items() if k != 'visualizations'}
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"{analysis_type.replace('_', ' ').title()} Analysis",
            analysis_type=f'bayesian_{analysis_type}',
            parameters=config,
            result_summary=result_summary,
            interpretation=analysis_result.get('interpretation', ''),
            visualizations=visualizations
        )
        
        return {
            'result_id': str(result.id),
            'summary': result_summary,
            'visualizations': len(visualizations)
        }
        
    def _execute_report_generation_step(self, step: WorkflowStep, dataset: Optional[Dataset],
                                      user: User, session: AnalysisSession, 
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a report generation step."""
        from ..services.report.report_generator_service import get_report_generator_service
        report_service = get_report_generator_service()
        
        # Get report configuration
        report_title = config.get('title', f"Analysis Report - {datetime.now().strftime('%Y-%m-%d')}")
        report_description = config.get('description', '')
        report_format = config.get('format', 'pdf')
        include_visualizations = config.get('include_visualizations', True)
        
        # Get analysis results
        analysis_ids = config.get('analysis_ids', [])
        if not analysis_ids:
            # Get all results from the workflow
            workflow = step.workflow
            analysis_results = []
            
            for workflow_step in workflow.steps.filter(execution_status='completed'):
                if workflow_step.analysis_session:
                    session_results = AnalysisResult.objects.filter(
                        session=workflow_step.analysis_session
                    )
                    analysis_results.extend(session_results)
        else:
            # Get specified results
            analysis_results = AnalysisResult.objects.filter(id__in=analysis_ids)
            
        if not analysis_results:
            raise ValueError("No analysis results found for report generation")
            
        # Generate report
        report_metadata, report_buffer = report_service.generate_report_from_analyses(
            user_id=str(user.id),
            analyses=analysis_results,
            title=report_title,
            description=report_description,
            report_format=report_format,
            include_visualizations=include_visualizations
        )
        
        if not report_metadata:
            raise ValueError("Failed to generate report")
            
        # Save result
        result = self.session_service.save_analysis_result(
            session=session,
            name=f"Report: {report_title}",
            analysis_type='report_generation',
            parameters=config,
            result_summary={
                'report_id': report_metadata.get('id'),
                'report_title': report_title,
                'report_format': report_format,
                'analysis_count': len(analysis_results),
                'file_path': report_metadata.get('file_path')
            },
            interpretation=f"Generated report with {len(analysis_results)} analyses"
        )
        
        return {
            'result_id': str(result.id),
            'summary': {
                'report_id': report_metadata.get('id'),
                'report_title': report_title,
                'report_format': report_format,
                'analysis_count': len(analysis_results)
            }
        }
        
    def get_execution_status(self, workflow_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Get the execution status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary with execution status
        """
        str_workflow_id = str(workflow_id)
        
        # Check active executions
        if str_workflow_id in self.active_executions:
            execution = self.active_executions[str_workflow_id]
            
            return {
                'status': 'in_progress',
                'workflow_id': str_workflow_id,
                'workflow_name': execution.get('workflow_name'),
                'start_time': execution.get('start_time').isoformat() if execution.get('start_time') else None,
                'current_step': execution.get('current_step_index'),
                'total_steps': execution.get('total_steps'),
                'progress': (execution.get('current_step_index', 0) / execution.get('total_steps', 1)) if execution.get('total_steps') else 0,
                'current_step_name': execution.get('current_step', {}).get('name') if execution.get('current_step') else None
            }
            
        # Check execution history
        if str_workflow_id in self.execution_history:
            execution = self.execution_history[str_workflow_id]
            
            return {
                'status': execution.get('status'),
                'workflow_id': str_workflow_id,
                'workflow_name': execution.get('workflow_name'),
                'start_time': execution.get('start_time').isoformat() if execution.get('start_time') else None,
                'end_time': execution.get('end_time').isoformat() if execution.get('end_time') else None,
                'error': execution.get('error'),
                'total_steps': execution.get('total_steps'),
                'results': execution.get('results')
            }
            
        # Get workflow from database
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            return {
                'status': 'error',
                'message': f'Workflow {workflow_id} not found'
            }
            
        # Return status from database
        return {
            'status': workflow.status,
            'workflow_id': str_workflow_id,
            'workflow_name': workflow.name,
            'steps_total': workflow.steps.count(),
            'steps_completed': workflow.steps.filter(execution_status='completed').count(),
            'steps_failed': workflow.steps.filter(execution_status='failed').count(),
            'steps_pending': workflow.steps.filter(execution_status='pending').count(),
            'steps_in_progress': workflow.steps.filter(execution_status='in_progress').count()
        }
        
    def cancel_execution(self, workflow_id: Union[str, uuid.UUID], user: User) -> Dict[str, Any]:
        """
        Cancel the execution of a workflow.
        
        Args:
            workflow_id: ID of the workflow to cancel
            user: User cancelling the execution
            
        Returns:
            Dictionary with cancellation status
        """
        str_workflow_id = str(workflow_id)
        
        # Check if workflow is executing
        if str_workflow_id in self.active_executions:
            execution = self.active_executions[str_workflow_id]
            
            # Check if user has permission
            if str(user.id) != execution.get('user_id') and not user.is_staff:
                return {
                    'status': 'error',
                    'message': 'You do not have permission to cancel this execution'
                }
                
            # Update execution status
            execution['status'] = 'cancelled'
            execution['end_time'] = datetime.now()
            
            # Move to history
            self.execution_history[str_workflow_id] = execution
            del self.active_executions[str_workflow_id]
            
            # Update workflow status
            workflow = self.workflow_service.get_workflow(workflow_id)
            if workflow:
                self.workflow_service.update_workflow_status(workflow, 'cancelled')
                
                # Update current step status if needed
                current_step_index = execution.get('current_step_index')
                if current_step_index is not None and current_step_index < len(workflow.steps.all()):
                    steps = list(workflow.steps.all().order_by('order'))
                    if current_step_index < len(steps):
                        current_step = steps[current_step_index]
                        if current_step.execution_status == 'in_progress':
                            self.workflow_service.update_step_status(
                                current_step,
                                'cancelled',
                                error_message='Execution cancelled by user'
                            )
                
            return {
                'status': 'success',
                'message': 'Workflow execution cancelled',
                'workflow_id': str_workflow_id
            }
            
        else:
            return {
                'status': 'error',
                'message': 'Workflow is not currently executing'
            }
        
    def get_execution_history(self, user: User, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get execution history for a user.
        
        Args:
            user: User to get history for
            limit: Maximum number of items to return
            
        Returns:
            List of execution history items
        """
        # Get all workflow IDs for the user
        user_workflows = Workflow.objects.filter(user=user).values_list('id', flat=True)
        user_workflow_ids = [str(wf_id) for wf_id in user_workflows]
        
        # Collect execution history for user workflows
        history = []
        
        # First check in-memory history
        for workflow_id, execution in self.execution_history.items():
            if workflow_id in user_workflow_ids:
                # Simplify execution data
                history.append({
                    'workflow_id': workflow_id,
                    'workflow_name': execution.get('workflow_name'),
                    'status': execution.get('status'),
                    'start_time': execution.get('start_time').isoformat() if execution.get('start_time') else None,
                    'end_time': execution.get('end_time').isoformat() if execution.get('end_time') else None,
                    'total_steps': execution.get('total_steps', 0),
                    'error': execution.get('error')
                })
                
        # Then check active executions
        for workflow_id, execution in self.active_executions.items():
            if workflow_id in user_workflow_ids:
                # Simplify execution data
                history.append({
                    'workflow_id': workflow_id,
                    'workflow_name': execution.get('workflow_name'),
                    'status': 'in_progress',
                    'start_time': execution.get('start_time').isoformat() if execution.get('start_time') else None,
                    'end_time': None,
                    'total_steps': execution.get('total_steps', 0),
                    'current_step': execution.get('current_step_index', 0),
                    'current_step_name': execution.get('current_step', {}).get('name') if execution.get('current_step') else None
                })
                
        # Sort by start time (newest first) and apply limit
        history.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return history[:limit]


# Create singleton instance
workflow_execution_service = WorkflowExecutionService()

def get_workflow_execution_service() -> WorkflowExecutionService:
    """Get global workflow execution service instance."""
    return workflow_execution_service