# RAG System API Documentation

This API provides access to the RAG (Retrieval-Augmented Generation) system functionality.

## Endpoints

### Document Management

#### `GET /api/documents/`
List all documents in the knowledge base, with optional filtering.

Query parameters:
- `document_type`: Filter by document type
- `module`: Filter by module
- `topic`: Filter by topic

#### `POST /api/documents/`
Create a new document in the knowledge base.

Request body:
```json
{
  "title": "Document Title",
  "content": "Document content text...",
  "document_type": "instruction",
  "module": "confidence_intervals",
  "topic": "basic_concepts",
  "metadata": {}
}
```

#### `GET /api/documents/{id}/`
Retrieve a specific document by ID.

#### `PUT /api/documents/{id}/`
Update a specific document.

#### `DELETE /api/documents/{id}/`
Delete a specific document.

#### `GET /api/documents/{id}/chunks/`
List all chunks for a specific document.

### Conversations

#### `GET /api/conversations/`
List all conversations for the current user.

#### `POST /api/conversations/`
Create a new conversation.

Request body:
```json
{
  "title": "Conversation Title",
  "context": {}
}
```

#### `GET /api/conversations/{id}/`
Retrieve a specific conversation by ID.

#### `PUT /api/conversations/{id}/`
Update a specific conversation.

#### `DELETE /api/conversations/{id}/`
Delete a specific conversation.

#### `GET /api/conversations/{id}/messages/`
List all messages in a specific conversation.

### Query Processing

#### `POST /api/query/`
Process a user query through the RAG system.

Request body:
```json
{
  "query": "How do I calculate a confidence interval?",
  "conversation_id": "optional-conversation-id",
  "context": {
    "module": "confidence_intervals",
    "analysis_type": "descriptive"
  },
  "filters": {
    "document_type": ["instruction", "example"],
    "module": ["confidence_intervals"]
  }
}
```

Response:
```json
{
  "response": "To calculate a confidence interval...",
  "conversation_id": "conversation-id",
  "sources": [
    {
      "document_id": "doc-id",
      "title": "Confidence Intervals Introduction",
      "chunk_text": "A confidence interval is...",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "conversation_id": "conversation-id",
    "response_id": "response-id",
    "sources": [],
    "processing_time": 0.25
  }
}
```

### Feedback

#### `POST /api/feedback/`
Submit feedback for a generated response.

Request body:
```json
{
  "response_id": "response-id",
  "rating": 4,
  "feedback_text": "This was helpful but could include more examples.",
  "improvement_suggestions": "Include step-by-step calculation examples."
}
```

### Recent Queries

#### `GET /api/recent-queries/`
Get recent queries made by the current user.

Query parameters:
- `limit`: Maximum number of queries to return (default: 10)

Response:
```json
[
  {
    "id": "query-id",
    "query_text": "How do I calculate a confidence interval?",
    "created_at": "2023-05-10T14:30:00Z",
    "response_text": "To calculate a confidence interval...",
    "response_id": "response-id",
    "conversation_id": "conversation-id"
  }
]
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response body:
```json
{
  "error": "Error message"
}
```

## Authentication

All endpoints require authentication. Include an authentication token in the request headers:

```
Authorization: Token YOUR_TOKEN_HERE
```