"""
Statistical Tests Service for StickForStats Platform.

This module provides services for various statistical hypothesis tests,
descriptive statistics, and normality testing. It's a direct migration 
from the original Streamlit-based statistical_tests.py.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional, Tuple
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

class StatisticalTestsService:
    """Service for statistical analysis and hypothesis testing."""

    def __init__(self):
        """Initialize the statistical tests service."""
        pass

    def check_normality(self, data: pd.Series) -> Dict[str, Any]:
        """
        Perform comprehensive normality testing.
        
        Args:
            data: Data series to test for normality
            
        Returns:
            Dictionary containing test results and interpretation
        """
        try:
            results = {
                'is_normal': True,
                'tests': {},
                'reasons': [],
                'visualization_data': {}
            }
            
            # Basic statistics
            n = len(data)
            skewness = stats.skew(data)
            kurtosis = stats.kurtosis(data)
            
            # Shapiro-Wilk Test
            shapiro_stat, shapiro_p = stats.shapiro(data)
            results['tests']['Shapiro-Wilk'] = {
                'statistic': float(shapiro_stat),
                'p_value': float(shapiro_p),
                'is_normal': shapiro_p > 0.05
            }
            
            # Anderson-Darling Test
            anderson_result = stats.anderson(data)
            results['tests']['Anderson-Darling'] = {
                'statistic': float(anderson_result.statistic),
                'critical_values': [float(cv) for cv in anderson_result.critical_values],
                'significance_levels': [float(sl) for sl in anderson_result.significance_level]
            }
            
            # D'Agostino's K² Test
            k2_stat, k2_p = stats.normaltest(data)
            results['tests']['D\'Agostino K²'] = {
                'statistic': float(k2_stat),
                'p_value': float(k2_p),
                'is_normal': k2_p > 0.05
            }
            
            # Store descriptive statistics
            results['descriptive'] = {
                'n': n,
                'mean': float(np.mean(data)),
                'std': float(np.std(data)),
                'skewness': float(skewness),
                'kurtosis': float(kurtosis),
                'min': float(np.min(data)),
                'q1': float(np.percentile(data, 25)),
                'median': float(np.median(data)),
                'q3': float(np.percentile(data, 75)),
                'max': float(np.max(data))
            }
            
            # Prepare Q-Q plot data
            qq_line = stats.probplot(data, dist="norm")
            results['visualization_data']['qq_plot'] = {
                'x_theoretical': qq_line[0][0].tolist(),
                'y_sample': qq_line[0][1].tolist(),
                'slope': float(qq_line[1][0]),
                'intercept': float(qq_line[1][1])
            }
            
            # Prepare histogram data
            hist, bin_edges = np.histogram(data, bins=30, density=True)
            kde = stats.gaussian_kde(data)
            x_range = np.linspace(min(data), max(data), 100)
            results['visualization_data']['histogram'] = {
                'histogram': hist.tolist(),
                'bin_edges': bin_edges.tolist(),
                'kde_x': x_range.tolist(),
                'kde_y': kde(x_range).tolist()
            }
            
            # Make normality determination
            if shapiro_p <= 0.05:
                results['is_normal'] = False
                results['reasons'].append(f"Shapiro-Wilk test indicates non-normal distribution (p={shapiro_p:.4f})")
            
            if abs(skewness) > 1:
                results['is_normal'] = False
                results['reasons'].append(f"High skewness ({skewness:.2f})")
            
            if abs(kurtosis) > 2:
                results['is_normal'] = False
                results['reasons'].append(f"Abnormal kurtosis ({kurtosis:.2f})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in normality check: {str(e)}")
            raise

    def perform_ttest(self, data: pd.DataFrame, test_type: str, **kwargs) -> Dict[str, Any]:
        """
        Perform t-test analysis.
        
        Args:
            data: Input DataFrame
            test_type: Type of t-test ('one_sample', 'independent', 'paired')
            **kwargs: Additional arguments specific to test type
            
        Returns:
            Dictionary containing test results and visualization data
        """
        try:
            results = {'test_type': test_type}
            
            if test_type == 'one_sample':
                column = kwargs.get('column')
                pop_mean = kwargs.get('pop_mean', 0)
                
                sample_data = data[column].dropna().values
                stat, p_value = stats.ttest_1samp(sample_data, pop_mean)
                results.update({
                    'statistic': float(stat),
                    'p_value': float(p_value),
                    'population_mean': float(pop_mean),
                    'sample_mean': float(np.mean(sample_data)),
                    'sample_std': float(np.std(sample_data, ddof=1)),
                    'sample_size': len(sample_data),
                    'effect_size': float((np.mean(sample_data) - pop_mean) / np.std(sample_data, ddof=1))
                })
                
                # Prepare visualization data
                results['visualization_data'] = {
                    'boxplot': self._prepare_boxplot_data(sample_data),
                    'population_mean': float(pop_mean)
                }
                
            elif test_type == 'independent':
                group_col = kwargs.get('group_col')
                value_col = kwargs.get('value_col')
                group1 = kwargs.get('group1')
                group2 = kwargs.get('group2')
                equal_var = kwargs.get('equal_var', True)
                
                group1_data = data[data[group_col] == group1][value_col].dropna().values
                group2_data = data[data[group_col] == group2][value_col].dropna().values
                
                stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=equal_var)
                
                # Calculate effect size (Cohen's d)
                n1, n2 = len(group1_data), len(group2_data)
                mean1, mean2 = np.mean(group1_data), np.mean(group2_data)
                var1, var2 = np.var(group1_data, ddof=1), np.var(group2_data, ddof=1)
                
                # Pooled standard deviation
                pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
                effect_size = (mean1 - mean2) / pooled_std
                
                results.update({
                    'statistic': float(stat),
                    'p_value': float(p_value),
                    'equal_variances_assumed': equal_var,
                    'group1': {
                        'name': str(group1),
                        'mean': float(mean1),
                        'std': float(np.std(group1_data, ddof=1)),
                        'n': n1
                    },
                    'group2': {
                        'name': str(group2),
                        'mean': float(mean2),
                        'std': float(np.std(group2_data, ddof=1)),
                        'n': n2
                    },
                    'effect_size': float(effect_size)
                })
                
                # Prepare visualization data
                results['visualization_data'] = {
                    'group1': self._prepare_boxplot_data(group1_data),
                    'group2': self._prepare_boxplot_data(group2_data)
                }
                
            elif test_type == 'paired':
                before_col = kwargs.get('before_col')
                after_col = kwargs.get('after_col')
                
                # Get paired data (drop rows with NaN in either column)
                paired_data = data[[before_col, after_col]].dropna()
                before_data = paired_data[before_col].values
                after_data = paired_data[after_col].values
                
                stat, p_value = stats.ttest_rel(before_data, after_data)
                
                # Calculate effect size (Cohen's d for paired samples)
                diff = after_data - before_data
                mean_diff = np.mean(diff)
                std_diff = np.std(diff, ddof=1)
                effect_size = mean_diff / std_diff
                
                results.update({
                    'statistic': float(stat),
                    'p_value': float(p_value),
                    'before': {
                        'name': before_col,
                        'mean': float(np.mean(before_data)),
                        'std': float(np.std(before_data, ddof=1))
                    },
                    'after': {
                        'name': after_col,
                        'mean': float(np.mean(after_data)),
                        'std': float(np.std(after_data, ddof=1))
                    },
                    'difference': {
                        'mean': float(mean_diff),
                        'std': float(std_diff)
                    },
                    'effect_size': float(effect_size),
                    'sample_size': len(before_data)
                })
                
                # Prepare visualization data
                results['visualization_data'] = {
                    'before': self._prepare_boxplot_data(before_data),
                    'after': self._prepare_boxplot_data(after_data),
                    'difference': self._prepare_boxplot_data(diff)
                }
                
            else:
                raise ValueError(f"Unsupported t-test type: {test_type}")
            
            results['interpretation'] = self._interpret_p_value(p_value)
            return results
            
        except Exception as e:
            logger.error(f"Error in t-test: {str(e)}")
            raise

    def perform_anova(self, data: pd.DataFrame, group_col: str, value_col: str) -> Dict[str, Any]:
        """
        Perform one-way ANOVA.
        
        Args:
            data: Input DataFrame
            group_col: Column with group labels
            value_col: Column with values to analyze
            
        Returns:
            Dictionary containing ANOVA results
        """
        try:
            # Group data and check for sufficient groups
            groups = data[group_col].unique()
            if len(groups) < 2:
                raise ValueError("ANOVA requires at least 2 groups")
            
            # Create list of arrays for each group
            group_data = []
            group_names = []
            
            for group in groups:
                values = data[data[group_col] == group][value_col].dropna().values
                if len(values) > 0:
                    group_data.append(values)
                    group_names.append(str(group))
            
            # Perform ANOVA
            f_stat, p_value = stats.f_oneway(*group_data)
            
            # Calculate effect size (Eta-squared)
            grand_mean = np.mean([val for group in group_data for val in group])
            ss_total = sum([(val - grand_mean)**2 for group in group_data for val in group])
            ss_between = sum([len(group) * (np.mean(group) - grand_mean)**2 for group in group_data])
            
            eta_squared = ss_between / ss_total if ss_total > 0 else 0
            
            # Prepare group statistics
            group_stats = []
            for i, group in enumerate(group_data):
                group_stats.append({
                    'name': group_names[i],
                    'n': len(group),
                    'mean': float(np.mean(group)),
                    'std': float(np.std(group, ddof=1)),
                    'min': float(np.min(group)),
                    'max': float(np.max(group))
                })
            
            results = {
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'groups': group_stats,
                'eta_squared': float(eta_squared),
                'interpretation': self._interpret_p_value(p_value)
            }
            
            # Prepare visualization data
            visualization_data = {}
            for i, group in enumerate(group_data):
                visualization_data[group_names[i]] = self._prepare_boxplot_data(group)
            
            results['visualization_data'] = visualization_data
            
            # If significant, perform post-hoc tests
            if p_value < 0.05:
                results['post_hoc'] = self._perform_tukey_hsd(group_data, group_names)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in ANOVA: {str(e)}")
            raise

    def perform_chi_square(self, data: pd.DataFrame, var1: str, var2: str = None) -> Dict[str, Any]:
        """
        Perform Chi-square test of independence or goodness of fit.
        
        Args:
            data: Input DataFrame
            var1: First categorical variable
            var2: Second categorical variable (for independence test)
            
        Returns:
            Dictionary containing Chi-square test results
        """
        try:
            if var2 is not None:
                # Test of independence
                contingency_table = pd.crosstab(data[var1], data[var2])
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                
                # Calculate effect size (Cramer's V)
                n = contingency_table.sum().sum()
                min_dim = min(contingency_table.shape) - 1
                cramer_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0
                
                results = {
                    'test_type': 'independence',
                    'chi2_statistic': float(chi2),
                    'p_value': float(p_value),
                    'degrees_of_freedom': int(dof),
                    'cramer_v': float(cramer_v),
                    'variables': [var1, var2],
                    'interpretation': self._interpret_p_value(p_value)
                }
                
                # Convert contingency table to serializable format
                results['observed'] = contingency_table.to_dict()
                results['expected'] = pd.DataFrame(
                    expected, 
                    index=contingency_table.index, 
                    columns=contingency_table.columns
                ).to_dict()
                
                # Calculate percentages
                row_percentages = contingency_table.div(contingency_table.sum(axis=1), axis=0) * 100
                col_percentages = contingency_table.div(contingency_table.sum(axis=0), axis=1) * 100
                
                results['row_percentages'] = row_percentages.to_dict()
                results['col_percentages'] = col_percentages.to_dict()
                
            else:
                # Goodness of fit test
                observed = data[var1].value_counts().sort_index()
                n = observed.sum()
                k = len(observed)
                expected = np.repeat(n / k, k)
                
                chi2, p_value = stats.chisquare(observed, expected)
                
                results = {
                    'test_type': 'goodness_of_fit',
                    'chi2_statistic': float(chi2),
                    'p_value': float(p_value),
                    'degrees_of_freedom': k - 1,
                    'variable': var1,
                    'interpretation': self._interpret_p_value(p_value)
                }
                
                # Convert data to serializable format
                results['observed'] = observed.to_dict()
                results['expected'] = dict(zip(observed.index, expected))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Chi-square test: {str(e)}")
            raise

    def perform_correlation(self, data: pd.DataFrame, method: str = 'pearson', 
                          variables: List[str] = None) -> Dict[str, Any]:
        """
        Perform correlation analysis on variables.
        
        Args:
            data: Input DataFrame
            method: Correlation method ('pearson', 'spearman', or 'kendall')
            variables: List of variables to correlate (default: all numeric)
            
        Returns:
            Dictionary containing correlation results
        """
        try:
            # Select numeric columns if variables not specified
            if variables is None:
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) < 2:
                    raise ValueError("Need at least 2 numeric columns for correlation analysis")
                variables = numeric_cols
            
            # Validate method
            valid_methods = ['pearson', 'spearman', 'kendall']
            if method not in valid_methods:
                raise ValueError(f"Method must be one of: {', '.join(valid_methods)}")
            
            # Calculate correlation matrix
            correlation_matrix = data[variables].corr(method=method)
            
            # Calculate p-values
            p_values = pd.DataFrame(np.zeros_like(correlation_matrix), 
                                  index=correlation_matrix.index, 
                                  columns=correlation_matrix.columns)
            
            n = len(data)
            for i, x in enumerate(variables):
                for j, y in enumerate(variables):
                    if i == j:
                        p_values.iloc[i, j] = 0
                    else:
                        if method == 'pearson':
                            _, p = stats.pearsonr(data[x].dropna(), data[y].dropna())
                        elif method == 'spearman':
                            _, p = stats.spearmanr(data[x].dropna(), data[y].dropna())
                        else:  # kendall
                            _, p = stats.kendalltau(data[x].dropna(), data[y].dropna())
                        p_values.iloc[i, j] = p
            
            results = {
                'method': method,
                'variables': variables,
                'sample_size': n,
                'correlation_matrix': correlation_matrix.to_dict(),
                'p_value_matrix': p_values.to_dict()
            }
            
            # Prepare scatter plot data for all pairs
            scatter_data = {}
            for i, x in enumerate(variables):
                for j, y in enumerate(variables):
                    if i < j:  # Only lower triangle
                        key = f"{x}_vs_{y}"
                        scatter_data[key] = {
                            'x': data[x].tolist(),
                            'y': data[y].tolist(),
                            'correlation': float(correlation_matrix.iloc[i, j]),
                            'p_value': float(p_values.iloc[i, j])
                        }
            
            results['visualization_data'] = scatter_data
            
            return results
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            raise

    def get_descriptive_statistics(self, data: pd.DataFrame, 
                                 variables: List[str] = None) -> Dict[str, Any]:
        """
        Perform descriptive statistics on data.
        
        Args:
            data: Input DataFrame
            variables: List of variables to analyze (default: all)
            
        Returns:
            Dictionary containing descriptive statistics
        """
        try:
            if variables is None:
                variables = data.columns.tolist()
                
            results = {'variables': {}}
            
            for var in variables:
                # Skip non-numeric variables
                if not pd.api.types.is_numeric_dtype(data[var]):
                    results['variables'][var] = {
                        'type': 'non-numeric',
                        'unique_values': data[var].nunique(),
                        'missing': int(data[var].isna().sum())
                    }
                    continue
                
                # Calculate statistics for numeric variables
                var_data = data[var].dropna()
                
                stats_dict = {
                    'type': 'numeric',
                    'n': len(var_data),
                    'missing': int(data[var].isna().sum()),
                    'mean': float(var_data.mean()),
                    'std': float(var_data.std()),
                    'min': float(var_data.min()),
                    'q1': float(var_data.quantile(0.25)),
                    'median': float(var_data.median()),
                    'q3': float(var_data.quantile(0.75)),
                    'max': float(var_data.max()),
                    'skewness': float(stats.skew(var_data)),
                    'kurtosis': float(stats.kurtosis(var_data)),
                    'normality': {}
                }
                
                # Check normality if enough data points
                if len(var_data) >= 8:  # Minimum for Shapiro-Wilk
                    shapiro_stat, shapiro_p = stats.shapiro(var_data)
                    stats_dict['normality'] = {
                        'shapiro_statistic': float(shapiro_stat),
                        'shapiro_p_value': float(shapiro_p),
                        'is_normal': shapiro_p > 0.05
                    }
                
                # Prepare histogram data
                hist, bin_edges = np.histogram(var_data, bins=30, density=True)
                stats_dict['visualization_data'] = {
                    'histogram': hist.tolist(),
                    'bin_edges': bin_edges.tolist(),
                    'boxplot': self._prepare_boxplot_data(var_data)
                }
                
                results['variables'][var] = stats_dict
                
            return results
            
        except Exception as e:
            logger.error(f"Error in descriptive statistics: {str(e)}")
            raise

    def _prepare_boxplot_data(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Prepare boxplot data for visualization.
        
        Args:
            data: Numpy array of data
            
        Returns:
            Dictionary with boxplot statistics
        """
        if len(data) == 0:
            return {
                'min': None,
                'q1': None,
                'median': None,
                'q3': None,
                'max': None,
                'outliers': []
            }
            
        q1 = float(np.percentile(data, 25))
        q3 = float(np.percentile(data, 75))
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [float(x) for x in data if x < lower_bound or x > upper_bound]
        non_outliers = [float(x) for x in data if lower_bound <= x <= upper_bound]
        
        if non_outliers:
            return {
                'min': float(min(non_outliers)),
                'q1': q1,
                'median': float(np.median(data)),
                'q3': q3,
                'max': float(max(non_outliers)),
                'outliers': outliers
            }
        else:
            # All values are outliers
            return {
                'min': float(np.min(data)),
                'q1': q1,
                'median': float(np.median(data)),
                'q3': q3,
                'max': float(np.max(data)),
                'outliers': []
            }

    def _perform_tukey_hsd(self, group_data: List[np.ndarray], 
                         group_names: List[str]) -> Dict[str, Any]:
        """
        Perform Tukey's HSD post-hoc test.
        
        Args:
            group_data: List of arrays containing group data
            group_names: List of group names
            
        Returns:
            Dictionary with post-hoc test results
        """
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        
        # Prepare data for Tukey's test
        all_data = np.concatenate(group_data)
        group_labels = np.concatenate([[name] * len(data) for name, data in zip(group_names, group_data)])
        
        # Perform Tukey's HSD
        tukey_result = pairwise_tukeyhsd(all_data, group_labels, alpha=0.05)
        
        # Convert to serializable format
        result_list = []
        for i in range(len(tukey_result.groupsunique)):
            for j in range(i + 1, len(tukey_result.groupsunique)):
                idx = np.where((tukey_result.data[:,1] == i) & (tukey_result.data[:,2] == j))[0]
                if len(idx) > 0:
                    idx = idx[0]
                    result_list.append({
                        'group1': str(tukey_result.groupsunique[i]),
                        'group2': str(tukey_result.groupsunique[j]),
                        'meandiff': float(tukey_result.meandiffs[idx]),
                        'p_value': float(tukey_result.pvalues[idx]),
                        'lower_ci': float(tukey_result.confint[idx][0]),
                        'upper_ci': float(tukey_result.confint[idx][1]),
                        'significant': bool(tukey_result.reject[idx])
                    })
        
        return {
            'method': 'Tukey HSD',
            'alpha': 0.05,
            'comparisons': result_list
        }

    def _interpret_p_value(self, p_value: float, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Interpret p-value and provide explanation.
        
        Args:
            p_value: The p-value to interpret
            alpha: Significance level (default 0.05)
            
        Returns:
            Dictionary with interpretation
        """
        significant = p_value <= alpha
        
        if significant:
            significance_level = "strong" if p_value <= 0.01 else "moderate"
            conclusion = "reject the null hypothesis"
        else:
            significance_level = "none"
            conclusion = "fail to reject the null hypothesis"
        
        interpretation = {
            'significant': significant,
            'significance_level': significance_level,
            'conclusion': conclusion,
            'explanation': self._get_p_value_explanation(p_value, alpha)
        }
        
        return interpretation
    
    def _get_p_value_explanation(self, p_value: float, alpha: float) -> str:
        """Provide a textual explanation of the p-value result."""
        if p_value <= 0.001:
            return f"The p-value of {p_value:.4f} provides very strong evidence against the null hypothesis (p ≤ 0.001)."
        elif p_value <= 0.01:
            return f"The p-value of {p_value:.4f} provides strong evidence against the null hypothesis (p ≤ 0.01)."
        elif p_value <= 0.05:
            return f"The p-value of {p_value:.4f} provides evidence against the null hypothesis at the conventional significance level (p ≤ 0.05)."
        elif p_value <= 0.1:
            return f"The p-value of {p_value:.4f} suggests a trend that does not reach conventional statistical significance (0.05 < p ≤ 0.10)."
        else:
            return f"The p-value of {p_value:.4f} does not provide evidence against the null hypothesis (p > {alpha})."