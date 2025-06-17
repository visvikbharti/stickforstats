"""
Time Series Service for StickForStats platform.
This module provides services for time series analysis and visualization based on the original
StickForStats Streamlit application, migrated to work as a Django service.
"""
import pandas as pd
import numpy as np
import json
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
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

class TimeSeriesService:
    """
    Service for time series analysis and forecasting.
    
    This service provides methods for:
    - Time series decomposition
    - Stationarity testing
    - ACF/PACF analysis
    - Basic forecasting using ARIMA, ETS models
    - Time series visualization
    
    Based on the original TimeSeriesAnalyzer class from the StickForStats Streamlit application.
    """
    
    def __init__(self):
        """Initialize time series service."""
        pass
    
    @safe_operation
    def check_stationarity(self, series: pd.Series) -> Dict[str, Any]:
        """
        Perform stationarity test using Augmented Dickey-Fuller test.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            
        Returns:
            Dictionary with test results
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        if len(clean_series) < 8:
            return {
                'error': "Not enough data points for stationarity test (minimum 8 required)",
                'is_stationary': None
            }
        
        # Perform Augmented Dickey-Fuller test
        result = adfuller(clean_series)
        
        return {
            'test_statistic': float(result[0]),
            'p_value': float(result[1]),
            'critical_values': result[4],
            'is_stationary': bool(result[1] < 0.05),
            'test_used': 'Augmented Dickey-Fuller'
        }
    
    @safe_operation
    def perform_decomposition(self, 
                            series: pd.Series, 
                            period: Optional[int] = None,
                            model: str = 'additive') -> Dict[str, Any]:
        """
        Perform seasonal decomposition of time series.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            period: Seasonality period (e.g., 12 for monthly, 7 for weekly)
            model: Decomposition model, 'additive' or 'multiplicative'
            
        Returns:
            Dictionary with decomposition results and visualization data
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Try to infer period if not provided
        if period is None:
            if hasattr(clean_series.index, 'freq'):
                if clean_series.index.freq == 'M':
                    period = 12  # Monthly data
                elif clean_series.index.freq == 'D':
                    period = 7   # Daily data (assume weekly seasonality)
                elif clean_series.index.freq == 'Q':
                    period = 4   # Quarterly data
                elif clean_series.index.freq == 'H':
                    period = 24  # Hourly data
                else:
                    # Default to 12 for unknown frequencies
                    period = 12
            else:
                # Try to infer from data
                if len(clean_series) < 24:
                    period = len(clean_series) // 2
                else:
                    period = 12  # Default to 12
        
        # Ensure period makes sense for the data
        if period > len(clean_series) // 2:
            period = len(clean_series) // 2
            logger.warning(f"Period adjusted to {period} based on data length")
        
        # Perform decomposition
        decomposition = seasonal_decompose(
            clean_series,
            model=model,
            period=period,
            extrapolate_trend='freq'
        )
        
        # Create visualization using Plotly
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=["Original", "Trend", "Seasonal", "Residual"]
        )
        
        # Add components to plot
        fig.add_trace(
            go.Scatter(x=clean_series.index, y=clean_series.values, name="Original"),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=clean_series.index, y=decomposition.trend, name="Trend"),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=clean_series.index, y=decomposition.seasonal, name="Seasonal"),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=clean_series.index, y=decomposition.resid, name="Residual"),
            row=4, col=1
        )
        
        fig.update_layout(
            height=900,
            title="Time Series Decomposition",
            showlegend=False
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        # Extract component data for API response
        components = {
            'trend': decomposition.trend.to_dict(),
            'seasonal': decomposition.seasonal.to_dict(),
            'residual': decomposition.resid.to_dict(),
            'period': period,
            'model': model
        }
        
        return {
            'components': components,
            'visualization': plot_json,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'period': period,
            'model': model
        }
    
    @safe_operation
    def analyze_acf_pacf(self, 
                       series: pd.Series, 
                       nlags: int = 40,
                       alpha: float = 0.05) -> Dict[str, Any]:
        """
        Calculate and visualize ACF and PACF.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            nlags: Number of lags to calculate
            alpha: Significance level for confidence intervals
            
        Returns:
            Dictionary with ACF/PACF values and visualization data
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Limit nlags to half the data length to avoid spurious correlations
        max_lags = len(clean_series) // 2
        if nlags > max_lags:
            nlags = max_lags
            logger.warning(f"nlags adjusted to {nlags} based on data length")
        
        # Calculate ACF and PACF
        acf_values = acf(clean_series, nlags=nlags, alpha=alpha)
        pacf_values = pacf(clean_series, nlags=nlags, alpha=alpha)
        
        # Extract confidence intervals
        acf_confint = None
        pacf_confint = None
        
        if len(acf_values) > 1 and isinstance(acf_values[1], tuple):
            # Extract confidence intervals if present
            acf_main = np.array([x[0] for x in acf_values])
            acf_confint = np.array([(x[1][0], x[1][1]) for x in acf_values])
            acf_values = acf_main
        
        if len(pacf_values) > 1 and isinstance(pacf_values[1], tuple):
            # Extract confidence intervals if present
            pacf_main = np.array([x[0] for x in pacf_values])
            pacf_confint = np.array([(x[1][0], x[1][1]) for x in pacf_values])
            pacf_values = pacf_main
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[
                "Autocorrelation Function (ACF)",
                "Partial Autocorrelation Function (PACF)"
            ]
        )
        
        # Add ACF plot
        fig.add_trace(
            go.Scatter(
                x=list(range(len(acf_values))),
                y=acf_values,
                mode='lines+markers',
                name='ACF'
            ),
            row=1, col=1
        )
        
        # Add PACF plot
        fig.add_trace(
            go.Scatter(
                x=list(range(len(pacf_values))),
                y=pacf_values,
                mode='lines+markers',
                name='PACF'
            ),
            row=2, col=1
        )
        
        # Add confidence intervals if available
        if acf_confint is not None:
            # Add confidence interval for ACF
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(acf_confint))),
                    y=acf_confint[:, 0],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(acf_confint))),
                    y=acf_confint[:, 1],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(68, 68, 68, 0.2)',
                    name=f'{int((1-alpha)*100)}% Confidence Interval'
                ),
                row=1, col=1
            )
        
        if pacf_confint is not None:
            # Add confidence interval for PACF
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(pacf_confint))),
                    y=pacf_confint[:, 0],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(pacf_confint))),
                    y=pacf_confint[:, 1],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(68, 68, 68, 0.2)',
                    name=f'{int((1-alpha)*100)}% Confidence Interval'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=600,
            title="ACF and PACF Analysis",
            showlegend=True
        )
        
        # Add zero lines
        fig.add_shape(
            type="line",
            x0=0,
            x1=nlags,
            y0=0,
            y1=0,
            line=dict(color="black", dash="dash"),
            row=1, col=1
        )
        fig.add_shape(
            type="line",
            x0=0,
            x1=nlags,
            y0=0,
            y1=0,
            line=dict(color="black", dash="dash"),
            row=2, col=1
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        # Prepare result
        result = {
            'acf': acf_values.tolist(),
            'pacf': pacf_values.tolist(),
            'nlags': nlags,
            'alpha': alpha,
            'visualization': plot_json,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add confidence intervals if available
        if acf_confint is not None:
            result['acf_confint'] = acf_confint.tolist()
        if pacf_confint is not None:
            result['pacf_confint'] = pacf_confint.tolist()
        
        return result
    
    @safe_operation
    def forecast_arima(self, 
                     series: pd.Series, 
                     order: Tuple[int, int, int] = (1, 1, 1),
                     seasonal_order: Optional[Tuple[int, int, int, int]] = None,
                     steps: int = 10) -> Dict[str, Any]:
        """
        Forecast time series using ARIMA or SARIMA model.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            order: ARIMA order (p, d, q)
            seasonal_order: Seasonal ARIMA order (P, D, Q, s)
            steps: Number of steps to forecast
            
        Returns:
            Dictionary with forecast results and visualization data
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Create model
        if seasonal_order:
            model = ARIMA(
                clean_series,
                order=order,
                seasonal_order=seasonal_order
            )
            model_type = "SARIMA"
            model_str = f"SARIMA{order}{seasonal_order}"
        else:
            model = ARIMA(
                clean_series,
                order=order
            )
            model_type = "ARIMA"
            model_str = f"ARIMA{order}"
        
        # Fit model
        results = model.fit()
        
        # Generate forecast
        forecast = results.forecast(steps=steps)
        
        # Create prediction intervals
        pred_intervals = results.get_forecast(steps=steps).conf_int()
        lower_bound = pred_intervals.iloc[:, 0]
        upper_bound = pred_intervals.iloc[:, 1]
        
        # Create visualization
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(
            go.Scatter(
                x=clean_series.index,
                y=clean_series.values,
                mode='lines',
                name='Historical Data'
            )
        )
        
        # Add forecast
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=forecast.values,
                mode='lines',
                name='Forecast',
                line=dict(dash='dash')
            )
        )
        
        # Add prediction intervals
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=upper_bound.values,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=lower_bound.values,
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(68, 68, 68, 0.2)',
                name='95% Confidence Interval'
            )
        )
        
        # Update layout
        fig.update_layout(
            title=f"{model_str} Forecast",
            xaxis_title="Date",
            yaxis_title="Value",
            legend_title="Legend"
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        # Prepare result
        result = {
            'forecast': forecast.to_dict(),
            'lower_bound': lower_bound.to_dict(),
            'upper_bound': upper_bound.to_dict(),
            'model_type': model_type,
            'order': order,
            'seasonal_order': seasonal_order,
            'steps': steps,
            'aic': float(results.aic),
            'bic': float(results.bic),
            'visualization': plot_json,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add residual statistics
        residuals = results.resid
        result['residuals'] = {
            'mean': float(residuals.mean()),
            'std': float(residuals.std()),
            'min': float(residuals.min()),
            'max': float(residuals.max())
        }
        
        return result
    
    @safe_operation
    def forecast_exponential_smoothing(self, 
                                     series: pd.Series,
                                     trend: Optional[str] = None,
                                     seasonal: Optional[str] = None,
                                     seasonal_periods: Optional[int] = None,
                                     steps: int = 10) -> Dict[str, Any]:
        """
        Forecast time series using Exponential Smoothing (Holt-Winters).
        
        Args:
            series: Time series data as Pandas Series with datetime index
            trend: Trend component type (None, 'add', or 'mul')
            seasonal: Seasonal component type (None, 'add', or 'mul')
            seasonal_periods: Number of periods in a complete seasonal cycle
            steps: Number of steps to forecast
            
        Returns:
            Dictionary with forecast results and visualization data
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Determine seasonal periods if not provided
        if seasonal and not seasonal_periods:
            if hasattr(clean_series.index, 'freq'):
                if clean_series.index.freq == 'M':
                    seasonal_periods = 12  # Monthly data
                elif clean_series.index.freq == 'D':
                    seasonal_periods = 7   # Daily data (assume weekly seasonality)
                elif clean_series.index.freq == 'Q':
                    seasonal_periods = 4   # Quarterly data
                elif clean_series.index.freq == 'H':
                    seasonal_periods = 24  # Hourly data
                else:
                    # Default to 12 for unknown frequencies
                    seasonal_periods = 12
            else:
                # Try to infer from data
                if len(clean_series) < 24:
                    seasonal_periods = len(clean_series) // 2
                else:
                    seasonal_periods = 12  # Default to 12
        
        # Create and fit model
        model = ExponentialSmoothing(
            clean_series,
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=seasonal_periods
        )
        results = model.fit()
        
        # Generate forecast
        forecast = results.forecast(steps)
        
        # Create forecast dates
        if hasattr(clean_series.index, 'freq'):
            forecast_dates = pd.date_range(
                start=clean_series.index[-1] + clean_series.index.freq,
                periods=steps,
                freq=clean_series.index.freq
            )
            forecast = pd.Series(forecast, index=forecast_dates)
        
        # Create visualization
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(
            go.Scatter(
                x=clean_series.index,
                y=clean_series.values,
                mode='lines',
                name='Historical Data'
            )
        )
        
        # Add forecast
        fig.add_trace(
            go.Scatter(
                x=forecast.index if hasattr(forecast, 'index') else range(len(clean_series), len(clean_series) + steps),
                y=forecast.values if hasattr(forecast, 'values') else forecast,
                mode='lines',
                name='Forecast',
                line=dict(dash='dash')
            )
        )
        
        # Update layout
        model_name = "Exponential Smoothing"
        if trend:
            model_name += f" with {trend} trend"
        if seasonal:
            model_name += f" and {seasonal} seasonality"
        
        fig.update_layout(
            title=f"{model_name} Forecast",
            xaxis_title="Date",
            yaxis_title="Value",
            legend_title="Legend"
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        # Prepare result
        if hasattr(forecast, 'to_dict'):
            forecast_dict = forecast.to_dict()
        else:
            forecast_dict = {i: v for i, v in enumerate(forecast)}
            
        result = {
            'forecast': forecast_dict,
            'model_type': 'Exponential Smoothing',
            'trend': trend,
            'seasonal': seasonal,
            'seasonal_periods': seasonal_periods,
            'steps': steps,
            'visualization': plot_json,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add model parameters
        result['model_params'] = {
            'smoothing_level': float(results.params['smoothing_level']),
            'initial_level': float(results.params['initial_level'])
        }
        
        if trend:
            result['model_params']['smoothing_trend'] = float(results.params['smoothing_trend'])
            result['model_params']['initial_trend'] = float(results.params['initial_trend'])
            
        if seasonal:
            result['model_params']['smoothing_seasonal'] = float(results.params['smoothing_seasonal'])
            
        return result
    
    @safe_operation
    def get_time_series_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate basic time series statistics.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            
        Returns:
            Dictionary with statistics
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Calculate basic statistics
        stats = clean_series.describe().to_dict()
        
        # Add additional time series specific statistics
        stats['start_date'] = clean_series.index.min().isoformat() if hasattr(clean_series.index[0], 'isoformat') else str(clean_series.index.min())
        stats['end_date'] = clean_series.index.max().isoformat() if hasattr(clean_series.index[-1], 'isoformat') else str(clean_series.index.max())
        stats['length'] = len(clean_series)
        stats['missing_values'] = (len(series) - len(clean_series))
        stats['missing_percentage'] = (len(series) - len(clean_series)) / len(series) * 100 if len(series) > 0 else 0
        
        # Calculate frequency statistics if datetime index
        if hasattr(clean_series.index, 'freq') and clean_series.index.freq:
            stats['frequency'] = clean_series.index.freq.name
        elif pd.api.types.is_datetime64_any_dtype(clean_series.index):
            # Try to infer frequency
            try:
                diff = pd.Series(clean_series.index).diff().value_counts()
                most_common_diff = diff.index[0]
                stats['most_common_diff'] = most_common_diff.days if hasattr(most_common_diff, 'days') else most_common_diff
                stats['most_common_diff_unit'] = 'days' if hasattr(most_common_diff, 'days') else 'ns'
                stats['frequency_consistency'] = (diff.iloc[0] / diff.sum()) * 100
            except:
                stats['frequency'] = 'irregular'
        
        # Create trend analysis
        try:
            # Simple linear trend
            x = np.arange(len(clean_series))
            coeffs = np.polyfit(x, clean_series.values, 1)
            slope = coeffs[0]
            
            stats['trend'] = {
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'slope': float(slope),
                'slope_percentage': float(slope / clean_series.mean() * 100)
            }
        except:
            pass
        
        # Check stationarity
        try:
            stationarity = self.check_stationarity(clean_series)
            stats['stationarity'] = {
                'is_stationary': stationarity['is_stationary'],
                'p_value': stationarity['p_value'],
                'test_statistic': stationarity['test_statistic']
            }
        except:
            pass
        
        return stats
    
    @safe_operation
    def create_time_series_plot(self, 
                              series: pd.Series,
                              plot_type: str = 'line',
                              title: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a time series visualization.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            plot_type: Type of plot ('line', 'area', or 'bar')
            title: Plot title
            
        Returns:
            Dictionary with visualization data
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Drop any missing values
        clean_series = series.dropna()
        
        # Set default title if not provided
        if title is None:
            title = "Time Series Plot"
        
        # Create figure based on plot type
        if plot_type == 'line':
            fig = px.line(
                x=clean_series.index,
                y=clean_series.values,
                title=title
            )
        elif plot_type == 'area':
            fig = px.area(
                x=clean_series.index,
                y=clean_series.values,
                title=title
            )
        elif plot_type == 'bar':
            fig = px.bar(
                x=clean_series.index,
                y=clean_series.values,
                title=title
            )
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
        
        # Update layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Value"
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        return {
            'visualization': plot_json,
            'plot_type': plot_type,
            'title': title,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }
    
    @safe_operation
    def aggregate_time_series(self, 
                            series: pd.Series,
                            freq: str,
                            agg_func: str = 'mean') -> Dict[str, Any]:
        """
        Aggregate time series to a different frequency.
        
        Args:
            series: Time series data as Pandas Series with datetime index
            freq: Target frequency (e.g., 'D', 'W', 'M', 'Q', 'Y')
            agg_func: Aggregation function ('mean', 'sum', 'min', 'max', 'first', 'last')
            
        Returns:
            Dictionary with aggregated time series and visualization
        """
        # Check input
        if not isinstance(series, pd.Series):
            raise ValueError("Input must be a pandas Series")
        
        # Validate frequency
        valid_freqs = ['D', 'W', 'M', 'Q', 'Y', 'H', 'T', 'S']
        if freq not in valid_freqs:
            raise ValueError(f"Invalid frequency: {freq}. Must be one of {valid_freqs}")
        
        # Validate aggregation function
        valid_funcs = ['mean', 'sum', 'min', 'max', 'first', 'last', 'median']
        if agg_func not in valid_funcs:
            raise ValueError(f"Invalid aggregation function: {agg_func}. Must be one of {valid_funcs}")
        
        # Ensure index is datetime
        if not pd.api.types.is_datetime64_any_dtype(series.index):
            raise ValueError("Series index must be datetime for aggregation")
        
        # Perform aggregation
        resampler = series.resample(freq)
        
        if agg_func == 'mean':
            result = resampler.mean()
        elif agg_func == 'sum':
            result = resampler.sum()
        elif agg_func == 'min':
            result = resampler.min()
        elif agg_func == 'max':
            result = resampler.max()
        elif agg_func == 'first':
            result = resampler.first()
        elif agg_func == 'last':
            result = resampler.last()
        elif agg_func == 'median':
            result = resampler.median()
        
        # Create visualization
        fig = go.Figure()
        
        # Add original series
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode='lines',
                name='Original'
            )
        )
        
        # Add aggregated series
        fig.add_trace(
            go.Scatter(
                x=result.index,
                y=result.values,
                mode='lines+markers',
                name=f'Aggregated ({agg_func})'
            )
        )
        
        # Update layout
        fig.update_layout(
            title=f"Time Series Aggregation ({freq}, {agg_func})",
            xaxis_title="Date",
            yaxis_title="Value",
            legend_title="Series"
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        return {
            'original': series.to_dict(),
            'aggregated': result.to_dict(),
            'freq': freq,
            'agg_func': agg_func,
            'visualization': plot_json,
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }

# Initialize global time series service
time_series_service = TimeSeriesService()

def get_time_series_service() -> TimeSeriesService:
    """Get the global time series service instance."""
    return time_series_service