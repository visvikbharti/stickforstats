"""
Data validation service for the StickForStats application.

This module provides services for validating data, checking data quality,
and ensuring data is suitable for statistical analyses. Adapted from the
original Streamlit-based data_validation.py and enhanced_validation.py.
"""
import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from django.core.files.uploadedfile import UploadedFile
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """A validation rule for data checking."""
    check_function: Callable[[pd.DataFrame], bool]
    message: str
    level: str = "error"  # "error", "warning", or "info"

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    messages: List[Dict[str, str]]
    data: Optional[pd.DataFrame] = None


class DataValidatorService:
    """
    Service for validating data quality and suitability for analysis.
    
    This service provides methods for:
    - Validating file uploads
    - Checking data quality
    - Ensuring data is suitable for specific statistical tests
    - Creating custom validation rules
    """
    
    def __init__(self):
        """Initialize validator service."""
        pass
    
    def create_validator(self) -> 'DataValidator':
        """
        Create a new data validator with custom rules.
        
        Returns:
            DataValidator instance for rule-based validation
        """
        return DataValidator()
    
    def validate_file(self, file: Union[UploadedFile, BytesIO], 
                    filename: str = None,
                    file_type: str = None,
                    max_size_mb: int = 100) -> ValidationResult:
        """
        Validate an uploaded file and load it into a DataFrame.
        
        Args:
            file: Uploaded file or file-like object
            filename: Name of the file (required if not using UploadedFile)
            file_type: Type of file (required if not using UploadedFile)
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            ValidationResult with the loaded DataFrame if valid
        """
        try:
            # Get file details
            if isinstance(file, UploadedFile):
                file_size = file.size / (1024 * 1024)  # Convert to MB
                file_name = file.name
                file_ext = file.name.split('.')[-1].lower()
            else:
                # For BytesIO objects
                file.seek(0, 2)  # Go to the end
                file_size = file.tell() / (1024 * 1024)  # Get size in MB
                file.seek(0)  # Go back to start
                
                if not filename:
                    return ValidationResult(
                        is_valid=False,
                        messages=[{"message": "Filename required for BytesIO objects", "level": "error"}],
                        data=None
                    )
                
                file_name = filename
                file_ext = filename.split('.')[-1].lower()
            
            # If file_type is explicitly provided, use it
            if file_type:
                file_ext = file_type.lower()
            
            # Check file size
            if file_size > max_size_mb:
                return ValidationResult(
                    is_valid=False,
                    messages=[{
                        "message": f"File too large ({file_size:.1f}MB). Maximum allowed size is {max_size_mb}MB",
                        "level": "error"
                    }],
                    data=None
                )
            
            # Check file extension
            if file_ext not in ['csv', 'xlsx', 'xls']:
                return ValidationResult(
                    is_valid=False,
                    messages=[{
                        "message": f"Unsupported file format: .{file_ext}. Please upload CSV or Excel files",
                        "level": "error"
                    }],
                    data=None
                )
            
            # Load file into DataFrame
            if file_ext == 'csv':
                data = pd.read_csv(file)
            else:
                data = pd.read_excel(file)
            
            # Basic validation
            validator = DataValidator()
            
            # Check if DataFrame is empty
            validator.add_rule(
                lambda df: not df.empty,
                "The uploaded file contains no data",
                "error"
            )
            
            # Check if DataFrame has at least one column
            validator.add_rule(
                lambda df: df.shape[1] > 0,
                "The uploaded file contains no columns",
                "error"
            )
            
            # Check for missing values
            validator.add_rule(
                lambda df: df.isnull().sum().sum() == 0,
                f"The uploaded file contains {data.isnull().sum().sum()} missing values. Consider using data preprocessing",
                "warning"
            )
            
            result = validator.validate(data)
            
            # Additional information messages
            if result.is_valid:
                result.messages.append({
                    "message": f"Successfully loaded file with {data.shape[0]} rows and {data.shape[1]} columns",
                    "level": "info"
                })
                
                # Add warning if file has many rows (might be slow)
                if data.shape[0] > 10000:
                    result.messages.append({
                        "message": f"Large dataset detected ({data.shape[0]} rows). Some operations may be slow",
                        "level": "warning"
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating uploaded file: {str(e)}")
            return ValidationResult(
                is_valid=False,
                messages=[{"message": f"Error processing file: {str(e)}", "level": "error"}],
                data=None
            )
    
    def validate_for_test(self, data: pd.DataFrame, test_type: str) -> ValidationResult:
        """
        Validate data for a specific statistical test.
        
        Args:
            data: DataFrame to validate
            test_type: Type of statistical test
            
        Returns:
            ValidationResult object with validation status and messages
        """
        validator = DataValidator()
        
        # Generic validations
        validator.add_rule(
            lambda df: not df.empty,
            "Dataset is empty",
            "error"
        )
        
        # Test-specific validations
        if test_type.lower() in ['ttest', 't-test', 'independent t-test']:
            # At least one numeric column
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=[np.number]).columns) > 0,
                "T-test requires at least one numeric column",
                "error"
            )
            
            # At least one categorical column with 2 groups
            def has_valid_groups(df):
                cat_cols = df.select_dtypes(include=['object', 'category']).columns
                return any(df[col].nunique() == 2 for col in cat_cols)
            
            validator.add_rule(
                has_valid_groups,
                "T-test requires a categorical column with exactly 2 groups",
                "error"
            )
        
        elif test_type.lower() in ['anova', 'one-way anova']:
            # At least one numeric column
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=[np.number]).columns) > 0,
                "ANOVA requires at least one numeric column",
                "error"
            )
            
            # At least one categorical column with 3+ groups
            def has_valid_groups(df):
                cat_cols = df.select_dtypes(include=['object', 'category']).columns
                return any(df[col].nunique() >= 3 for col in cat_cols)
            
            validator.add_rule(
                has_valid_groups,
                "ANOVA requires a categorical column with 3 or more groups",
                "error"
            )
        
        elif test_type.lower() in ['correlation', 'pearson', 'spearman']:
            # At least two numeric columns
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=[np.number]).columns) >= 2,
                "Correlation analysis requires at least two numeric columns",
                "error"
            )
        
        elif test_type.lower() in ['chi_square', 'chi-square', 'chi2']:
            # At least two categorical columns
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=['object', 'category']).columns) >= 2,
                "Chi-square test requires at least two categorical columns",
                "error"
            )
        
        elif test_type.lower() in ['time_series', 'timeseries', 'time series']:
            # At least one datetime column
            validator.add_rule(
                lambda df: any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns),
                "Time series analysis requires at least one datetime column",
                "error"
            )
            
            # At least one numeric column
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=[np.number]).columns) > 0,
                "Time series analysis requires at least one numeric column",
                "error"
            )
        
        elif test_type.lower() in ['regression', 'linear regression']:
            # At least one dependent variable (numeric)
            validator.add_rule(
                lambda df: len(df.select_dtypes(include=[np.number]).columns) > 0,
                "Regression requires at least one numeric column for the dependent variable",
                "error"
            )
            
            # At least one independent variable
            validator.add_rule(
                lambda df: df.shape[1] >= 2,
                "Regression requires at least one additional column for independent variables",
                "error"
            )
        
        # Add more test validations as needed
        
        return validator.validate(data)
    
    def validate_numeric_columns(self, data: pd.DataFrame, 
                              required_cols: int = 1) -> ValidationResult:
        """
        Validate that data has sufficient numeric columns.
        
        Args:
            data: DataFrame to validate
            required_cols: Minimum number of numeric columns required
            
        Returns:
            ValidationResult object with validation status and messages
        """
        validator = DataValidator()
        
        validator.add_rule(
            lambda df: len(df.select_dtypes(include=[np.number]).columns) >= required_cols,
            f"Analysis requires at least {required_cols} numeric column(s)",
            "error"
        )
        
        return validator.validate(data)
    
    def validate_categorical_columns(self, data: pd.DataFrame, 
                                  required_cols: int = 1) -> ValidationResult:
        """
        Validate that data has sufficient categorical columns.
        
        Args:
            data: DataFrame to validate
            required_cols: Minimum number of categorical columns required
            
        Returns:
            ValidationResult object with validation status and messages
        """
        validator = DataValidator()
        
        validator.add_rule(
            lambda df: len(df.select_dtypes(include=['object', 'category']).columns) >= required_cols,
            f"Analysis requires at least {required_cols} categorical column(s)",
            "error"
        )
        
        return validator.validate(data)
    
    def validate_datetime_columns(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate that data has at least one datetime column for time series analysis.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            ValidationResult object with validation status and messages
        """
        validator = DataValidator()
        
        validator.add_rule(
            lambda df: any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns),
            "Time series analysis requires at least one datetime column",
            "error"
        )
        
        return validator.validate(data)
    
    def preprocess_data(self, data: pd.DataFrame, 
                     handle_missing: bool = True,
                     handle_outliers: bool = False,
                     encode_categories: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Preprocess data with cleaning and transformation operations.
        
        Args:
            data: DataFrame to preprocess
            handle_missing: Whether to handle missing values
            handle_outliers: Whether to handle outliers
            encode_categories: Whether to encode categorical variables
            
        Returns:
            Tuple of (processed DataFrame, processing summary)
        """
        processing_summary = {}
        processed_data = data.copy()
        
        # Handle missing values
        if handle_missing:
            # Identify numeric and categorical columns
            numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
            categorical_columns = processed_data.select_dtypes(include=['object', 'category']).columns
            
            # Track missing values before processing
            missing_before = processed_data.isnull().sum().sum()
            
            # Fill numeric columns with mean
            if len(numeric_columns) > 0:
                processed_data[numeric_columns] = processed_data[numeric_columns].fillna(
                    processed_data[numeric_columns].mean()
                )
            
            # Fill categorical columns with mode
            for col in categorical_columns:
                if processed_data[col].isnull().any():
                    # Get mode value
                    mode_value = processed_data[col].mode()
                    fill_value = mode_value[0] if not mode_value.empty else "Unknown"
                    processed_data[col] = processed_data[col].fillna(fill_value)
            
            # Track missing values after processing
            missing_after = processed_data.isnull().sum().sum()
            
            processing_summary['missing_values'] = {
                'before': int(missing_before),
                'after': int(missing_after),
                'filled': int(missing_before - missing_after)
            }
        
        # Handle outliers
        if handle_outliers:
            # Use IQR method for outlier detection
            numeric_columns = processed_data.select_dtypes(include=[np.number]).columns
            outlier_counts = {}
            
            for col in numeric_columns:
                q1 = processed_data[col].quantile(0.25)
                q3 = processed_data[col].quantile(0.75)
                iqr = q3 - q1
                
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                # Count outliers
                outliers_mask = (processed_data[col] < lower_bound) | (processed_data[col] > upper_bound)
                outlier_counts[col] = outliers_mask.sum()
                
                # Clip outliers to bounds
                processed_data[col] = processed_data[col].clip(lower=lower_bound, upper=upper_bound)
            
            processing_summary['outliers'] = {
                'detected': outlier_counts,
                'method': 'IQR (1.5 * IQR)'
            }
        
        # Encode categorical variables
        if encode_categories:
            categorical_columns = processed_data.select_dtypes(include=['object', 'category']).columns
            encoding_map = {}
            
            for col in categorical_columns:
                # Get unique values and create mapping
                unique_values = processed_data[col].unique()
                col_map = {val: idx for idx, val in enumerate(unique_values)}
                
                # Encode column
                processed_data[f"{col}_encoded"] = processed_data[col].map(col_map)
                
                # Store mapping
                encoding_map[col] = col_map
            
            processing_summary['category_encoding'] = {
                'columns': list(categorical_columns),
                'mapping': encoding_map
            }
        
        return processed_data, processing_summary


class DataValidator:
    """Validates data against a set of rules."""
    
    def __init__(self):
        """Initialize the validator with an empty set of rules."""
        self.rules: List[ValidationRule] = []
        
    def add_rule(self, check_function: Callable[[pd.DataFrame], bool], 
                message: str, level: str = "error") -> None:
        """
        Add a validation rule.
        
        Args:
            check_function: Function that takes a DataFrame and returns True if valid
            message: Message to display if validation fails
            level: Severity level of the failure ("error", "warning", or "info")
        """
        self.rules.append(ValidationRule(check_function, message, level))
        
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate data against all rules.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            ValidationResult object with validation status and messages
        """
        is_valid = True
        messages = []
        
        for rule in self.rules:
            try:
                check_result = rule.check_function(data)
                if not check_result:
                    messages.append({
                        "message": rule.message,
                        "level": rule.level
                    })
                    if rule.level == "error":
                        is_valid = False
            except Exception as e:
                logger.error(f"Error during validation: {str(e)}")
                messages.append({
                    "message": f"Validation error: {str(e)}",
                    "level": "error"
                })
                is_valid = False
        
        return ValidationResult(is_valid=is_valid, messages=messages, data=data)


# Create singleton instance
data_validator_service = DataValidatorService()

def get_data_validator_service() -> DataValidatorService:
    """Get global data validator service instance."""
    return data_validator_service