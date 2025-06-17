"""
Models for the SQC Analysis module.
"""

from stickforstats.sqc_analysis.models.models import (
    ControlChartAnalysis,
    ProcessCapabilityAnalysis,
    AcceptanceSamplingPlan,
    MeasurementSystemAnalysis, 
    SPCImplementationPlan
)

from stickforstats.sqc_analysis.models.economic_design import EconomicDesignAnalysis

# For backwards compatibility
from stickforstats.sqc_analysis.models.models import EconomicDesign