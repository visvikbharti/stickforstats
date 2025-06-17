# Performance Optimization Guide

## Overview

This document outlines specific strategies for optimizing performance in high-load operations across the StickForStats platform. The optimizations focus on the following key areas:

1. Data loading and processing
2. Statistical computations
3. Database interactions
4. Caching strategies
5. Asynchronous processing

## High-Load Operations

The following operations have been identified as performance-critical:

1. **Dataset Upload and Validation**
2. **Statistical Analysis Computations**
3. **Data Visualization Rendering**
4. **Large Dataset Handling**
5. **Multiple Concurrent Users**

## Optimization Strategies

### 1. Dataset Service Optimization

#### Current Implementation Issues

The `DatasetService` class processes datasets sequentially, which can become a bottleneck for large files:

- File reading and validation happen in the same request
- Statistical summaries are generated for all columns
- No chunking for large datasets

#### Recommended Improvements

```python
# 1. Implement chunked file reading for large datasets
def _read_dataset_file(self, dataset: Dataset, chunk_size=10000) -> Optional[pd.DataFrame]:
    """Read dataset file with chunking support for large files."""
    try:
        file_path = dataset.file.path
        
        # For small files, read directly
        if dataset.size_bytes < 10 * 1024 * 1024:  # Less than 10MB
            return self._read_file_direct(dataset)
        
        # For large files, use chunking
        chunks = []
        if dataset.file_type == 'csv':
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
        elif dataset.file_type == 'excel':
            # Excel doesn't support chunking, so read directly
            return pd.read_excel(file_path)
        elif dataset.file_type == 'json':
            # JSON lines format can be chunked
            for chunk in pd.read_json(file_path, lines=True, chunksize=chunk_size):
                chunks.append(chunk)
        
        if chunks:
            return pd.concat(chunks)
        return None
    except Exception as e:
        logger.error(f"Error reading dataset file: {str(e)}")
        return None

# 2. Use sampling for initial validation of large datasets
def quick_validate_dataset(self, dataset: Dataset, sample_size=1000) -> DatasetValidationResult:
    """Perform quick validation on a sample of a large dataset."""
    try:
        df = self._read_dataset_file(dataset)
        if df is None or df.empty:
            return DatasetValidationResult(is_valid=False, errors=["Unable to read file"], warnings=[])
            
        # Take a sample for initial validation
        if len(df) > sample_size:
            df_sample = df.sample(sample_size, random_state=42)
        else:
            df_sample = df
            
        # Basic validation checks on sample
        # ...validation code...
        
        return DatasetValidationResult(
            is_valid=True,
            errors=[],
            warnings=[f"Initial validation based on {sample_size} sample rows"],
            data_info={"total_rows": len(df), "sample_rows": len(df_sample)}
        )
    except Exception as e:
        return DatasetValidationResult(is_valid=False, errors=[str(e)], warnings=[])

# 3. Implement asynchronous metadata generation
def async_generate_metadata(self, dataset_id: int) -> None:
    """Asynchronously generate complete metadata for a dataset."""
    # This would be run as a Celery task
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        df = self._read_dataset_file(dataset)
        if df is None:
            return
            
        # Calculate comprehensive metadata
        metadata = self._generate_metadata(df)
        
        # Update dataset with metadata
        dataset.metadata = metadata
        dataset.save()
    except Exception as e:
        logger.error(f"Error in async metadata generation: {str(e)}")
```

### 2. Statistical Analysis Optimization

#### Current Implementation Issues

The `AdvancedStatisticalAnalysisService` performs intensive computations:

- All statistical tests run synchronously in the request
- Computational complexity increases with dataset size
- No caching of intermediate results
- No parallelization for independent operations

#### Recommended Improvements

