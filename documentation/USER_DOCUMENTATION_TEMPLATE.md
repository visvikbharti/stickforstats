# StickForStats User Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Account Creation](#account-creation)
   - [Logging In](#logging-in)
   - [Dashboard Overview](#dashboard-overview)
3. [Dataset Management](#dataset-management)
   - [Uploading Datasets](#uploading-datasets)
   - [Viewing Dataset Information](#viewing-dataset-information)
   - [Managing Datasets](#managing-datasets)
4. [Statistical Modules](#statistical-modules)
   - [Core Statistical Features](#core-statistical-features)
   - [Statistical Quality Control (SQC)](#statistical-quality-control-sqc)
   - [Design of Experiments (DOE)](#design-of-experiments-doe)
   - [Principal Component Analysis (PCA)](#principal-component-analysis-pca)
   - [Confidence Intervals](#confidence-intervals)
   - [Probability Distributions](#probability-distributions)
5. [Reports and Workflows](#reports-and-workflows)
   - [Creating Reports](#creating-reports)
   - [Building Workflows](#building-workflows)
6. [RAG Assistant](#rag-assistant)
7. [Troubleshooting](#troubleshooting)
8. [Appendices](#appendices)

## Introduction

StickForStats is a comprehensive statistical analysis platform designed for scientists, engineers, and quality professionals. The platform provides a range of statistical tools and visualizations to help you analyze data, make informed decisions, and communicate your findings effectively.

The platform includes the following key features:

- **Dataset Management**: Upload, view, and manage various types of datasets
- **Statistical Analysis**: Perform a wide range of statistical tests and analyses
- **Visualization Tools**: Create interactive visualizations to explore and present your data
- **Report Generation**: Generate comprehensive reports of your analyses
- **Workflow Automation**: Create and save workflows for repeated analyses
- **RAG Assistant**: Get context-aware statistical guidance and explanations

This user guide will walk you through the features and functionality of StickForStats, providing step-by-step instructions and examples to help you get the most out of the platform.

## Getting Started

### Account Creation

To create a new account:

1. Navigate to the StickForStats login page
2. Click on "Create Account"
3. Enter your email address and a secure password
4. Click "Create Account"
5. Verify your email address by clicking the link sent to your email

### Logging In

To log in to your account:

1. Navigate to the StickForStats login page
2. Enter your email address and password
3. Click "Log In"

### Dashboard Overview

Once logged in, you'll be taken to the dashboard, which provides an overview of your recent activity and quick access to the platform's features.

The dashboard includes:

- **Recent Datasets**: Your most recently uploaded or accessed datasets
- **Recent Analyses**: Your most recently performed analyses
- **Quick Start**: Shortcuts to common actions (upload dataset, create workflow, etc.)
- **Notifications**: System notifications and updates

![Dashboard Overview](dashboard_overview.png)

## Dataset Management

### Uploading Datasets

To upload a new dataset:

1. Click on "Datasets" in the main navigation menu
2. Click the "Upload Dataset" button
3. Enter a name and description for your dataset
4. Select the file to upload (CSV, Excel, or JSON format)
5. Click "Upload"

The system will validate your dataset and display a summary of the data, including:
- Number of rows and columns
- Column names and data types
- Basic statistics for numerical columns
- Missing value information

![Dataset Upload](dataset_upload.png)

### Viewing Dataset Information

To view information about a dataset:

1. Click on "Datasets" in the main navigation menu
2. Click on the dataset name in the list
3. The dataset overview page shows:
   - Dataset metadata (name, description, upload date, etc.)
   - Data preview
   - Column information
   - Basic statistics
   - Visualizations of data distribution

![Dataset Information](dataset_info.png)

### Managing Datasets

From the Datasets page, you can:

- **Search** for datasets by name or description
- **Filter** datasets by date, tags, or other criteria
- **Delete** datasets you no longer need
- **Share** datasets with other users (Enterprise plan only)
- **Download** datasets in various formats

## Statistical Modules

### Core Statistical Features

The Core Statistical Features module provides fundamental statistical analyses:

- **Descriptive Statistics**: Mean, median, mode, standard deviation, etc.
- **Correlation Analysis**: Pearson, Spearman, and Kendall correlation coefficients
- **Hypothesis Testing**: t-tests, chi-square tests, ANOVA, etc.
- **Regression Analysis**: Linear regression, multiple regression, etc.

To use the Core Statistical Features:

1. Go to "Statistics" in the main navigation menu
2. Select the dataset you want to analyze
3. Choose the type of analysis to perform
4. Configure the analysis parameters
5. Click "Run Analysis"

![Core Statistical Features](core_stats.png)

### Statistical Quality Control (SQC)

The Statistical Quality Control (SQC) module provides tools for monitoring and improving process quality:

- **Control Charts**: Create and analyze various types of control charts (X-bar, R, p, c, u, etc.)
- **Process Capability Analysis**: Calculate and visualize process capability indices (Cp, Cpk, Pp, Ppk)
- **Acceptance Sampling**: Create and evaluate acceptance sampling plans
- **Measurement System Analysis**: Conduct Gage R&R studies, linearity, and bias analyses
- **SPC Implementation**: Tools and guidance for implementing statistical process control

To use the SQC module:

1. Go to "SQC Analysis" in the main navigation menu
2. Select the dataset you want to analyze
3. Choose the type of analysis to perform
4. Configure the analysis parameters
5. Click "Generate" or "Analyze"

![SQC Analysis](sqc_analysis.png)

### Design of Experiments (DOE)

The Design of Experiments (DOE) module helps you design, analyze, and optimize experiments:

- **Experiment Design**: Create various types of experimental designs (factorial, response surface, etc.)
- **Design Analysis**: Analyze experimental results to identify significant factors
- **Response Optimization**: Find optimal settings for your process
- **Visualization**: View main effects, interaction plots, and response surfaces

To use the DOE module:

1. Go to "DOE Analysis" in the main navigation menu
2. Select "Create New Design" or "Analyze Existing Design"
3. For new designs:
   - Choose the design type
   - Specify factors and levels
   - Configure design parameters
   - Click "Generate Design"
4. For existing designs:
   - Upload or select a dataset with experimental results
   - Map columns to factors and responses
   - Click "Analyze Design"

![DOE Analysis](doe_analysis.png)

### Principal Component Analysis (PCA)

The Principal Component Analysis (PCA) module helps you analyze high-dimensional data:

- **Dimension Reduction**: Reduce the dimensionality of your data while preserving variance
- **Data Visualization**: Visualize high-dimensional data in 2D or 3D plots
- **Sample Grouping**: Identify clusters or groups in your data
- **Variable Importance**: Determine which variables contribute most to the variation

To use the PCA module:

1. Go to "PCA Analysis" in the main navigation menu
2. Select the dataset you want to analyze
3. Choose the variables to include in the analysis
4. Configure the analysis parameters
5. Click "Run PCA"

![PCA Analysis](pca_analysis.png)

### Confidence Intervals

The Confidence Intervals module provides tools for calculating and understanding confidence intervals:

- **Interval Calculations**: Calculate confidence intervals for various statistics
- **Interactive Simulations**: Explore concepts like sample size, coverage, and non-normality
- **Advanced Methods**: Bootstrap, transformation, and other advanced CI methods
- **Educational Content**: Learn about the theory and applications of confidence intervals

To use the Confidence Intervals module:

1. Go to "Confidence Intervals" in the main navigation menu
2. Select "Calculator" or "Simulations"
3. For calculators:
   - Choose the type of confidence interval
   - Input your data or statistics
   - Select confidence level
   - Click "Calculate"
4. For simulations:
   - Choose the simulation type
   - Configure simulation parameters
   - Click "Run Simulation"

![Confidence Intervals](confidence_intervals.png)

### Probability Distributions

The Probability Distributions module allows you to explore and utilize various probability distributions:

- **Distribution Visualization**: Visualize probability density/mass functions and cumulative distribution functions
- **Parameter Estimation**: Estimate distribution parameters from data
- **Probability Calculations**: Calculate probabilities for given distributions
- **Random Sampling**: Generate random samples from distributions
- **Distribution Fitting**: Find the best-fitting distribution for your data

To use the Probability Distributions module:

1. Go to "Probability Distributions" in the main navigation menu
2. Select a distribution type
3. Configure distribution parameters
4. Use the tools to calculate probabilities, generate samples, or visualize the distribution

![Probability Distributions](probability_distributions.png)

## Reports and Workflows

### Creating Reports

Reports allow you to compile and share your analyses:

1. Go to "Reports" in the main navigation menu
2. Click "Create New Report"
3. Enter a name and description for your report
4. Add sections to your report:
   - Text sections for explanations and context
   - Analysis results from any module
   - Visualizations and tables
   - References and citations
5. Arrange and format the sections as desired
6. Click "Save Report" to save as a draft or "Finalize Report" to complete
7. Share or export the report as needed

![Report Creation](report_creation.png)

### Building Workflows

Workflows allow you to automate sequences of analyses:

1. Go to "Workflows" in the main navigation menu
2. Click "Create New Workflow"
3. Enter a name and description for your workflow
4. Add steps to your workflow:
   - Data import or preprocessing
   - Analysis from any module
   - Conditional branching based on results
   - Output generation
5. Configure each step with appropriate parameters
6. Click "Save Workflow"
7. Run the workflow on new datasets as needed

![Workflow Builder](workflow_builder.png)

## RAG Assistant

The RAG (Retrieval-Augmented Generation) Assistant provides context-aware guidance and explanations:

1. Click the assistant icon in the bottom right corner of any page
2. Type your question or request in the chat box
3. The assistant will provide:
   - Explanations of statistical concepts
   - Guidance on using platform features
   - Suggestions for appropriate analyses
   - Interpretations of results
   - References to relevant documentation

![RAG Assistant](rag_assistant.png)

## Troubleshooting

### Common Issues

**Issue**: Unable to upload dataset
**Solution**: Ensure your file is in a supported format (CSV, Excel, JSON) and contains valid data. Check the file size limit (100MB).

**Issue**: Analysis fails to run
**Solution**: Check that your dataset is compatible with the analysis type. Ensure you've selected appropriate variables and parameters.

**Issue**: Visualizations not displaying
**Solution**: Try refreshing the page. Ensure your browser is up to date. Check for console errors in your browser's developer tools.

**Issue**: Performance issues with large datasets
**Solution**: Consider preprocessing your data to reduce size before upload. Use sampling features when available.

### Getting Help

If you encounter issues not covered in this documentation:

1. Check the **FAQs** section on the Support page
2. Use the **RAG Assistant** for contextual help
3. **Contact Support** via the link in the footer
4. Join the **User Community** forum for peer assistance

## Appendices

### Data Format Requirements

| Format | Requirements |
|--------|--------------|
| CSV    | Comma-separated values, UTF-8 encoding, first row as headers |
| Excel  | .xlsx format, first sheet used for data, first row as headers |
| JSON   | Array of objects with consistent keys, or object with arrays as values |

### Statistical Test Selection Guide

| Question Type | Recommended Test |
|---------------|------------------|
| Compare one group to a known value | One-sample t-test |
| Compare two independent groups | Two-sample t-test |
| Compare two related groups | Paired t-test |
| Compare three or more independent groups | ANOVA |
| Compare three or more related groups | Repeated measures ANOVA |
| Examine relationship between two continuous variables | Correlation, Linear Regression |
| Examine relationship between categorical variables | Chi-square test |

### Glossary of Terms

**ANOVA**: Analysis of Variance, a statistical test used to compare means across multiple groups.

**Bootstrap**: A resampling technique that involves random sampling with replacement to estimate statistical properties.

**Confidence Interval**: A range of values that is likely to contain a population parameter with a certain level of confidence.

**Control Chart**: A graphical tool used to monitor process stability over time.

**DOE**: Design of Experiments, a systematic approach to determine cause-and-effect relationships.

**PCA**: Principal Component Analysis, a technique for reducing the dimensionality of a dataset.

**Process Capability**: A measure of how well a process meets specifications.

**RAG**: Retrieval-Augmented Generation, a technique that combines information retrieval with text generation to provide contextual responses.

**SPC**: Statistical Process Control, a method for monitoring and controlling quality during manufacturing.

**Workflow**: A sequence of connected steps or analyses that can be automated and reused.