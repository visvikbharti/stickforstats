"""
Machine Learning Service for StickForStats platform.
This module provides services for machine learning analysis based on the original
StickForStats Streamlit application, migrated to work as a Django service.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR, SVC
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                           accuracy_score, classification_report, confusion_matrix,
                           precision_recall_curve, roc_curve, auc)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple, Optional, Union
import logging
import json
import os
import uuid
import pickle
from pathlib import Path
from datetime import datetime

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

class MachineLearningService:
    """
    Machine Learning Service for StickForStats platform.
    
    This service provides methods for:
    - Data preparation and preprocessing
    - Model training with hyperparameter tuning
    - Model evaluation and metrics calculation
    - Visualization results preparation
    - Clustering and dimensionality reduction
    
    Based on the original MLAnalyzer class from the StickForStats Streamlit application.
    """
    
    def __init__(self):
        """Initialize machine learning service with model configurations."""
        self.regression_models = {
            'linear_regression': {
                'name': 'Linear Regression',
                'model': LinearRegression(),
                'params': {},
                'description': 'A simple linear regression model that assumes a linear relationship between inputs and target.'
            },
            'random_forest_regression': {
                'name': 'Random Forest Regression',
                'model': RandomForestRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10]
                },
                'description': 'An ensemble method that builds multiple decision trees and aggregates their predictions.'
            },
            'svr': {
                'name': 'Support Vector Regression',
                'model': SVR(),
                'params': {
                    'C': [0.1, 1, 10],
                    'kernel': ['linear', 'rbf'],
                    'gamma': ['scale', 'auto']
                },
                'description': 'A regression method based on support vector machines that's effective for non-linear relationships.'
            },
            'lasso': {
                'name': 'Lasso Regression',
                'model': Lasso(random_state=42),
                'params': {
                    'alpha': [0.01, 0.1, 1.0, 10.0],
                    'max_iter': [1000, 2000, 5000]
                },
                'description': 'Linear regression with L1 regularization that can eliminate irrelevant features.'
            },
            'ridge': {
                'name': 'Ridge Regression',
                'model': Ridge(random_state=42),
                'params': {
                    'alpha': [0.01, 0.1, 1.0, 10.0]
                },
                'description': 'Linear regression with L2 regularization that works well when features are correlated.'
            }
        }
        
        self.classification_models = {
            'logistic_regression': {
                'name': 'Logistic Regression',
                'model': LogisticRegression(random_state=42),
                'params': {
                    'C': [0.1, 1, 10],
                    'solver': ['lbfgs', 'liblinear'],
                    'max_iter': [1000, 2000]
                },
                'description': 'A classification algorithm that predicts the probability of categorical outcomes.'
            },
            'random_forest_classification': {
                'name': 'Random Forest Classification',
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10]
                },
                'description': 'An ensemble of decision trees for classification that's robust to overfitting.'
            },
            'svc': {
                'name': 'Support Vector Classification',
                'model': SVC(random_state=42, probability=True),
                'params': {
                    'C': [0.1, 1, 10],
                    'kernel': ['linear', 'rbf'],
                    'gamma': ['scale', 'auto']
                },
                'description': 'A classification method that finds the optimal hyperplane to separate classes.'
            }
        }
        
        self.clustering_models = {
            'kmeans': {
                'name': 'K-Means Clustering',
                'model': KMeans(random_state=42),
                'params': {
                    'n_clusters': [2, 3, 4, 5, 6, 7, 8],
                    'init': ['k-means++', 'random']
                },
                'description': 'A clustering algorithm that groups data points into k clusters based on similarity.'
            }
        }
        
        # Ensure model storage directory exists
        self.models_dir = Path('data/models')
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    @safe_operation
    def get_available_models(self, task_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Get available models for a specific task type.
        
        Args:
            task_type: Type of task ('regression', 'classification', 'clustering')
            
        Returns:
            Dictionary of available models with their configurations
        """
        if task_type == 'regression':
            return self.regression_models
        elif task_type == 'classification':
            return self.classification_models
        elif task_type == 'clustering':
            return self.clustering_models
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    @safe_operation
    def prepare_data(self, data: pd.DataFrame, target: str, 
                   features: List[str], test_size: float = 0.2,
                   handle_categorical: bool = True,
                   scale_features: bool = True) -> Dict[str, Any]:
        """
        Prepare data for machine learning.
        
        Args:
            data: Input DataFrame
            target: Target variable name
            features: List of feature variable names
            test_size: Proportion of data to use for testing
            handle_categorical: Whether to encode categorical variables
            scale_features: Whether to scale features
            
        Returns:
            Dictionary with processed data
        """
        # Validate inputs
        if target not in data.columns:
            raise ValueError(f"Target column '{target}' not found in data")
            
        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            raise ValueError(f"Feature columns {missing_features} not found in data")
        
        # Extract features and target
        X = data[features].copy()
        y = data[target].copy()
        
        # Track preprocessing steps for reproducibility
        preprocessing_steps = []
        
        # Handle categorical variables
        categorical_encoders = {}
        
        if handle_categorical:
            categorical_cols = X.select_dtypes(include=['object', 'category']).columns
            
            if not categorical_cols.empty:
                for col in categorical_cols:
                    # Use one-hot encoding to be consistent with the original Streamlit implementation
                    X = pd.get_dummies(X, columns=[col], drop_first=True)
                    preprocessing_steps.append(f"One-hot encoded '{col}'")
        
        # Store variable types for target
        is_classification = False
        target_encoder = None
        
        if y.dtype in ['object', 'category'] or y.nunique() < 10:
            is_classification = True
            if handle_categorical:
                target_encoder = LabelEncoder()
                y = target_encoder.fit_transform(y)
                preprocessing_steps.append(f"Label encoded target '{target}' with {len(target_encoder.classes_)} classes")
        
        # Scale features if requested
        feature_scaler = None
        
        if scale_features:
            feature_scaler = StandardScaler()
            X_columns = X.columns
            X = pd.DataFrame(feature_scaler.fit_transform(X), columns=X_columns, index=X.index)
            preprocessing_steps.append(f"Scaled features using StandardScaler")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        preprocessing_steps.append(f"Split data into {len(X_train)} training and {len(X_test)} testing samples")
        
        # Return processed data
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': X.columns.tolist(),
            'preprocessing': {
                'steps': preprocessing_steps,
                'categorical_encoders': categorical_encoders,
                'feature_scaler': feature_scaler,
                'target_encoder': target_encoder
            },
            'task_type': 'classification' if is_classification else 'regression'
        }
    
    @safe_operation
    def train_model(self, prepared_data: Dict[str, Any], 
                  model_id: str, hyper_params: Optional[Dict[str, Any]] = None,
                  perform_gridsearch: bool = True, 
                  cv_folds: int = 5) -> Dict[str, Any]:
        """
        Train a machine learning model with optional hyperparameter tuning.
        
        Args:
            prepared_data: Data prepared by prepare_data
            model_id: ID of the model to train
            hyper_params: Optional hyperparameters to override the defaults
            perform_gridsearch: Whether to perform grid search
            cv_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with training results
        """
        task_type = prepared_data['task_type']
        
        # Get the appropriate model configuration
        if task_type == 'regression':
            model_configs = self.regression_models
        elif task_type == 'classification':
            model_configs = self.classification_models
        elif task_type == 'clustering':
            model_configs = self.clustering_models
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        if model_id not in model_configs:
            raise ValueError(f"Unknown model ID: {model_id}")
            
        model_config = model_configs[model_id]
        model_inst = model_config['model']
        param_grid = hyper_params or model_config['params']
        
        # Extract training data
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        
        # Record start time
        start_time = datetime.now()
        
        # Train the model
        if perform_gridsearch and param_grid:
            scoring = 'r2' if task_type == 'regression' else 'accuracy'
            
            grid_search = GridSearchCV(
                estimator=model_inst,
                param_grid=param_grid,
                cv=cv_folds,
                n_jobs=-1,
                scoring=scoring,
                return_train_score=True
            )
            
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            cv_results = grid_search.cv_results_
        else:
            model_copy = model_inst.__class__(**model_inst.get_params())
            
            if hyper_params:
                model_copy.set_params(**hyper_params)
                
            best_model = model_copy
            best_model.fit(X_train, y_train)
            best_params = model_copy.get_params()
            
            # Compute cross-validation scores
            scoring = 'r2' if task_type == 'regression' else 'accuracy'
            cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv_folds, scoring=scoring)
            cv_results = {
                'mean_test_score': np.mean(cv_scores),
                'std_test_score': np.std(cv_scores)
            }
        
        # Record end time and compute training time
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        # Generate a unique model ID
        model_uuid = str(uuid.uuid4())
        
        # Save the model
        model_path = self.models_dir / f"{model_uuid}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': best_model,
                'preprocessing': prepared_data['preprocessing'],
                'feature_names': prepared_data['feature_names'],
                'task_type': task_type,
                'training_info': {
                    'model_id': model_id,
                    'model_name': model_config['name'],
                    'params': best_params,
                    'training_time': training_time,
                    'train_samples': len(X_train)
                }
            }, f)
        
        # Extract feature importance if available
        feature_importance = self._extract_feature_importance(best_model, prepared_data['feature_names'])
        
        # Return training results
        return {
            'model_uuid': model_uuid,
            'model_type': model_id,
            'model_name': model_config['name'],
            'best_params': best_params,
            'training_time': training_time,
            'cv_results': cv_results,
            'task_type': task_type,
            'model_path': str(model_path),
            'training_size': len(X_train),
            'feature_importance': feature_importance
        }
    
    def _extract_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """Extract feature importance if available."""
        feature_importance = {}
        
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                feature_importance = {name: float(value) for name, value 
                                     in zip(feature_names, importance)}
            elif hasattr(model, 'coef_'):
                coef = model.coef_
                # Handle different shapes of coefficients
                if len(coef.shape) == 1:
                    # Single target or binary classification
                    feature_importance = {name: float(value) for name, value 
                                         in zip(feature_names, np.abs(coef))}
                else:
                    # Multi-class or multi-target
                    avg_importance = np.mean(np.abs(coef), axis=0)
                    feature_importance = {name: float(value) for name, value 
                                         in zip(feature_names, avg_importance)}
        except Exception as e:
            logger.warning(f"Could not extract feature importance: {e}")
        
        return feature_importance
    
    @safe_operation
    def evaluate_model(self, model_uuid: str, prepared_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a trained model.
        
        Args:
            model_uuid: UUID of the trained model
            prepared_data: Data prepared by prepare_data
            
        Returns:
            Dictionary with evaluation results
        """
        # Load the model
        model_path = self.models_dir / f"{model_uuid}.pkl"
        if not os.path.exists(model_path):
            raise ValueError(f"Model with UUID {model_uuid} not found")
            
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            
        model = model_data['model']
        task_type = model_data['task_type']
        
        # Extract test data
        X_test = prepared_data['X_test']
        y_test = prepared_data['y_test']
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics based on task type
        if task_type == 'regression':
            results = self._evaluate_regression(y_test, y_pred, X_test, model)
        elif task_type == 'classification':
            results = self._evaluate_classification(y_test, y_pred, X_test, model)
        elif task_type == 'clustering':
            results = self._evaluate_clustering(X_test, model)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
            
        # Add model information to results
        results['model_uuid'] = model_uuid
        results['model_type'] = model_data['training_info']['model_id']
        results['model_name'] = model_data['training_info']['model_name']
        results['task_type'] = task_type
        
        return results
    
    def _evaluate_regression(self, y_true: np.ndarray, y_pred: np.ndarray, 
                           X_test: pd.DataFrame, model: Any) -> Dict[str, Any]:
        """Evaluate regression model."""
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Create visualization data
        fig = px.scatter(
            x=y_true, y=y_pred,
            labels={'x': 'Actual', 'y': 'Predicted'},
            title='Actual vs Predicted Values'
        )
        fig.add_trace(
            go.Scatter(x=[min(y_true), max(y_true)],
                      y=[min(y_true), max(y_true)],
                      mode='lines', name='Perfect Prediction')
        )
        
        # Convert to JSON for serialization
        plot_json = json.loads(fig.to_json())
        
        return {
            'metrics': {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2)
            },
            'predictions': {
                'true': y_true.tolist(),
                'predicted': y_pred.tolist()
            },
            'visualization': {
                'actual_vs_predicted': plot_json
            }
        }
    
    def _evaluate_classification(self, y_true: np.ndarray, y_pred: np.ndarray, 
                               X_test: pd.DataFrame, model: Any) -> Dict[str, Any]:
        """Evaluate classification model."""
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        conf_matrix = confusion_matrix(y_true, y_pred)
        class_report = classification_report(y_true, y_pred, output_dict=True)
        
        # Create confusion matrix visualization
        fig_cm = px.imshow(
            conf_matrix,
            labels=dict(x="Predicted", y="Actual"),
            title="Confusion Matrix"
        )
        
        visualization = {
            'confusion_matrix': json.loads(fig_cm.to_json())
        }
        
        # ROC curve for binary classification with probability
        if hasattr(model, 'predict_proba') and len(np.unique(y_true)) == 2:
            y_proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, thresholds = roc_curve(y_true, y_proba)
            roc_auc = auc(fpr, tpr)
            
            fig_roc = px.line(
                x=fpr, y=tpr,
                labels={'x': 'False Positive Rate', 'y': 'True Positive Rate'},
                title=f'ROC Curve (AUC = {roc_auc:.3f})'
            )
            fig_roc.add_trace(
                go.Scatter(x=[0, 1], y=[0, 1],
                          mode='lines', name='Random',
                          line=dict(dash='dash'))
            )
            
            visualization['roc_curve'] = json.loads(fig_roc.to_json())
            
            # Add probabilities and ROC data to results
            return {
                'metrics': {
                    'accuracy': float(accuracy),
                    'class_report': class_report,
                    'auc': float(roc_auc)
                },
                'confusion_matrix': conf_matrix.tolist(),
                'predictions': {
                    'true': y_true.tolist(),
                    'predicted': y_pred.tolist(),
                    'probabilities': y_proba.tolist()
                },
                'roc_data': {
                    'fpr': fpr.tolist(),
                    'tpr': tpr.tolist(),
                    'thresholds': thresholds.tolist()
                },
                'visualization': visualization
            }
        else:
            # For multiclass or models without probability
            return {
                'metrics': {
                    'accuracy': float(accuracy),
                    'class_report': class_report
                },
                'confusion_matrix': conf_matrix.tolist(),
                'predictions': {
                    'true': y_true.tolist(),
                    'predicted': y_pred.tolist()
                },
                'visualization': visualization
            }
    
    def _evaluate_clustering(self, X: pd.DataFrame, model: Any) -> Dict[str, Any]:
        """Evaluate clustering model."""
        # Make predictions
        clusters = model.predict(X)
        centroids = model.cluster_centers_
        
        # Calculate silhouette score if scikit-learn is recent enough
        try:
            from sklearn.metrics import silhouette_score
            sil_score = silhouette_score(X, clusters)
        except Exception as e:
            logger.warning(f"Could not calculate silhouette score: {e}")
            sil_score = None
        
        # Calculate inertia (sum of squared distances to closest centroid)
        inertia = model.inertia_
        
        # Perform PCA for visualization
        if X.shape[1] > 2:
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)
            centroids_pca = pca.transform(centroids)
            explained_variance = pca.explained_variance_ratio_
        else:
            X_pca = X.values
            centroids_pca = centroids
            explained_variance = np.array([1.0, 0.0] if X.shape[1] == 1 else [0.5, 0.5])
        
        # Create clustering visualization
        fig = px.scatter(
            x=X_pca[:, 0], y=X_pca[:, 1],
            color=clusters.astype(str),
            labels={'x': 'Component 1', 'y': 'Component 2'},
            title='Clustering Results (PCA Visualization)'
        )
        
        # Add centroids to the plot
        for i, centroid in enumerate(centroids_pca):
            fig.add_trace(
                go.Scatter(
                    x=[centroid[0]], y=[centroid[1]],
                    mode='markers',
                    marker=dict(size=15, symbol='x'),
                    name=f'Centroid {i}'
                )
            )
        
        return {
            'metrics': {
                'inertia': float(inertia),
                'silhouette_score': float(sil_score) if sil_score is not None else None,
                'n_clusters': len(centroids)
            },
            'clusters': clusters.tolist(),
            'centroids': centroids.tolist(),
            'pca_results': {
                'points': X_pca.tolist(),
                'centroids': centroids_pca.tolist(),
                'explained_variance': explained_variance.tolist()
            },
            'visualization': {
                'clustering': json.loads(fig.to_json())
            }
        }
    
    @safe_operation
    def perform_clustering(self, data: pd.DataFrame, n_clusters: int = 3, 
                        algorithm: str = 'kmeans',
                        features: Optional[List[str]] = None,
                        scaling: bool = True) -> Dict[str, Any]:
        """
        Perform clustering analysis.
        
        Args:
            data: Input DataFrame
            n_clusters: Number of clusters
            algorithm: Clustering algorithm to use
            features: Features to use for clustering (default: all numeric)
            scaling: Whether to scale features
            
        Returns:
            Dictionary with clustering results
        """
        # Use all numeric features if none specified
        if features is None:
            features = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Check features
        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            raise ValueError(f"Missing features in input data: {missing_features}")
        
        # Extract features
        X = data[features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features if requested
        scaler = None
        if scaling:
            scaler = StandardScaler()
            X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
        
        # Perform clustering
        if algorithm == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42)
            model.fit(X)
            
            # Evaluate the clustering
            return self._evaluate_clustering(X, model)
        else:
            raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
    
    @safe_operation
    def predict(self, model_uuid: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Make predictions with a trained model.
        
        Args:
            model_uuid: UUID of the trained model
            data: Input data for prediction
            
        Returns:
            Dictionary with predictions
        """
        # Load the model
        model_path = self.models_dir / f"{model_uuid}.pkl"
        if not os.path.exists(model_path):
            raise ValueError(f"Model with UUID {model_uuid} not found")
            
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            
        model = model_data['model']
        task_type = model_data['task_type']
        preprocessing = model_data['preprocessing']
        feature_names = model_data['feature_names']
        
        # Check features
        missing_original_features = []
        
        # Handle categorical variables if needed
        X = data.copy()
        
        # Handle categorical features (one-hot encoding)
        if preprocessing.get('categorical_encoders'):
            try:
                # Perform one-hot encoding if needed
                X = pd.get_dummies(X, drop_first=True)
                
                # Check if all required features are present
                missing_features = [f for f in feature_names if f not in X.columns]
                if missing_features:
                    return {'error': f"Missing features in input data after encoding: {missing_features}"}
                
                # Reorder columns to match training data
                X = X[feature_names]
            except Exception as e:
                return {'error': f"Error preprocessing data: {str(e)}"}
        else:
            # Without categorical encoding, just check the original features
            missing_features = [f for f in feature_names if f not in X.columns]
            if missing_features:
                return {'error': f"Missing features in input data: {missing_features}"}
            
            # Reorder columns to match training data
            X = X[feature_names]
        
        # Apply feature scaling if needed
        if preprocessing.get('feature_scaler'):
            feature_scaler = preprocessing['feature_scaler']
            X = pd.DataFrame(feature_scaler.transform(X), columns=feature_names, index=X.index)
        
        # Make predictions
        try:
            y_pred = model.predict(X)
            
            # Handle classification predictions with label encoding
            if task_type == 'classification' and preprocessing.get('target_encoder'):
                target_encoder = preprocessing['target_encoder']
                y_pred_labels = target_encoder.inverse_transform(y_pred)
                
                # For probability predictions if available
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X)
                    
                    # Create probabilities with class labels
                    probabilities = {
                        'values': y_proba.tolist(),
                        'classes': target_encoder.classes_.tolist()
                    }
                    
                    return {
                        'predictions': y_pred_labels.tolist(),
                        'predicted_classes': y_pred.tolist(),  # Numeric class indices
                        'probabilities': probabilities
                    }
                else:
                    return {
                        'predictions': y_pred_labels.tolist(),
                        'predicted_classes': y_pred.tolist()  # Numeric class indices
                    }
            elif task_type == 'clustering':
                # For clustering, also return distances to cluster centers if possible
                if hasattr(model, 'transform'):
                    distances = model.transform(X)
                    return {
                        'clusters': y_pred.tolist(),
                        'distances': distances.tolist()
                    }
                else:
                    return {
                        'clusters': y_pred.tolist()
                    }
            else:
                # For regression
                return {
                    'predictions': y_pred.tolist()
                }
                
        except Exception as e:
            return {'error': f"Error making predictions: {str(e)}"}
    
    @safe_operation
    def get_model_info(self, model_uuid: str) -> Dict[str, Any]:
        """
        Get information about a trained model.
        
        Args:
            model_uuid: UUID of the trained model
            
        Returns:
            Dictionary with model information
        """
        # Load the model
        model_path = self.models_dir / f"{model_uuid}.pkl"
        if not os.path.exists(model_path):
            raise ValueError(f"Model with UUID {model_uuid} not found")
            
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        # Remove actual model object for serialization
        model_info = {
            'uuid': model_uuid,
            'feature_names': model_data['feature_names'],
            'task_type': model_data['task_type'],
            'training_info': model_data['training_info'],
            'preprocessing_steps': model_data['preprocessing']['steps']
        }
        
        return model_info
    
    @safe_operation
    def list_trained_models(self) -> List[Dict[str, Any]]:
        """
        List all trained models.
        
        Returns:
            List of dictionaries with model information
        """
        models = []
        
        for model_file in self.models_dir.glob('*.pkl'):
            model_uuid = model_file.stem
            try:
                model_info = self.get_model_info(model_uuid)
                models.append(model_info)
            except Exception as e:
                logger.warning(f"Error loading model {model_uuid}: {str(e)}")
        
        return models
    
    @safe_operation
    def delete_model(self, model_uuid: str) -> bool:
        """
        Delete a trained model.
        
        Args:
            model_uuid: UUID of the trained model
            
        Returns:
            True if deletion was successful
        """
        model_path = self.models_dir / f"{model_uuid}.pkl"
        if not os.path.exists(model_path):
            raise ValueError(f"Model with UUID {model_uuid} not found")
            
        os.remove(model_path)
        
        return True

# Initialize global ML service
ml_service = MachineLearningService()

def get_ml_service() -> MachineLearningService:
    """Get the global ML service instance."""
    return ml_service