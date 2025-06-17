"""
Visualization Service for StickForStats platform.
This module provides services for creating various data visualizations,
including distributions, relationships, comparisons, and time series plots.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from typing import Dict, Any, List, Optional, Tuple, Union, BinaryIO
import logging
import io
import json
from datetime import datetime
import uuid
import base64
from PIL import Image as PILImage
from io import BytesIO
import os
from pathlib import Path

# Import services - will need to update with proper imports in integrated environment
try:
    from stickforstats.core.services.data_processing.statistical_utils import StatisticalUtilsService
    from stickforstats.core.services.error_handler import safe_operation, try_except
    from stickforstats.core.models import Visualization
except ImportError:
    # Fallback if core services aren't available
    # Define simple decorator for error handling
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

    # Define a simple StatisticalUtilsService stub
    class StatisticalUtilsService:
        def compute_descriptive_stats(self, data):
            results = {}
            for col in data.columns:
                results[col] = {
                    'mean': data[col].mean(),
                    'median': data[col].median(),
                    'std': data[col].std(),
                    'min': data[col].min(),
                    'max': data[col].max(),
                    'q1': data[col].quantile(0.25),
                    'q3': data[col].quantile(0.75),
                    'iqr': data[col].quantile(0.75) - data[col].quantile(0.25),
                    'range': data[col].max() - data[col].min(),
                    'skewness': stats.skew(data[col].dropna()),
                    'kurtosis': stats.kurtosis(data[col].dropna())
                }
            return results
        
        def perform_inferential_tests(self, data):
            results = {}
            for col in data.columns:
                values = data[col].dropna()
                results[col] = {
                    'normality_tests': {
                        'shapiro': {
                            'statistic': stats.shapiro(values[:min(5000, len(values))])[0],
                            'p_value': stats.shapiro(values[:min(5000, len(values))])[1]
                        }
                    }
                }
            return results
        
        def analyze_distributions(self, data):
            results = {}
            for col in data.columns:
                values = data[col].dropna()
                results[col] = {
                    'distribution_fit': {
                        'normal': {
                            'params': stats.norm.fit(values),
                            'ks_test': {
                                'statistic': stats.kstest(values, 'norm')[0],
                                'p_value': stats.kstest(values, 'norm')[1]
                            }
                        }
                    }
                }
            return results

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service for data visualization and plot generation.

    This service provides methods for:
    - Creating various types of data visualizations
    - Preparing plots for reports
    - Saving and retrieving visualizations
    - Exporting visualizations to different formats
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """Get singleton instance of visualization service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize visualization service."""
        self.color_schemes = {
            'default': px.colors.qualitative.Set3,
            'sequential': px.colors.sequential.Viridis,
            'diverging': px.colors.diverging.RdBu
        }

        # Set default configuration
        self.default_config = {
            'plot_width': 800,
            'plot_height': 600,
            'title_font_size': 16,
            'axis_font_size': 12,
            'legend_font_size': 10,
            'show_watermark': False,
            'interactive': True
        }

        # Visualization save directory
        self.plots_dir = Path('data/plots')
        self.plots_dir.mkdir(parents=True, exist_ok=True)

        # Initialize report service if available
        try:
            from stickforstats.core.services.report.report_service import ReportService
            self.report_service = ReportService()
        except Exception as e:
            logger.warning(f"Could not initialize report service: {e}")
            self.report_service = None
    
    @safe_operation
    def create_distribution_plots(self, data: pd.DataFrame, column: str, 
                               plot_types: List[str]) -> Dict[str, Any]:
        """
        Create distribution plots for a numeric column.
        
        Args:
            data: Input DataFrame
            column: Column name to visualize
            plot_types: List of plot types to create
            
        Returns:
            Dictionary with visualization results
        """
        results = {
            'type': 'distribution', 
            'plots': [], 
            'statistics': {}
        }
        
        if column not in data.columns:
            logger.warning(f"Column {column} not found in data")
            return results
        
        # Generate statistics for context
        stats_utils = StatisticalUtilsService()
        stats_context = {
            'descriptive': stats_utils.compute_descriptive_stats(data[[column]]),
            'inferential': stats_utils.perform_inferential_tests(data[[column]]),
            'distribution': stats_utils.analyze_distributions(data[[column]])
        }
        
        # Store statistics in results
        results['statistics'] = stats_context
        stats_desc = stats_context['descriptive'][column]
        
        for plot_type in plot_types:
            fig = None
            description = ""
            plot_config = {}
            
            if plot_type == "histogram":
                # Create histogram with statistical overlay
                fig = go.Figure()
                
                # Add histogram
                fig.add_trace(go.Histogram(
                    x=data[column],
                    nbinsx=30,
                    name="Data",
                    histnorm='probability density'
                ))
                
                # Add normal distribution overlay
                x_range = np.linspace(data[column].min(), data[column].max(), 100)
                norm_dist = stats.norm.pdf(x_range, stats_desc['mean'], stats_desc['std'])
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=norm_dist,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='red', dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Distribution of {column}",
                    xaxis_title=column,
                    yaxis_title="Density",
                    showlegend=True
                )
                
                # Create comprehensive description
                normality_test = stats_context['inferential'][column]['normality_tests']['shapiro']
                description = (
                    f"Distribution Analysis:\n"
                    f"• Mean: {stats_desc['mean']:.2f}\n"
                    f"• Median: {stats_desc['median']:.2f}\n"
                    f"• Standard Deviation: {stats_desc['std']:.2f}\n"
                    f"• Skewness: {stats_desc['skewness']:.2f} "
                    f"({'Positively' if stats_desc['skewness'] > 0 else 'Negatively'} skewed)\n"
                    f"• Kurtosis: {stats_desc['kurtosis']:.2f} "
                    f"({'Heavy-tailed' if stats_desc['kurtosis'] > 0 else 'Light-tailed'} distribution)\n"
                    f"• Normality Test (Shapiro-Wilk): p-value = {normality_test['p_value']:.4f} "
                    f"({'Normally distributed' if normality_test['p_value'] > 0.05 else 'Not normally distributed'})"
                )
                
                plot_config = {
                    'bins': 30,
                    'show_normal_overlay': True
                }
            
            elif plot_type == "boxplot":
                fig = go.Figure()
                
                # Add box plot
                fig.add_trace(go.Box(
                    y=data[column],
                    name=column,
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8
                ))
                
                # Add statistical annotations
                fig.add_annotation(
                    x=0.95,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=f"Q1: {stats_desc['q1']:.2f}\nMedian: {stats_desc['median']:.2f}\nQ3: {stats_desc['q3']:.2f}",
                    showarrow=False,
                    align="left",
                    bgcolor="rgba(255, 255, 255, 0.8)"
                )
                
                fig.update_layout(
                    title=f"Box Plot of {column}",
                    yaxis_title=column,
                    showlegend=False
                )
                
                description = (
                    f"Box Plot Analysis:\n"
                    f"• Q1 (25th percentile): {stats_desc['q1']:.2f}\n"
                    f"• Median: {stats_desc['median']:.2f}\n"
                    f"• Q3 (75th percentile): {stats_desc['q3']:.2f}\n"
                    f"• IQR: {stats_desc['iqr']:.2f}\n"
                    f"• Range: {stats_desc['range']:.2f}"
                )
            
            elif plot_type == "violinplot":
                fig = go.Figure()
                
                # Add violin plot
                fig.add_trace(go.Violin(
                    y=data[column],
                    box_visible=True,
                    meanline_visible=True,
                    points="outliers"
                ))
                
                fig.update_layout(
                    title=f"Violin Plot of {column}",
                    yaxis_title=column
                )
                
                description = (
                    f"Violin Plot Analysis:\n"
                    f"• Shows the probability density of data at different values\n"
                    f"• Mean: {stats_desc['mean']:.2f}\n"
                    f"• Median: {stats_desc['median']:.2f}\n"
                    f"• Data spread indicated by width of violin"
                )
            
            elif plot_type == "kdeplot":
                # Calculate KDE
                kde = stats.gaussian_kde(data[column].dropna())
                x_range = np.linspace(data[column].min(), data[column].max(), 100)
                y_kde = kde(x_range)
                
                fig = go.Figure()
                
                # Add KDE
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_kde,
                    mode='lines',
                    name='KDE',
                    fill='tozeroy'
                ))
                
                # Add mean and median lines
                fig.add_vline(x=stats_desc['mean'], line_dash="dash", line_color="red",
                            annotation_text="Mean")
                fig.add_vline(x=stats_desc['median'], line_dash="dash", line_color="green",
                            annotation_text="Median")
                
                fig.update_layout(
                    title=f"Kernel Density Estimation for {column}",
                    xaxis_title=column,
                    yaxis_title="Density"
                )
                
                description = (
                    f"KDE Analysis:\n"
                    f"• Non-parametric estimation of the probability density function\n"
                    f"• Mean: {stats_desc['mean']:.2f}\n"
                    f"• Median: {stats_desc['median']:.2f}\n"
                    f"• Distribution shape: "
                    f"{'Symmetric' if abs(stats_desc['skewness']) < 0.5 else 'Asymmetric'}"
                )
            
            elif plot_type == "qqplot":
                # Calculate Q-Q plot data
                qq_data = stats.probplot(data[column].dropna(), dist="norm")
                
                fig = go.Figure()
                
                # Add scatter points
                fig.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[0][1],
                    mode='markers',
                    name='Data Points'
                ))
                
                # Add reference line
                fig.add_trace(go.Scatter(
                    x=qq_data[0][0],
                    y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
                    mode='lines',
                    name='Reference Line',
                    line=dict(color='red', dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Q-Q Plot for {column}",
                    xaxis_title="Theoretical Quantiles",
                    yaxis_title="Sample Quantiles"
                )
                
                # Test for normality
                normality_test = stats_context['inferential'][column]['normality_tests']['shapiro']
                description = (
                    f"Q-Q Plot Analysis:\n"
                    f"• Visual assessment of normality\n"
                    f"• Shapiro-Wilk test: p-value = {normality_test['p_value']:.4f}\n"
                    f"• Interpretation: "
                    f"{'Data appears normally distributed' if normality_test['p_value'] > 0.05 else 'Data deviates from normal distribution'}\n"
                    f"• Points following the reference line indicate normality"
                )
            
            if fig:
                # Convert to JSON for serialization
                plot_json = self._fig_to_json(fig)
                
                results['plots'].append({
                    'id': str(uuid.uuid4()),
                    'type': plot_type,
                    'plot_data': plot_json,
                    'title': f"{plot_type} of {column}",
                    'description': description,
                    'config': plot_config,
                    'created_at': datetime.now().isoformat()
                })
        
        return results
    
    @safe_operation
    def create_relationship_plots(self, data: pd.DataFrame, x_col: str, y_col: str, 
                               plot_types: List[str], color_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Create relationship plots between two numeric columns.
        
        Args:
            data: Input DataFrame
            x_col: X-axis column name
            y_col: Y-axis column name
            plot_types: List of plot types to create
            color_col: Optional column to use for coloring points
            
        Returns:
            Dictionary with visualization results
        """
        results = {'type': 'relationship', 'plots': []}
        
        if x_col not in data.columns or y_col not in data.columns:
            logger.warning(f"Column {x_col} or {y_col} not found in data")
            return results
        
        # Calculate correlation for description
        correlation = data[[x_col, y_col]].corr().iloc[0, 1]
        
        for plot_type in plot_types:
            fig = None
            description = ""
            plot_config = {}
            
            if plot_type == "scatter":
                plot_config = {'color_by': color_col if color_col else None}
                
                if color_col and color_col in data.columns:
                    fig = px.scatter(
                        data, 
                        x=x_col, 
                        y=y_col,
                        color=color_col,
                        title=f"Scatter Plot: {x_col} vs {y_col}"
                    )
                else:
                    fig = px.scatter(
                        data, 
                        x=x_col, 
                        y=y_col,
                        title=f"Scatter Plot: {x_col} vs {y_col}"
                    )
                
                description = (
                    f"Scatter Plot Analysis:\n"
                    f"• Relationship between {x_col} and {y_col}\n"
                    f"• Correlation coefficient: {correlation:.4f}\n"
                    f"• Strength: {self._describe_correlation(correlation)}"
                )
            
            elif plot_type == "line":
                fig = px.line(
                    data.sort_values(x_col), 
                    x=x_col, 
                    y=y_col,
                    color=color_col if color_col in data.columns else None,
                    title=f"Line Plot: {x_col} vs {y_col}"
                )
                
                description = (
                    f"Line Plot Analysis:\n"
                    f"• Trend between {x_col} and {y_col}\n"
                    f"• Correlation coefficient: {correlation:.4f}"
                )
                
                plot_config = {'sorted_by': x_col}
            
            elif plot_type == "hexbin":
                fig = px.density_heatmap(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"Hex Plot: {x_col} vs {y_col}",
                    marginal_x="histogram",
                    marginal_y="histogram"
                )
                
                description = (
                    f"Hexbin Plot Analysis:\n"
                    f"• Density of points between {x_col} and {y_col}\n"
                    f"• Useful for visualizing large datasets\n"
                    f"• Shows concentration of observations"
                )
            
            elif plot_type == "regression":
                fig = px.scatter(
                    data, 
                    x=x_col, 
                    y=y_col,
                    color=color_col if color_col in data.columns else None,
                    trendline="ols",
                    title=f"Regression Plot: {x_col} vs {y_col}"
                )
                
                # Try to extract regression metrics 
                import statsmodels.api as sm
                
                try:
                    X = sm.add_constant(data[x_col])
                    model = sm.OLS(data[y_col], X).fit()
                    r_squared = model.rsquared
                    p_value = model.f_pvalue
                    slope = model.params[1]
                    
                    plot_config = {
                        'r_squared': r_squared,
                        'p_value': p_value,
                        'slope': slope
                    }
                    
                    description = (
                        f"Regression Analysis:\n"
                        f"• Linear relationship between {x_col} and {y_col}\n"
                        f"• R-squared: {r_squared:.4f}\n"
                        f"• p-value: {p_value:.4f}\n"
                        f"• Slope: {slope:.4f}\n"
                        f"• Interpretation: {self._interpret_regression(r_squared, p_value)}"
                    )
                except Exception as e:
                    logger.warning(f"Error calculating regression metrics: {str(e)}")
                    description = (
                        f"Regression Analysis:\n"
                        f"• Linear relationship between {x_col} and {y_col}\n"
                        f"• Correlation coefficient: {correlation:.4f}"
                    )
            
            if fig:
                # Convert to JSON for serialization
                plot_json = self._fig_to_json(fig)
                
                results['plots'].append({
                    'id': str(uuid.uuid4()),
                    'type': plot_type,
                    'plot_data': plot_json,
                    'title': f"{plot_type} of {x_col} vs {y_col}",
                    'description': description,
                    'config': plot_config,
                    'created_at': datetime.now().isoformat()
                })
        
        return results
    
    @safe_operation
    def create_comparison_plots(self, data: pd.DataFrame, category_col: str, value_col: str, 
                             plot_type: str, **kwargs) -> Dict[str, Any]:
        """
        Create comparison plots between a categorical and numeric column.
        
        Args:
            data: Input DataFrame
            category_col: Categorical column name
            value_col: Numeric column name
            plot_type: Type of plot to create
            **kwargs: Additional plot-specific parameters
            
        Returns:
            Dictionary with visualization results
        """
        results = {'type': 'comparison', 'plots': []}
        
        if category_col not in data.columns or value_col not in data.columns:
            logger.warning(f"Column {category_col} or {value_col} not found in data")
            return results
        
        fig = None
        description = ""
        plot_config = {}
        
        if plot_type == "bar":
            agg_func = kwargs.get('agg_func', 'mean')
            plot_config = {'agg_func': agg_func}
            
            grouped_data = data.groupby(category_col)[value_col].agg(agg_func).reset_index()
            fig = px.bar(
                grouped_data,
                x=category_col, 
                y=value_col,
                title=f"{agg_func.capitalize()} of {value_col} by {category_col}",
                color=category_col
            )
            
            description = (
                f"Bar Plot Analysis:\n"
                f"• Comparison of {value_col} ({agg_func}) across {category_col} categories\n"
                f"• {len(grouped_data)} categories represented\n"
                f"• Highest value: {grouped_data[value_col].max():.2f} ({grouped_data.loc[grouped_data[value_col].idxmax(), category_col]})\n"
                f"• Lowest value: {grouped_data[value_col].min():.2f} ({grouped_data.loc[grouped_data[value_col].idxmin(), category_col]})"
            )
        
        elif plot_type == "box":
            fig = px.box(
                data, 
                x=category_col, 
                y=value_col,
                title=f"Box Plot of {value_col} by {category_col}",
                color=category_col
            )
            
            # Generate descriptive statistics per group
            grouped_stats = {}
            for group in data[category_col].unique():
                group_data = data[data[category_col] == group][value_col]
                grouped_stats[group] = {
                    'median': group_data.median(),
                    'q1': group_data.quantile(0.25),
                    'q3': group_data.quantile(0.75),
                    'min': group_data.min(),
                    'max': group_data.max()
                }
            
            plot_config = {'grouped_stats': grouped_stats}
            
            description = (
                f"Box Plot Analysis:\n"
                f"• Distribution of {value_col} across {category_col} categories\n"
                f"• Shows median, quartiles, and outliers for each group\n"
                f"• Useful for comparing distributions and identifying outliers"
            )
        
        elif plot_type == "violin":
            show_points = kwargs.get('show_points', False)
            plot_config = {'show_points': show_points}
            
            fig = px.violin(
                data, 
                x=category_col, 
                y=value_col,
                title=f"Violin Plot of {value_col} by {category_col}",
                color=category_col,
                box=True, 
                points="all" if show_points else None
            )
            
            description = (
                f"Violin Plot Analysis:\n"
                f"• Distribution density of {value_col} across {category_col} categories\n"
                f"• Wider sections represent higher density of points\n"
                f"• Shows both distribution shape and summary statistics"
            )
        
        elif plot_type == "strip":
            jitter = kwargs.get('jitter', 0.5)
            plot_config = {'jitter': jitter}
            
            fig = px.strip(
                data, 
                x=category_col, 
                y=value_col,
                title=f"Strip Plot of {value_col} by {category_col}",
                color=category_col
            )
            fig.update_traces(jitter=jitter)
            
            description = (
                f"Strip Plot Analysis:\n"
                f"• Individual observations of {value_col} across {category_col} categories\n"
                f"• Each point represents an observation\n"
                f"• Useful for seeing the actual distribution of data points"
            )
        
        if fig:
            # Convert to JSON for serialization
            plot_json = self._fig_to_json(fig)
            
            results['plots'].append({
                'id': str(uuid.uuid4()),
                'type': plot_type,
                'plot_data': plot_json,
                'title': f"{plot_type} of {value_col} by {category_col}",
                'description': description,
                'config': plot_config,
                'created_at': datetime.now().isoformat()
            })
        
        return results
    
    def _fig_to_json(self, fig) -> Dict[str, Any]:
        """Convert a Plotly figure to JSON for serialization."""
        return json.loads(fig.to_json())
    
    def _describe_correlation(self, corr: float) -> str:
        """Provide a qualitative description of a correlation coefficient."""
        abs_corr = abs(corr)
        if abs_corr < 0.1:
            strength = "Negligible"
        elif abs_corr < 0.3:
            strength = "Weak"
        elif abs_corr < 0.5:
            strength = "Moderate"
        elif abs_corr < 0.7:
            strength = "Strong"
        else:
            strength = "Very strong"
            
        direction = "positive" if corr >= 0 else "negative"
        return f"{strength} {direction} correlation"
    
    def _interpret_regression(self, r_squared: float, p_value: float) -> str:
        """Interpret regression results."""
        if p_value < 0.05:
            significance = "Statistically significant"
        else:
            significance = "Not statistically significant"

        if r_squared < 0.1:
            fit = "Very poor fit"
        elif r_squared < 0.3:
            fit = "Poor fit"
        elif r_squared < 0.5:
            fit = "Moderate fit"
        elif r_squared < 0.7:
            fit = "Good fit"
        else:
            fit = "Excellent fit"

        return f"{significance} relationship with {fit} (R² = {r_squared:.2f})"