```python
# 1. Implement caching for expensive computations
import functools
from django.core.cache import cache

def cached_analysis(func):
    """Cache decorator for analysis functions."""
    @functools.wraps(func)
    def wrapper(self, data, test_type, variables, options):
        # Create a cache key based on input parameters
        cache_key = f"analysis_{test_type.value}_{hash(tuple(variables.dependent_variables))}_" \
                   f"{hash(tuple(variables.independent_variables))}_" \
                   f"{hash(frozenset(options.__dict__.items()))}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for {test_type.value}")
            return cached_result
        
        # Calculate result
        result = func(self, data, test_type, variables, options)
        
        # Store in cache with timeout
        cache.set(cache_key, result, timeout=3600)  # 1 hour timeout
        return result
    return wrapper

# 2. Add the decorator to the analyze method
@cached_analysis
def analyze(self, data, test_type, variables, options):
    # Existing implementation
    # ...

# 3. Implement async analysis for long-running tests
from celery import shared_task

@shared_task
def run_analysis_task(data_dict, test_type_value, variables_dict, options_dict):
    """Celery task for running analysis asynchronously."""
    from .types import TestType, VariableSelection, AnalysisOptions
    
    # Convert back from serializable format
    data = pd.DataFrame(data_dict)
    test_type = TestType(test_type_value)
    variables = VariableSelection(**variables_dict)
    options = AnalysisOptions(**options_dict)
    
    # Create service and run analysis
    service = AdvancedStatisticalAnalysisService()
    result = service.analyze(data, test_type, variables, options)
    return result

# 4. Add method to trigger async analysis
def analyze_async(self, data, test_type, variables, options):
    """Start asynchronous analysis and return task ID."""
    # Convert to serializable format
    data_dict = data.to_dict()
    test_type_value = test_type.value
    variables_dict = variables.__dict__
    options_dict = options.__dict__
    
    # Start async task
    task = run_analysis_task.delay(data_dict, test_type_value, variables_dict, options_dict)
    return {"task_id": task.id, "status": "processing"}
```

### 3. Database Optimization

#### Current Implementation Issues

- Multiple database queries for related data
- N+1 query patterns
- Missing indices on frequently queried fields

#### Recommended Improvements

1. **Add Database Indices**

```python
# In models.py
class Dataset(models.Model):
    # Existing fields...
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['file_type']),
            models.Index(fields=['name']),
        ]

class Analysis(models.Model):
    # Existing fields...
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['dataset']),
            models.Index(fields=['analysis_type']),
        ]
```

2. **Use Select Related and Prefetch Related**

```python
# Instead of:
analyses = Analysis.objects.filter(user=user)
for analysis in analyses:
    dataset = analysis.dataset  # This causes N+1 queries

# Use:
analyses = Analysis.objects.filter(user=user).select_related('dataset')
for analysis in analyses:
    dataset = analysis.dataset  # No additional query
```

3. **Batch Database Operations**

```python
# Instead of:
for item in items:
    Model.objects.create(field1=item.value1, field2=item.value2)

# Use:
Model.objects.bulk_create([
    Model(field1=item.value1, field2=item.value2)
    for item in items
])
```

### 4. Caching Strategy

Implement a comprehensive caching strategy:

1. **Django Cache Framework**

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# User-specific data caching
def get_user_datasets(user_id):
    cache_key = f"user_datasets_{user_id}"
    datasets = cache.get(cache_key)
    if not datasets:
        datasets = list(Dataset.objects.filter(user_id=user_id))
        cache.set(cache_key, datasets, timeout=300)  # 5 minutes
    return datasets
```

2. **Template Fragment Caching**

```html
{% load cache %}

{% cache 300 user_dashboard request.user.id %}
    <!-- Dashboard content -->
{% endcache %}
```

3. **Response Caching with Middleware**

```python
# middleware.py
class APIResponseCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip caching for non-GET requests
        if request.method != 'GET':
            return self.get_response(request)
            
        # Generate cache key based on path and query params
        cache_key = f"api_response_{request.path}_{hash(frozenset(request.GET.items()))}"
        
        # Try to get from cache
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
            
        # Process the request
        response = self.get_response(request)
        
        # Cache successful responses for API endpoints
        if response.status_code == 200 and request.path.startswith('/api/'):
            cache.set(cache_key, response, timeout=60)  # 1 minute
            
        return response
```

### 5. Asynchronous Processing

Implement Celery for asynchronous processing:

1. **Configuration**

```python
# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')

app = Celery('stickforstats')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

2. **Task Definition**

