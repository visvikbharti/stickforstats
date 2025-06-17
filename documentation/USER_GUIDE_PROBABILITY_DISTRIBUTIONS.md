# Probability Distributions Module - User Guide

## Overview

The Probability Distributions module provides comprehensive tools for exploring, visualizing, and applying probability distributions in your statistical analyses. This module allows you to:

- Visualize probability density/mass functions and cumulative distribution functions
- Calculate probabilities for various distributions
- Generate random samples from distributions
- Estimate distribution parameters from your data
- Find the best-fitting distribution for your datasets
- Explore approximations and relationships between distributions
- Learn about theoretical foundations and applications of different distributions

This guide will walk you through each feature of the module and provide examples of common use cases.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Distribution Explorer](#distribution-explorer)
3. [Probability Calculator](#probability-calculator)
4. [Random Sample Generator](#random-sample-generator)
5. [Data Fitting](#data-fitting)
6. [Distribution Comparison](#distribution-comparison)
7. [Educational Content](#educational-content)
8. [Application Simulations](#application-simulations)
9. [Working with Custom Distributions](#working-with-custom-distributions)
10. [Saving and Sharing](#saving-and-sharing)
11. [Troubleshooting](#troubleshooting)

## Getting Started

To access the Probability Distributions module:

1. Log in to your StickForStats account
2. Click on "Probability Distributions" in the main navigation menu
3. The module's dashboard will display, showing the main features and any saved distributions

![Probability Distributions Dashboard](probability_distributions_dashboard.png)

## Distribution Explorer

The Distribution Explorer is the main interface for visualizing and exploring probability distributions.

### Selecting a Distribution

1. In the left panel, select a distribution from the dropdown menu
2. Common distributions include:
   - Normal (Gaussian)
   - Student's t
   - Chi-Square
   - F
   - Binomial
   - Poisson
   - Exponential
   - Gamma
   - Beta
   - Weibull
   - Lognormal
   - Uniform

### Configuring Parameters

After selecting a distribution, you'll see parameters specific to that distribution:

- **Normal**: Mean (μ) and Standard Deviation (σ)
- **Binomial**: Number of trials (n) and Success probability (p)
- **Poisson**: Rate (λ)
- **Exponential**: Rate (λ)
- etc.

Adjust the parameters using the sliders or input fields to see how they affect the distribution.

### Visualization Options

The main visualization area offers several display options:

- **Probability Density Function (PDF)** / **Probability Mass Function (PMF)**: Shows the density or probability of each value
- **Cumulative Distribution Function (CDF)**: Shows the probability of a value being less than or equal to a given value
- **Both PDF/PMF and CDF**: Shows both functions together
- **3D Parameter Exploration**: Visualizes how changes in parameters affect the distribution

Use the toolbar above the visualization to:
- Zoom in/out
- Pan the view
- Save the visualization as an image
- Toggle between linear and logarithmic scales
- Change the color scheme

### Example: Exploring the Normal Distribution

1. Select "Normal" from the distribution dropdown
2. Set Mean (μ) to 0 and Standard Deviation (σ) to 1 for the standard normal distribution
3. Observe the bell-shaped curve of the PDF
4. Switch to CDF view to see the S-shaped curve from 0 to 1
5. Try adjusting the parameters to see how they affect the shape:
   - Increasing μ shifts the distribution right
   - Increasing σ makes the distribution wider (more spread out)
   - Decreasing σ makes the distribution narrower (less spread out)

## Probability Calculator

The Probability Calculator allows you to calculate probabilities for specific values or ranges.

### Calculating Probabilities

1. Select the "Probability Calculator" tab
2. Choose a distribution and set its parameters
3. Select the type of probability calculation:
   - **P(X ≤ x)**: Probability of X being less than or equal to x
   - **P(X ≥ x)**: Probability of X being greater than or equal to x
   - **P(x₁ ≤ X ≤ x₂)**: Probability of X being between x₁ and x₂
   - **P(X = x)**: Probability of X being exactly x (for discrete distributions)
4. Enter the value(s) of x
5. Click "Calculate" to see the result

The result will show both the numerical probability and a visualization highlighting the relevant area under the curve.

### Example: Normal Distribution Probability

1. Select "Normal" distribution
2. Set Mean (μ) to 0 and Standard Deviation (σ) to 1
3. Choose "P(X ≤ x)"
4. Enter x = 1.96
5. Click "Calculate"
6. Result should be approximately 0.975 (97.5%)
7. The visualization will highlight the area from negative infinity to 1.96 under the normal curve

## Random Sample Generator

The Random Sample Generator allows you to create random samples from any distribution.

### Generating Random Samples

1. Select the "Random Sample Generator" tab
2. Choose a distribution and set its parameters
3. Enter the sample size (number of random values to generate)
4. Click "Generate Sample"

The results will include:
- A table of the generated values
- A histogram of the sample
- Descriptive statistics of the sample
- A Q-Q plot comparing the sample to the theoretical distribution

### Example: Generating Samples from a Binomial Distribution

1. Select "Binomial" distribution
2. Set Number of trials (n) to 20 and Success probability (p) to 0.3
3. Enter sample size of 100
4. Click "Generate Sample"
5. Observe the histogram showing the frequency of different values
6. Note how closely the sample matches the theoretical distribution

### Exporting Generated Samples

You can export the generated samples for use in other analyses:

1. Click the "Export" button below the sample table
2. Choose the export format (CSV, Excel, or JSON)
3. Save the file to your computer

## Data Fitting

The Data Fitting feature helps you find which probability distribution best fits your data.

### Fitting Distributions to Data

1. Select the "Data Fitting" tab
2. Upload your data or select an existing dataset
   - For new data: Click "Upload Data" and select a CSV or Excel file
   - For existing data: Click "Select Dataset" and choose from your datasets
3. Select the column containing the data you want to analyze
4. Click "Fit Distributions"

The system will fit multiple distributions to your data and rank them by goodness of fit, showing:
- A table of distributions and their goodness-of-fit statistics (AIC, BIC, K-S test, etc.)
- A visualization comparing the top-ranked distributions to your data
- Estimated parameters for each distribution

### Example: Finding the Best Distribution for Process Data

1. Select the "Data Fitting" tab
2. Upload a dataset containing process measurements
3. Select the measurement column
4. Click "Fit Distributions"
5. Review the results to see which distribution best represents your process
6. Click on a distribution in the results table to see detailed information about that fit

### Using the Fitted Distribution

After finding the best-fitting distribution, you can:

1. Click "Use This Distribution" to load it into the Distribution Explorer
2. Click "Save Distribution" to save it for later use
3. Click "Generate Report" to create a detailed report of the distribution fitting analysis

## Distribution Comparison

The Distribution Comparison feature allows you to compare multiple distributions side by side.

### Comparing Distributions

1. Select the "Distribution Comparison" tab
2. Add distributions to compare:
   - Click "Add Distribution"
   - Select a distribution type and set its parameters
   - Repeat to add more distributions (up to 5)
3. Choose the comparison visualizations:
   - PDF/PMF comparison
   - CDF comparison
   - Quantile comparison
   - Summary statistics comparison

### Example: Comparing Normal and Student's t Distributions

1. Select the "Distribution Comparison" tab
2. Click "Add Distribution" and select "Normal"
   - Set Mean (μ) to 0 and Standard Deviation (σ) to 1
3. Click "Add Distribution" and select "Student's t"
   - Set Degrees of Freedom (df) to 5
4. Observe the differences in the tails of the distributions
5. Note how the t-distribution has heavier tails than the normal distribution

## Educational Content

The Educational Content section provides theoretical background and practical information about probability distributions.

### Accessing Educational Content

1. Select the "Learn" tab
2. Choose a topic from the menu:
   - **Introduction to Probability Distributions**: Basic concepts and terminology
   - **Continuous Distributions**: Detailed information about continuous distributions
   - **Discrete Distributions**: Detailed information about discrete distributions
   - **Distribution Relationships**: How different distributions relate to each other
   - **Central Limit Theorem**: Interactive demonstration of the CLT
   - **Applications in Statistics**: How distributions are used in statistical analyses

### Interactive Demonstrations

Many educational topics include interactive demonstrations:

1. **Central Limit Theorem Simulator**:
   - Choose a parent distribution (e.g., uniform, exponential)
   - Set the sample size
   - Specify the number of samples
   - Observe how the sampling distribution approaches a normal distribution

2. **Distribution Animation**:
   - Watch animated visualizations of how distributions change with parameters
   - Control the animation speed and pause to examine specific values

## Application Simulations

The Application Simulations feature provides real-world examples of probability distributions in action.

### Running Simulations

1. Select the "Applications" tab
2. Choose a simulation from the list:
   - **Quality Control Decisions**: Simulates acceptance sampling using binomial distribution
   - **Reliability Engineering**: Simulates component failures using exponential or Weibull distributions
   - **Financial Risk Analysis**: Simulates investment returns using normal or lognormal distributions
   - **Queuing Theory**: Simulates arrival and service times using Poisson and exponential distributions
3. Configure the simulation parameters
4. Click "Run Simulation"
5. Observe the results and the associated visualizations

### Example: Quality Control Simulation

1. Select the "Applications" tab
2. Choose "Quality Control Decisions"
3. Set the following parameters:
   - Lot size: 1000
   - Acceptable quality level (AQL): 1%
   - Sample size: 100
   - Acceptance number: 2
4. Click "Run Simulation"
5. The simulation will show:
   - The probability of accepting lots at different defect levels
   - The operating characteristic (OC) curve
   - Risk calculations for producer and consumer
   - Animated demonstrations of the sampling process

## Working with Custom Distributions

You can create and use custom distributions based on your specific needs.

### Creating a Custom Distribution

1. Click on "Custom Distribution" in the left panel
2. Choose a method to define your distribution:
   - **Empirical**: Based directly on your data
   - **Mixture**: Combination of two or more standard distributions
   - **Truncated**: Standard distribution with restricted range
   - **Transformed**: Apply mathematical transformation to a standard distribution
3. Configure the parameters for your custom distribution
4. Click "Create Distribution"

### Example: Creating a Mixture Distribution

1. Click on "Custom Distribution"
2. Select "Mixture Distribution"
3. Add component distributions:
   - Component 1: Normal distribution with μ=0, σ=1, weight=0.7
   - Component 2: Normal distribution with μ=5, σ=0.5, weight=0.3
4. Click "Create Distribution"
5. The resulting bimodal distribution will appear in the Distribution Explorer
6. Use this custom distribution like any standard distribution

## Saving and Sharing

You can save distributions for future use and share them with colleagues.

### Saving a Distribution

1. Configure a distribution in any of the module's tools
2. Click the "Save" button
3. Enter a name and description for the distribution
4. Click "Save Distribution"

### Accessing Saved Distributions

1. Click on "My Distributions" in the left panel
2. Select a saved distribution from the list
3. The distribution will load with all its parameters

### Sharing Distributions

1. Go to "My Distributions"
2. Select the distribution you want to share
3. Click the "Share" button
4. Choose a sharing method:
   - **Link**: Generate a shareable link
   - **Export**: Download as a JSON file
   - **Workspace**: Share with your team workspace (Enterprise plan only)

## Troubleshooting

### Common Issues

**Issue**: Distribution visualization not updating
**Solution**: Ensure all parameters are within valid ranges. Try refreshing the page or clearing your browser cache.

**Issue**: Data fitting fails
**Solution**: Check your data for extreme outliers or invalid values. Ensure your dataset isn't too large (limit: 10,000 points).

**Issue**: Random sample generation is slow
**Solution**: Reduce the sample size. For very large samples, consider generating them in smaller batches.

**Issue**: Custom distribution creation error
**Solution**: Verify that all component distributions have valid parameters and weights sum to 1.0.

### Getting Help

If you encounter issues not covered here:

1. Click the "Help" button in the top right corner of the module
2. Use the RAG Assistant for contextual help
3. Check the FAQs section
4. Contact support through the support form

## Appendix: Distribution Formulas

### Continuous Distributions

**Normal Distribution**:
f(x) = (1/(σ√2π)) * e^(-(x-μ)²/(2σ²))

**Exponential Distribution**:
f(x) = λe^(-λx) for x ≥ 0

**Gamma Distribution**:
f(x) = (β^α/Γ(α)) * x^(α-1) * e^(-βx) for x > 0

### Discrete Distributions

**Binomial Distribution**:
P(X = k) = (n choose k) * p^k * (1-p)^(n-k)

**Poisson Distribution**:
P(X = k) = (λ^k * e^(-λ))/k!

**Geometric Distribution**:
P(X = k) = (1-p)^(k-1) * p for k ≥ 1