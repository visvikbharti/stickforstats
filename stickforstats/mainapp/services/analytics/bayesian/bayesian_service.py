"""
Bayesian Analysis Service for StickForStats platform.
This module provides Bayesian statistical analysis functionality,
including Bayesian regression, hierarchical models, MCMC sampling,
and various Bayesian inference techniques.
"""
import pandas as pd
import numpy as np
from scipy import stats
import pymc3 as pm
import arviz as az
from typing import Dict, List, Optional, Union, Tuple, Any

class BayesianAnalysisService:
    """
    Provides Bayesian statistical analysis functionality.
    """
    
    def __init__(self):
        """Initialize the Bayesian Analysis Service."""
        pass
    
    def perform_bayesian_t_test(self, 
                               data1: List[float], 
                               data2: Optional[List[float]] = None, 
                               rope_bounds: Optional[Tuple[float, float]] = None,
                               prior_scale: float = 0.5,
                               samples: int = 10000) -> Dict[str, Any]:
        """
        Perform a Bayesian t-test (one or two sample).
        
        Args:
            data1: First sample data
            data2: Optional second sample data for two-sample test
            rope_bounds: Region of practical equivalence bounds (default: None)
            prior_scale: Scale parameter for the prior distribution (default: 0.5)
            samples: Number of posterior samples to draw (default: 10000)
            
        Returns:
            Dictionary containing posterior samples, summary statistics, 
            and probability estimates for hypothesis testing
        """
        try:
            if data2 is None:
                # One-sample test against 0
                with pm.Model() as model:
                    # Priors
                    mu = pm.Normal('mu', mu=0, sigma=prior_scale)
                    sigma = pm.HalfCauchy('sigma', beta=0.5)
                    
                    # Likelihood
                    likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=data1)
                    
                    # Sample from posterior
                    trace = pm.sample(samples, return_inferencedata=True)
                
                # Get posterior samples
                posterior_samples = az.extract(trace, var_names=['mu'])
                mu_samples = posterior_samples['mu'].values
                
                # Calculate posterior probabilities
                p_greater_than_zero = (mu_samples > 0).mean()
                p_less_than_zero = (mu_samples < 0).mean()
                
                # ROPE calculations if provided
                if rope_bounds:
                    p_rope = ((mu_samples > rope_bounds[0]) & 
                             (mu_samples < rope_bounds[1])).mean()
                else:
                    p_rope = None
                
                # Calculate Bayes factor approximation
                # Using Savage-Dickey density ratio for simple cases
                bf_01 = self._approximate_savage_dickey(mu_samples, 0, prior_scale)
                
                # Summary statistics
                summary = az.summary(trace, var_names=['mu', 'sigma'])
                
                return {
                    'test_type': 'one_sample',
                    'posterior_mean': float(summary.loc['mu', 'mean']),
                    'posterior_sd': float(summary.loc['mu', 'sd']),
                    'hdi_94': [
                        float(summary.loc['mu', 'hdi_3%']), 
                        float(summary.loc['mu', 'hdi_97%'])
                    ],
                    'p_greater_than_zero': float(p_greater_than_zero),
                    'p_less_than_zero': float(p_less_than_zero),
                    'p_rope': float(p_rope) if p_rope is not None else None,
                    'rope_bounds': rope_bounds,
                    'bayes_factor_01': float(bf_01),
                    'n_samples': len(data1)
                }
            else:
                # Two-sample test
                with pm.Model() as model:
                    # Priors
                    mu1 = pm.Normal('mu1', mu=0, sigma=prior_scale)
                    mu2 = pm.Normal('mu2', mu=0, sigma=prior_scale)
                    sigma1 = pm.HalfCauchy('sigma1', beta=0.5)
                    sigma2 = pm.HalfCauchy('sigma2', beta=0.5)
                    
                    # Difference in means
                    diff = pm.Deterministic('diff', mu1 - mu2)
                    
                    # Likelihood
                    likelihood1 = pm.Normal('likelihood1', mu=mu1, sigma=sigma1, observed=data1)
                    likelihood2 = pm.Normal('likelihood2', mu=mu2, sigma=sigma2, observed=data2)
                    
                    # Sample from posterior
                    trace = pm.sample(samples, return_inferencedata=True)
                
                # Get posterior samples
                posterior_samples = az.extract(trace, var_names=['diff'])
                diff_samples = posterior_samples['diff'].values
                
                # Calculate posterior probabilities
                p_greater_than_zero = (diff_samples > 0).mean()
                p_less_than_zero = (diff_samples < 0).mean()
                
                # ROPE calculations if provided
                if rope_bounds:
                    p_rope = ((diff_samples > rope_bounds[0]) & 
                             (diff_samples < rope_bounds[1])).mean()
                else:
                    p_rope = None
                
                # Calculate Bayes factor approximation
                bf_01 = self._approximate_savage_dickey(diff_samples, 0, prior_scale)
                
                # Summary statistics
                summary = az.summary(trace, var_names=['diff'])
                
                return {
                    'test_type': 'two_sample',
                    'posterior_mean_diff': float(summary.loc['diff', 'mean']),
                    'posterior_sd_diff': float(summary.loc['diff', 'sd']),
                    'hdi_94_diff': [
                        float(summary.loc['diff', 'hdi_3%']), 
                        float(summary.loc['diff', 'hdi_97%'])
                    ],
                    'p_greater_than_zero': float(p_greater_than_zero),
                    'p_less_than_zero': float(p_less_than_zero),
                    'p_rope': float(p_rope) if p_rope is not None else None,
                    'rope_bounds': rope_bounds,
                    'bayes_factor_01': float(bf_01),
                    'n_samples': [len(data1), len(data2)]
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'test_type': 'one_sample' if data2 is None else 'two_sample'
            }
    
    def _approximate_savage_dickey(self, 
                                  posterior_samples: np.ndarray, 
                                  point: float, 
                                  prior_scale: float) -> float:
        """
        Approximate the Bayes factor using the Savage-Dickey density ratio.
        
        Args:
            posterior_samples: Posterior samples
            point: Point at which to evaluate the Savage-Dickey ratio
            prior_scale: Scale parameter for the prior distribution
        
        Returns:
            Approximate Bayes factor BF01
        """
        # Estimate posterior density at point
        kde = stats.gaussian_kde(posterior_samples)
        posterior_density = kde(point)[0]
        
        # Calculate prior density at point
        prior_density = stats.norm.pdf(point, loc=0, scale=prior_scale)
        
        # Savage-Dickey ratio: prior_density / posterior_density
        bf_01 = prior_density / posterior_density
        
        return bf_01
    
    def perform_bayesian_correlation(self, 
                                    x: List[float], 
                                    y: List[float],
                                    prior_conc: float = 1.0,
                                    samples: int = 10000) -> Dict[str, Any]:
        """
        Perform Bayesian correlation analysis.
        
        Args:
            x: First variable data
            y: Second variable data
            prior_conc: Concentration parameter for the LKJ prior (default: 1.0)
            samples: Number of posterior samples to draw (default: 10000)
            
        Returns:
            Dictionary containing posterior correlation samples, summary statistics,
            and probability estimates for hypothesis testing
        """
        try:
            data = np.vstack([x, y]).T
            
            with pm.Model() as model:
                # Priors
                mu = pm.Normal('mu', mu=0, sigma=10, shape=2)
                sigma = pm.HalfCauchy('sigma', beta=5, shape=2)
                
                # LKJ prior for correlation matrix
                chol, corr, stds = pm.LKJCholeskyCov(
                    'chol', n=2, eta=prior_conc, sd_dist=pm.Deterministic.dist(name='stds', var=sigma), compute_corr=True
                )
                
                # Extract correlation coefficient
                rho = pm.Deterministic('rho', corr[0, 1])
                
                # Likelihood - multivariate normal
                likelihood = pm.MvNormal('likelihood', mu=mu, chol=chol, observed=data)
                
                # Sample from posterior
                trace = pm.sample(samples, return_inferencedata=True)
            
            # Get posterior samples
            posterior_samples = az.extract(trace, var_names=['rho'])
            rho_samples = posterior_samples['rho'].values
            
            # Calculate posterior probabilities
            p_greater_than_zero = (rho_samples > 0).mean()
            p_less_than_zero = (rho_samples < 0).mean()
            
            # ROPE calculations - using [-0.1, 0.1] as default ROPE
            rope_bounds = (-0.1, 0.1)
            p_rope = ((rho_samples > rope_bounds[0]) & 
                      (rho_samples < rope_bounds[1])).mean()
            
            # Summary statistics
            summary = az.summary(trace, var_names=['rho'])
            
            return {
                'posterior_mean_rho': float(summary.loc['rho', 'mean']),
                'posterior_sd_rho': float(summary.loc['rho', 'sd']),
                'hdi_94_rho': [
                    float(summary.loc['rho', 'hdi_3%']), 
                    float(summary.loc['rho', 'hdi_97%'])
                ],
                'p_greater_than_zero': float(p_greater_than_zero),
                'p_less_than_zero': float(p_less_than_zero),
                'p_rope': float(p_rope),
                'rope_bounds': rope_bounds,
                'n_samples': len(x)
            }
                
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def perform_bayesian_regression(self, 
                                   X: pd.DataFrame, 
                                   y: List[float],
                                   prior_scale: float = 1.0,
                                   samples: int = 10000) -> Dict[str, Any]:
        """
        Perform Bayesian linear regression.
        
        Args:
            X: Feature data (DataFrame)
            y: Target variable data
            prior_scale: Scale parameter for coefficient priors (default: 1.0)
            samples: Number of posterior samples to draw (default: 10000)
            
        Returns:
            Dictionary containing posterior coefficient samples, summary statistics,
            and model fit metrics
        """
        try:
            n_features = X.shape[1]
            feature_names = X.columns.tolist()
            
            with pm.Model() as model:
                # Priors
                alpha = pm.Normal('alpha', mu=0, sigma=10)
                betas = pm.Normal('betas', mu=0, sigma=prior_scale, shape=n_features)
                sigma = pm.HalfCauchy('sigma', beta=5)
                
                # Expected value
                mu = alpha
                for i in range(n_features):
                    mu = mu + betas[i] * X.iloc[:, i].values
                
                # Likelihood
                likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=y)
                
                # Sample from posterior
                trace = pm.sample(samples, return_inferencedata=True)
            
            # Extract parameter samples
            posterior_samples = az.extract(trace, var_names=['alpha', 'betas', 'sigma'])
            
            # Summary statistics
            summary = az.summary(trace)
            
            # Calculate mean predictions and residuals
            y_pred_mean = summary.loc['alpha', 'mean']
            for i in range(n_features):
                y_pred_mean += summary.loc[f'betas[{i}]', 'mean'] * X.iloc[:, i].values
            
            # Calculate R² (Bayesian R²)
            residuals = np.array(y) - y_pred_mean
            ss_residual = np.sum(residuals**2)
            ss_total = np.sum((np.array(y) - np.mean(y))**2)
            r_squared = 1 - (ss_residual / ss_total)
            
            # Prepare coefficient information
            coefficients = {}
            coefficients['intercept'] = {
                'mean': float(summary.loc['alpha', 'mean']),
                'sd': float(summary.loc['alpha', 'sd']),
                'hdi_94': [
                    float(summary.loc['alpha', 'hdi_3%']),
                    float(summary.loc['alpha', 'hdi_97%'])
                ],
                'p_greater_than_zero': float((posterior_samples['alpha'].values > 0).mean()),
                'p_less_than_zero': float((posterior_samples['alpha'].values < 0).mean())
            }
            
            for i, name in enumerate(feature_names):
                beta_key = f'betas[{i}]'
                coefficients[name] = {
                    'mean': float(summary.loc[beta_key, 'mean']),
                    'sd': float(summary.loc[beta_key, 'sd']),
                    'hdi_94': [
                        float(summary.loc[beta_key, 'hdi_3%']),
                        float(summary.loc[beta_key, 'hdi_97%'])
                    ],
                    'p_greater_than_zero': float((posterior_samples['betas'].values[:, i] > 0).mean()),
                    'p_less_than_zero': float((posterior_samples['betas'].values[:, i] < 0).mean())
                }
            
            return {
                'coefficients': coefficients,
                'sigma': float(summary.loc['sigma', 'mean']),
                'r_squared': float(r_squared),
                'n_samples': len(y),
                'n_features': n_features,
                'feature_names': feature_names,
                'waic': float(pm.waic(trace, model=model).waic),
                'loo': float(pm.loo(trace, model=model).loo)
            }
                
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def perform_bayesian_anova(self, 
                              data: pd.DataFrame, 
                              outcome_var: str,
                              group_var: str,
                              prior_scale: float = 1.0,
                              samples: int = 10000) -> Dict[str, Any]:
        """
        Perform Bayesian ANOVA (Analysis of Variance).
        
        Args:
            data: DataFrame containing the data
            outcome_var: Name of the outcome variable
            group_var: Name of the grouping variable
            prior_scale: Scale parameter for priors (default: 1.0)
            samples: Number of posterior samples to draw (default: 10000)
            
        Returns:
            Dictionary containing group comparisons, effect size estimates,
            and model fit metrics
        """
        try:
            # Extract data
            y = data[outcome_var].values
            groups = data[group_var].values
            unique_groups = np.unique(groups)
            n_groups = len(unique_groups)
            
            # Create design matrix for fixed effects
            groups_idx = np.zeros(len(groups), dtype=int)
            for i, grp in enumerate(unique_groups):
                groups_idx[groups == grp] = i
            
            with pm.Model() as model:
                # Hyperpriors
                mu = pm.Normal('mu', mu=0, sigma=10)
                sigma = pm.HalfCauchy('sigma', beta=5)
                
                # Group effects
                group_means = pm.Normal('group_means', mu=mu, sigma=prior_scale, shape=n_groups)
                
                # Expected outcome based on group
                expected = group_means[groups_idx]
                
                # Likelihood
                likelihood = pm.Normal('likelihood', mu=expected, sigma=sigma, observed=y)
                
                # Sample from posterior
                trace = pm.sample(samples, return_inferencedata=True)
                
                # Calculate contrasts (all pairwise comparisons)
                contrasts = {}
                for i in range(n_groups):
                    for j in range(i+1, n_groups):
                        contrast_name = f"{unique_groups[i]}_vs_{unique_groups[j]}"
                        contrasts[contrast_name] = pm.Deterministic(
                            contrast_name,
                            group_means[i] - group_means[j]
                        )
                
                # Re-sample with contrasts added
                trace = pm.sample(samples, return_inferencedata=True)
            
            # Summary statistics
            summary = az.summary(trace)
            
            # Calculate effect size (eta-squared)
            group_means_samples = az.extract(trace, var_names=['group_means']).group_means.values
            
            # Get mean for each group
            group_means_posterior = []
            for i in range(n_groups):
                group_means_posterior.append(group_means_samples[:, i])
            
            # Calculate eta-squared from group means
            grand_mean = np.mean(group_means_posterior)
            ss_between = 0
            for i, grp in enumerate(unique_groups):
                n_i = np.sum(groups == grp)
                ss_between += n_i * (np.mean(group_means_posterior[i]) - grand_mean)**2
            
            ss_total = np.sum((y - np.mean(y))**2)
            eta_squared = ss_between / ss_total
            
            # Prepare group information
            groups_info = {}
            for i, grp in enumerate(unique_groups):
                groups_info[str(grp)] = {
                    'mean': float(summary.loc[f'group_means[{i}]', 'mean']),
                    'sd': float(summary.loc[f'group_means[{i}]', 'sd']),
                    'hdi_94': [
                        float(summary.loc[f'group_means[{i}]', 'hdi_3%']),
                        float(summary.loc[f'group_means[{i}]', 'hdi_97%'])
                    ],
                    'n': int(np.sum(groups == grp))
                }
            
            # Prepare contrast information
            contrasts_info = {}
            for i in range(n_groups):
                for j in range(i+1, n_groups):
                    contrast_name = f"{unique_groups[i]}_vs_{unique_groups[j]}"
                    contrast_samples = az.extract(trace, var_names=[contrast_name])[contrast_name].values
                    
                    contrasts_info[contrast_name] = {
                        'mean': float(summary.loc[contrast_name, 'mean']),
                        'sd': float(summary.loc[contrast_name, 'sd']),
                        'hdi_94': [
                            float(summary.loc[contrast_name, 'hdi_3%']),
                            float(summary.loc[contrast_name, 'hdi_97%'])
                        ],
                        'p_greater_than_zero': float((contrast_samples > 0).mean()),
                        'p_less_than_zero': float((contrast_samples < 0).mean())
                    }
                    
                    # Add ROPE analysis for each contrast
                    rope_bounds = (-0.1, 0.1)  # Can be parameterized in future versions
                    p_rope = ((contrast_samples > rope_bounds[0]) & 
                           (contrast_samples < rope_bounds[1])).mean()
                    contrasts_info[contrast_name]['p_rope'] = float(p_rope)
                    contrasts_info[contrast_name]['rope_bounds'] = rope_bounds
            
            return {
                'groups': groups_info,
                'contrasts': contrasts_info,
                'eta_squared': float(eta_squared),
                'n_samples': len(y),
                'n_groups': n_groups,
                'group_names': unique_groups.tolist(),
                'waic': float(pm.waic(trace, model=model).waic),
                'loo': float(pm.loo(trace, model=model).loo)
            }
                
        except Exception as e:
            return {
                'error': str(e)
            }