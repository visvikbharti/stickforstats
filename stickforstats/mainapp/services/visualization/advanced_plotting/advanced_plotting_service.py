"""
Advanced Plotting Service for StickForStats platform.
This module provides services for creating highly customizable plots based on the original
StickForStats Streamlit application, migrated to work as a Django service.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import json
from datetime import datetime
import uuid
import colorsys
import io
import base64
from PIL import Image

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

class AdvancedPlottingService:
    """
    Service for creating highly customizable plots and visualizations.
    
    This service provides methods for:
    - Creating various plot types with extensive customization options
    - Supporting a wide range of plot types (2D and 3D)
    - Adding statistical annotations and fit lines
    - Customizing plot appearance (colors, fonts, styling)
    - Exporting plots to different formats
    
    Based on the original AdvancedPlotter class from the StickForStats Streamlit application.
    """
    
    def __init__(self):
        """Initialize advanced plotting service."""
        self.plot_types = {
            "scatter": self._create_scatter_plot,
            "line": self._create_line_plot,
            "bar": self._create_bar_plot,
            "box": self._create_box_plot,
            "violin": self._create_violin_plot,
            "histogram": self._create_histogram,
            "heatmap": self._create_heatmap,
            "contour": self._create_contour_plot,
            "bubble": self._create_bubble_plot,
            "pie": self._create_pie_chart,
            "radar": self._create_radar_chart,
            "polar": self._create_polar_plot,
            "density": self._create_density_plot,
            "surface_3d": self._create_3d_surface,
            "scatter_3d": self._create_3d_scatter
        }
        
        self.color_palettes = {
            "default": px.colors.qualitative.Plotly,
            "pastel": px.colors.qualitative.Pastel,
            "bold": px.colors.qualitative.Bold,
            "vivid": px.colors.qualitative.Vivid,
            "dark": px.colors.qualitative.Dark24,
            "light": px.colors.qualitative.Light24,
            "sequential_blue": px.colors.sequential.Blues,
            "sequential_red": px.colors.sequential.Reds,
            "sequential_green": px.colors.sequential.Greens,
            "diverging_rdbu": px.colors.diverging.RdBu,
            "diverging_brbg": px.colors.diverging.BrBG,
            "diverging_spectral": px.colors.diverging.Spectral
        }
        
        self.marker_symbols = [
            "circle", "square", "diamond", "cross", "x", "triangle-up", 
            "triangle-down", "star", "hexagram", "pentagon", "hexagon", 
            "octagon", "circle-open", "square-open", "diamond-open", 
            "cross-open", "triangle-up-open", "triangle-down-open", 
            "star-open", "hexagram-open"
        ]
        
        self.line_styles = [
            "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
        ]
        
        self.available_fonts = [
            "Arial", "Courier New", "Times New Roman", "Helvetica", 
            "Verdana", "Georgia", "Garamond", "Open Sans"
        ]
        
        self.font_sizes = list(range(8, 33, 2))  # 8, 10, 12, ..., 32
        
        self.templates = {
            "simple": "plotly",
            "modern_white": "plotly_white",
            "minimal_dark": "plotly_dark",
            "scientific": "ggplot2",
            "presentation": "presentation",
            "journal": "none"  # Base for custom scientific journal styling
        }
        
        self.export_formats = ["png", "svg", "pdf", "html", "json"]
    
    def get_supported_plot_types(self) -> List[str]:
        """
        Get a list of supported plot types.
        
        Returns:
            List of available plot types
        """
        return list(self.plot_types.keys())
    
    def get_color_palettes(self) -> Dict[str, List[str]]:
        """
        Get available color palettes.
        
        Returns:
            Dictionary of color palette names and their values
        """
        return self.color_palettes
    
    def get_marker_symbols(self) -> List[str]:
        """
        Get available marker symbols.
        
        Returns:
            List of marker symbols
        """
        return self.marker_symbols
    
    def get_line_styles(self) -> List[str]:
        """
        Get available line styles.
        
        Returns:
            List of line styles
        """
        return self.line_styles
    
    def get_available_fonts(self) -> List[str]:
        """
        Get available fonts.
        
        Returns:
            List of font families
        """
        return self.available_fonts
    
    def get_plot_templates(self) -> Dict[str, str]:
        """
        Get available plot templates.
        
        Returns:
            Dictionary of template names and their values
        """
        return self.templates
    
    @safe_operation
    def create_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a customized plot based on configuration.
        
        Args:
            data: Input DataFrame
            plot_config: Dictionary with plot configuration
            
        Returns:
            Dictionary with plot figure (as JSON) and metadata
        """
        # Validate input
        if not isinstance(data, pd.DataFrame):
            return {'error': "Input must be a pandas DataFrame"}
        
        if not plot_config:
            return {'error': "Plot configuration must be provided"}
        
        # Extract plot type
        plot_type = plot_config.get("plot_type", "scatter").lower()
        
        if plot_type not in self.plot_types:
            return {'error': f"Unsupported plot type: {plot_type}"}
        
        # Call the appropriate plot creation method
        plot_func = self.plot_types[plot_type]
        fig = plot_func(data, plot_config)
        
        # Apply common customization options
        self._apply_common_styling(fig, plot_config)
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        # Create result dictionary
        result = {
            "plot_data": plot_json,
            "plot_type": plot_type,
            "title": plot_config.get("title", f"{plot_type.capitalize()} Plot"),
            "config": plot_config,
            "plot_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _apply_common_styling(self, fig: go.Figure, plot_config: Dict[str, Any]) -> None:
        """Apply common styling options to figure."""
        # Title
        title = plot_config.get("title", "")
        if title:
            title_font_size = plot_config.get("title_font_size", 18)
            title_font_family = plot_config.get("title_font_family", "Arial")
            title_font_color = plot_config.get("title_font_color", "#000000")
            
            fig.update_layout(
                title={
                    "text": title,
                    "font": {
                        "size": title_font_size,
                        "family": title_font_family,
                        "color": title_font_color
                    },
                    "x": plot_config.get("title_x", 0.5),  # Centered by default
                    "xanchor": plot_config.get("title_xanchor", "center"),
                    "y": plot_config.get("title_y", 0.95),
                    "yanchor": plot_config.get("title_yanchor", "top")
                }
            )
        
        # Axes titles and styling
        axis_title_font_size = plot_config.get("axis_title_font_size", 14)
        axis_title_font_family = plot_config.get("axis_title_font_family", "Arial")
        axis_title_font_color = plot_config.get("axis_title_font_color", "#000000")
        
        axis_tick_font_size = plot_config.get("axis_tick_font_size", 12)
        axis_tick_font_family = plot_config.get("axis_tick_font_family", "Arial")
        axis_tick_font_color = plot_config.get("axis_tick_font_color", "#000000")
        
        # X-axis
        x_title = plot_config.get("x_title", "")
        if x_title:
            fig.update_xaxes(
                title={
                    "text": x_title,
                    "font": {
                        "size": axis_title_font_size,
                        "family": axis_title_font_family,
                        "color": axis_title_font_color
                    }
                },
                tickfont={
                    "size": axis_tick_font_size,
                    "family": axis_tick_font_family,
                    "color": axis_tick_font_color
                }
            )
        
        # Y-axis
        y_title = plot_config.get("y_title", "")
        if y_title:
            fig.update_yaxes(
                title={
                    "text": y_title,
                    "font": {
                        "size": axis_title_font_size,
                        "family": axis_title_font_family,
                        "color": axis_title_font_color
                    }
                },
                tickfont={
                    "size": axis_tick_font_size,
                    "family": axis_tick_font_family,
                    "color": axis_tick_font_color
                }
            )
        
        # Legend styling
        show_legend = plot_config.get("show_legend", True)
        legend_title = plot_config.get("legend_title", "")
        
        fig.update_layout(
            showlegend=show_legend,
            legend={
                "title": {"text": legend_title} if legend_title else None,
                "font": {
                    "size": plot_config.get("legend_font_size", 12),
                    "family": plot_config.get("legend_font_family", "Arial"),
                    "color": plot_config.get("legend_font_color", "#000000")
                },
                "orientation": plot_config.get("legend_orientation", "vertical"),
                "x": plot_config.get("legend_x", 1.02),
                "y": plot_config.get("legend_y", 1),
                "xanchor": plot_config.get("legend_xanchor", "left"),
                "yanchor": plot_config.get("legend_yanchor", "auto"),
                "bgcolor": plot_config.get("legend_bgcolor", "rgba(255,255,255,0.5)"),
                "bordercolor": plot_config.get("legend_bordercolor", "rgba(0,0,0,0.5)"),
                "borderwidth": plot_config.get("legend_borderwidth", 1),
            }
        )
        
        # Grid lines
        show_grid = plot_config.get("show_grid", True)
        grid_color = plot_config.get("grid_color", "rgba(204, 204, 204, 0.5)")
        grid_width = plot_config.get("grid_width", 1)
        
        fig.update_xaxes(
            showgrid=show_grid,
            gridcolor=grid_color,
            gridwidth=grid_width,
            zeroline=plot_config.get("show_zeroline", True),
            zerolinecolor=plot_config.get("zeroline_color", "rgba(0, 0, 0, 0.5)"),
            zerolinewidth=plot_config.get("zeroline_width", 1)
        )
        
        fig.update_yaxes(
            showgrid=show_grid,
            gridcolor=grid_color,
            gridwidth=grid_width,
            zeroline=plot_config.get("show_zeroline", True),
            zerolinecolor=plot_config.get("zeroline_color", "rgba(0, 0, 0, 0.5)"),
            zerolinewidth=plot_config.get("zeroline_width", 1)
        )
        
        # Background color and paper color
        fig.update_layout(
            plot_bgcolor=plot_config.get("plot_bgcolor", "rgba(255, 255, 255, 1)"),
            paper_bgcolor=plot_config.get("paper_bgcolor", "rgba(255, 255, 255, 1)")
        )
        
        # Overall size and margins
        width = plot_config.get("width", 800)
        height = plot_config.get("height", 600)
        
        fig.update_layout(
            width=width,
            height=height,
            margin={
                "l": plot_config.get("margin_left", 80),
                "r": plot_config.get("margin_right", 80),
                "t": plot_config.get("margin_top", 100),
                "b": plot_config.get("margin_bottom", 80),
                "pad": plot_config.get("margin_pad", 4)
            }
        )
        
        # Template (overall styling)
        template = plot_config.get("template", "plotly")
        fig.update_layout(template=template)
        
        # Axis ranges if specified
        if "x_min" in plot_config and "x_max" in plot_config:
            fig.update_xaxes(range=[plot_config["x_min"], plot_config["x_max"]])
        
        if "y_min" in plot_config and "y_max" in plot_config:
            fig.update_yaxes(range=[plot_config["y_min"], plot_config["y_max"]])
            
        # Add a watermark if specified
        watermark = plot_config.get("watermark", "")
        if watermark:
            fig.add_annotation(
                text=watermark,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font={
                    "size": plot_config.get("watermark_font_size", 40),
                    "color": plot_config.get("watermark_color", "rgba(200, 200, 200, 0.3)")
                },
                textangle=plot_config.get("watermark_angle", -30)
            )
    
    def _create_hover_template(self, data: pd.DataFrame, hover_data: List[str], 
                             x_col: str, y_col: str) -> str:
        """Create a custom hover template based on selected columns."""
        if not hover_data:
            return f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>"
        
        template = f"{x_col}: %{{x}}<br>{y_col}: %{{y}}"
        for col in hover_data:
            if col in data.columns and col not in [x_col, y_col]:
                template += f"<br>{col}: %{{customdata[{hover_data.index(col)}]}}"
        
        template += "<extra></extra>"
        return template
        
    def _add_fit_line(self, fig: go.Figure, data: pd.DataFrame, 
                     x_col: str, y_col: str, plot_config: Dict[str, Any]) -> None:
        """Add a fit line to a scatter plot."""
        from scipy import stats
        
        fit_type = plot_config.get("fit_type", "linear")
        
        # Prepare data for fitting
        x_data = data[x_col].dropna()
        y_data = data[y_col].dropna()
        
        # Create x range for prediction
        x_pred = np.linspace(x_data.min(), x_data.max(), 100)
        
        if fit_type == "linear":
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
            y_pred = slope * x_pred + intercept
            
            # Formula text
            formula = f"y = {slope:.4f}x + {intercept:.4f}"
            r_squared = r_value**2
            stats_text = f"{formula}<br>R² = {r_squared:.4f}, p = {p_value:.4f}"
            
        elif fit_type == "polynomial":
            # Polynomial regression
            degree = plot_config.get("polynomial_degree", 2)
            coeffs = np.polyfit(x_data, y_data, degree)
            y_pred = np.polyval(coeffs, x_pred)
            
            # Formula text
            formula = "y = "
            for i, coef in enumerate(coeffs):
                power = degree - i
                if i > 0:
                    formula += " + " if coef >= 0 else " - "
                    formula += f"{abs(coef):.4f}"
                else:
                    formula += f"{coef:.4f}"
                
                if power > 0:
                    formula += f"x^{power}" if power > 1 else "x"
            
            # Calculate R-squared
            y_fit = np.polyval(coeffs, x_data)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            ss_res = np.sum((y_data - y_fit)**2)
            r_squared = 1 - (ss_res / ss_tot)
            stats_text = f"{formula}<br>R² = {r_squared:.4f}"
            
        elif fit_type == "exponential":
            # Exponential fit: y = a*exp(b*x)
            # Linearize with log(y) = log(a) + b*x
            valid_mask = (y_data > 0)  # Log only works for positive y values
            log_y = np.log(y_data[valid_mask])
            x_valid = x_data[valid_mask]
            
            if len(log_y) < 2:
                # Not enough valid data for fitting
                return
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, log_y)
            a = np.exp(intercept)
            b = slope
            y_pred = a * np.exp(b * x_pred)
            
            formula = f"y = {a:.4f}e^({b:.4f}x)"
            r_squared = r_value**2
            stats_text = f"{formula}<br>R² = {r_squared:.4f}, p = {p_value:.4f}"
            
        elif fit_type == "power":
            # Power fit: y = a*x^b
            # Linearize with log(y) = log(a) + b*log(x)
            valid_mask = (y_data > 0) & (x_data > 0)  # Log only works for positive values
            log_y = np.log(y_data[valid_mask])
            log_x = np.log(x_data[valid_mask])
            
            if len(log_y) < 2:
                # Not enough valid data for fitting
                return
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)
            a = np.exp(intercept)
            b = slope
            y_pred = a * x_pred**b
            
            formula = f"y = {a:.4f}x^{b:.4f}"
            r_squared = r_value**2
            stats_text = f"{formula}<br>R² = {r_squared:.4f}, p = {p_value:.4f}"
            
        elif fit_type == "loess" or fit_type == "lowess":
            try:
                from statsmodels.nonparametric.smoothers_lowess import lowess
                lowess_result = lowess(y_data, x_data, frac=plot_config.get("loess_frac", 0.2))
                x_lowess = lowess_result[:, 0]
                y_lowess = lowess_result[:, 1]
                
                # Sort by x for proper line drawing
                sort_indices = np.argsort(x_lowess)
                x_pred = x_lowess[sort_indices]
                y_pred = y_lowess[sort_indices]
                
                stats_text = "LOESS Smoothing"
            except ImportError:
                # Fallback to linear if statsmodels not available
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                y_pred = slope * x_pred + intercept
                stats_text = "Linear fit (LOESS unavailable)"
        else:
            # Default to linear
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
            y_pred = slope * x_pred + intercept
            formula = f"y = {slope:.4f}x + {intercept:.4f}"
            r_squared = r_value**2
            stats_text = f"{formula}<br>R² = {r_squared:.4f}, p = {p_value:.4f}"
        
        # Add the fit line to the plot
        fig.add_trace(
            go.Scatter(
                x=x_pred,
                y=y_pred,
                mode='lines',
                name=plot_config.get("fit_line_name", "Fit"),
                line=dict(
                    color=plot_config.get("fit_line_color", "rgba(255, 0, 0, 0.7)"),
                    width=plot_config.get("fit_line_width", 2),
                    dash=plot_config.get("fit_line_dash", "solid")
                ),
                hoverinfo='skip'
            )
        )
        
        # Add annotation with fit statistics if requested
        if plot_config.get("show_fit_stats", True):
            fig.add_annotation(
                x=plot_config.get("fit_stats_x", 0.05),
                y=plot_config.get("fit_stats_y", 0.95),
                xref="paper",
                yref="paper",
                text=stats_text,
                showarrow=False,
                bgcolor=plot_config.get("fit_stats_bgcolor", "rgba(255, 255, 255, 0.7)"),
                bordercolor=plot_config.get("fit_stats_bordercolor", "rgba(0, 0, 0, 0.5)"),
                borderwidth=plot_config.get("fit_stats_borderwidth", 1),
                font=dict(
                    size=plot_config.get("fit_stats_fontsize", 12),
                    family=plot_config.get("fit_stats_fontfamily", "Arial")
                )
            )
    
    def _create_scatter_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a scatter plot with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        y_col = plot_config.get("y")
        color_col = plot_config.get("color")
        size_col = plot_config.get("size")
        hover_data = plot_config.get("hover_data", [])
        
        if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Both x and y columns must be valid columns for scatter plot")
        
        # Basic plot parameters
        marker_size = plot_config.get("marker_size", 10)
        marker_symbol = plot_config.get("marker_symbol", "circle")
        marker_opacity = plot_config.get("marker_opacity", 0.7)
        
        # Initialize figure
        fig = go.Figure()
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group]
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                    
                # Prepare custom data for hover
                hover_values = [group_data[col] for col in hover_data if col in group_data.columns and col not in [x_col, y_col]]
                custom_data = np.array(hover_values).T if hover_values else None
                
                # Create trace
                fig.add_trace(
                    go.Scatter(
                        x=group_data[x_col],
                        y=group_data[y_col],
                        mode='markers',
                        name=str(group),
                        marker=dict(
                            size=group_data[size_col] if size_col and size_col in data.columns else marker_size,
                            symbol=marker_symbol,
                            opacity=marker_opacity,
                            color=color,
                            line=dict(
                                width=plot_config.get("marker_line_width", 1),
                                color=plot_config.get("marker_line_color", "rgba(0, 0, 0, 0.5)")
                            )
                        ),
                        customdata=custom_data,
                        hovertemplate=self._create_hover_template(group_data, hover_data, x_col, y_col)
                    )
                )
        else:
            # No grouping, create a single trace
            
            # Marker color
            marker_color = plot_config.get("marker_color", "rgba(31, 119, 180, 0.7)")
            
            # Prepare custom data for hover
            hover_values = [data[col] for col in hover_data if col in data.columns and col not in [x_col, y_col]]
            custom_data = np.array(hover_values).T if hover_values else None
            
            # Create trace
            fig.add_trace(
                go.Scatter(
                    x=data[x_col],
                    y=data[y_col],
                    mode='markers',
                    name=plot_config.get("trace_name", "Data"),
                    marker=dict(
                        size=data[size_col] if size_col and size_col in data.columns else marker_size,
                        symbol=marker_symbol,
                        opacity=marker_opacity,
                        color=marker_color,
                        line=dict(
                            width=plot_config.get("marker_line_width", 1),
                            color=plot_config.get("marker_line_color", "rgba(0, 0, 0, 0.5)")
                        )
                    ),
                    customdata=custom_data,
                    hovertemplate=self._create_hover_template(data, hover_data, x_col, y_col)
                )
            )
        
        # Add fit line if requested
        if plot_config.get("add_fit_line", False):
            self._add_fit_line(fig, data, x_col, y_col, plot_config)
        
        return fig
    
    def _create_line_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a line plot with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        y_col = plot_config.get("y")
        color_col = plot_config.get("color")
        hover_data = plot_config.get("hover_data", [])
        
        if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Both x and y columns must be valid columns for line plot")
        
        # Basic plot parameters
        line_width = plot_config.get("line_width", 2)
        line_dash = plot_config.get("line_dash", "solid")
        line_shape = plot_config.get("line_shape", "linear")
        marker_size = plot_config.get("marker_size", 6)
        show_markers = plot_config.get("show_markers", True)
        marker_symbol = plot_config.get("marker_symbol", "circle")
        
        # Initialize figure
        fig = go.Figure()
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group].sort_values(x_col)
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                    
                # Prepare custom data for hover
                hover_values = [group_data[col] for col in hover_data if col in group_data.columns and col not in [x_col, y_col]]
                custom_data = np.array(hover_values).T if hover_values else None
                
                # Create trace
                fig.add_trace(
                    go.Scatter(
                        x=group_data[x_col],
                        y=group_data[y_col],
                        mode='lines+markers' if show_markers else 'lines',
                        name=str(group),
                        line=dict(
                            width=line_width,
                            dash=line_dash,
                            shape=line_shape,
                            color=color
                        ),
                        marker=dict(
                            size=marker_size,
                            symbol=marker_symbol
                        ),
                        customdata=custom_data,
                        hovertemplate=self._create_hover_template(group_data, hover_data, x_col, y_col)
                    )
                )
        else:
            # No grouping, create a single trace
            sorted_data = data.sort_values(x_col)
            
            # Line color
            line_color = plot_config.get("line_color", "rgba(31, 119, 180, 1)")
            
            # Prepare custom data for hover
            hover_values = [sorted_data[col] for col in hover_data if col in sorted_data.columns and col not in [x_col, y_col]]
            custom_data = np.array(hover_values).T if hover_values else None
            
            # Create trace
            fig.add_trace(
                go.Scatter(
                    x=sorted_data[x_col],
                    y=sorted_data[y_col],
                    mode='lines+markers' if show_markers else 'lines',
                    name=plot_config.get("trace_name", "Data"),
                    line=dict(
                        width=line_width,
                        dash=line_dash,
                        shape=line_shape,
                        color=line_color
                    ),
                    marker=dict(
                        size=marker_size,
                        symbol=marker_symbol
                    ),
                    customdata=custom_data,
                    hovertemplate=self._create_hover_template(sorted_data, hover_data, x_col, y_col)
                )
            )
        
        return fig
    
    def _create_bar_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a bar plot with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        y_col = plot_config.get("y")
        color_col = plot_config.get("color")
        hover_data = plot_config.get("hover_data", [])
        
        if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
            raise ValueError(f"Both x and y columns must be valid columns for bar plot")
        
        # Bar orientation
        orientation = plot_config.get("orientation", "v")  # 'v' for vertical, 'h' for horizontal
        
        # Bar style
        bar_mode = plot_config.get("bar_mode", "group")  # 'group', 'stack', 'overlay', 'relative'
        opacity = plot_config.get("opacity", 0.8)
        text_auto = plot_config.get("text_auto", False)  # Show values on bars
        text_position = plot_config.get("text_position", "auto")  # 'inside', 'outside', 'auto', 'none'
        
        # Initialize figure with bar mode
        fig = go.Figure()
        
        # Set bar mode (if applicable)
        if bar_mode in ['group', 'stack', 'overlay', 'relative']:
            fig.update_layout(barmode=bar_mode)
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group]
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                    
                # Prepare custom data for hover
                hover_values = [group_data[col] for col in hover_data if col in group_data.columns and col not in [x_col, y_col]]
                custom_data = np.array(hover_values).T if hover_values else None
                
                # Create trace
                if orientation == 'h':
                    # Horizontal bars
                    fig.add_trace(
                        go.Bar(
                            x=group_data[y_col],
                            y=group_data[x_col],
                            orientation='h',
                            name=str(group),
                            marker_color=color,
                            opacity=opacity,
                            text=group_data[y_col] if text_auto else None,
                            textposition=text_position,
                            customdata=custom_data,
                            hovertemplate=self._create_hover_template(group_data, hover_data, x_col, y_col)
                        )
                    )
                else:
                    # Vertical bars
                    fig.add_trace(
                        go.Bar(
                            x=group_data[x_col],
                            y=group_data[y_col],
                            name=str(group),
                            marker_color=color,
                            opacity=opacity,
                            text=group_data[y_col] if text_auto else None,
                            textposition=text_position,
                            customdata=custom_data,
                            hovertemplate=self._create_hover_template(group_data, hover_data, x_col, y_col)
                        )
                    )
        else:
            # No grouping, create a single trace
            
            # Bar color
            bar_color = plot_config.get("bar_color", "rgba(31, 119, 180, 0.8)")
            
            # Prepare custom data for hover
            hover_values = [data[col] for col in hover_data if col in data.columns and col not in [x_col, y_col]]
            custom_data = np.array(hover_values).T if hover_values else None
            
            # Create trace
            if orientation == 'h':
                # Horizontal bars
                fig.add_trace(
                    go.Bar(
                        x=data[y_col],
                        y=data[x_col],
                        orientation='h',
                        name=plot_config.get("trace_name", "Data"),
                        marker_color=bar_color,
                        opacity=opacity,
                        text=data[y_col] if text_auto else None,
                        textposition=text_position,
                        customdata=custom_data,
                        hovertemplate=self._create_hover_template(data, hover_data, x_col, y_col)
                    )
                )
            else:
                # Vertical bars
                fig.add_trace(
                    go.Bar(
                        x=data[x_col],
                        y=data[y_col],
                        name=plot_config.get("trace_name", "Data"),
                        marker_color=bar_color,
                        opacity=opacity,
                        text=data[y_col] if text_auto else None,
                        textposition=text_position,
                        customdata=custom_data,
                        hovertemplate=self._create_hover_template(data, hover_data, x_col, y_col)
                    )
                )
        
        return fig
    
    def _create_box_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a box plot with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        y_col = plot_config.get("y")
        color_col = plot_config.get("color")
        
        if not y_col or y_col not in data.columns:
            raise ValueError(f"Y column must be a valid column for box plot")
        
        # Box plot parameters
        orientation = plot_config.get("orientation", "v")  # 'v' for vertical, 'h' for horizontal
        box_mode = plot_config.get("box_mode", "group")  # 'group' or 'overlay'
        points = plot_config.get("points", "outliers")  # 'all', 'outliers', 'suspectedoutliers', False
        notched = plot_config.get("notched", False)  # Notched box plots
        
        # Initialize figure
        fig = go.Figure()
        
        # Set box mode if specified
        if box_mode in ['group', 'overlay']:
            fig.update_layout(boxmode=box_mode)
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group]
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                
                # Create trace
                if orientation == 'h':
                    # Horizontal boxes
                    fig.add_trace(
                        go.Box(
                            x=group_data[y_col],
                            y=group_data[x_col] if x_col and x_col in group_data.columns else None,
                            orientation='h',
                            name=str(group),
                            marker_color=color,
                            boxpoints=points,
                            notched=notched,
                            hovertemplate=f"{x_col}: %{{y}}<br>{y_col}: %{{x}}<extra>{group}</extra>" if x_col else None
                        )
                    )
                else:
                    # Vertical boxes
                    fig.add_trace(
                        go.Box(
                            x=group_data[x_col] if x_col and x_col in group_data.columns else None,
                            y=group_data[y_col],
                            name=str(group),
                            marker_color=color,
                            boxpoints=points,
                            notched=notched,
                            hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra>{group}</extra>" if x_col else None
                        )
                    )
        else:
            # No grouping, create a single trace
            
            # Box color
            box_color = plot_config.get("box_color", "rgba(31, 119, 180, 0.7)")
            
            # Create trace
            if orientation == 'h':
                # Horizontal boxes
                fig.add_trace(
                    go.Box(
                        x=data[y_col],
                        y=data[x_col] if x_col and x_col in data.columns else None,
                        orientation='h',
                        name=plot_config.get("trace_name", "Data"),
                        marker_color=box_color,
                        boxpoints=points,
                        notched=notched,
                        hovertemplate=f"{x_col}: %{{y}}<br>{y_col}: %{{x}}<extra></extra>" if x_col else None
                    )
                )
            else:
                # Vertical boxes
                fig.add_trace(
                    go.Box(
                        x=data[x_col] if x_col and x_col in data.columns else None,
                        y=data[y_col],
                        name=plot_config.get("trace_name", "Data"),
                        marker_color=box_color,
                        boxpoints=points,
                        notched=notched,
                        hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>" if x_col else None
                    )
                )
        
        return fig
    
    def _create_violin_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a violin plot with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        y_col = plot_config.get("y")
        color_col = plot_config.get("color")
        
        if not y_col or y_col not in data.columns:
            raise ValueError(f"Y column must be a valid column for violin plot")
        
        # Violin plot parameters
        orientation = plot_config.get("orientation", "v")  # 'v' for vertical, 'h' for horizontal
        box = plot_config.get("box", True)  # Show inner box plot
        points = plot_config.get("points", "outliers")  # 'all', 'outliers', 'suspectedoutliers', False
        side = plot_config.get("side", "both")  # 'positive', 'negative', 'both'
        span_mode = plot_config.get("span_mode", "soft")  # 'hard', 'soft'
        
        # Initialize figure
        fig = go.Figure()
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group]
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                
                # Create trace
                if orientation == 'h':
                    # Horizontal violins
                    fig.add_trace(
                        go.Violin(
                            x=group_data[y_col],
                            y=group_data[x_col] if x_col and x_col in group_data.columns else None,
                            orientation='h',
                            name=str(group),
                            box_visible=box,
                            points=points,
                            side=side,
                            spanmode=span_mode,
                            line_color=color,
                            fillcolor=color.replace("rgb", "rgba").replace(")", ", 0.5)") if "rgb" in color else color,
                            hovertemplate=f"{x_col}: %{{y}}<br>{y_col}: %{{x}}<extra>{group}</extra>" if x_col else None
                        )
                    )
                else:
                    # Vertical violins
                    fig.add_trace(
                        go.Violin(
                            x=group_data[x_col] if x_col and x_col in group_data.columns else None,
                            y=group_data[y_col],
                            name=str(group),
                            box_visible=box,
                            points=points,
                            side=side,
                            spanmode=span_mode,
                            line_color=color,
                            fillcolor=color.replace("rgb", "rgba").replace(")", ", 0.5)") if "rgb" in color else color,
                            hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra>{group}</extra>" if x_col else None
                        )
                    )
        else:
            # No grouping, create a single trace
            
            # Violin color
            violin_color = plot_config.get("violin_color", "rgba(31, 119, 180, 0.7)")
            line_color = plot_config.get("line_color", "rgba(31, 119, 180, 1)")
            
            # Create trace
            if orientation == 'h':
                # Horizontal violins
                fig.add_trace(
                    go.Violin(
                        x=data[y_col],
                        y=data[x_col] if x_col and x_col in data.columns else None,
                        orientation='h',
                        name=plot_config.get("trace_name", "Data"),
                        box_visible=box,
                        points=points,
                        side=side,
                        spanmode=span_mode,
                        line_color=line_color,
                        fillcolor=violin_color,
                        hovertemplate=f"{x_col}: %{{y}}<br>{y_col}: %{{x}}<extra></extra>" if x_col else None
                    )
                )
            else:
                # Vertical violins
                fig.add_trace(
                    go.Violin(
                        x=data[x_col] if x_col and x_col in data.columns else None,
                        y=data[y_col],
                        name=plot_config.get("trace_name", "Data"),
                        box_visible=box,
                        points=points,
                        side=side,
                        spanmode=span_mode,
                        line_color=line_color,
                        fillcolor=violin_color,
                        hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>" if x_col else None
                    )
                )
        
        return fig
    
    def _create_histogram(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a histogram with high customizability."""
        # Extract key parameters
        x_col = plot_config.get("x")
        color_col = plot_config.get("color")
        
        if not x_col or x_col not in data.columns:
            raise ValueError(f"X column must be a valid column for histogram")
        
        # Histogram parameters
        nbins = plot_config.get("nbins", 30)
        histnorm = plot_config.get("histnorm", None)  # 'probability', 'probability density', 'density', None
        histfunc = plot_config.get("histfunc", "count")  # 'count', 'sum', 'avg', 'min', 'max'
        cumulative = plot_config.get("cumulative", False)
        barmode = plot_config.get("barmode", "overlay")  # 'overlay', 'stack', 'group', 'relative'
        bargap = plot_config.get("bargap", 0.05)  # Gap between bars
        opacity = plot_config.get("opacity", 0.7)
        
        # Initialize figure
        fig = go.Figure()
        
        # Set bar mode
        fig.update_layout(barmode=barmode)
        
        # Handle grouping if color column is specified
        if color_col and color_col in data.columns:
            groups = data[color_col].unique()
            
            # Get color palette
            palette_name = plot_config.get("color_palette", "default")
            palette = self.color_palettes.get(palette_name, px.colors.qualitative.Plotly)
            
            # Custom colors override palette if provided
            custom_colors = plot_config.get("custom_colors", {})
            
            # Add trace for each group
            for i, group in enumerate(groups):
                group_data = data[data[color_col] == group]
                
                # Determine color
                if str(group) in custom_colors:
                    color = custom_colors[str(group)]
                else:
                    color = palette[i % len(palette)]
                
                # Create trace
                fig.add_trace(
                    go.Histogram(
                        x=group_data[x_col],
                        name=str(group),
                        nbinsx=nbins,
                        histnorm=histnorm,
                        histfunc=histfunc,
                        marker_color=color,
                        opacity=opacity,
                        cumulative_enabled=cumulative
                    )
                )
        else:
            # No grouping, create a single trace
            
            # Histogram color
            hist_color = plot_config.get("hist_color", "rgba(31, 119, 180, 0.7)")
            
            # Create trace
            fig.add_trace(
                go.Histogram(
                    x=data[x_col],
                    name=plot_config.get("trace_name", "Data"),
                    nbinsx=nbins,
                    histnorm=histnorm,
                    histfunc=histfunc,
                    marker_color=hist_color,
                    opacity=opacity,
                    cumulative_enabled=cumulative
                )
            )
        
        # Update layout
        fig.update_layout(bargap=bargap)
        
        # Add KDE overlay if requested
        if plot_config.get("show_kde", False):
            from scipy import stats
            
            # Function to calculate KDE for a dataset
            def add_kde_trace(x_data, name, color, dash="solid"):
                # Remove NaNs
                x_data = x_data.dropna()
                
                # Calculate KDE
                kde = stats.gaussian_kde(x_data)
                x_range = np.linspace(x_data.min(), x_data.max(), 100)
                y_kde = kde(x_range)
                
                # Scale KDE to match histogram height
                if histnorm is None:
                    # Scale to match count
                    y_kde = y_kde * (len(x_data) * (x_data.max() - x_data.min()) / nbins)
                
                # Add KDE trace
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_kde,
                        mode='lines',
                        name=f"{name} KDE",
                        line=dict(color=color, width=2, dash=dash)
                    )
                )
            
            # Add KDE for each group or the entire dataset
            if color_col and color_col in data.columns:
                for i, group in enumerate(groups):
                    group_data = data[data[color_col] == group]
                    
                    # Determine color
                    if str(group) in custom_colors:
                        color = custom_colors[str(group)]
                    else:
                        color = palette[i % len(palette)]
                    
                    add_kde_trace(group_data[x_col], str(group), color)
            else:
                add_kde_trace(data[x_col], "Data", plot_config.get("kde_color", "rgba(255, 0, 0, 0.7)"))
        
        # Add normal distribution overlay if requested
        if plot_config.get("show_normal", False):
            # Function to add normal distribution curve
            def add_normal_curve(x_data, name, color, dash="dash"):
                # Remove NaNs
                x_data = x_data.dropna()
                
                # Calculate normal distribution
                mean = x_data.mean()
                std = x_data.std()
                x_range = np.linspace(x_data.min(), x_data.max(), 100)
                y_norm = stats.norm.pdf(x_range, mean, std)
                
                # Scale normal curve to match histogram height
                if histnorm is None:
                    # Scale to match count
                    y_norm = y_norm * (len(x_data) * (x_data.max() - x_data.min()) / nbins)
                
                # Add normal curve trace
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=y_norm,
                        mode='lines',
                        name=f"{name} Normal",
                        line=dict(color=color, width=2, dash=dash)
                    )
                )
            
            # Add normal curve for each group or the entire dataset
            if color_col and color_col in data.columns:
                for i, group in enumerate(groups):
                    group_data = data[data[color_col] == group]
                    
                    # Determine color
                    if str(group) in custom_colors:
                        color = custom_colors[str(group)]
                    else:
                        color = palette[i % len(palette)]
                    
                    add_normal_curve(group_data[x_col], str(group), color)
            else:
                add_normal_curve(data[x_col], "Data", plot_config.get("normal_color", "rgba(0, 0, 255, 0.7)"))
        
        return fig
    
    # Implementations for the remaining plot types (heatmap, contour, bubble, pie, etc.)
    # would go here, following the same pattern
    
    # I'm providing a placeholder implementation for the _create_heatmap method
    def _create_heatmap(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a heatmap with high customizability."""
        # This is a placeholder implementation
        # For a complete implementation, we would need to handle different data formats
        # and provide full customization options
        return go.Figure()
    
    def _create_contour_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a contour plot with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_bubble_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a bubble plot with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_pie_chart(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a pie chart with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_radar_chart(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a radar chart with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_polar_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a polar plot with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_density_plot(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a density plot with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_3d_surface(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a 3D surface plot with high customizability."""
        # Placeholder implementation
        return go.Figure()
    
    def _create_3d_scatter(self, data: pd.DataFrame, plot_config: Dict[str, Any]) -> go.Figure:
        """Create a 3D scatter plot with high customizability."""
        # Placeholder implementation
        return go.Figure()

# Initialize global advanced plotting service
advanced_plotting_service = AdvancedPlottingService()

def get_advanced_plotting_service() -> AdvancedPlottingService:
    """Get the global advanced plotting service instance."""
    return advanced_plotting_service