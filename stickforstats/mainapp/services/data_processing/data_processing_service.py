"""
Data Processing Service for StickForStats platform.
This module provides services for data preprocessing and transformation based on the original
StickForStats Streamlit application, migrated to work as a Django service.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, PolynomialFeatures, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import json
from datetime import datetime
import uuid

# Try importing error handling utilities, with fallback if not available
try:
    from stickforstats.core.services.error_handler import safe_operation, try_except
except ImportError:
    # Define simple decorator for error handling if core services aren't available
    def safe_operation(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
                return {"error": str(e)}
        return wrapper
    
    def try_except(func, fallback, error_message=None):
        try:
            return func()
        except Exception as e:
            if error_message:
                logging.error(f"{error_message}: {e}")
            return fallback

# Configure logging
logger = logging.getLogger(__name__)

class DataProcessingService:
    """
    Service for data preprocessing and transformation.
    
    This service provides methods for:
    - Handling missing values
    - Feature scaling
    - Categorical encoding
    - Feature engineering
    - Data validation
    - Data profiling and analysis
    
    Based on the original data_processing.py from the StickForStats Streamlit application.
    """
    
    def __init__(self):
        """Initialize data processing service."""
        pass
    
    @safe_operation
    def handle_missing_values(self, 
                           data: pd.DataFrame, 
                           method: str,
                           columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Handle missing values in the dataset.
        
        Args:
            data: Input DataFrame
            method: Method for handling missing values ('drop_rows', 'fill_mean', 
                    'fill_median', 'fill_mode', 'fill_constant')
            columns: Optional list of columns to process (default: all columns)
            
        Returns:
            Dictionary with processed data and metadata
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if method not in ['drop_rows', 'fill_mean', 'fill_median', 'fill_mode', 'fill_constant', 
                         'fill_forward', 'fill_backward', 'drop_columns']:
            return {'error': f"Invalid method: {method}"}
        
        # Use provided columns or all columns
        if columns is None:
            columns = data.columns.tolist()
        else:
            # Check if all columns exist
            missing_cols = [col for col in columns if col not in data.columns]
            if missing_cols:
                return {'error': f"Columns not found in data: {missing_cols}"}
        
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Count missing values before processing
        missing_before = df[columns].isnull().sum().to_dict()
        total_missing_before = sum(missing_before.values())
        
        # Process based on method
        if method == 'drop_rows':
            # Drop rows with missing values in specified columns
            df = df.dropna(subset=columns)
            action_description = "Dropped rows with missing values"
        
        elif method == 'fill_mean':
            # Fill missing values with column mean (numeric columns only)
            numeric_cols = [col for col in columns if np.issubdtype(df[col].dtype, np.number)]
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].mean())
            action_description = "Filled missing values with column means"
        
        elif method == 'fill_median':
            # Fill missing values with column median (numeric columns only)
            numeric_cols = [col for col in columns if np.issubdtype(df[col].dtype, np.number)]
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())
            action_description = "Filled missing values with column medians"
        
        elif method == 'fill_mode':
            # Fill missing values with column mode
            for col in columns:
                mode_value = df[col].mode()
                if not mode_value.empty:
                    df[col] = df[col].fillna(mode_value[0])
            action_description = "Filled missing values with column modes"
        
        elif method == 'fill_constant':
            # Fill missing values with a constant (0 for numeric, 'Unknown' for non-numeric)
            for col in columns:
                if np.issubdtype(df[col].dtype, np.number):
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna('Unknown')
            action_description = "Filled missing values with constants (0 or 'Unknown')"
        
        elif method == 'fill_forward':
            # Forward fill (use previous value)
            df[columns] = df[columns].ffill()
            action_description = "Filled missing values using forward fill method"
        
        elif method == 'fill_backward':
            # Backward fill (use next value)
            df[columns] = df[columns].bfill()
            action_description = "Filled missing values using backward fill method"
        
        elif method == 'drop_columns':
            # Drop columns with too many missing values (>50%)
            cols_to_drop = []
            for col in columns:
                if df[col].isnull().mean() > 0.5:  # More than 50% missing
                    cols_to_drop.append(col)
            
            df = df.drop(columns=cols_to_drop)
            action_description = f"Dropped columns with >50% missing values: {cols_to_drop}"
        
        # Count missing values after processing
        remaining_columns = [col for col in columns if col in df.columns]
        missing_after = df[remaining_columns].isnull().sum().to_dict()
        total_missing_after = sum(missing_after.values())
        
        return {
            'data': df,
            'method': method,
            'columns_processed': columns,
            'action_description': action_description,
            'rows_before': len(data),
            'rows_after': len(df),
            'columns_before': len(data.columns),
            'columns_after': len(df.columns),
            'missing_values_before': missing_before,
            'missing_values_after': missing_after,
            'total_missing_before': total_missing_before,
            'total_missing_after': total_missing_after,
            'processing_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def scale_features(self, 
                     data: pd.DataFrame, 
                     method: str,
                     columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scale numerical features in the dataset.
        
        Args:
            data: Input DataFrame
            method: Scaling method ('standard', 'minmax', 'robust')
            columns: Optional list of columns to process (default: all numeric columns)
            
        Returns:
            Dictionary with processed data and scaling information
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if method not in ['standard', 'minmax', 'robust']:
            return {'error': f"Invalid scaling method: {method}"}
        
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Identify numeric columns if not specified
        if columns is None:
            columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        else:
            # Check if all columns exist and are numeric
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {'error': f"Columns not found in data: {missing_cols}"}
            
            non_numeric_cols = [col for col in columns 
                              if not np.issubdtype(df[col].dtype, np.number)]
            if non_numeric_cols:
                return {'error': f"Non-numeric columns cannot be scaled: {non_numeric_cols}"}
        
        # Check if there are any numeric columns to scale
        if not columns:
            return {
                'data': df,
                'method': method,
                'columns_processed': [],
                'action_description': "No numeric columns to scale",
                'processing_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat()
            }
        
        # Apply scaling based on method
        scaler = None
        if method == 'standard':
            scaler = StandardScaler()
            action_description = "Applied standard scaling (mean=0, std=1)"
        elif method == 'minmax':
            scaler = MinMaxScaler()
            action_description = "Applied min-max scaling (range=[0, 1])"
        elif method == 'robust':
            scaler = RobustScaler()
            action_description = "Applied robust scaling (using median and IQR)"
        
        # Store original stats for reference
        original_stats = {}
        for col in columns:
            original_stats[col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median())
            }
        
        # Apply scaling
        df[columns] = scaler.fit_transform(df[columns])
        
        # Calculate new stats
        new_stats = {}
        for col in columns:
            new_stats[col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median())
            }
        
        # Get scaler parameters if available
        scaler_params = {}
        if hasattr(scaler, 'mean_') and hasattr(scaler, 'scale_'):
            # Standard scaler
            scaler_params = {
                'mean': scaler.mean_.tolist(),
                'scale': scaler.scale_.tolist()
            }
        elif hasattr(scaler, 'min_') and hasattr(scaler, 'scale_'):
            # MinMax scaler
            scaler_params = {
                'min': scaler.min_.tolist(),
                'scale': scaler.scale_.tolist(),
                'data_min': scaler.data_min_.tolist(),
                'data_max': scaler.data_max_.tolist(),
                'data_range': scaler.data_range_.tolist()
            }
        elif hasattr(scaler, 'center_') and hasattr(scaler, 'scale_'):
            # Robust scaler
            scaler_params = {
                'center': scaler.center_.tolist(),
                'scale': scaler.scale_.tolist()
            }
        
        return {
            'data': df,
            'method': method,
            'columns_processed': columns,
            'action_description': action_description,
            'original_stats': original_stats,
            'new_stats': new_stats,
            'scaler_params': scaler_params,
            'processing_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def encode_categorical(self, 
                        data: pd.DataFrame, 
                        method: str,
                        columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Encode categorical variables in the dataset.
        
        Args:
            data: Input DataFrame
            method: Encoding method ('one_hot', 'label', 'ordinal')
            columns: Optional list of columns to process (default: all object/category columns)
            
        Returns:
            Dictionary with processed data and encoding information
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if method not in ['one_hot', 'label', 'ordinal']:
            return {'error': f"Invalid encoding method: {method}"}
        
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Identify categorical columns if not specified
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        else:
            # Check if all columns exist
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {'error': f"Columns not found in data: {missing_cols}"}
        
        # Check if there are any categorical columns to encode
        if not columns:
            return {
                'data': df,
                'method': method,
                'columns_processed': [],
                'action_description': "No categorical columns to encode",
                'processing_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat()
            }
        
        # Store mapping for reference
        encoding_mapping = {}
        columns_created = []
        columns_removed = []
        
        # Apply encoding based on method
        if method == 'one_hot':
            # Track original shape
            original_shape = df.shape
            
            # One-hot encoding with pandas
            df = pd.get_dummies(df, columns=columns, drop_first=False)
            
            # Determine new columns created
            columns_created = [col for col in df.columns if col not in data.columns]
            columns_removed = columns
            
            action_description = f"Applied one-hot encoding, creating {len(columns_created)} new columns"
            
            # Create mapping information
            for col in columns:
                unique_values = data[col].dropna().unique().tolist()
                encoding_mapping[col] = {
                    'original_column': col,
                    'encoded_columns': [f"{col}_{val}" for val in unique_values],
                    'unique_values': unique_values
                }
        
        elif method == 'label':
            # Label encoding (convert to numeric codes)
            for col in columns:
                # Store original categories for mapping
                categories = df[col].dropna().unique().tolist()
                # Apply label encoding
                df[col] = pd.Categorical(df[col]).codes
                
                # Store mapping
                encoding_mapping[col] = {
                    'categories': categories,
                    'codes': list(range(len(categories)))
                }
            
            action_description = "Applied label encoding (converted to numeric codes)"
        
        elif method == 'ordinal':
            # Ordinal encoding (assumes categories are already in the correct order)
            for col in columns:
                # Get categories and sort them
                categories = df[col].dropna().unique().tolist()
                categories.sort()  # Default sorting
                
                # Create mapping dictionary
                mapping = {cat: i for i, cat in enumerate(categories)}
                
                # Apply mapping
                df[col] = df[col].map(mapping)
                
                # Store mapping
                encoding_mapping[col] = {
                    'categories': categories,
                    'codes': list(range(len(categories)))
                }
            
            action_description = "Applied ordinal encoding (assumes natural ordering)"
        
        return {
            'data': df,
            'method': method,
            'columns_processed': columns,
            'columns_created': columns_created,
            'columns_removed': columns_removed,
            'action_description': action_description,
            'encoding_mapping': encoding_mapping,
            'rows_before': len(data),
            'rows_after': len(df),
            'columns_before': len(data.columns),
            'columns_after': len(df.columns),
            'processing_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def create_feature_interactions(self, 
                                 data: pd.DataFrame,
                                 columns: List[str],
                                 interaction_type: str = 'polynomial',
                                 degree: int = 2) -> Dict[str, Any]:
        """
        Create interaction features between selected columns.
        
        Args:
            data: Input DataFrame
            columns: List of columns to create interactions for
            interaction_type: Type of interaction ('polynomial', 'multiplication')
            degree: Degree of polynomial features
            
        Returns:
            Dictionary with processed data and interaction information
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if interaction_type not in ['polynomial', 'multiplication']:
            return {'error': f"Invalid interaction type: {interaction_type}"}
        
        if not columns:
            return {'error': "No columns specified for interaction"}
        
        # Check if all columns exist and are numeric
        missing_cols = [col for col in columns if col not in data.columns]
        if missing_cols:
            return {'error': f"Columns not found in data: {missing_cols}"}
        
        non_numeric_cols = [col for col in columns 
                          if not np.issubdtype(data[col].dtype, np.number)]
        if non_numeric_cols:
            return {'error': f"Non-numeric columns cannot be used for interaction: {non_numeric_cols}"}
        
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Apply interaction based on type
        if interaction_type == 'polynomial':
            # Create polynomial features
            poly = PolynomialFeatures(degree=degree, include_bias=False)
            
            # Fit and transform
            poly_features = poly.fit_transform(df[columns])
            
            # Get feature names
            if hasattr(poly, 'get_feature_names_out'):
                feature_names = poly.get_feature_names_out(columns)
            else:
                # Fallback for older scikit-learn versions
                feature_names = poly.get_feature_names(columns)
            
            # Filter out the original features (they are included at the beginning)
            new_features = feature_names[len(columns):]
            
            # Create a DataFrame with the new features
            poly_df = pd.DataFrame(poly_features[:, len(columns):], columns=new_features, index=df.index)
            
            # Add new features to the original DataFrame
            df = pd.concat([df, poly_df], axis=1)
            
            action_description = f"Created polynomial features (degree={degree})"
        
        elif interaction_type == 'multiplication':
            # Create simple multiplicative interaction terms
            for i in range(len(columns)):
                for j in range(i+1, len(columns)):
                    col1, col2 = columns[i], columns[j]
                    interaction_name = f"{col1}_x_{col2}"
                    df[interaction_name] = df[col1] * df[col2]
            
            action_description = "Created multiplicative interaction terms"
        
        # Calculate new columns
        new_columns = [col for col in df.columns if col not in data.columns]
        
        return {
            'data': df,
            'method': interaction_type,
            'columns_processed': columns,
            'columns_created': new_columns,
            'action_description': action_description,
            'degree': degree if interaction_type == 'polynomial' else None,
            'num_features_before': len(data.columns),
            'num_features_after': len(df.columns),
            'processing_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def select_features(self, 
                      data: pd.DataFrame,
                      target_column: str,
                      num_features: int,
                      method: str = 'f_regression') -> Dict[str, Any]:
        """
        Select the most important features for a regression task.
        
        Args:
            data: Input DataFrame
            target_column: Target variable column name
            num_features: Number of features to select
            method: Feature selection method ('f_regression', 'mutual_info')
            
        Returns:
            Dictionary with selected features and importance scores
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if target_column not in data.columns:
            return {'error': f"Target column {target_column} not found in data"}
        
        if method not in ['f_regression', 'mutual_info']:
            return {'error': f"Invalid feature selection method: {method}"}
        
        # Extract features (X) and target (y)
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Identify numeric columns (only these can be used for feature selection)
        numeric_cols = X.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        if not numeric_cols:
            return {'error': "No numeric feature columns available for selection"}
        
        # Use only numeric columns
        X = X[numeric_cols]
        
        # Check if number of features requested is valid
        if num_features <= 0:
            return {'error': "Number of features must be positive"}
        if num_features > len(numeric_cols):
            num_features = len(numeric_cols)
        
        # Select features based on method
        if method == 'f_regression':
            selector = SelectKBest(score_func=f_regression, k=num_features)
            selected_features = selector.fit_transform(X, y)
            scores = selector.scores_
            score_name = "F-scores"
            action_description = f"Selected top {num_features} features using F-test (ANOVA)"
        
        elif method == 'mutual_info':
            selector = SelectKBest(score_func=mutual_info_regression, k=num_features)
            selected_features = selector.fit_transform(X, y)
            scores = selector.scores_
            score_name = "Mutual Information scores"
            action_description = f"Selected top {num_features} features using Mutual Information"
        
        # Get selected feature indices and names
        selected_indices = selector.get_support(indices=True)
        selected_column_names = [numeric_cols[i] for i in selected_indices]
        
        # Create a DataFrame with feature scores
        feature_scores = pd.DataFrame({
            'Feature': numeric_cols,
            'Score': scores
        }).sort_values('Score', ascending=False)
        
        # Create a new DataFrame with only selected features and target
        selected_df = data[selected_column_names + [target_column]]
        
        return {
            'data': selected_df,
            'feature_scores': feature_scores.to_dict(orient='records'),
            'selected_features': selected_column_names,
            'method': method,
            'score_name': score_name,
            'action_description': action_description,
            'num_features_before': len(numeric_cols),
            'num_features_selected': len(selected_column_names),
            'target_column': target_column,
            'processing_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def generate_data_profile(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive profile of the dataset.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Dictionary with data profiling information
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        # Create basic dataset information
        basic_info = {
            'num_rows': len(data),
            'num_columns': len(data.columns),
            'memory_usage': data.memory_usage(deep=True).sum(),
            'memory_usage_formatted': f"{data.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB"
        }
        
        # Analyze missing values
        missing_values = data.isnull().sum().to_dict()
        missing_percentage = (data.isnull().sum() / len(data) * 100).to_dict()
        
        # Count data types
        dtypes_count = data.dtypes.value_counts().to_dict()
        dtypes_count = {str(k): int(v) for k, v in dtypes_count.items()}
        
        # Generate column profiles
        column_profiles = {}
        
        for col in data.columns:
            profile = {
                'name': col,
                'dtype': str(data[col].dtype),
                'missing_count': int(data[col].isnull().sum()),
                'missing_percentage': float(data[col].isnull().sum() / len(data) * 100),
                'unique_count': int(data[col].nunique()),
                'unique_percentage': float(data[col].nunique() / len(data) * 100 if len(data) > 0 else 0)
            }
            
            # Add numeric statistics if applicable
            if np.issubdtype(data[col].dtype, np.number):
                numeric_stats = {
                    'min': float(data[col].min()) if not pd.isna(data[col].min()) else None,
                    'max': float(data[col].max()) if not pd.isna(data[col].max()) else None,
                    'mean': float(data[col].mean()) if not pd.isna(data[col].mean()) else None,
                    'median': float(data[col].median()) if not pd.isna(data[col].median()) else None,
                    'std': float(data[col].std()) if not pd.isna(data[col].std()) else None,
                    'skewness': float(data[col].skew()) if not pd.isna(data[col].skew()) else None,
                    'kurtosis': float(data[col].kurtosis()) if not pd.isna(data[col].kurtosis()) else None,
                    'is_skewed': abs(float(data[col].skew())) > 1 if not pd.isna(data[col].skew()) else None
                }
                profile.update(numeric_stats)
                
                # Add quartiles
                if not pd.isna(data[col].quantile(0.25)):
                    profile['q1'] = float(data[col].quantile(0.25))
                    profile['q3'] = float(data[col].quantile(0.75))
                    profile['iqr'] = float(profile['q3'] - profile['q1'])
                
                # Check for potential outliers
                if 'q1' in profile and 'iqr' in profile:
                    lower_bound = profile['q1'] - 1.5 * profile['iqr']
                    upper_bound = profile['q3'] + 1.5 * profile['iqr']
                    outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)][col]
                    profile['outlier_count'] = len(outliers)
                    profile['outlier_percentage'] = float(len(outliers) / len(data) * 100)
            
            # Add categorical statistics if applicable
            elif pd.api.types.is_object_dtype(data[col]) or pd.api.types.is_categorical_dtype(data[col]):
                # Get value counts
                value_counts = data[col].value_counts()
                if not value_counts.empty:
                    top_values = value_counts.head(5).to_dict()
                    # Convert keys to strings to ensure JSON serialization
                    top_values = {str(k): int(v) for k, v in top_values.items()}
                    
                    categorical_stats = {
                        'top_values': top_values,
                        'mode': str(data[col].mode().iloc[0]) if not data[col].mode().empty else None,
                        'mode_count': int(value_counts.iloc[0]) if not value_counts.empty else 0,
                        'mode_percentage': float(value_counts.iloc[0] / len(data) * 100) if not value_counts.empty else 0
                    }
                    profile.update(categorical_stats)
            
            # Add datetime statistics if applicable
            elif pd.api.types.is_datetime64_any_dtype(data[col]):
                datetime_stats = {
                    'min_date': data[col].min().isoformat() if not pd.isna(data[col].min()) else None,
                    'max_date': data[col].max().isoformat() if not pd.isna(data[col].max()) else None,
                    'range_days': float((data[col].max() - data[col].min()).days) if not pd.isna(data[col].min()) and not pd.isna(data[col].max()) else None
                }
                profile.update(datetime_stats)
            
            column_profiles[col] = profile
        
        # Calculate correlation matrix for numeric columns
        correlation_matrix = None
        numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if len(numeric_columns) > 1:
            corr_matrix = data[numeric_columns].corr().round(3)
            # Convert to a nested dictionary for easier serialization
            correlation_matrix = corr_matrix.to_dict(orient='index')
            
            # Find high correlations
            high_correlations = []
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    col1, col2 = numeric_columns[i], numeric_columns[j]
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:
                        high_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': float(corr_value)
                        })
        
        return {
            'basic_info': basic_info,
            'missing_values': missing_values,
            'missing_percentage': {k: float(v) for k, v in missing_percentage.items()},
            'dtypes_count': dtypes_count,
            'column_profiles': column_profiles,
            'correlation_matrix': correlation_matrix,
            'high_correlations': high_correlations if 'high_correlations' in locals() else None,
            'profile_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }

# Initialize global data processing service
data_processing_service = DataProcessingService()

def get_data_processing_service() -> DataProcessingService:
    """Get the global data processing service instance."""
    return data_processing_service