```python
# tasks.py
from celery import shared_task
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_large_dataset(dataset_id):
    """Process a large dataset asynchronously."""
    from .models import Dataset
    from .services.dataset_service import DatasetService
    
    service = DatasetService()
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        df = service._read_dataset_file(dataset)
        if df is not None:
            # Perform computationally intensive operations
            result = service._generate_metadata(df)
            
            # Update dataset
            dataset.metadata = result
            dataset.processing_status = 'completed'
            dataset.save()
            
            return {"status": "success", "dataset_id": dataset_id}
    except Exception as e:
        logger.error(f"Error processing dataset {dataset_id}: {e}")
        # Update status
        dataset = Dataset.objects.get(id=dataset_id)
        dataset.processing_status = 'failed'
        dataset.processing_error = str(e)
        dataset.save()
        return {"status": "error", "dataset_id": dataset_id, "error": str(e)}
```

3. **API Endpoint for Task Status**

```python
# views.py
class TaskStatusView(APIView):
    """View for checking task status."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        
        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        })
```

### 6. Frontend Optimization

Optimize data loading and rendering on the frontend:

1. **Virtualized Lists for Large Datasets**

```jsx
import { FixedSizeList } from 'react-window';

const VirtualizedTable = ({ data }) => {
  const Row = ({ index, style }) => (
    <div style={style} className="row">
      {Object.values(data[index]).map((value, idx) => (
        <div key={idx} className="cell">{value}</div>
      ))}
    </div>
  );

  return (
    <FixedSizeList
      height={400}
      width="100%"
      itemCount={data.length}
      itemSize={35}
    >
      {Row}
    </FixedSizeList>
  );
};
```

2. **Lazy Loading Components**

```jsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyAnalysisComponent = lazy(() => import('./HeavyAnalysisComponent'));

function Dashboard() {
  return (
    <div>
      <Suspense fallback={<div>Loading analysis...</div>}>
        <HeavyAnalysisComponent />
      </Suspense>
    </div>
  );
}
```

3. **Progressive Loading and Pagination**

```jsx
function DatasetViewer({ datasetId }) {
  const [page, setPage] = useState(1);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const response = await fetch(`/api/datasets/${datasetId}/data?page=${page}&limit=100`);
      const newData = await response.json();
      setData(newData);
      setLoading(false);
    };
    
    loadData();
  }, [datasetId, page]);
  
  return (
    <div>
      {loading ? (
        <div>Loading data...</div>
      ) : (
        <>
          <DataTable data={data} />
          <Pagination
            current={page}
            onChange={setPage}
            onPageSizeChange={setPageSize}
          />
        </>
      )}
    </div>
  );
}
```

## Implementation Priorities

1. **High Priority**
   - Implement caching for statistical analysis results
   - Add database indices for frequently accessed fields
   - Set up asynchronous processing for large dataset operations

2. **Medium Priority**
   - Implement chunked file reading for large datasets
   - Add frontend optimizations for data visualization
   - Refactor N+1 query patterns

3. **Lower Priority**
   - Implement response caching middleware
   - Add virtualized rendering for all tables
   - Optimize memory usage in statistical algorithms

## Monitoring and Performance Testing

After implementing optimizations, set up monitoring to verify improvements:

1. **Load Testing**
   - Use tools like Locust or JMeter to simulate multiple users
   - Test with progressively larger datasets
   - Measure response times for common operations

2. **Profiling**
   - Django Debug Toolbar for database query analysis
   - Python profiling for CPU-intensive operations
   - React Profiler for frontend component rendering

3. **Performance Metrics**
   - Track average response times for key API endpoints
   - Monitor server resource usage (CPU, memory, disk I/O)
   - Measure database query times and cache hit rates

## Conclusion

By implementing these optimizations, the StickForStats platform will be able to handle larger datasets, more concurrent users, and more complex statistical analyses with improved performance. The most significant improvements will come from:

1. Moving computation-intensive operations to asynchronous tasks
2. Implementing appropriate caching strategies
3. Optimizing database access patterns
4. Using progressive and virtualized loading for large datasets

These enhancements will ensure that the platform remains responsive even under heavy load, providing a better user experience for data scientists and analysts working with large datasets.