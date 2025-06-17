from rest_framework import serializers
from ..models import (
    Document, 
    DocumentChunk, 
    UserQuery, 
    RetrievedDocument, 
    GeneratedResponse, 
    Conversation,
    ConversationMessage
)


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'content', 'document_type', 'module', 
            'topic', 'created_at', 'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentChunkSerializer(serializers.ModelSerializer):
    """Serializer for DocumentChunk model."""
    
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'document', 'chunk_index', 'text', 'created_at', 
            'updated_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserQuerySerializer(serializers.ModelSerializer):
    """Serializer for UserQuery model."""
    
    class Meta:
        model = UserQuery
        fields = [
            'id', 'user', 'query_text', 'created_at', 'context',
            'conversation'
        ]
        read_only_fields = ['id', 'created_at']


class RetrievedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for RetrievedDocument model."""
    document_chunk = DocumentChunkSerializer(read_only=True)
    
    class Meta:
        model = RetrievedDocument
        fields = [
            'id', 'user_query', 'document_chunk', 'relevance_score',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GeneratedResponseSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedResponse model."""
    retrieved_documents = RetrievedDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = GeneratedResponse
        fields = [
            'id', 'user_query', 'response_text', 'created_at',
            'relevance_score', 'retrieved_documents', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationMessageSerializer(serializers.ModelSerializer):
    """Serializer for ConversationMessage model."""
    
    class Meta:
        model = ConversationMessage
        fields = [
            'id', 'conversation', 'message_type', 'content',
            'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    messages = ConversationMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'title', 'created_at', 'updated_at',
            'context', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QueryRequestSerializer(serializers.Serializer):
    """Serializer for query requests."""
    query = serializers.CharField(required=True)
    conversation_id = serializers.CharField(required=False, allow_null=True)
    context = serializers.JSONField(required=False, allow_null=True)
    filters = serializers.JSONField(required=False, allow_null=True)


class QueryResponseSerializer(serializers.Serializer):
    """Serializer for query responses."""
    response = serializers.CharField()
    conversation_id = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.JSONField(),
        required=False
    )
    metadata = serializers.JSONField(required=False)


class FeedbackSerializer(serializers.Serializer):
    """Serializer for feedback on a generated response."""
    response_id = serializers.CharField(required=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback_text = serializers.CharField(required=False, allow_null=True)
    improvement_suggestions = serializers.CharField(required=False, allow_null=True)