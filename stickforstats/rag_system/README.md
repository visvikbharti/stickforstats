# RAG System for StickForStats

This module implements a Retrieval-Augmented Generation (RAG) system for the StickForStats platform. The RAG system provides intelligent guidance and contextual responses to user queries by leveraging a knowledge base of documents and language models.

## Architecture

The RAG system follows a modular architecture with the following components:

1. **Models**: Data storage for documents, chunks, embeddings, user queries, and generated responses
2. **Services**: Core business logic for embedding, retrieval, generation, and the main RAG pipeline
3. **API**: RESTful API endpoints for interacting with the RAG system
4. **Frontend**: React components for the user interface

### Core Components

#### Embedding Service

The embedding service is responsible for:
- Converting text to vector embeddings
- Chunking documents into smaller pieces
- Storing embeddings in the database

#### Retrieval Service

The retrieval service is responsible for:
- Performing vector similarity search
- Ranking results by relevance
- Filtering results based on user context

#### Generation Service

The generation service is responsible for:
- Constructing prompts for the language model
- Generating responses based on retrieved context
- Formatting responses for display

#### RAG Service

The main RAG service combines the above services into a complete pipeline:
- Processes user queries
- Manages conversations and their history
- Handles document management
- Collects user feedback

## API Endpoints

The RAG system exposes the following API endpoints:

- `/rag_system/api/documents/`: CRUD operations for knowledge base documents
- `/rag_system/api/conversations/`: CRUD operations for user conversations
- `/rag_system/api/query/`: Process user queries through the RAG pipeline
- `/rag_system/api/feedback/`: Submit feedback for generated responses
- `/rag_system/api/recent-queries/`: Retrieve recent user queries

For detailed API documentation, see [API Documentation](api/README.md).

## Frontend Components

The RAG system includes several React components:

- `QueryInterface`: A chat-like interface for submitting queries and viewing responses
- `SourcesExplorer`: A component for managing knowledge base documents
- `ConversationHistory`: A component for viewing and managing conversation history
- `RAGDashboard`: A top-level component that combines the above components

## Usage

### Integrating with Other Modules

To integrate the RAG system with other modules:

1. Add the RAG Dashboard component to your module:

```jsx
import { RAGDashboard } from '../components/rag';

const YourModule = () => {
  return (
    <div>
      {/* Your module content */}
      <RAGDashboard moduleContext="your_module_name" />
    </div>
  );
};
```

2. Add documents to the knowledge base for your module:

```python
from stickforstats.rag_system.models import Document

Document.objects.create(
    title="Document Title",
    content="Document content...",
    document_type="instruction",
    module="your_module_name",
    topic="topic_name"
)
```

### Using the QueryInterface Component

For more fine-grained control, you can use the QueryInterface component directly:

```jsx
import { QueryInterface } from '../components/rag';

const YourComponent = () => {
  return (
    <div>
      {/* Your component content */}
      <QueryInterface moduleContext="your_module_name" />
    </div>
  );
};
```

## Extending the RAG System

### Adding New Document Types

To add a new document type:

1. Update the `documentTypeOptions` in `SourcesExplorer.jsx`
2. Add the new type to the database

### Customizing Response Generation

To customize how responses are generated:

1. Modify the `generate_response` method in `GenerationService`
2. Update the prompt templates in the service

## Performance Considerations

- Embeddings are cached to improve performance
- Vector similarity search is optimized for fast retrieval
- Responses are generated asynchronously where possible