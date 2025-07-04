"""
Data Service

This module provides a central service for data operations across all modules.
It handles dataset transformations, caching, and cross-module data sharing.
"""

import logging
import pandas as pd
import numpy as np
import json
import hashlib
import os
from typing import Dict, List, Tuple, Optional, Any, Union
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
import uuid
from datetime import datetime, timedelta

from ..models import Dataset, Analysis
from ...core.registry import get_registry

logger = logging.getLogger(__name__)

class DataService:
    """
    Service for managing datasets and data operations.
    
    This service provides centralized data management including:
    - Dataset loading, validation, and transformation
    - Caching for performance optimization
    - Cross-module data sharing
    - Dataset versioning and tracking
    """
    
    def __init__(self):
        """Initialize the data service."""
        self.registry = get_registry()
        self.cache_timeout = getattr(settings, 'DATA_CACHE_TIMEOUT', 3600)  # 1 hour default
        self.temp_dir = getattr(settings, 'DATA_TEMP_DIR', 'temp')
    
    def load_dataset(self, dataset_id: str, module: Optional[str] = None) -> pd.DataFrame:
        """
        Load a dataset by ID, with optional module-specific transformations.
        
        Args:
            dataset_id: The ID of the dataset to load
            module: Optional module name for module-specific transformations
            
        Returns:
            The loaded DataFrame
        """
        try:
            # Check cache first
            cache_key = f"dataset_{dataset_id}"
            if module:
                cache_key += f"_{module}"
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for dataset {dataset_id}")
                return pd.read_json(cached_data)
            
            # Load dataset
            dataset = Dataset.objects.get(id=dataset_id)
            
            # Load data
            if dataset.file:
                df = self._load_from_file(dataset.file.path)
            elif dataset.data_json:
                df = pd.read_json(dataset.data_json)
            else:
                raise ValueError(f"Dataset {dataset_id} has no data")
            
            # Apply transformations if module is specified
            if module:
                df = self._apply_module_transformations(df, module)
            
            # Cache results
            cache.set(cache_key, df.to_json(), self.cache_timeout)
            
            return df
            
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_id}: {str(e)}")
            raise
    
    def save_dataset(self, 
                     df: pd.DataFrame, 
                     name: str, 
                     description: Optional[str] = None,
                     user_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     module: Optional[str] = None,
                     analysis_id: Optional[str] = None,
                     parent_dataset_id: Optional[str] = None) -> Dataset:
        """
        Save a DataFrame as a dataset.
        
        Args:
            df: The DataFrame to save
            name: The name for the dataset
            description: Optional description
            user_id: Optional user ID to associate with the dataset
            metadata: Optional metadata for the dataset
            module: Optional module that created the dataset
            analysis_id: Optional analysis ID that created the dataset
            parent_dataset_id: Optional parent dataset ID for derived datasets
            
        Returns:
            The created Dataset object
        """
        try:
            # Create dataset record
            dataset = Dataset(
                name=name,
                description=description or '',
                created_at=timezone.now(),
                updated_at=timezone.now(),
                metadata=metadata or {},
                source_module=module,
                row_count=len(df),
                column_count=len(df.columns)
            )
            
            # Set user if provided
            if user_id:
                dataset.user_id = user_id
            
            # Set analysis if provided
            if analysis_id:
                dataset.analysis_id = analysis_id
            
            # Set parent dataset if provided
            if parent_dataset_id:
                dataset.parent_dataset_id = parent_dataset_id
            
            # Generate schema
            dataset.schema = self._generate_schema(df)
            
            # Save data
            if len(df) > 1000 or df.memory_usage(deep=True).sum() > 1024 * 1024:  # > 1MB
                # Save to file for large datasets
                file_path = self._save_to_file(df, name)
                dataset.file = file_path
            else:
                # Save directly to JSON for small datasets
                dataset.data_json = df.to_json()
            
            # Calculate hash for data integrity
            dataset.data_hash = self._calculate_hash(df)
            
            # Save to database
            dataset.save()
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error saving dataset {name}: {str(e)}")
            raise
    
    def transform_dataset(self, 
                         dataset_id: str, 
                         transformations: List[Dict[str, Any]],
                         new_name: Optional[str] = None,
                         save_transformed: bool = True) -> Tuple[pd.DataFrame, Optional[Dataset]]:
        """
        Apply a series of transformations to a dataset.
        
        Args:
            dataset_id: The ID of the dataset to transform
            transformations: List of transformation operations
            new_name: Optional name for the transformed dataset
            save_transformed: Whether to save the transformed dataset
            
        Returns:
            Tuple of (transformed DataFrame, new Dataset if saved else None)
        """
        try:
            # Load original dataset
            df = self.load_dataset(dataset_id)
            original_dataset = Dataset.objects.get(id=dataset_id)
            
            # Apply transformations
            transformed_df = self._apply_transformations(df, transformations)
            
            # Save transformed dataset if requested
            new_dataset = None
            if save_transformed:
                new_name = new_name or f"{original_dataset.name} (Transformed)"
                metadata = original_dataset.metadata.copy() if original_dataset.metadata else {}
                metadata['transformations'] = transformations
                
                new_dataset = self.save_dataset(
                    df=transformed_df,
                    name=new_name,
                    description=f"Transformed from dataset: {original_dataset.name}",
                    user_id=original_dataset.user_id,
                    metadata=metadata,
                    module="core",
                    parent_dataset_id=str(original_dataset.id)
                )
            
            return transformed_df, new_dataset
            
        except Exception as e:
            logger.error(f"Error transforming dataset {dataset_id}: {str(e)}")
            raise
    
    def get_dataset_summary(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get a statistical summary of a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            
        Returns:
            Dictionary containing dataset summary statistics
        """
        try:
            # Try to get from cache
            cache_key = f"dataset_summary_{dataset_id}"
            cached_summary = cache.get(cache_key)
            if cached_summary is not None:
                return json.loads(cached_summary)
            
            # Load dataset
            df = self.load_dataset(dataset_id)
            
            # Generate summary
            summary = {
                'shape': df.shape,
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_columns': {},
                'categorical_columns': {},
                'date_columns': {}
            }
            
            # Numeric column summaries
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                summary['numeric_columns'][col] = {
                    'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                    'missing': int(df[col].isnull().sum())
                }
            
            # Categorical column summaries
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                value_counts = df[col].value_counts()
                summary['categorical_columns'][col] = {
                    'unique_values': int(df[col].nunique()),
                    'top_values': value_counts.head(5).to_dict(),
                    'missing': int(df[col].isnull().sum())
                }
            
            # Date column summaries
            date_cols = df.select_dtypes(include=['datetime']).columns
            for col in date_cols:
                summary['date_columns'][col] = {
                    'min': df[col].min().isoformat() if not pd.isna(df[col].min()) else None,
                    'max': df[col].max().isoformat() if not pd.isna(df[col].max()) else None,
                    'missing': int(df[col].isnull().sum())
                }
            
            # Cache summary
            cache.set(cache_key, json.dumps(summary, default=str), self.cache_timeout)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting summary for dataset {dataset_id}: {str(e)}")
            raise
    
    def get_dataset_preview(self, dataset_id: str, rows: int = 10) -> Dict[str, Any]:
        """
        Get a preview of a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            rows: Number of rows to include in the preview
            
        Returns:
            Dictionary containing dataset preview
        """
        try:
            # Load dataset
            df = self.load_dataset(dataset_id)
            
            # Get preview
            preview_df = df.head(rows)
            
            # Convert to JSON-serializable format
            preview = {
                'columns': list(preview_df.columns),
                'data': preview_df.to_dict(orient='records'),
                'total_rows': len(df),
                'preview_rows': len(preview_df)
            }
            
            return preview
            
        except Exception as e:
            logger.error(f"Error getting preview for dataset {dataset_id}: {str(e)}")
            raise
    
    def convert_for_module(self, dataset_id: str, target_module: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Convert a dataset for use in a specific module.
        
        Args:
            dataset_id: The ID of the dataset to convert
            target_module: The module to convert for
            
        Returns:
            Tuple of (converted DataFrame, conversion metadata)
        """
        try:
            # Load the dataset
            df = self.load_dataset(dataset_id)
            
            # Get module-specific handlers
            handlers = self.registry.get_data_handlers('dataset_conversion')
            
            # Find handler for target module
            target_handler = None
            for handler in handlers:
                if handler['module'] == target_module:
                    target_handler = handler['handler']
                    break
            
            if not target_handler:
                # Use default transformation if no specific handler
                converted_df = self._apply_module_transformations(df, target_module)
                metadata = {'conversion_type': 'default'}
            else:
                # Use module-specific handler
                handler_parts = target_handler.split('.')
                module_name = '.'.join(handler_parts[:-1])
                function_name = handler_parts[-1]
                
                module = __import__(module_name, fromlist=[function_name])
                handler_function = getattr(module, function_name)
                
                converted_df, metadata = handler_function(df)
            
            return converted_df, metadata
            
        except Exception as e:
            logger.error(f"Error converting dataset {dataset_id} for module {target_module}: {str(e)}")
            raise
    
    def get_compatible_modules(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of modules compatible with a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            
        Returns:
            List of compatible modules with metadata
        """
        try:
            # Load dataset
            df = self.load_dataset(dataset_id)
            
            # Get all modules
            modules = self.registry.get_enabled_modules()
            
            # Check compatibility with each module
            compatible_modules = []
            
            for module_name, module_info in modules.items():
                # Skip if module doesn't have a compatibility checker
                if 'data_compatibility_checker' not in module_info.get('metadata', {}):
                    continue
                
                # Get compatibility checker
                checker_path = module_info['metadata']['data_compatibility_checker']
                checker_parts = checker_path.split('.')
                checker_module_name = '.'.join(checker_parts[:-1])
                checker_function_name = checker_parts[-1]
                
                try:
                    checker_module = __import__(checker_module_name, fromlist=[checker_function_name])
                    checker_function = getattr(checker_module, checker_function_name)
                    
                    # Check compatibility
                    is_compatible, compatibility_info = checker_function(df)
                    
                    if is_compatible:
                        compatible_modules.append({
                            'module_name': module_name,
                            'module_info': module_info,
                            'compatibility_info': compatibility_info
                        })
                        
                except Exception as checker_error:
                    logger.warning(f"Error checking compatibility for module {module_name}: {str(checker_error)}")
            
            return compatible_modules
            
        except Exception as e:
            logger.error(f"Error getting compatible modules for dataset {dataset_id}: {str(e)}")
            raise
    
    def share_with_module(self, dataset_id: str, target_module: str, 
                         analysis_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Share a dataset with another module.
        
        Args:
            dataset_id: The ID of the dataset to share
            target_module: The module to share with
            analysis_context: Optional context for the analysis
            
        Returns:
            Dictionary with sharing results
        """
        try:
            # Convert dataset for target module
            df, conversion_metadata = self.convert_for_module(dataset_id, target_module)
            
            # Get original dataset
            original_dataset = Dataset.objects.get(id=dataset_id)
            
            # Create new dataset for target module
            module_dataset = self.save_dataset(
                df=df,
                name=f"{original_dataset.name} (for {target_module})",
                description=f"Converted from dataset: {original_dataset.name} for use in {target_module}",
                user_id=original_dataset.user_id,
                metadata={
                    'original_dataset_id': str(original_dataset.id),
                    'conversion_metadata': conversion_metadata,
                    'analysis_context': analysis_context or {}
                },
                module=target_module,
                parent_dataset_id=str(original_dataset.id)
            )
            
            # Create link in registry
            sharing_key = f"shared_dataset_{original_dataset.id}_{target_module}"
            sharing_info = {
                'original_dataset_id': str(original_dataset.id),
                'module_dataset_id': str(module_dataset.id),
                'target_module': target_module,
                'shared_at': timezone.now().isoformat(),
                'conversion_metadata': conversion_metadata,
                'analysis_context': analysis_context or {}
            }
            
            # Return sharing information
            return {
                'original_dataset_id': str(original_dataset.id),
                'module_dataset_id': str(module_dataset.id),
                'target_module': target_module,
                'sharing_key': sharing_key,
                'sharing_info': sharing_info
            }
            
        except Exception as e:
            logger.error(f"Error sharing dataset {dataset_id} with module {target_module}: {str(e)}")
            raise
    
    def _load_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Load a dataset from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The loaded DataFrame
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext == '.xlsx' or file_ext == '.xls':
            return pd.read_excel(file_path)
        elif file_ext == '.json':
            return pd.read_json(file_path)
        elif file_ext == '.pkl' or file_ext == '.pickle':
            return pd.read_pickle(file_path)
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path)
        elif file_ext == '.feather':
            return pd.read_feather(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
    
    def _save_to_file(self, df: pd.DataFrame, name: str) -> str:
        """
        Save a DataFrame to a file.
        
        Args:
            df: The DataFrame to save
            name: Base name for the file
            
        Returns:
            Path to the saved file
        """
        # Create safe filename
        safe_name = ''.join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.parquet"
        
        # Ensure temp directory exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, self.temp_dir), exist_ok=True)
        
        # Save to parquet for efficiency
        file_path = os.path.join(self.temp_dir, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        df.to_parquet(full_path, index=False)
        
        return file_path
    
    def _generate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a schema for a DataFrame.
        
        Args:
            df: The DataFrame
            
        Returns:
            Dictionary containing schema information
        """
        schema = {
            'columns': [],
            'index_dtype': str(df.index.dtype),
            'row_count': len(df),
            'column_count': len(df.columns)
        }
        
        for col in df.columns:
            col_schema = {
                'name': col,
                'dtype': str(df[col].dtype),
                'nullable': bool(df[col].isna().any())
            }
            
            # Add more info based on dtype
            if pd.api.types.is_numeric_dtype(df[col]):
                col_schema['min'] = float(df[col].min()) if not pd.isna(df[col].min()) else None
                col_schema['max'] = float(df[col].max()) if not pd.isna(df[col].max()) else None
            elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                col_schema['unique_count'] = df[col].nunique()
            
            schema['columns'].append(col_schema)
        
        return schema
    
    def _calculate_hash(self, df: pd.DataFrame) -> str:
        """
        Calculate a hash for a DataFrame for data integrity checking.
        
        Args:
            df: The DataFrame
            
        Returns:
            Hash string
        """
        # Convert to string and hash
        df_str = df.to_csv(index=False)
        return hashlib.sha256(df_str.encode()).hexdigest()
    
    def _apply_transformations(self, df: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply a series of transformations to a DataFrame.
        
        Args:
            df: The DataFrame to transform
            transformations: List of transformation operations
            
        Returns:
            The transformed DataFrame
        """
        result_df = df.copy()
        
        for transform in transformations:
            transform_type = transform.get('type')
            
            if transform_type == 'filter':
                column = transform.get('column')
                operator = transform.get('operator')
                value = transform.get('value')
                
                if operator == 'equals':
                    result_df = result_df[result_df[column] == value]
                elif operator == 'not_equals':
                    result_df = result_df[result_df[column] != value]
                elif operator == 'greater_than':
                    result_df = result_df[result_df[column] > value]
                elif operator == 'less_than':
                    result_df = result_df[result_df[column] < value]
                elif operator == 'contains':
                    result_df = result_df[result_df[column].astype(str).str.contains(str(value))]
                elif operator == 'in':
                    result_df = result_df[result_df[column].isin(value)]
                
            elif transform_type == 'select':
                columns = transform.get('columns', [])
                result_df = result_df[columns]
                
            elif transform_type == 'rename':
                mapping = transform.get('mapping', {})
                result_df = result_df.rename(columns=mapping)
                
            elif transform_type == 'drop':
                columns = transform.get('columns', [])
                result_df = result_df.drop(columns=columns)
                
            elif transform_type == 'fill_na':
                column = transform.get('column')
                value = transform.get('value')
                if column:
                    result_df[column] = result_df[column].fillna(value)
                else:
                    result_df = result_df.fillna(value)
                    
            elif transform_type == 'drop_na':
                columns = transform.get('columns')
                how = transform.get('how', 'any')
                result_df = result_df.dropna(subset=columns, how=how)
                
            elif transform_type == 'type_convert':
                column = transform.get('column')
                dtype = transform.get('dtype')
                result_df[column] = result_df[column].astype(dtype)
                
            elif transform_type == 'custom':
                # Execute custom transformation defined as a Python expression
                # This is potentially dangerous and should be used with caution
                # Only enable for trusted environments
                code = transform.get('code')
                if code and getattr(settings, 'ALLOW_CUSTOM_TRANSFORMATIONS', False):
                    # Use locals to capture the result
                    local_vars = {'df': result_df, 'np': np, 'pd': pd}
                    exec(code, {}, local_vars)
                    result_df = local_vars['df']
        
        return result_df
    
    def _apply_module_transformations(self, df: pd.DataFrame, module: str) -> pd.DataFrame:
        """
        Apply module-specific transformations to a DataFrame.
        
        Args:
            df: The DataFrame to transform
            module: The module name
            
        Returns:
            The transformed DataFrame
        """
        # Get module information
        module_info = self.registry.get_module(module)
        
        if not module_info:
            logger.warning(f"Module {module} not found in registry")
            return df
        
        # Check if module has data transformations
        if 'data_transformations' not in module_info.get('metadata', {}):
            return df
        
        # Get transformations
        transformations = module_info['metadata']['data_transformations']
        
        # Apply transformations
        return self._apply_transformations(df, transformations)


# Create singleton instance
data_service = DataService()

def get_data_service() -> DataService:
    """Get the singleton data service instance."""
    return data_service